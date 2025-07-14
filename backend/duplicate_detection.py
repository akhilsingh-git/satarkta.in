import json
import logging
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
import boto3
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)
s3 = boto3.client('s3')

class DuplicatePaymentDetector:
    def __init__(self, s3_bucket):
        self.s3_bucket = s3_bucket
        self.scaler = StandardScaler()
        self.knn_model = None
        self.payment_history = []
        self.feature_names = ['amount', 'vendor_hash', 'days_from_epoch']
        
    def _load_payment_history(self, days_back=90):
        """Load payment history from S3 for the last N days"""
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            payments = []
            
            # List objects in S3 bucket with date prefix
            paginator = s3.get_paginator('list_objects_v2')
            prefix = "invoice-analysis/"
            
            for page in paginator.paginate(Bucket=self.s3_bucket, Prefix=prefix):
                if 'Contents' not in page:
                    continue
                    
                for obj in page['Contents']:
                    try:
                        # Extract date from key
                        key_parts = obj['Key'].split('/')
                        if len(key_parts) >= 4:
                            year, month, day = int(key_parts[1]), int(key_parts[2]), int(key_parts[3])
                            obj_date = datetime(year, month, day)
                            
                            # Check if within date range
                            if start_date <= obj_date <= end_date:
                                # Load the invoice data
                                response = s3.get_object(Bucket=self.s3_bucket, Key=obj['Key'])
                                invoice_data = json.loads(response['Body'].read())
                                payments.append(invoice_data)
                    except Exception as e:
                        logger.error(f"Error loading invoice {obj['Key']}: {e}")
                        continue
            
            self.payment_history = payments
            logger.info(f"Loaded {len(payments)} payments from history")
            return payments
            
        except Exception as e:
            logger.error(f"Error loading payment history: {e}")
            return []
    
    def _extract_features(self, invoice_data):
        """Extract numerical features from invoice for K-NN"""
        features = []
        
        # 1. Amount
        try:
            amount_str = invoice_data.get('amount', invoice_data.get('total_amount', '0'))
            amount = float(re.sub(r'[^\d.]', '', str(amount_str)))
        except:
            amount = 0.0
        features.append(amount)
        
        # 2. Vendor hash (convert vendor GSTIN/name to numerical)
        vendor_gstin = invoice_data.get('vendor_gstin', '')
        vendor_name = invoice_data.get('vendor_name', '')
        vendor_str = f"{vendor_gstin}_{vendor_name}"
        vendor_hash = hash(vendor_str) % 1000000  # Normalize to reasonable range
        features.append(vendor_hash)
        
        # 3. Days from epoch (for temporal proximity)
        try:
            if 'processed_at' in invoice_data:
                invoice_date = datetime.fromisoformat(invoice_data['processed_at'].replace('Z', '+00:00'))
            elif 'invoice_date' in invoice_data:
                # Parse various date formats
                date_str = invoice_data['invoice_date']
                for fmt in ['%d-%m-%Y', '%d/%m/%Y', '%Y-%m-%d', '%d-%b-%Y']:
                    try:
                        invoice_date = datetime.strptime(date_str, fmt)
                        break
                    except:
                        continue
                else:
                    invoice_date = datetime.now()
            else:
                invoice_date = datetime.now()
                
            days_from_epoch = (invoice_date - datetime(1970, 1, 1)).days
        except:
            days_from_epoch = (datetime.now() - datetime(1970, 1, 1)).days
            
        features.append(days_from_epoch)
        
        return np.array(features)
    
    def train_model(self):
        """Train K-NN model on payment history"""
        if not self.payment_history:
            self._load_payment_history()
            
        if len(self.payment_history) < 2:
            logger.warning("Not enough payment history to train model")
            return False
            
        # Extract features from all payments
        feature_matrix = []
        for payment in self.payment_history:
            features = self._extract_features(payment)
            feature_matrix.append(features)
        
        feature_matrix = np.array(feature_matrix)
        
        # Scale features
        self.scaler.fit(feature_matrix)
        scaled_features = self.scaler.transform(feature_matrix)
        
        # Train K-NN model with k=3
        self.knn_model = NearestNeighbors(n_neighbors=min(3, len(self.payment_history)), 
                                          algorithm='kd_tree')
        self.knn_model.fit(scaled_features)
        
        logger.info("K-NN model trained successfully")
        return True
    
    def check_duplicate(self, invoice_data, threshold=0.1):
        """
        Check if invoice is potentially a duplicate
        Returns: (is_duplicate, similarity_score, similar_invoices)
        """
        if self.knn_model is None:
            if not self.train_model():
                return False, 0.0, []
        
        # Extract features from current invoice
        features = self._extract_features(invoice_data)
        scaled_features = self.scaler.transform([features])
        
        # Find nearest neighbors
        distances, indices = self.knn_model.kneighbors(scaled_features)
        
        # Check if any neighbor is suspiciously close
        min_distance = distances[0][0] if len(distances[0]) > 0 else float('inf')
        
        # Get similar invoices
        similar_invoices = []
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if dist < threshold and idx < len(self.payment_history):
                similar_invoice = self.payment_history[idx].copy()
                similar_invoice['similarity_distance'] = float(dist)
                similar_invoices.append(similar_invoice)
        
        # Calculate similarity score (0-100, where 100 is identical)
        similarity_score = max(0, (1 - min_distance) * 100) if min_distance != float('inf') else 0
        
        # Consider it a potential duplicate if distance is below threshold
        is_duplicate = min_distance < threshold
        
        return is_duplicate, similarity_score, similar_invoices
    
    def get_duplicate_report(self, invoice_data):
        """Generate a detailed duplicate analysis report"""
        is_duplicate, similarity_score, similar_invoices = self.check_duplicate(invoice_data)
        
        report = {
            'is_potential_duplicate': is_duplicate,
            'similarity_score': similarity_score,
            'similar_invoice_count': len(similar_invoices),
            'analysis_date': datetime.now().isoformat(),
            'similar_invoices': []
        }
        
        # Add details of similar invoices
        for similar in similar_invoices[:3]:  # Top 3 most similar
            report['similar_invoices'].append({
                'invoice_number': similar.get('invoice_number', 'N/A'),
                'vendor_name': similar.get('vendor_name', 'N/A'),
                'amount': similar.get('amount', similar.get('total_amount', 'N/A')),
                'date': similar.get('invoice_date', 'N/A'),
                'similarity_distance': similar.get('similarity_distance', 0),
                'processed_date': similar.get('processed_at', 'N/A')
            })
        
        return report