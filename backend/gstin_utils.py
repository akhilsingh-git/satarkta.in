# Updated gstin_utils.py with corrected GST returns tracking API

import requests
import logging
import time
from typing import Dict, Optional, Tuple, Union, List
from datetime import datetime

logger = logging.getLogger(__name__)

def authenticate(api_key: str, api_secret: str) -> Optional[str]:
    """
    Authenticate and get access token for Sandbox API
    Returns the raw token (not prefixed with "Bearer ")
    """
    try:
        auth_headers = {
            "accept": "application/json",
            "x-api-key": api_key,
            "x-api-secret": api_secret,
            "x-api-version": "1.0",
        }
        
        response = requests.post(
            "https://api.sandbox.co.in/authenticate", 
            headers=auth_headers, 
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            # Get the token from the correct path based on your working example
            access_token = token_data.get("data", {}).get("access_token")
            if access_token:
                return access_token  # Return raw token, not prefixed with "Bearer "
        
        logger.error(f"Authentication failed: {response.status_code} - {response.text}")
        return None
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Authentication request error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected authentication error: {e}")
        return None

def get_vendor_name_from_gstin(gstin: str, api_key: str, api_secret: str) -> Optional[str]:
    """
    Fetch vendor name dynamically using GSTIN lookup via Sandbox API
    """
    if not gstin or len(gstin) != 15:
        return None
    
    try:
        # If API access is restricted, provide a fallback method
        # For now, we'll return None but you can implement more sophisticated fallback
        
        token = authenticate(api_key, api_secret)
        if not token:
            logger.warning(f"Could not authenticate for GSTIN {gstin}")
            return None
        
        # Updated API endpoint for GSTIN lookup
        url = "https://api.sandbox.co.in/gst/compliance/public/gstin/search"
        headers = {
            'authorization': token,
            'x-api-key': api_key,
            'x-api-version': '1.0',
            'x-accept-cache': 'true',
            'accept': 'application/json',
            'content-type': 'application/json'
        }
        
        response = requests.post(url, headers=headers, json={'gstin': gstin}, timeout=10)
        
        if response.status_code == 403:
            logger.error(f"API access restricted for GSTIN lookup: {response.text}")
            return None
        
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            logger.error(f"GSTIN lookup failed: {response.status_code} - {response.text}")
            return None
        
        data = response.json()
        
        # Extract legal name (lgnm) from multiple possible paths
        vendor_name = (
            data.get('data', {}).get('data', {}).get('lgnm') or
            data.get('data', {}).get('data', {}).get('tradeNam') or
            data.get('data', {}).get('data', {}).get('legalName') or
            data.get('data', {}).get('data', {}).get('tradeName')
        )
        
        return vendor_name.strip() if vendor_name else None
        
    except Exception as e:
        logger.error(f"Error fetching vendor name: {e}")
        return None

def get_vendor_name(gstin: str, api_key: str, api_secret: str) -> Optional[str]:
    """
    Wrapper function for getting vendor name via GSTIN
    """
    return get_vendor_name_from_gstin(gstin, api_key, api_secret)

def get_financial_year(date_str: str) -> str:
    """
    Convert date to Indian financial year format
    Financial year runs from April 1 to March 31
    Example: Date 20/09/2023 -> Financial year 2023-24
    """
    try:
        # Parse date from various formats
        date_formats = [
            "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%Y/%m/%d",
            "%d/%m/%y", "%d-%m-%y", "%b %d, %Y", "%B %d, %Y",
            "%d %b %Y", "%d %B %Y"
        ]
        
        date_obj = None
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str.strip(), fmt)
                break
            except ValueError:
                continue
        
        if not date_obj:
            logger.error(f"Could not parse date: {date_str}")
            return ""
        
        # Determine financial year
        year = date_obj.year
        month = date_obj.month
        
        if month >= 4:  # April to December
            financial_year = f"{year}-{str(year + 1)[2:]}"
        else:  # January to March
            financial_year = f"{year - 1}-{str(year)[2:]}"
        
        return financial_year
        
    except Exception as e:
        logger.error(f"Error calculating financial year: {e}")
        return ""

