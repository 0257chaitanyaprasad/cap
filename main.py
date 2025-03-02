from flask import Flask, request, jsonify
import smtplib
import dns.resolver

app = Flask(__name__)

@app.route('/')
def welcome():
    return jsonify({"message": "Email Validation API is Running 🔥"})

@app.route('/validate-email', methods=['GET'])
def validate_email():
    email = request.args.get("email")
    if not email:
        return jsonify({"is_email_valid": False, "message": "Email is Required"})
    
    domain = email.split('@')[-1]
    
    try:
        # Check if Domain Exists
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        return jsonify({"is_email_valid": False, "message": "Invalid Domain or Domain Does Not Exist"})
    except Exception as e:
        return jsonify({"is_email_valid": False, "message": str(e)})

    try:
        # SMTP Connection
        server = smtplib.SMTP(mx_record)
        server.helo()
        server.mail("test@gmail.com")
        code, _ = server.rcpt(email)
        server.quit()
        
        if code == 250:
            return jsonify({"is_email_valid": True, "email": email, "message": "Email is Valid ✅"})
        else:
            return jsonify({"is_email_valid": False, "email": email, "message": "Email Does Not Exist ❌"})
    
    except Exception as e:
        return jsonify({"is_email_valid": False, "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
