from flask import Flask, request, jsonify
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
        # Check if Domain Exists with MX Records
        mx_records = dns.resolver.resolve(domain, 'MX')
        if not mx_records:
            return jsonify({"is_email_valid": False, "message": "No MX Records Found"})
        return jsonify({"is_email_valid": True, "email": email, "message": "Email is Valid ✅ (MX Record Found)"})
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return jsonify({"is_email_valid": False, "message": "Invalid Domain or Domain Does Not Exist"})
    except Exception as e:
        return jsonify({"is_email_valid": False, "message": str(e)})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 10000))
    app.run(debug=True, host='0.0.0.0', port=port)
