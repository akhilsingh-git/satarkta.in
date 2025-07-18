import os
import logging
import requests
import json
import re
from datetime import datetime
from requests.exceptions import HTTPError
from dotenv import load_dotenv
from gstin_utils import verify_gstin, get_return_history

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
    Perform comprehensive fraud checks on invoice data with GST returns history
    Returns detailed fraud check results
    """
    results = {
        "fraud_score": 0,
        "fraud_flags": [],
        "checks": {},
        "gst_filing_history": {}
    }
    
    gstin = invoice_data.get("vendor_gstin", "")
    inv_no = invoice_data.get("invoice_number", "")
    inv_date = invoice_data.get("invoice_date", "")
    amount = invoice_data.get("total_amount", "0")
    
    # Check GST returns filing history
    if gstin and inv_date:
        try:
            history_result = get_return_history(
                gstin=gstin,
                api_key=API_KEY,
                api_secret=API_SECRET,
                invoice_date=inv_date
            )
            
            if history_result.get('success'):
                results['gst_filing_history'] = history_result.get('filing_history', {})
                results['checks']['gst_filing_history'] = history_result.get('summary', '')
                
                total_returns = history_result.get('total_returns', 0)
                
                if total_returns == 0:
                    results["fraud_flags"].append("No GST returns filed in last 3 years")
                    results["fraud_score"] += 40
                elif total_returns < 6:  # Less than 2 returns per year average
                    results["fraud_flags"].append(f"Low GST filing activity ({total_returns} returns in 3 years)")
                    results["fraud_score"] += 20
                else:
                    results["fraud_flags"].append(f"Regular GST filing ({total_returns} returns in 3 years)")
                    results["fraud_score"] += 0  # Good sign, no penalty
                    
            else:
                error = history_result.get('error', 'Unknown error')
                results["checks"]["gst_filing_history"] = f"Check failed: {error}"
                results["fraud_flags"].append("Unable to verify GST filing history")
                results["fraud_score"] += 15
                
        except Exception as e:
            logger.error(f"Error checking GST filing history: {e}")
            results["checks"]["gst_filing_history"] = "Check failed"
            results["fraud_flags"].append("GST filing history check failed")
            results["fraud_score"] += 15
    
    # Amount validation
    try:
        amount_val = float(re.sub(r'[^\d.]', '', str(amount)))
        if amount_val > 1000000:  # 10 lakh
            results["fraud_flags"].append("High-value transaction - requires extra verification")
            results["fraud_score"] += 10
    except:
        pass
    
    # Check if invoice number exists
    if not inv_no:
        results["fraud_flags"].append("Invoice number missing")
        results["fraud_score"] += 15
    
    # Check if amount exists
    if not amount or amount == '0':
        results["fraud_flags"].append("Amount not detected or zero")
        results["fraud_score"] += 15
    
    return results