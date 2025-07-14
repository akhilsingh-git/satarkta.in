import uuid
import time
import logging
import boto3
import re
import json
from word2number import w2n
from botocore.exceptions import ClientError
import gstin_utils

logger = logging.getLogger(__name__)
s3 = boto3.client('s3')
textract = boto3.client('textract')

def _get_full_text(bucket: str, key: str) -> str:
    """Get full text from PDF using AWS Textract"""
    resp = textract.start_document_text_detection(
        DocumentLocation={'S3Object': {'Bucket': bucket, 'Name': key}}
    )
    job_id = resp['JobId']
    
    # Poll for completion
    while True:
        out = textract.get_document_text_detection(JobId=job_id)
        if out['JobStatus'] in ('SUCCEEDED', 'FAILED'):
            break
        time.sleep(2)
    
    if out['JobStatus'] != 'SUCCEEDED':
        raise RuntimeError("OCR failed")
    
    # Extract text maintaining structure
    lines = []
    for block in out.get('Blocks', []):
        if block['BlockType'] == 'LINE':
            lines.append(block['Text'])
    
    return '\n'.join(lines)

def extract_fields(pdf_bytes: bytes, bucket: str, sandbox_api_key: str = None, sandbox_api_secret: str = None) -> dict:
    """
    Upload invoice PDF to S3, OCR via Textract, and extract key fields
    """
    # Upload to S3
    key = f"raw_invoices/{uuid.uuid4()}.pdf"
    s3.put_object(Bucket=bucket, Key=key, Body=pdf_bytes)
    
    try:
        # Get OCR text
        full_text = _get_full_text(bucket, key)
        logger.info(f"OCR Text (first 500 chars): {full_text[:500]}")
        
        # Initialize result
        inv = {
            'invoice_number': '',
            'invoice_date': '',
            'total_amount': '',
            'vendor_name': '',
            'vendor_gstin': ''
        }
        
        # Clean text for processing
        text_lines = [line.strip() for line in full_text.split('\n') if line.strip()]
        text_upper = full_text.upper()
        
        # 1. Extract GSTIN (most reliable pattern)
        gstin_pattern = r'\b\d{2}[A-Z]{5}\d{4}[A-Z][0-9A-Z]Z[0-9A-Z]\b'
        gstin_matches = re.findall(gstin_pattern, full_text.upper())
        
        if gstin_matches:
            # Take the first valid GSTIN
            inv['vendor_gstin'] = gstin_matches[0]
            logger.info(f"Found GSTIN: {inv['vendor_gstin']}")
            
            # Try to get vendor name from API
            if sandbox_api_key and sandbox_api_secret and inv['vendor_gstin']:
                try:
                    vendor_details = gstin_utils.verify_gstin_and_get_details(
                        inv['vendor_gstin'], 
                        sandbox_api_key, 
                        sandbox_api_secret
                    )
                    
                    if vendor_details.get('vendor_name'):
                        inv['vendor_name'] = vendor_details['vendor_name']
                        logger.info(f"Got vendor name from API: {inv['vendor_name']}")
                except Exception as e:
                    logger.error(f"Error fetching vendor details: {e}")
        
        # 2. Extract Invoice Number (enhanced patterns)
        invoice_patterns = [
            r'\b(UTL/PI\d+)\b',
            r'\b(AIN\d{10,})\b',
            r'\b(ININMH\d{10,})\b',
            r'(?:INVOICE|INV|BILL)\s*(?:NO|NUMBER|#)?\s*[:.-]?\s*([A-Z0-9][-A-Z0-9/\\]{4,})',
            r'(?:INVOICE NUMBER|INV NO|BILL NO)\s*[:.-]?\s*([A-Z0-9][-A-Z0-9/\\]{4,})',
            r'(?:INVOICE|PROFORMA INVOICE)\s+([A-Z0-9][-A-Z0-9/\\]{4,})\s+(?:DATED|DATE)',
            r'\b([A-Z]{2,5}/[A-Z0-9]+/?\d+)\b',
            r'\b([A-Z]{2,5}-\d{4,})\b',
            r'\b(INV-?\d{4,})\b',
        ]
        
        for line in text_lines[:30]:
            line_upper = line.upper().strip()
            if re.search(r'\b(UTL/PI\d+|AIN\d{10,}|ININMH\d{10,})\b', line_upper):
                match = re.search(r'\b(UTL/PI\d+|AIN\d{10,}|ININMH\d{10,})\b', line_upper)
                if match:
                    inv['invoice_number'] = match.group(1)
                    logger.info(f"Found invoice number (direct match): {inv['invoice_number']}")
                    break
        
        if not inv['invoice_number']:
            for pattern in invoice_patterns:
                matches = re.findall(pattern, text_upper, re.MULTILINE)
                if matches:
                    valid_matches = []
                    for match in matches:
                        match_clean = match.strip()
                        if (len(match_clean) >= 4 and 
                            not re.match(r'^(DATE|DATED|TIME|GSTIN|GST|PAN|CIN|UNITED|AKHIL|NAME|EMAIL|PHONE|MOBILE|ADDRESS|TOTAL|AMOUNT|CUSTOMER|ENTORY|INVENTORY)$', match_clean) and
                            not re.match(r'^\d{10}$', match_clean) and
                            not re.match(r'^\d{6}$', match_clean) and
                            not re.search(r'(ROAD|STREET|FLOOR|BUILDING|BANGALORE|DELHI|MUMBAI|CHENNAI|KOLKATA)', match_clean)):
                            valid_matches.append(match_clean)
                    
                    if valid_matches:
                        for vm in valid_matches:
                            if re.match(r'^(UTL/|AIN|ININMH)', vm):
                                inv['invoice_number'] = vm
                                break
                        
                        if not inv['invoice_number']:
                            structured_matches = [m for m in valid_matches if re.search(r'[A-Z]', m) and re.search(r'\d', m) and ('/' in m or '-' in m)]
                            if structured_matches:
                                inv['invoice_number'] = structured_matches[0]
                            elif valid_matches:
                                inv['invoice_number'] = valid_matches[0]
                        
                        if inv['invoice_number']:
                            logger.info(f"Found invoice number: {inv['invoice_number']}")
                            break
        
        # 3. Extract Date (enhanced patterns)
        date_patterns = [
            r'(?:DATE|DATED|INVOICE DATE|BILL DATE)?\s*[:.-]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{4})',
            r'(?:DATE|DATED)?\s*[:.-]?\s*(\d{1,2}[-/](?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[-/]\d{4})',
            r'(?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{1,2},?\s+\d{4}',
            r'(?:DATE|DATED)?\s*[:.-]?\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})',
            r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b',
            r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text_upper, re.IGNORECASE)
            if matches:
                inv['invoice_date'] = matches[0]
                logger.info(f"Found invoice date: {inv['invoice_date']}")
                break
        
        # 4. Extract Amount (UPDATED LOGIC)
        final_amount = None

        # Priority 1: Search for the most reliable keywords for the final amount.
        priority_1_pattern = r'(?:GRAND TOTAL|FINAL AMOUNT|TOTAL AMOUNT IN INR)\s*(?:₹|RS\.?|INR)?\s*([0-9,]+(?:\.[0-9]{2})?)'
        matches = re.findall(priority_1_pattern, full_text, re.IGNORECASE)
        if matches:
            try:
                clean_amount = re.sub(r'[^\d.]', '', matches[0])
                final_amount = float(clean_amount)
                logger.info(f"Found priority 1 amount: {final_amount}")
            except (ValueError, IndexError):
                pass

        # If no high-priority amount found, collect all possible amounts and pick the largest.
        if final_amount is None:
            all_amounts = []
            amount_patterns = [
                r'(?:TOTAL|SUBTOTAL|TOTAL AMOUNT|NET AMOUNT)\s*(?:₹|RS\.?|INR)?\s*([0-9,]+(?:\.[0-9]{2})?)',
                r'₹\s*([0-9,]+(?:\.[0-9]{2})?)',
                r'Rs\.?\s*([0-9,]+(?:\.[0-9]{2})?)',
                r'\b([0-9]{1,3}(?:,[0-9]{3})+(?:\.[0-9]{2})?)\b'
            ]

            for pattern in amount_patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    try:
                        clean_amount_str = re.sub(r'[^\d.]', '', str(match))
                        if clean_amount_str and not all(c in '0.' for c in clean_amount_str):
                            amount_val = float(clean_amount_str)
                            if not (len(clean_amount_str) == 10 and clean_amount_str[0] in '6789') and \
                               not (len(clean_amount_str) == 6 and '.' not in clean_amount_str):
                                if 0.01 <= amount_val <= 100000000:
                                    all_amounts.append(amount_val)
                    except ValueError:
                        continue
            
            if all_amounts:
                unique_amounts = sorted(list(set(all_amounts)), reverse=True)
                logger.info(f"Found potential amounts: {unique_amounts}")
                final_amount = unique_amounts[0]

        # Fallback to amount in words if no numeric amount is found.
        if final_amount is None:
            word_patterns = [
                r"Amount in words[:\-\s]*:?\s*([A-Za-z\s\-]+?)(?:\n|$|Rs|Rupees)",
            ]
            for pattern in word_patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                if matches:
                    try:
                        word_amount = matches[0].strip()
                        word_amount = re.sub(r'(?:rupees?|only|and|paise|rs\.?)', '', word_amount, flags=re.IGNORECASE).strip()
                        if word_amount:
                            numeric_amount = w2n.word_to_num(word_amount)
                            if 100 <= numeric_amount <= 100000000:
                                final_amount = numeric_amount
                                logger.info(f"Found amount from words: {final_amount}")
                                break
                    except Exception:
                        continue

        if final_amount is not None:
            inv['total_amount'] = str(final_amount)
            logger.info(f"Final extracted amount: {inv['total_amount']}")
        
        # 5. Extract Vendor Name (if not from API)
        if not inv['vendor_name']:
            if 'AMAZON WEB SERVICES' in text_upper:
                inv['vendor_name'] = 'Amazon Web Services India Private Limited'
            elif 'ATLYS' in text_upper:
                inv['vendor_name'] = 'Atlys India Private Limited'
            elif 'UNITED TECHNOLINK' in text_upper:
                inv['vendor_name'] = 'United Technolink Pvt Ltd'
            else:
                vendor_patterns = [
                    r'^([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+(?:PVT\.?\s*)?(?:LTD|LIMITED)\.?)$',
                    r'^([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+(?:PRIVATE\s+)?LIMITED)$',
                    r'^([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*\s+(?:TECHNOLOGIES|SOLUTIONS|SERVICES|ENTERPRISES|INDUSTRIES))$',
                    r'(?:FROM|SOLD BY|SUPPLIER|VENDOR)\s*[:.-]\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)',
                ]
                
                for line in text_lines[:15]:
                    line = line.strip()
                    
                    if (len(line) < 5 or 
                        re.search(r'(?:INVOICE|BILL|GST|GSTIN|DATE|ORIGINAL|TAX|PROFORMA|SIGNATURE)', line, re.IGNORECASE) or
                        re.search(r'^\d+$', line) or
                        re.search(r'\d{2}[-/]\d{2}[-/]\d{4}', line) or
                        line.upper() in ['NAME: AKHIL SINGH', 'AKHIL SINGH']):
                        continue
                    
                    for pattern in vendor_patterns:
                        match = re.match(pattern, line, re.IGNORECASE)
                        if match:
                            inv['vendor_name'] = match.group(1).strip()
                            logger.info(f"Found vendor name from OCR: {inv['vendor_name']}")
                            break
                    
                    if inv['vendor_name']:
                        break
            
            logger.info(f"Final vendor name: {inv['vendor_name']}")
        
        logger.info(f"Extraction complete: {json.dumps(inv, indent=2)}")
        
        for key in inv:
            if isinstance(inv[key], str):
                inv[key] = inv[key].strip()
        
        return inv
        
    except Exception as e:
        logger.error(f"Error extracting invoice fields: {e}")
        return {
            'invoice_number': '',
            'invoice_date': '',
            'total_amount': '',
            'vendor_name': '',
            'vendor_gstin': ''
        }
    finally:
        try:
            s3.delete_object(Bucket=bucket, Key=key)
        except:
            pass
