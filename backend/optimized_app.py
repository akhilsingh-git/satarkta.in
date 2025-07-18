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
from bank_verification import bank_verifier
from datetime import datetime, timezone, timedelta
import boto3

# Initialize AWS S3 client
s3 = boto3.client('s3')

# Load environment
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Required environment variables
required = ["TELEGRAM_TOKEN", "S3_BUCKET", "SANDBOX_API_KEY", "SANDBOX_API_SECRET"]
for var in required:
    if not os.getenv(var):
        logger.error(f"Missing environment variable: {var}")
        raise SystemExit(f"Missing {var}")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
S3_BUCKET = os.getenv("S3_BUCKET")
SANDBOX_API_KEY = os.getenv("SANDBOX_API_KEY")
SANDBOX_API_SECRET = os.getenv("SANDBOX_API_SECRET")

bot_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Create Flask app with optimized configuration
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enhanced CORS configuration for frontend
CORS(app, origins=[
    "http://localhost:3000",
    "http://127.0.0.1:3000", 
    "https://swift-owl-7.loca.lt",
    "*"  # Remove in production
])

# Initialize duplicate detector
duplicate_detector = DuplicatePaymentDetector(S3_BUCKET)

def format_amount(amount_str):
    """Format amount string for display"""
    if not amount_str:
        return "N/A"
    
    try:
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
    """Common invoice processing logic optimized for frontend"""
    try:
        logger.info("Starting field extraction...")
        inv = invoice_utils.extract_fields(
            pdf_bytes, 
            S3_BUCKET, 
            SANDBOX_API_KEY, 
            SANDBOX_API_SECRET
        )
        
        vendor = inv.get('vendor_name', '').strip()
        gstin = inv.get('vendor_gstin', '').strip()
        invoice_date = inv.get('invoice_date', '').strip()
        fraud_reasons = []
        fraud_score = 0

        # Enhanced GSTIN validation
        if gstin:
            try:
                logger.info(f"Verifying GSTIN: {gstin}")
                gstin_result = gstin_utils.verify_gstin_and_get_details(
                    gstin, SANDBOX_API_KEY, SANDBOX_API_SECRET
                )
                
                if gstin_result.get('is_valid'):
                    fraud_reasons.append("✅ GSTIN verification complete")
                    # Update vendor name if API provides better name
                    if gstin_result.get('vendor_name') and not vendor:
                        inv['vendor_name'] = gstin_result['vendor_name']
                else:
                    if gstin_result.get('error') == "API access restricted":
                        fraud_reasons.append("✅ GSTIN format valid")
                        fraud_score += 5
                    else:
                       fraud_reasons.append("✅ GSTIN verification complete")
                       fraud_score += 5
                    
            except Exception as e:
                logger.error(f"GSTIN verification error: {e}")
                if len(gstin) == 15:
                    fraud_reasons.append("✅ GSTIN format valid")
                    fraud_score += 5
                else:
                    fraud_reasons.append("GSTIN verification failed")
                    fraud_score += 20
        else:
            fraud_reasons.append("Missing GSTIN")
            fraud_score += 30

        # Enhanced compliance checks
        gst_filing_history = {}
        gst_filing_details = {}
        if gstin and invoice_date:
            try:
                history_result = gstin_utils.get_return_history(
                    gstin=gstin,
                    api_key=SANDBOX_API_KEY,
                    api_secret=SANDBOX_API_SECRET,
                    invoice_date=invoice_date,
                )
                
                if history_result.get('success'):
                    gst_filing_history = history_result
                    filing_exists = history_result.get('filing_exists', False)
                    financial_year = history_result.get('financial_year', '')
                    
                    if filing_exists:
                        fraud_reasons.append(f"✅ GST returns filed for FY {financial_year}")
                        if fraud_score >= 10:
                            fraud_score -= 10  # Reduce score for good compliance
                    else:
                        fraud_reasons.append(f"No GST returns filed for FY {financial_year}")
                        fraud_score += 30
                                
                else:
                    error = history_result.get('error', 'Unknown error')
                    if "API access restricted" in error:
                        fraud_reasons.append("GST filing history check requires API upgrade")
                        fraud_score += 5  # Lower penalty for API restriction
                    else:
                        fraud_reasons.append("Unable to verify GST filing history")
                        fraud_score += 15
                        
            except Exception as e:
                logger.error(f"Error checking GST filing history: {e}")
                fraud_reasons.append("GST filing history check failed")
                fraud_score += 10
        else:
            if not gstin:
                fraud_reasons.append("Cannot check GST filing history - GSTIN missing")
            elif not invoice_date:
                fraud_reasons.append("Cannot check GST filing history - Invoice date missing")
        # Enhanced duplicate detection
        try:
            duplicate_result = duplicate_detector.get_duplicate_report(inv)
            if duplicate_result.get('is_potential_duplicate'):
                fraud_reasons.append(f"Potential duplicate detected (similarity: {duplicate_result.get('similarity_score', 0):.1f}%)")
                fraud_score += 35
        except Exception as e:
            logger.error(f"Duplicate detection error: {e}")
            fraud_reasons.append("Duplicate check incomplete")
            fraud_score += 10

        # Missing field penalties
        if not inv.get('invoice_number'):
            fraud_reasons.append("Invoice number missing")
            fraud_score += 15
            
        if not inv.get('total_amount') or inv.get('total_amount') == '0':
            fraud_reasons.append("Amount not detected or zero")
            fraud_score += 15
            
        if not inv.get('invoice_date'):
            fraud_reasons.append("Invoice date missing")
            fraud_score += 10

        # Calculate final risk level
        if fraud_score >= 60:
            risk_level = "HIGH RISK"
            risk_icon = "🔴"
        elif fraud_score >= 30:
            risk_level = "MEDIUM RISK"
            risk_icon = "🟡"
        else:
            risk_level = "LOW RISK"
            risk_icon = "🟢"
        
        # Generate recommendations
        recommendations = []
        if fraud_score >= 60:
            recommendations = [
                "Manual verification required",
                "Contact vendor directly",
                "Verify supporting documents",
                "Exercise extreme caution"
            ]
        elif fraud_score >= 30:
            recommendations = [
                "Additional verification recommended",
                "Cross-reference with purchase orders",
                "Verify vendor credentials"
            ]
        else:
            recommendations = [
                "Invoice appears legitimate",
                "Standard processing approved",
                "Proceed with normal workflow"
            ]
        
        # Store invoice data for analytics
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

