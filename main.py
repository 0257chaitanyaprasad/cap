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
        dns.resolver.resolve(domain, 'MX')
    except dns.resolver.NoAnswer:
        return jsonify({"is_email_valid": False, "message": "Invalid Domain"})
    except dns.resolver.NXDOMAIN:
        return jsonify({"is_email_valid": False, "message": "Domain Does Not Exist"})
    except Exception as e:
        return jsonify({"is_email_valid": False, "message": str(e)})

    try:
        # Connect to SMTP server to verify Email
        server = smtplib.SMTP(timeout=10)
        server.set_debuglevel(0)
        server.connect(dns.resolver.resolve(domain, 'MX')[0].exchange.to_text())
        server.helo()
        server.mail("test@gmail.com")  # Dummy sender email
        code, _ = server.rcpt(email)
        server.quit()
        if code == 250:
            return jsonify({"is_email_valid": True, "email": email, "message": "Email is Valid ✅"})
        else:
            return jsonify({"is_email_valid": False, "email": email, "message": "Email Does Not Exist ❌"})
    except Exception as e:
        return jsonify({"is_email_valid": False, "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=10000)
