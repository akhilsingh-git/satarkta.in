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
            return data.get("access_token")
            
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
            
            headers = {
                "accept": "application/json",
                "authorization": f"Bearer {token}",
                "x-api-key": self.api_key,
                "x-api-version": self.api_version,
                "content-type": "application/json"
            }
            
            payload = {
                "account_number": account_number,
                "ifsc": ifsc_code
            }
            
            # Add account holder name if provided
            if account_holder_name:
                payload["account_holder_name"] = account_holder_name
            
            response = requests.post(
                f"{self.base_url}/bank_account_verification",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                return {
                    "success": True,
                    "account_exists": data.get("account_exists", False),
                    "account_holder_name": data.get("account_holder_name"),
                    "name_match": data.get("name_match"),
                    "bank_name": data.get("bank_name"),
                    "branch_name": data.get("branch_name"),
                    "account_type": data.get("account_type"),
                    "verification_id": data.get("verification_id"),
                    "verified_at": datetime.now().isoformat(),
                    "status": "VERIFIED" if data.get("account_exists") else "NOT_FOUND"
                }
            
            elif response.status_code == 400:
                return {
                    "success": False,
                    "error": "Invalid account details",
                    "status": "INVALID_DETAILS"
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "Account not found",
                    "status": "ACCOUNT_NOT_FOUND"
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
                "authorization": f"Bearer {token}",
                "x-api-key": self.api_key,
                "x-api-version": self.api_version,
            }
            
            response = requests.get(
                f"{self.base_url}/ifsc/{ifsc_code}",
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "bank_name": data.get("bank"),
                    "branch_name": data.get("branch"),
                    "address": data.get("address"),
                    "city": data.get("city"),
                    "state": data.get("state"),
                    "contact": data.get("contact"),
                    "rtgs": data.get("rtgs"),
                    "neft": data.get("neft"),
                    "imps": data.get("imps"),
                    "upi": data.get("upi")
                }
            else:
                return {
                    "success": False,
                    "error": "Invalid IFSC code"
                }
                
        except Exception as e:
            logger.error(f"IFSC verification failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
bank_verifier = BankAccountVerifier()