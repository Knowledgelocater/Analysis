# Email Configuration Setup Guide

## Overview
The dashboard is now automatically sent to users via email after analysis completes.

## Configuration Steps

### 1. Update `.env` File
Create or update your `.env` file in the `autoAnalysis/` directory with:

```env
# Existing settings
GROQ_API_KEY=your_groq_key_here
REDIS_URL=redis://localhost:6379/0

# Email settings (Gmail example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
ENABLE_EMAIL=True
```

### 2. Gmail Configuration (Recommended)

#### Option A: Using App Password (Recommended - 2FA enabled)
1. Go to [Google Account](https://myaccount.google.com)
2. Navigate to **Security** → **App passwords**
3. Select **Mail** and **Windows Computer**
4. Google will generate a 16-character password
5. Copy this password to `SENDER_PASSWORD` in `.env`

#### Option B: Using Account Password (No 2FA)
1. Use your Gmail password directly
2. May not work if 2FA is enabled

### 3. Other Email Providers

**Outlook/Hotmail:**
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SENDER_EMAIL=your_email@outlook.com
SENDER_PASSWORD=your_password
```

**Yahoo Mail:**
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SENDER_EMAIL=your_email@yahoo.com
SENDER_PASSWORD=your_app_password
```

---

## How It Works

### User Flow:
1. **User visits** `http://localhost:8000/`
2. **User enters** email address and uploads file
3. **File is processed** in background (Celery worker)
4. **Dashboard is generated** automatically
5. **Email is sent** with both HTML dashboard and JSON analysis
6. **User receives** email with attachments

### Email Contents:
- ✅ **Subject**: "📊 Data Analysis Report - [filename]"
- ✅ **HTML Body**: Instructions on how to use the dashboard
- ✅ **Attachment 1**: `*_dashboard.html` - Interactive dashboard
- ✅ **Attachment 2**: `*_analysis.json` - Statistical data

---

## Testing Email

### Method 1: Via Upload Form
1. Start all services (Redis, Celery, FastAPI)
2. Go to `http://localhost:8000/`
3. Enter your email and upload a test file
4. Wait for processing
5. Check your inbox (may be in spam)

### Method 2: Manual Python Test
```python
from app.services.email_service import email_service

# Test email sending
success = email_service.send_dashboard_email(
    recipient_email="your_email@gmail.com",
    file_name="test_file.xlsx",
    dashboard_path="outputs/test_dashboard.html",
    analysis_path="outputs/test_analysis.json"
)

print(f"Email sent: {success}")
```

---

## Troubleshooting

### Email not received?
1. **Check ENABLE_EMAIL** - Must be `True` in `.env`
2. **Check SENDER_EMAIL and SENDER_PASSWORD** - Must be correct
3. **Check spam folder** - Gmail may flag it as spam initially
4. **Check terminal logs** - Look for error messages in Celery worker
5. **Test credentials** - Try sending a test email manually

### Gmail Authentication Failed?
- Make sure you're using **App Password**, not your account password
- Generate new password if old one is > 30 days old

### SMTP Connection Error?
- Verify SMTP_SERVER and SMTP_PORT are correct
- Check firewall isn't blocking port 587
- Try connecting manually:
```python
import smtplib
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login("your_email@gmail.com", "app_password")
```

---

## Advanced Configuration

### Disable Email (Optional)
```env
ENABLE_EMAIL=False
```

### Custom Email Template
Edit `app/services/email_service.py` → `send_dashboard_email()` method to customize the HTML body.

### Attach Additional Files
```python
# In app/services/email_service.py, modify send_dashboard_email()
message.attach(MIMEText(body, "html"))
# Add more attachments here
self._attach_file(message, "path_to_additional_file")
```

---

## Required New Packages

Install if not already present:
```bash
pip install python-multipart
```

---

## Testing Locally Without Real Email

For development without sending real emails:

```python
# In app/services/email_service.py, replace send_message() with:
print(f"Would send email to: {recipient_email}")
print(f"Attachments: {len(message.get_payload())}")
return True
```

Then set `ENABLE_EMAIL=False` in tests.
