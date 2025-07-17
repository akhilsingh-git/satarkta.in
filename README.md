# Satarkta - AI-Powered Invoice Fraud Detection Platform

## Overview
Satarkta is a comprehensive fraud detection platform that uses AI and machine learning to analyze invoices and detect potential fraud indicators. The platform now includes bank account verification capabilities using penny-less verification.

## Features

### Core Features
- **AI-Powered Invoice Analysis**: Advanced OCR and ML algorithms for invoice processing
- **GSTIN Verification**: Real-time verification against government databases
- **Duplicate Detection**: Machine learning-based duplicate invoice detection
- **Compliance Checking**: GSTR-2B reconciliation and e-invoice IRN validation
- **Risk Scoring**: Intelligent fraud risk assessment (0-100 scale)

### New Features
- **Bank Account Verification**: Penny-less bank account verification using Sandbox API
- **IFSC Code Validation**: Real-time IFSC code verification with bank details
- **Enhanced Dashboard**: Tabbed interface with multiple verification tools
- **Optimized API**: RESTful API endpoints optimized for frontend integration

## Architecture

### Backend (Python Flask)
- **optimized_app.py**: Main Flask application with enhanced API endpoints
- **bank_verification.py**: Bank account verification module
- **invoice_utils.py**: Invoice processing and OCR utilities
- **compliance_utils.py**: GST compliance checking
- **gstin_utils.py**: GSTIN verification utilities
- **duplicate_detection.py**: ML-based duplicate detection

### Frontend (Next.js)
- **Enhanced Dashboard**: Multi-tab interface for different verification tools
- **Bank Verification Component**: User-friendly bank account verification
- **Real-time Processing**: Optimized API integration
- **Responsive Design**: Mobile-friendly interface

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- AWS Account (for S3 storage)
- Sandbox API Account (for GSTIN and bank verification)

### Backend Setup
1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file with required variables:
   ```env
   TELEGRAM_TOKEN=your_telegram_bot_token
   S3_BUCKET=your_s3_bucket_name
   SANDBOX_API_KEY=your_sandbox_api_key
   SANDBOX_API_SECRET=your_sandbox_api_secret
   AWS_ACCESS_KEY_ID=your_aws_access_key
   AWS_SECRET_ACCESS_KEY=your_aws_secret_key
   ```

4. Run the backend:
   ```bash
   python optimized_app.py
   ```

### Frontend Setup
1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

### Running Both Services
You can run both backend and frontend simultaneously:
```bash
cd frontend
npm run dev:all
```

## API Endpoints

### Invoice Processing
- `POST /api/process-invoice` - Process uploaded invoice PDF
- `GET /api/recent-scans` - Get recent invoice scans
- `GET /api/dashboard-stats` - Get dashboard statistics

### Bank Verification
- `POST /api/verify-bank-account` - Verify bank account details
- `POST /api/verify-ifsc` - Verify IFSC code

### System
- `GET /api/health` - Health check endpoint

## Usage

### Invoice Processing
1. Upload PDF invoice through the dashboard
2. System extracts key information using OCR
3. Performs multiple fraud checks:
   - GSTIN verification
   - Duplicate detection
   - Compliance checking
   - Risk scoring
4. Returns detailed analysis with recommendations

### Bank Account Verification
1. Enter account number and IFSC code
2. Optionally provide account holder name for matching
3. System verifies account existence and details
4. Returns verification status and bank information

## Deployment

### Without LocalTunnel
The optimized backend runs on `localhost:5001` and the frontend on `localhost:3000`. For production deployment:

1. **Backend**: Deploy to cloud service (AWS EC2, Google Cloud, etc.)
2. **Frontend**: Build and deploy to static hosting (Vercel, Netlify, etc.)
3. **Update API URLs**: Change frontend API calls to production backend URL

### Environment Variables for Production
```env
# Backend
FLASK_ENV=production
PORT=5001

# Frontend
NEXT_PUBLIC_API_URL=https://your-backend-domain.com
```

## Security Features
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure file upload handling
- Data encryption in transit
- Audit trail for all operations

## Monitoring and Analytics
- Real-time fraud detection metrics
- Historical analysis and trends
- Risk distribution analytics
- Performance monitoring

## Support
For technical support or questions, contact: support@satarkta.in

## License
Proprietary - All rights reserved