from flask import Flask, request, jsonify
import smtplib
import dns.resolver
import re
import os

app = Flask(__name__)

@app.route('/')
def welcome():
    return jsonify({"message": "Email Validation API is Running 🔥"})

# Email Regex Pattern
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

@app.route('/validate-email', methods=['GET'])
def validate_email():
    email = request.args.get("email")
    if not email:
        return jsonify({"is_email_valid": False, "message": "Email is Required"})
    
    if not re.match(EMAIL_REGEX, email):
        return jsonify({"is_email_valid": False, "message": "Invalid Email Format"})

    domain = email.split('@')[-1]
    
    try:
        # Check if Domain Exists
        mx_records = dns.resolver.resolve(domain, 'MX')
        if not mx_records:
            return jsonify({"is_email_valid": False, "message": "No MX Records Found"})
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return jsonify({"is_email_valid": False, "message": "Invalid Domain or Domain Does Not Exist"})
    except Exception as e:
        return jsonify({"is_email_valid": False, "message": str(e)})

    try:
        # Connect to SMTP server to verify Email
        mx_record = str(mx_records[0].exchange).strip()
        server = smtplib.SMTP(mx_record, 25, timeout=10)
        server.set_debuglevel(0)
        server.helo()
        server.mail("test@gmail.com")  # Dummy sender email
        code, message = server.rcpt(email)
        server.quit()
        
        if code == 250:
            return jsonify({"is_email_valid": True, "email": email, "message": "Email is Valid ✅"})
        else:
            return jsonify({"is_email_valid": False, "email": email, "message": "Email Does Not Exist ❌"})
    except smtplib.SMTPConnectError:
        return jsonify({"is_email_valid": False, "message": "SMTP Connection Failed"})
    except Exception as e:
        return jsonify({"is_email_valid": False, "message": str(e)})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
