# Fixed gstin_utils.py with enhanced error handling

import requests
import logging
import time
from typing import Dict, Optional, Tuple, Union

logger = logging.getLogger(__name__)

def authenticate(api_key: str, api_secret: str) -> Optional[str]:
    """
    Authenticate and get access token for Sandbox API
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
            access_token = token_data.get("access_token")
            if access_token:
                return f"Bearer {access_token}"
        
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
            "content-type": "application/json"
        }
        
        url = "https://api.sandbox.co.in/gst/compliance/taxpayer/gstin"
        payload = {"gstin": gstin}
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 403:
            result['error'] = "API access restricted"
            logger.error(f"API access restricted for GSTIN verification: {response.text}")
            return result
        
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