"""
Bank Account Verification Module using Sandbox API
Implements penny-less bank account verification
"""

import os
import logging
import requests
from datetime import datetime
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class BankAccountVerifier:
    def __init__(self):
        self.base_url = "https://api.sandbox.co.in"
        self.api_key = os.getenv("SANDBOX_API_KEY")
        self.api_secret = os.getenv("SANDBOX_API_SECRET")
        self.api_version = "1.0"
        
    def _get_auth_token(self) -> Optional[str]:
        """Get authentication token from Sandbox API"""
        try:
            headers = {
                "accept": "application/json",
                "x-api-key": self.api_key,
                "x-api-secret": self.api_secret,
                "x-api-version": self.api_version,
            }
            
            response = requests.post(
                f"{self.base_url}/authenticate", 
                headers=headers, 
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            # Extract the access_token from the response
            access_token = data.get("data", {}).get("access_token")
            if access_token:
                return access_token
            
            logger.error(f"No access token in response: {data}")
            return None
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return None
    
    def verify_bank_account(self, account_number: str, ifsc_code: str, 
                          account_holder_name: str = None) -> Dict:
        """
        Verify bank account using penny-less verification
        
        Args:
            account_number: Bank account number
            ifsc_code: IFSC code of the bank
            account_holder_name: Optional account holder name for name matching
            
        Returns:
            Dict containing verification results
        """
        try:
            token = self._get_auth_token()
            if not token:
                return {
                    "success": False,
                    "error": "Authentication failed",
                    "status": "AUTH_ERROR"
                }
            
            # Extract bank code from IFSC (first 4 characters)
            if len(ifsc_code) < 4:
                return {
                    "success": False,
                    "error": "Invalid IFSC code format",
                    "status": "INVALID_IFSC"
                }
            
            bank_code = ifsc_code[:4]
            
            # Construct the URL as per the API documentation
            url = f"{self.base_url}/bank/{ifsc_code}/accounts/{account_number}/penniless-verify"
            
            headers = {
                "accept": "application/json",
                "authorization": token,  # Use the token directly
                "x-api-key": self.api_key,
                "x-accept-cache": "true",
                "x-api-version": self.api_version
            }
            
            logger.info(f"Making request to: {url}")
            
            response = requests.get(url, headers=headers, timeout=30)
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response text: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("code") == 200:
                    response_data = data.get("data", {})
                    account_exists = response_data.get("account_exists", False)
                    name_at_bank = response_data.get("name_at_bank", "")
                    
                    # Calculate name match if account holder name is provided
                    name_match = None
                    if account_holder_name and name_at_bank:
                        # Simple name matching - can be enhanced
                        name_match = account_holder_name.upper().strip() == name_at_bank.upper().strip()
                    
                    return {
                        "success": True,
                        "account_exists": account_exists,
                        "account_holder_name": name_at_bank,
                        "name_match": name_match,
                        "bank_name": self._get_bank_name_from_ifsc(ifsc_code),
                        "branch_name": None,  # Not provided in this API
                        "account_type": None,  # Not provided in this API
                        "verification_id": data.get("transaction_id"),
                        "verified_at": datetime.now().isoformat(),
                        "status": "VERIFIED" if account_exists else "ACCOUNT_NOT_FOUND",
                        "message": response_data.get("message", "")
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API returned code: {data.get('code')}",
                        "status": "API_ERROR"
                    }
            
            elif response.status_code == 400:
                return {
                    "success": False,
                    "error": "Invalid account details or IFSC code",
                    "status": "INVALID_DETAILS"
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "Account not found",
                    "status": "ACCOUNT_NOT_FOUND"
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Authentication failed - check API credentials",
                    "status": "AUTH_ERROR"
                }
            else:
                logger.error(f"Bank verification API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "status": "API_ERROR"
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Request timeout",
                "status": "TIMEOUT"
            }
        except Exception as e:
            logger.error(f"Bank account verification failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "ERROR"
            }
    
    def _get_bank_name_from_ifsc(self, ifsc_code: str) -> str:
        """Get bank name from IFSC code"""
        bank_codes = {
            "ICIC": "ICICI Bank",
            "SBIN": "State Bank of India",
            "HDFC": "HDFC Bank",
            "AXIS": "Axis Bank",
            "KOTAK": "Kotak Mahindra Bank",
            "INDB": "Indian Bank",
            "PUNB": "Punjab National Bank",
            "UBIN": "Union Bank of India",
            "CNRB": "Canara Bank",
            "BARB": "Bank of Baroda"
        }
        
        bank_code = ifsc_code[:4] if len(ifsc_code) >= 4 else ""
        return bank_codes.get(bank_code, f"Bank ({bank_code})")
    
    def verify_ifsc(self, ifsc_code: str) -> Dict:
        """
        Verify IFSC code and get bank details
        
        Args:
            ifsc_code: IFSC code to verify
            
        Returns:
            Dict containing IFSC verification results
        """
        try:
            token = self._get_auth_token()
            if not token:
                return {
                    "success": False,
                    "error": "Authentication failed"
                }
            
            headers = {
                "accept": "application/json",
                "authorization": token,
                "x-api-key": self.api_key,
                "x-api-version": self.api_version,
            }
            
            # Use the IFSC lookup endpoint
            url = f"{self.base_url}/ifsc/{ifsc_code}"
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 200:
                    ifsc_data = data.get("data", {})
                    return {
                        "success": True,
                        "bank_name": ifsc_data.get("bank"),
                        "branch_name": ifsc_data.get("branch"),
                        "address": ifsc_data.get("address"),
                        "city": ifsc_data.get("city"),
                        "state": ifsc_data.get("state"),
                        "contact": ifsc_data.get("contact"),
                        "rtgs": ifsc_data.get("rtgs"),
                        "neft": ifsc_data.get("neft"),
                        "imps": ifsc_data.get("imps"),
                        "upi": ifsc_data.get("upi")
                    }
                else:
                    return {
                        "success": False,
                        "error": "Invalid IFSC code"
                    }
            else:
                return {
                    "success": False,
                    "error": "Invalid IFSC code or API error"
                }
                
        except Exception as e:
            logger.error(f"IFSC verification failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
bank_verifier = BankAccountVerifier()