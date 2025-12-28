# force redeploy
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from fpdf import FPDF
import yagmail, base64, datetime, os

app = Flask(__name__)
CORS(app)

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

def generate_pdf(name, email, date, sig_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('Helvetica','','',uni=False)
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0,8,txt="研究參與同意書 / Consent to Participate in Research Project",align='C')
    pdf.ln(8)
    pdf.multi_cell(0,8,f"姓名: {name}\n電郵: {email}\n日期: {date}\n",align='L')
    pdf.ln(5)
    pdf.multi_cell(0,8,
    f"""研究項目: 連結點滴：探討風險與保護因素對香港長者孤獨類型與心理健康的影響
Connecting the Dots: Examining the Impact of Risk and Protective Factors on Loneliness Types and Mental Health in Hong Kong's Elderly

我，{name}，特此同意參與由 Dr Ngai Sing Bik Cindy 主導之研究。
I, {name}, hereby consent to participate in the above research conducted by Dr Ngai Sing Bik Cindy.
""")
    pdf.ln(10)
    pdf.cell(0,8,"簽名 / Signature:",ln=1)
    if os.path.exists(sig_path):
        pdf.image(sig_path,x=30,w=80)
    filename=f"{name}_consent.pdf"
    pdf.output(filename)
    return filename

@app.route("/submit",methods=["POST"])
def submit():
    data=request.get_json()
    name=data["name"]; email=data["email"]; date=data["date"]
    sig_bytes=base64.b64decode(data["signature"].split(",")[1])
    sig_path=f"{name}_signature.png"
    with open(sig_path,"wb") as f: f.write(sig_bytes)
    pdf_path=generate_pdf(name,email,date,sig_path)
    yag=yagmail.SMTP(user=SENDER_EMAIL,password=APP_PASSWORD)
    yag.send(
        to=RECEIVER_EMAIL,
        subject=f"New Consent Form - {name}",
        contents=[f"Name: {name}<br>Email: {email}<br>Date: {date}<br><br>Signed consent attached."],
        attachments=[pdf_path]
    )
    print(f"✅ sent {pdf_path} to {RECEIVER_EMAIL}")
    return jsonify({"ok":True})

@app.route("/")
def index():
    return send_from_directory(".", "consent_form.html")

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
