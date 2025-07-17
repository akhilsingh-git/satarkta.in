import os
import logging
import threading
import requests
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
import invoice_utils
import compliance_utils
import gstin_utils
from duplicate_detection import DuplicatePaymentDetector
from datetime import datetime, timezone
from datetime import timedelta
import boto3

# Initialize AWS S3 client
s3 = boto3.client('s3')

# Load environment
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Required environment variables
required = ["TELEGRAM_TOKEN","PUBLIC_URL","S3_BUCKET","SANDBOX_API_KEY","SANDBOX_API_SECRET"]
for var in required:
    if not os.getenv(var):
        logger.error(f"Missing environment variable: {var}")
        raise SystemExit(f"Missing {var}")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
PUBLIC_URL = os.getenv("PUBLIC_URL").rstrip("/")
S3_BUCKET = os.getenv("S3_BUCKET")
SANDBOX_API_KEY = os.getenv("SANDBOX_API_KEY")
SANDBOX_API_SECRET = os.getenv("SANDBOX_API_SECRET")

bot_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Create Flask app FIRST
app = Flask(__name__)

# THEN add CORS support
CORS(app)

# Initialize duplicate detector
duplicate_detector = DuplicatePaymentDetector(S3_BUCKET)

def format_amount(amount_str):
    """Format amount string for display"""
    if not amount_str:
        return "N/A"
    
    try:
        # Remove any non-numeric characters except decimal point
        clean_amount = re.sub(r'[^\d.]', '', str(amount_str))
        if not clean_amount:
            return "N/A"
            
        amount = float(clean_amount)
        if amount == int(amount):
            return f"₹{int(amount):,}"
        else:
            return f"₹{amount:,.2f}"
    except (ValueError, TypeError):
        return f"₹{amount_str}"

def process_invoice_common(pdf_bytes):
    """Common invoice processing logic for both bot and web"""
    try:
        # Extract fields with API credentials for dynamic vendor lookup
        logger.info("Starting field extraction...")
        inv = invoice_utils.extract_fields(
            pdf_bytes, 
            S3_BUCKET, 
            SANDBOX_API_KEY, 
            SANDBOX_API_SECRET
        )
        
        vendor = inv.get('vendor_name', '').strip()
        gstin = inv.get('vendor_gstin', '').strip()
        
        fraud_reasons = []
        fraud_score = 0

        # Enhanced GSTIN validation with fallback
        if gstin:
            try:
                logger.info(f"Verifying GSTIN: {gstin}")
                # Minimal GSTIN validation without full API access
                if len(gstin) == 15:
                    # Basic structure validation
                    fraud_reasons.append("GSTIN verification incomplete due to API restrictions")
                    fraud_score += 10
                else:
                    fraud_reasons.append("Invalid GSTIN format")
                    fraud_score += 20
            except Exception as e:
                logger.error(f"GSTIN verification error: {e}")
                fraud_reasons.append("GSTIN verification failed")
                fraud_score += 20
        else:
            fraud_reasons.append("Missing GSTIN")
            fraud_score += 30

        # Check for missing invoice number
        if not inv.get('invoice_number'):
            fraud_reasons.append("Invoice number missing")
            fraud_score += 15
            
        # Check for missing amount
        if not inv.get('total_amount') or inv.get('total_amount') == '0':
            fraud_reasons.append("Amount not detected or zero")
            fraud_score += 15

        # Simplified compliance checks
        if gstin and inv.get('invoice_date'):
            fraud_reasons.append("ITC reconciliation not verified")
            fraud_score += 15
            fraud_reasons.append("E-Invoice IRN not verified")
            fraud_score += 15

        # Duplicate check
        if inv.get('invoice_number') and inv.get('total_amount'):
            fraud_reasons.append("Duplicate check not comprehensive")
            fraud_score += 10

        # Calculate final risk level with modified scoring
        if fraud_score >= 50:
            risk_level = "HIGH RISK"
            risk_icon = "🔴"
        elif fraud_score >= 25:
            risk_level = "MEDIUM RISK"
            risk_icon = "🟡"
        else:
            risk_level = "LOW RISK"
            risk_icon = "🟢"
        
        # Prepare recommendations
        recommendations = []
        if fraud_score >= 50:
            recommendations = [
                "Manual verification recommended",
                "Contact vendor directly",
                "Exercise caution with payment",
                "Gather additional documentation"
            ]
        elif fraud_score >= 25:
            recommendations = [
                "Verify key details",
                "Cross-reference with records",
                "Additional due diligence"
            ]
        else:
            recommendations = [
                "Invoice appears legitimate",
                "Standard processing",
                "Proceed with normal workflow"
            ]
        
        # Store invoice data
        _store_invoice_data(inv, fraud_score, fraud_reasons)
        
        return {
            'invoice_data': inv,
            'fraud_score': fraud_score,
            'fraud_reasons': fraud_reasons,
            'risk_level': risk_level,
            'risk_icon': risk_icon,
            'recommendations': recommendations
        }
        
    except Exception as e:
        logger.error(f"Error processing invoice: {e}")
        raise