def get_return_history(gstin: str, api_key: str, api_secret: str, invoice_date: str) -> Dict[str, any]:
    """
    Get GST return filing status for a GSTIN for the specific financial year of the invoice date
    Returns whether returns were filed for that period
    """
    result = {
        'success': False,
        'filing_exists': False,
        'financial_year': None,
        'error': None,
        'details': [],
        'summary': 'No filing data found'
    }
    
    if not gstin or len(gstin) != 15:
        result['error'] = "Invalid GSTIN format"
        return result
    
    if not invoice_date:
        result['error'] = "Invoice date is required"
        return result
    
    try:
        # Get authentication token
        token = authenticate(api_key, api_secret)
        if not token:
            result['error'] = "Authentication failed"
            return result
        
        # Get financial year from invoice date
        financial_year = get_financial_year(invoice_date)
        if not financial_year:
            result['error'] = "Could not determine financial year from invoice date"
            return result
        
        result['financial_year'] = financial_year
        logger.info(f"Checking GST returns for {gstin} in FY: {financial_year}")
        
        # Prepare API request - EXACTLY as shown in curl example
        headers = {
            'accept': 'application/json',
            'authorization': token,  # Already includes "Bearer " prefix from authenticate()
            'content-type': 'application/json',
            'x-accept-cache': 'true',
            'x-api-key': api_key,
            'x-api-version': '1.0'
        }
        
        # URL with financial_year as query parameter
        url = f'https://api.sandbox.co.in/gst/compliance/public/gstrs/track?financial_year={financial_year}'
        
        # IMPORTANT: Body should ONLY contain gstin - nothing else!
        payload = {'gstin': gstin}
        
        logger.info(f"Making API request to: {url}")
        logger.info(f"With payload: {payload}")
        
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        
        logger.info(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if API response is valid
            if data.get('code') == 200 and 'data' in data:
                outer_data = data.get('data', {})
                inner_data = outer_data.get('data', {})
                efiled_list = inner_data.get('EFiledlist', [])
                
                logger.info(f"Found {len(efiled_list)} returns in response")
                
                # Extract filed returns
                filed_returns = []
                for ret in efiled_list:
                    if ret.get('status') == 'Filed':
                        filed_returns.append({
                            'type': ret.get('rtntype', ''),
                            'period': ret.get('ret_prd', ''),
                            'date_of_filing': ret.get('dof', ''),
                            'arn': ret.get('arn', ''),
                            'mode': ret.get('mof', '')
                        })
                
                if filed_returns:
                    result['success'] = True
                    result['filing_exists'] = True
                    result['details'] = filed_returns
                    result['summary'] = f"GST filings exist for FY {financial_year}"
                    logger.info(f"Found {len(filed_returns)} filed returns for {gstin} in FY {financial_year}")
                else:
                    result['success'] = True
                    result['summary'] = f"No GST filings found for FY {financial_year}"
                    logger.info(f"No filed returns found for {gstin} in FY {financial_year}")
                    
            else:
                result['error'] = f"Unexpected API response format: {data}"
                logger.error(f"Unexpected API response: {data}")
                
        elif response.status_code == 403:
            result['error'] = "API access restricted - Check API permissions"
            logger.error(f"API access restricted: {response.text}")
            # Still mark as success but with no filings to continue processing
            result['success'] = True
            result['filing_exists'] = False
            result['summary'] = "GST filing check requires API upgrade"
            
        elif response.status_code == 404:
            result['success'] = True  # Considered successful but no filings
            result['summary'] = f"No GST filings found for FY {financial_year}"
            logger.info(f"API returned 404 - No returns found for {gstin}")
            
        else:
            result['error'] = f"API error: {response.status_code} - {response.text}"
            logger.error(f"API error: {response.status_code} - {response.text}")
            
    except Exception as e:
        result['error'] = f"Request failed: {str(e)}"
        logger.error(f"GST return history error: {e}", exc_info=True)
    
    return result

def verify_gstin_and_get_details(gstin: str, api_key: str, api_secret: str) -> Dict[str, any]:
    """
    Verify GSTIN and return both validity status and vendor details
    """
    result = {
        'is_valid': False,
        'vendor_name': None,
        'status': None,
        'registration_date': None,
        'business_type': None,
        'error': None
    }
    
    if not gstin or len(gstin) != 15:
        result['error'] = "Invalid GSTIN format"
        return result
    
    try:
        # First get authentication token
        token = authenticate(api_key, api_secret)
        if not token:
            result['error'] = "Authentication failed"
            return result
        
        # Now make GSTIN verification request
        headers = {
            "accept": "application/json",
            "authorization": token,
            "x-api-key": api_key,
            "x-api-version": "1.0",
            "x-accept-cache": "true",  # Added as per API requirement
            "content-type": "application/json"
        }
        
        url = "https://api.sandbox.co.in/gst/compliance/taxpayer/gstin"
        payload = {"gstin": gstin}
        
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 400 and "Credential" in response.text:
            return {
            'is_valid': False,
            'vendor_name': None,
            'error': "API endpoint now requires AWS SigV4 signed headers, not just Bearer token"
        }
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                taxpayer_data = data.get('data', {})
                
                # Extract all relevant information
                status = taxpayer_data.get('status', taxpayer_data.get('taxpayerStatus', 'Unknown'))
                result['is_valid'] = status.upper() == 'ACTIVE'
                result['status'] = status
                
                # Get vendor name
                result['vendor_name'] = (
                    taxpayer_data.get('legalName') or 
                    taxpayer_data.get('legal_name') or
                    taxpayer_data.get('tradeName') or
                    taxpayer_data.get('trade_name') or 
                    taxpayer_data.get('businessName') or
                    taxpayer_data.get('business_name') or 
                    taxpayer_data.get('taxpayerName') or
                    taxpayer_data.get('taxpayer_name') or
                    taxpayer_data.get('companyName') or
                    taxpayer_data.get('company_name') or
                    taxpayer_data.get('name')
                )
                
                # Get other details
                result['registration_date'] = taxpayer_data.get('registrationDate', taxpayer_data.get('registration_date'))
                result['business_type'] = taxpayer_data.get('businessType', taxpayer_data.get('business_type'))
                
                if result['vendor_name']:
                    result['vendor_name'] = result['vendor_name'].strip()
                
                logger.info(f"GSTIN verification successful: {gstin} - {result['vendor_name']} ({result['status']})")
                
            else:
                result['error'] = "GSTIN not found or invalid"
                logger.warning(f"GSTIN verification failed: {gstin} - {data}")
                
        elif response.status_code == 401:
            result['error'] = "API authentication failed"
            logger.error("API authentication failed")
        elif response.status_code == 429:
            result['error'] = "API rate limit exceeded"
            logger.warning("API rate limit exceeded")
        else:
            result['error'] = f"API error: {response.status_code}"
            logger.error(f"API request failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        result['error'] = f"Request failed: {str(e)}"
        logger.error(f"GSTIN verification error: {e}")
    
    return result

def verify_gstin(gstin: str, api_key: str, api_secret: str) -> bool:
    """
    Legacy function for backward compatibility
    """
    result = verify_gstin_and_get_details(gstin, api_key, api_secret)
    return result['is_valid']
