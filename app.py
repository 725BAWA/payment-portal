from flask import Flask, render_template, request
import os
import csv
from datetime import datetime

app = Flask(__name__)

# Upload folder setup
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# CSV file path
CSV_FILE = 'deposits.csv'

# Bank info
BANK_DETAILS = {
    "bank_name": "State Bank of Example",
    "account_no": "123456789012",
    "ifsc": "SBIN0000123",
    "upi_id": "yourname@upi",
    "qr_image": "example_qr.png"
}

# Home Page
@app.route('/')
def home():
    return render_template('home.html')

# Deposit Page
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        utr = request.form['utr']
        slip = request.files['slip']
        if utr and slip:
            filename = f"{utr}_{slip.filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            slip.save(filepath)

            with open(CSV_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([datetime.now(), utr, filename, 'Pending'])

            return render_template('success.html', utr=utr)
        return "Missing UTR or Slip!"
    return render_template('deposit.html', bank=BANK_DETAILS)

# Admin Panel
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    deposits = []
    if request.method == 'POST':
        action = request.form['action']
        utr_to_update = request.form['utr']
        updated_rows = []
        with open(CSV_FILE, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[1] == utr_to_update:
                    row[3] = 'Approved' if action == 'approve' else 'Rejected'
                updated_rows.append(row)
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(updated_rows)

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                deposits.append({
                    "time": row[0],
                    "utr": row[1],
                    "filename": row[2],
                    "status": row[3]
                })
    return render_template('admin.html', deposits=deposits)

# UTR Status Check
@app.route('/status', methods=['GET', 'POST'])
def check_status():
    result = None
    if request.method == 'POST':
        utr_input = request.form['utr']
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[1] == utr_input:
                        result = {
                            "utr": row[1],
                            "status": row[3]
                        }
                        break
    return render_template('status.html', result=result)

# Run the app (Render-friendly)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