@app.route(f'/{TELEGRAM_TOKEN}', methods=["POST"])
def telegram_webhook():
    update = request.get_json(force=True)
    logger.info("Received update: %s", str(update)[:200])
    if not update or 'message' not in update:
        return 'OK', 200

    msg = update['message']
    chat_id = msg['chat']['id']
    text = msg.get('text', '').strip().lower()

    # Command: daily fraud report
    if text == '/fraud_report':
        report = _load_fraud_report()
        send_reply(chat_id, f"📊 *Daily Fraud Report:*{report}", parse_mode="Markdown")
        return 'OK', 200

    if 'document' in msg:
        doc = msg['document']
        if doc.get('mime_type') != 'application/pdf':
            send_reply(chat_id, "Please send a PDF invoice.")
            return 'OK', 200
        file_id = doc['file_id']
        threading.Thread(target=process_invoice_telegram, args=(file_id, chat_id), daemon=True).start()
    else:
        send_reply(chat_id, "Send a PDF invoice to process or /fraud_report to view today's flagged invoices.")

    return 'OK', 200

@app.route('/process-invoice', methods=['POST', 'OPTIONS'])
@cross_origin()
def process_invoice_web():
    """Process invoice uploaded from web interface"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are allowed'}), 400
        
        # Read PDF bytes
        pdf_bytes = file.read()
        
        # Use common processing logic
        result = process_invoice_common(pdf_bytes)
        
        # Return response for web
        return jsonify({
            'invoice_number': result['invoice_data'].get('invoice_number', 'N/A'),
            'vendor_name': result['invoice_data'].get('vendor_name', 'N/A'),
            'vendor_gstin': result['invoice_data'].get('vendor_gstin', 'N/A'),
            'amount': format_amount(result['invoice_data'].get('total_amount', '0')),
            'invoice_date': result['invoice_data'].get('invoice_date', 'N/A'),
            'fraud_score': result['fraud_score'],
            'risk_level': result['risk_level'],
            'risk_icon': result['risk_icon'],
            'risk_factors': result['fraud_reasons'],
            'recommendations': result['recommendations']
        })
        
    except Exception as e:
        logger.error(f"Error processing web invoice: {e}")
        return jsonify({'error': str(e)}), 500

def send_reply(chat_id: int, text: str, parse_mode: str = None):
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        requests.post(f"{bot_url}/sendMessage", json=payload)
    except Exception:
        logger.exception("Failed to send reply")

def process_invoice_telegram(file_id: str, chat_id: int):
    """Process invoice from Telegram"""
    try:
        # 1. Send processing message
        send_reply(chat_id, "🔄 Processing invoice... Please wait.")
        
        # 2. Download PDF
        info = requests.get(f"{bot_url}/getFile?file_id={file_id}").json()['result']
        pdf_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{info['file_path']}"
        pdf_bytes = requests.get(pdf_url).content

        # 3. Use common processing logic
        result = process_invoice_common(pdf_bytes)
        
        inv = result['invoice_data']
        vendor = inv.get('vendor_name', '').strip()
        gstin = inv.get('vendor_gstin', '').strip()
        
        # Build response lines with extracted information
        lines = [
            f"📄 *Invoice #{inv.get('invoice_number', 'N/A')}*",
            f"🏢 Vendor: {vendor or 'N/A'}",
            f"💰 Amount: {format_amount(inv.get('total_amount', '0'))}"
        ]
        
        invoice_date = inv.get('invoice_date', '').strip()
        if invoice_date:
            lines.append(f"📅 Date: {invoice_date}")
        
        # GSTIN info
        if gstin:
            lines.append(f"🆔 GSTIN: `{gstin}` ⚠️ API Access Limited")
            lines.append("   💡 Some verification features may be restricted")
        else:
            lines.append("❌ No GSTIN found")

        # Compliance checks
        if gstin and invoice_date:
            lines.append("📊 ITC Reconciliation: ⚠️ Verification Unavailable")
            lines.append("   💡 API access required for detailed check")
            lines.append("📜 E-Invoice IRN: ⚠️ Verification Unavailable")
            lines.append("   💡 API access required for detailed check")

        # Duplicate check
        if inv.get('invoice_number') and inv.get('total_amount'):
            lines.append("🔄 Duplicate Check: ⚠️ Limited Verification")
            lines.append("   💡 Full duplicate analysis requires additional access")

        # Add fraud assessment
        risk_icon = "🚨" if result['fraud_score'] >= 50 else "⚠️" if result['fraud_score'] >= 25 else "✅"
        lines.append(f"\n{risk_icon} *Fraud Risk: {result['risk_icon']} {result['risk_level']}*")
        lines.append(f"📈 Risk Score: {result['fraud_score']}/100")
        
        if result['fraud_reasons']:
            lines.append("\n🚩 *Risk Factors:*")
            for reason in result['fraud_reasons']:
                lines.append(f"  • {reason}")

        # Add recommendations
        lines.append("\n💡 *Recommendations:*")
        for rec in result['recommendations']:
            icon = "🔍" if "Manual" in rec else "📞" if "Contact" in rec else "🔒" if "caution" in rec else "✅"
            lines.append(f"  • {icon} {rec}")

        # Add extraction status if any fields missing
        if not inv.get('invoice_number') or not inv.get('vendor_name') or not inv.get('total_amount'):
            lines.append("\n⚠️ *Note:* Some invoice details could not be extracted.")
            lines.append("Please ensure the PDF is clear and legible.")

        # Send response
        response = "\n".join(lines)
        send_reply(chat_id, response, parse_mode="Markdown")
        
        # Send alert for high-risk invoices
        if result['fraud_score'] >= 50:
            alert_msg = f"🚨 *POTENTIAL RISK INVOICE*\n\n"
            alert_msg += f"Invoice: {inv.get('invoice_number', 'N/A')}\n"
            alert_msg += f"Vendor: {inv.get('vendor_name', 'N/A')}\n"
            alert_msg += f"Amount: {format_amount(inv.get('total_amount', '0'))}\n"
            alert_msg += f"Risk Score: {result['fraud_score']}/100\n\n"
            alert_msg += "Requires further investigation!"
            
            # Send to fraud monitoring channel (if configured)
            fraud_channel = os.getenv("FRAUD_ALERT_CHANNEL")
            if fraud_channel:
                send_reply(fraud_channel, alert_msg, parse_mode="Markdown")

    except Exception as e:
        logger.exception("Error processing invoice")
        error_msg = "❌ Error processing invoice.\n\n"
        error_msg += "This could be due to:\n"
        error_msg += "• Unsupported PDF format\n"
        error_msg += "• Text extraction issues\n"
        error_msg += "• Technical processing problems\n\n"
        error_msg += f"Error details: {str(e)[:100]}"
        send_reply(chat_id, error_msg)

def _store_invoice_data(invoice_data, fraud_score, fraud_reasons):
    """Store invoice data for reporting and analysis"""
    try:
        # Create invoice record
        record = {
            'invoice_number': invoice_data.get('invoice_number'),
            'vendor_name': invoice_data.get('vendor_name'),
            'vendor_gstin': invoice_data.get('vendor_gstin'),
            'amount': invoice_data.get('total_amount'),
            'invoice_date': invoice_data.get('invoice_date'),
            'fraud_score': fraud_score,
            'fraud_reasons': fraud_reasons,
            'processed_at': datetime.now(timezone.utc).isoformat(),
            'risk_level': 'HIGH' if fraud_score >= 60 else 'MEDIUM' if fraud_score >= 30 else 'LOW'
        }
        
        # Store in S3 for analysis
        key = f"invoice-analysis/{datetime.now().strftime('%Y/%m/%d')}/{record['invoice_number']}_{int(datetime.now().timestamp())}.json"
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(record),
            ContentType='application/json'
        )
        
        logger.info(f"Stored invoice analysis: {key}")
        
    except Exception as e:
        logger.error(f"Error storing invoice data: {e}")

def _load_fraud_report():
    """Load today's fraud report"""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        prefix = f"invoice-analysis/{today.replace('-', '/')}/"
        
        response = s3.list_objects_v2(
            Bucket=S3_BUCKET,
            Prefix=prefix
        )
        
        if 'Contents' not in response:
            return "\n\n📊 No invoices processed today."
        
        total_invoices = len(response['Contents'])
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        
        # Count risk levels
        for obj in response['Contents']:
            try:
                obj_response = s3.get_object(Bucket=S3_BUCKET, Key=obj['Key'])
                data = json.loads(obj_response['Body'].read())
                risk_level = data.get('risk_level', 'LOW')
                
                if risk_level == 'HIGH':
                    high_risk += 1
                elif risk_level == 'MEDIUM':
                    medium_risk += 1
                else:
                    low_risk += 1
                    
            except Exception as e:
                logger.error(f"Error reading fraud report data: {e}")
                continue
        
        report = f"\n\n📊 **Today's Summary ({today}):**\n"
        report += f"📄 Total Invoices: {total_invoices}\n"
        report += f"🔴 High Risk: {high_risk}\n"
        report += f"🟡 Medium Risk: {medium_risk}\n"
        report += f"🟢 Low Risk: {low_risk}\n"
        
        if high_risk > 0:
            report += f"\n🚨 **{high_risk} invoices require immediate attention!**"
        
        return report
        
    except Exception as e:
        logger.error(f"Error loading fraud report: {e}")
        return "\n\n❌ Error loading fraud report."

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

