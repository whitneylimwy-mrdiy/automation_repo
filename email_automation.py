import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import pandas as pd
from google.oauth2.service_account import Credentials
import requests
import pandas as pd
import urllib3
import io

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def get_receivers_from_sheet():
    sheet_id = "1IPs5mX0IHZ0CnNShpSnX6pXD33K3bUpxpaTXjDEnF5w"
    gid      = "0"
    csv_url  = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    response = requests.get(csv_url, verify=False)
    
    if "<!DOCTYPE html>" in response.text:
        print("❌ Google returned a login page!")
        print("👉 Fix: Share your Google Sheet → 'Anyone with the link can view'")
        return []
    
    df = pd.read_csv(io.StringIO(response.text))
    print("✅ Columns found:", df.columns.tolist())
    
    # ── Handle different possible column names ───────────────────
    # Check what your actual column name is
    email_col = None
    for col in df.columns:
        if "email" in col.lower() or "mail" in col.lower():
            email_col = col
            break
    
    if email_col is None:
        print("❌ No email column found! Available columns:", df.columns.tolist())
        print("👉 Rename your column header to 'email' in Google Sheet")
        return []
    
    emails = df[email_col].tolist()
    emails = [e for e in emails if isinstance(e, str) and "@" in e]
    print(f"📧 Found {len(emails)} recipients: {emails}")
    return emails

def send_email():
    sender   = "whitney.limwy@mrdiy.com"
    password = os.environ.get("EMAIL_PASSWORD")
    
    receivers     = get_receivers_from_sheet()
    receivers_str = ", ".join(receivers)  # "a@gmail.com, b@gmail.com"
    
    print(f"📧 Sending to: {receivers_str}")

    message             = MIMEMultipart("alternative")
    message["From"]     = sender
    message["To"]       = receivers_str   # ← Dynamic from sheet!
    message["Subject"]  = "Big Query Usage Notification [Automated Email]"

    html_body = """
    <html>
    <body style="font-family: Arial, sans-serif; font-size: 14px;">
        <p>Dear Team,</p>
        <p>Hope this email finds you well! Here I attached the <strong>Big Query GB usage</strong>,
        this email could help us keep track on Big Query Usage.</p>
        <p>Here I attached the spreadsheet link, if you guys have any new dashboard, please fill in the Dashboard URL.</p>
        <a href="https://docs.google.com/spreadsheets/d/1G4bb5CW4wA7IiFrLic_1rGta1-93g7VGmP9e96jxOos/edit?gid=70880802#gid=70880802">
    Click here to view the sheet
    </a>>
        <p>Best Regards,<br><strong>Whitney</strong></p>
    </body>
    </html>
    """
    message.attach(MIMEText(html_body, "html"))


    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receivers, message.as_string())
        print(f"✅ Email sent to {len(receivers)} recipients!")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    send_email()