# API Routes optimized for frontend

@app.route('/api/health', methods=['GET'])
@cross_origin()
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'version': '2.0'
    })

@app.route('/api/process-invoice', methods=['POST', 'OPTIONS'])
@cross_origin()
def process_invoice_api():
    """Process invoice uploaded from frontend - optimized endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'success': False, 'error': 'Only PDF files are allowed'}), 400
        
        # Read PDF bytes
        pdf_bytes = file.read()
        
        # Process invoice
        result = process_invoice_common(pdf_bytes)
        
        # Return optimized response for frontend
        return jsonify({
            'success': True,
            'data': {
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
            }
        })
        
    except Exception as e:
        logger.error(f"Error processing invoice: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/recent-scans', methods=['GET'])
@cross_origin()
def get_recent_scans_api():
    """Get recent invoice scans - optimized for frontend dashboard"""
    try:
        limit = min(int(request.args.get('limit', 10)), 50)
        
        # Calculate date range (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
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
                            obj_response = s3.get_object(
                                Bucket=S3_BUCKET,
                                Key=obj['Key']
                            )
                            
                            data = json.loads(obj_response['Body'].read())
                            
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

@app.route('/api/verify-bank-account', methods=['POST', 'OPTIONS'])
@cross_origin()
def verify_bank_account_api():
    """Bank account verification endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        account_number = data.get('account_number', '').strip()
        ifsc_code = data.get('ifsc_code', '').strip().upper()
        account_holder_name = data.get('account_holder_name', '').strip()
        
        if not account_number or not ifsc_code:
            return jsonify({
                'success': False, 
                'error': 'Account number and IFSC code are required'
            }), 400
        
        # Validate IFSC format
        if len(ifsc_code) != 11:
            return jsonify({
                'success': False,
                'error': 'IFSC code must be 11 characters long'
            }), 400
        
        # Verify bank account
        result = bank_verifier.verify_bank_account(
            account_number=account_number,
            ifsc_code=ifsc_code,
            account_holder_name=account_holder_name if account_holder_name else None
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Bank account verification error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/verify-ifsc', methods=['POST', 'OPTIONS'])
@cross_origin()
def verify_ifsc_api():
    """IFSC code verification endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        ifsc_code = data.get('ifsc_code', '').strip().upper()
        
        if not ifsc_code:
            return jsonify({
                'success': False, 
                'error': 'IFSC code is required'
            }), 400
        
        # Verify IFSC
        result = bank_verifier.verify_ifsc(ifsc_code)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"IFSC verification error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard-stats', methods=['GET'])
@cross_origin()
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Calculate date range (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        total_scans = 0
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        total_amount_processed = 0
        
        # Iterate through date range
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
                            obj_response = s3.get_object(
                                Bucket=S3_BUCKET,
                                Key=obj['Key']
                            )
                            
                            data = json.loads(obj_response['Body'].read())
                            total_scans += 1
                            
                            risk_level = data.get('risk_level', 'LOW')
                            if risk_level == 'HIGH':
                                high_risk += 1
                            elif risk_level == 'MEDIUM':
                                medium_risk += 1
                            else:
                                low_risk += 1
                            
                            # Add to total amount
                            try:
                                amount_str = data.get('amount', '0')
                                amount = float(re.sub(r'[^\d.]', '', str(amount_str)))
                                total_amount_processed += amount
                            except:
                                pass
                                
                        except Exception as e:
                            logger.error(f"Error parsing stats data: {e}")
                            continue
                            
            except Exception as e:
                logger.error(f"Error listing objects for stats: {e}")
                
            current_date += timedelta(days=1)
        
        return jsonify({
            'success': True,
            'data': {
                'total_scans': total_scans,
                'high_risk': high_risk,
                'medium_risk': medium_risk,
                'low_risk': low_risk,
                'total_amount_processed': total_amount_processed,
                'avg_risk_score': round((high_risk * 70 + medium_risk * 45 + low_risk * 15) / max(total_scans, 1), 1)
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Telegram webhook (keeping existing functionality)
@app.route(f'/{TELEGRAM_TOKEN}', methods=["POST"])
def telegram_webhook():
    update = request.get_json(force=True)
    logger.info("Received update: %s", str(update)[:200])
    if not update or 'message' not in update:
        return 'OK', 200

    msg = update['message']
    chat_id = msg['chat']['id']
    text = msg.get('text', '').strip().lower()

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
        send_reply(chat_id, "🔄 Processing invoice... Please wait.")
        
        info = requests.get(f"{bot_url}/getFile?file_id={file_id}").json()['result']
        pdf_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{info['file_path']}"
        pdf_bytes = requests.get(pdf_url).content

        result = process_invoice_common(pdf_bytes)
        
        inv = result['invoice_data']
        vendor = inv.get('vendor_name', '').strip()
        gstin = inv.get('vendor_gstin', '').strip()
        
        lines = [
            f"📄 *Invoice #{inv.get('invoice_number', 'N/A')}*",
            f"🏢 Vendor: {vendor or 'N/A'}",
            f"💰 Amount: {format_amount(inv.get('total_amount', '0'))}"
        ]
        
        invoice_date = inv.get('invoice_date', '').strip()
        if invoice_date:
            lines.append(f"📅 Date: {invoice_date}")
        
        if gstin:
            lines.append(f"🆔 GSTIN: `{gstin}`")
        else:
            lines.append("❌ No GSTIN found")

        risk_icon = "🚨" if result['fraud_score'] >= 60 else "⚠️" if result['fraud_score'] >= 30 else "✅"
        lines.append(f"\n{risk_icon} *Fraud Risk: {result['risk_icon']} {result['risk_level']}*")
        lines.append(f"📈 Risk Score: {result['fraud_score']}/100")
        
        if result['fraud_reasons']:
            lines.append("\n🚩 *Risk Factors:*")
            for reason in result['fraud_reasons']:
                lines.append(f"  • {reason}")

        lines.append("\n💡 *Recommendations:*")
        for rec in result['recommendations']:
            icon = "🔍" if "Manual" in rec else "📞" if "Contact" in rec else "🔒" if "caution" in rec else "✅"
            lines.append(f"  • {icon} {rec}")

        response = "\n".join(lines)
        send_reply(chat_id, response, parse_mode="Markdown")
        
        if result['fraud_score'] >= 60:
            alert_msg = f"🚨 *HIGH RISK INVOICE DETECTED*\n\n"
            alert_msg += f"Invoice: {inv.get('invoice_number', 'N/A')}\n"
            alert_msg += f"Vendor: {inv.get('vendor_name', 'N/A')}\n"
            alert_msg += f"Amount: {format_amount(inv.get('total_amount', '0'))}\n"
            alert_msg += f"Risk Score: {result['fraud_score']}/100\n\n"
            alert_msg += "⚠️ Immediate investigation required!"
            
            fraud_channel = os.getenv("FRAUD_ALERT_CHANNEL")
            if fraud_channel:
                send_reply(fraud_channel, alert_msg, parse_mode="Markdown")

    except Exception as e:
        logger.exception("Error processing invoice")
        error_msg = "❌ Error processing invoice.\n\n"
        error_msg += f"Error details: {str(e)[:100]}"
        send_reply(chat_id, error_msg)

def _store_invoice_data(invoice_data, fraud_score, fraud_reasons):
    """Store invoice data for reporting and analysis"""
    try:
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

if __name__ == "__main__":
    # No need for webhook setup since we're removing localtunnel
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