@app.route('/recent-scans', methods=['GET'])
@cross_origin()
def get_recent_scans():
    """Get recent invoice scans for dashboard display"""
    try:
        # Get limit from query params (default 10, max 50)
        limit = min(int(request.args.get('limit', 10)), 50)
        
        # Calculate date range (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # List all objects in the date range
        scans = []
        
        # Iterate through each day in the range
        current_date = start_date
        while current_date <= end_date:
            prefix = f"invoice-analysis/{current_date.strftime('%Y/%m/%d')}/"
            
            try:
                response = s3.list_objects_v2(
                    Bucket=S3_BUCKET,
                    Prefix=prefix
                )
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        try:
                            # Get the object
                            obj_response = s3.get_object(
                                Bucket=S3_BUCKET,
                                Key=obj['Key']
                            )
                            
                            # Parse the JSON data
                            data = json.loads(obj_response['Body'].read())
                            
                            # Add formatted data to scans list
                            scans.append({
                                'id': obj['Key'].split('/')[-1].replace('.json', ''),
                                'invoiceNumber': data.get('invoice_number', 'N/A'),
                                'vendorName': data.get('vendor_name', 'N/A'),
                                'amount': format_amount(data.get('amount', '0')),
                                'date': data.get('invoice_date', 'N/A'),
                                'fraudScore': data.get('fraud_score', 0),
                                'riskLevel': data.get('risk_level', 'LOW'),
                                'processedAt': data.get('processed_at', obj['LastModified'].isoformat()),
                                'fraudReasons': data.get('fraud_reasons', [])
                            })
                            
                        except Exception as e:
                            logger.error(f"Error parsing scan data: {e}")
                            continue
                            
            except Exception as e:
                logger.error(f"Error listing objects for {prefix}: {e}")
                
            current_date += timedelta(days=1)
        
        # Sort by processed time (newest first)
        scans.sort(key=lambda x: x['processedAt'], reverse=True)
        
        # Apply limit
        scans = scans[:limit]
        
        # Calculate summary stats
        total_scans = len(scans)
        high_risk_count = sum(1 for s in scans if s['riskLevel'] == 'HIGH')
        medium_risk_count = sum(1 for s in scans if s['riskLevel'] == 'MEDIUM')
        low_risk_count = sum(1 for s in scans if s['riskLevel'] == 'LOW')
        
        return jsonify({
            'success': True,
            'data': {
                'scans': scans,
                'summary': {
                    'total': total_scans,
                    'highRisk': high_risk_count,
                    'mediumRisk': medium_risk_count,
                    'lowRisk': low_risk_count
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching recent scans: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/webhook/setup', methods=['POST'])
def setup_webhook():
    """Setup Telegram webhook"""
    try:
        webhook_url = f"{PUBLIC_URL}/{TELEGRAM_TOKEN}"
        response = requests.post(
            f"{bot_url}/setWebhook",
            json={"url": webhook_url}
        )
        
        if response.json().get('ok'):
            return {'status': 'success', 'webhook_url': webhook_url}
        else:
            return {'status': 'error', 'message': response.json()}, 400
            
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")
        return {'status': 'error', 'message': str(e)}, 500

if __name__ == "__main__":
    # Set up webhook on startup
    try:
        webhook_url = f"{PUBLIC_URL}/{TELEGRAM_TOKEN}"
        response = requests.post(
            f"{bot_url}/setWebhook",
            json={"url": webhook_url}
        )
        
        if response.json().get('ok'):
            logger.info(f"Webhook set up successfully: {webhook_url}")
        else:
            logger.error(f"Failed to set up webhook: {response.json()}")
            
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")
    
    # Start the Flask app
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
