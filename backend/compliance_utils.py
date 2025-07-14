# Fixed compliance_utils.py with proper Sandbox API integration

import os
import logging
import requests
import json
import re
from datetime import datetime
from requests.exceptions import HTTPError
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

BASE_URL = "https://api.sandbox.co.in"
API_KEY = os.getenv("SANDBOX_API_KEY")
API_SECRET = os.getenv("SANDBOX_API_SECRET")
API_VERSION = "1.0"

def auth_token() -> str:
    """Get authentication token from Sandbox API"""
    headers = {
        "accept": "application/json",
        "x-api-key": API_KEY,
        "x-api-secret": API_SECRET,
        "x-api-version": API_VERSION,
    }
    try:
        resp = requests.post(f"{BASE_URL}/authenticate", headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json().get("access_token", "")
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        return ""

def fetch_gstr2b(gstin: str, fp: str) -> dict:
    """
    Fetch GSTR-2B data for a given GSTIN and financial period
    fp: financial period in YYYYMM format, e.g. "202502" for Feb 2025
    Returns the raw JSON payload
    """
    try:
        token = auth_token()
        if not token:
            return {"error": "AUTH_ERROR"}
        
        headers = {
            "authorization": f"Bearer {token}",
            "x-api-key": API_KEY,
            "x-api-version": API_VERSION,
            "accept": "application/json",
        }
        
        year, month = fp[:4], fp[4:]
        url = f"{BASE_URL}/gst/compliance/tax-payer/gstrs/gstr-2b/{year}/{month}"
        
        logger.info(f"Fetching GSTR-2B for GSTIN {gstin}, period {fp}")
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        
        return resp.json()
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": "PERIOD_NOT_FOUND"}
        elif e.response.status_code == 401:
            return {"error": "UNAUTHORIZED"}
        else:
            logger.error(f"GSTR-2B API HTTP error: {e.response.status_code} - {e.response.text}")
            return {"error": "API_ERROR"}
    except Exception as e:
        logger.error(f"GSTR-2B fetch failed: {e}")
        return {"error": "ERROR"}

def reconcile_invoice(invoice: dict) -> str:
    """
    Reconcile invoice against GSTR-2B data
    invoice: {
        'vendor_gstin': '29AABCU8606Q1ZK',
        'invoice_number': 'UTL/PI0239', 
        'invoice_date': '20/02/2025',
        'total_amount': '342200'
    }
    Returns one of: MATCHED, MISMATCH (showing GSTR2B value), MISSING, ERROR
    """
    try:
        # Parse invoice date
        dt = parse_invoice_date(invoice['invoice_date'])
        if not dt:
            return "DATE_ERROR"
            
        # Build period key (YYYYMM format)
        fp = f"{dt.year}{dt.month:02d}"
        
        # Fetch GSTR-2B data
        data = fetch_gstr2b(invoice['vendor_gstin'], fp)
        
        if 'error' in data:
            return data['error']
        
        # Extract invoice details
        inv_no = invoice['invoice_number']
        inv_amt = float(re.sub(r"[^\d.]", "", str(invoice['total_amount'])))
        vendor_gstin = invoice['vendor_gstin']
        
        # Scan B2B entries in GSTR-2B
        b2b_entries = data.get("b2b", [])
        
        for entry in b2b_entries:
            if entry.get("ctin") == vendor_gstin:
                # Check invoices under this supplier
                invoices = entry.get("inv", [])
                for inv in invoices:
                    if inv.get("inum") == inv_no:
                        # Found matching invoice, check amount
                        gst_val = float(re.sub(r"[^\d.]", "", str(inv.get("val", 0))))
                        if abs(gst_val - inv_amt) < 1e-2:
                            return "MATCHED"
                        else:
                            return f"MISMATCH (GSTR-2B shows ₹{gst_val:,.2f})"
        
        return "MISSING"
        
    except Exception as e:
        logger.error(f"Invoice reconciliation failed: {e}")
        return "ERROR"

def check_gstr2b_reconciliation(gstin: str, invoice_number: str, invoice_date: str, amount: str) -> str:
    """
    Check if invoice exists in GSTR-2B using the new reconciliation logic
    """
    invoice = {
        'vendor_gstin': gstin,
        'invoice_number': invoice_number,
        'invoice_date': invoice_date,
        'total_amount': amount
    }
    
    result = reconcile_invoice(invoice)
    
    # Map results to expected format
    if result == "MATCHED":
        return "MATCHED"
    elif result == "MISSING":
        return "NOT_FILED"
    elif result.startswith("MISMATCH"):
        return f"AMOUNT_MISMATCH ({result.split('(')[1].rstrip(')')})"
    else:
        return result

def check_einvoice_irn(gstin: str, invoice_number: str, invoice_date: str, amount: str) -> str:
    """
    Check if invoice has a valid IRN (Invoice Reference Number)
    """
    try:
        token = auth_token()
        if not token:
            return "AUTH_ERROR"
        
        dt = parse_invoice_date(invoice_date)
        if not dt:
            return "DATE_ERROR"
        
        formatted_date = dt.strftime("%d/%m/%Y")
        
        # E-Invoice IRN search endpoint
        url = f"{BASE_URL}/gst/compliance/einvoice/irn"
        
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {token}",
            "x-api-key": API_KEY,
            "x-api-version": API_VERSION,
            "content-type": "application/json"
        }
        
        payload = {
            "gstin": gstin,
            "doc_num": invoice_number,
            "doc_date": formatted_date,
            "doc_amount": float(re.sub(r'[^\d.]', '', str(amount)))
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "success":
                irn = data.get("data", {}).get("irn")
                if irn:
                    return f"FOUND ({irn[:16]}...)"
                else:
                    return "NOT_GENERATED"
            else:
                return "NOT_FOUND"
        
        elif response.status_code == 404:
            return "NOT_FOUND"
        elif response.status_code == 401:
            return "UNAUTHORIZED"
        else:
            logger.error(f"E-Invoice IRN API error: {response.status_code} - {response.text}")
            return "API_ERROR"
            
    except Exception as e:
        logger.error(f"E-Invoice IRN check failed: {e}")
        return "ERROR"

def check_gst_return_filing_status(gstin: str, period: str) -> str:
    """
    Check if GST returns are filed for a specific period
    """
    try:
        token = auth_token()
        if not token:
            return "AUTH_ERROR"
        
        url = f"{BASE_URL}/gst/compliance/taxpayer/returns"
        
        headers = {
            "accept": "application/json",
            "authorization": f"Bearer {token}",
            "x-api-key": API_KEY,
            "x-api-version": API_VERSION,
            "content-type": "application/json"
        }
        
        payload = {
            "gstin": gstin,
            "ret_period": period
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            returns = data.get("data", {}).get("returns", [])
            
            gstr1_status = "NOT_FILED"
            gstr3b_status = "NOT_FILED"
            
            for ret in returns:
                if ret.get("ret_typ") == "GSTR1":
                    gstr1_status = ret.get("status", "NOT_FILED")
                elif ret.get("ret_typ") == "GSTR3B":
                    gstr3b_status = ret.get("status", "NOT_FILED")
            
            return f"GSTR-1: {gstr1_status}, GSTR-3B: {gstr3b_status}"
        
        else:
            return "API_ERROR"
            
    except Exception as e:
        logger.error(f"GST return filing check failed: {e}")
        return "ERROR"

def parse_invoice_date(date_str: str) -> datetime:
    """Parse invoice date from various formats"""
    if not date_str:
        return None
    
    date_formats = [
        "%d-%m-%Y",    # 20-09-2023
        "%d/%m/%Y",    # 20/09/2023
        "%Y-%m-%d",    # 2023-09-20
        "%Y/%m/%d",    # 2023/09/20
        "%d-%m-%y",    # 20-09-23
        "%d/%m/%y",    # 20/09/23
        "%b %d, %Y",   # Sep 20, 2023
        "%B %d, %Y",   # September 20, 2023
        "%d %b %Y",    # 20 Sep 2023
        "%d %B %Y",    # 20 September 2023
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    
    return None

def enhanced_fraud_check(invoice_data: dict) -> dict:
    """
    Perform comprehensive fraud checks on invoice data
    Returns detailed fraud check results
    """
    results = {
        "fraud_score": 0,
        "fraud_flags": [],
        "checks": {}
    }
    
    gstin = invoice_data.get("vendor_gstin", "")
    inv_no = invoice_data.get("invoice_number", "")
    inv_date = invoice_data.get("invoice_date", "")
    amount = invoice_data.get("total_amount", "0")
    
    # ITC Reconciliation
    if gstin and inv_no and inv_date and amount:
        itc_result = check_gstr2b_reconciliation(gstin, inv_no, inv_date, amount)
        results["checks"]["itc_reconciliation"] = itc_result
        
        if itc_result in ["NOT_FILED", "MISSING"]:
            results["fraud_flags"].append("ITC reconciliation failed")
            results["fraud_score"] += 30
        elif itc_result.startswith("AMOUNT_MISMATCH"):
            results["fraud_flags"].append("Amount mismatch in GSTR-1")
            results["fraud_score"] += 25
    
    # E-Invoice IRN validation
    if gstin and inv_no and inv_date and amount:
        irn_result = check_einvoice_irn(gstin, inv_no, inv_date, amount)
        results["checks"]["einvoice_irn"] = irn_result
        
        try:
            amount_val = float(re.sub(r'[^\d.]', '', str(amount)))
            if amount_val > 50000000:  # 5 crores
                if irn_result in ["NOT_FOUND", "NOT_GENERATED"]:
                    results["fraud_flags"].append("E-Invoice IRN missing for high-value invoice")
                    results["fraud_score"] += 40
        except:
            pass
    
    # GST Return Filing Status
    if gstin and inv_date:
        dt = parse_invoice_date(inv_date)
        if dt:
            period = f"{dt.month:02d}{dt.year}"
            filing_status = check_gst_return_filing_status(gstin, period)
            results["checks"]["gst_filing_status"] = filing_status
            
            if "NOT_FILED" in filing_status:
                results["fraud_flags"].append("GST returns not filed for invoice period")
                results["fraud_score"] += 20
    
    # Amount validation
    try:
        amount_val = float(re.sub(r'[^\d.]', '', str(amount)))
        if amount_val > 1000000:  # 10 lakh
            results["fraud_flags"].append("High-value transaction - requires extra verification")
            results["fraud_score"] += 10
    except:
        pass
    
    return results

# Legacy functions for backward compatibility
def check_gstr2b(invoice: dict) -> str:
    """Legacy function - use check_gstr2b_reconciliation instead"""
    return check_gstr2b_reconciliation(
        invoice.get("vendor_gstin", ""),
        invoice.get("invoice_number", ""),
        invoice.get("invoice_date", ""),
        invoice.get("total_amount", "0")
    )

def check_irp_duplicate(invoice: dict) -> bool:
    """Check if invoice has duplicate IRN"""
    irn_result = check_einvoice_irn(
        invoice.get("vendor_gstin", ""),
        invoice.get("invoice_number", ""),
        invoice.get("invoice_date", ""),
        invoice.get("total_amount", "0")
    )
    return "FOUND" in irn_result