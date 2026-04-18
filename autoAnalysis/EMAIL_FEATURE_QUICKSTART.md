# 📧 Email Dashboard Feature - Quick Start

## What's New? ✨
Users can now receive their dashboard analysis directly via **email with attachments**!

### Workflow:
```
User Uploads File + Email 
    ↓
File Analyzed & Dashboard Generated
    ↓
Email Sent with Attachments
    ↓
User Receives HTML Dashboard + JSON Analysis
```

---

## Setup Instructions

### Step 1: Configure Email Credentials

1. **Copy the template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your email credentials:
   ```env
   ENABLE_EMAIL=True
   SENDER_EMAIL=your_email@gmail.com
   SENDER_PASSWORD=your_app_password
   ```

### Step 2: Gmail Setup (Recommended)

For Gmail with 2FA enabled:
1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **Security** (left sidebar)
3. Find **App passwords** → Select **Mail** and **Windows Computer**
4. Copy the 16-character password
5. Paste into `SENDER_PASSWORD` in `.env`

### Step 3: Start Services

**Terminal 1 - Redis:**
```bash
redis-server --port 6379
```

**Terminal 2 - Celery Worker:**
```bash
cd autoAnalysis
python -m celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

**Terminal 3 - FastAPI Server:**
```bash
cd autoAnalysis
python -m uvicorn app.main:app --reload
```

---

## How Users Upload Files

1. **Visit:** `http://localhost:8000/`
2. **Enter email address**
3. **Select Excel file** (.xlsx or .xls)
4. **Click "Upload & Analyze"**
5. **Check email** for dashboard (may be in spam folder)

---

## New Files Created

| File | Purpose |
|------|---------|
| `app/services/email_service.py` | Email sending logic |
| `app/dashboard_routes.py` | Dashboard API endpoints |
| `app/dashboard.py` | Dashboard HTML generation |
| `EMAIL_SETUP.md` | Detailed email configuration |
| `.env.example` | Template for environment variables |

---

## Files Modified

| File | Changes |
|------|---------|
| `app/main.py` | Added email field to upload form + validation |
| `app/tasks.py` | Added dashboard generation + email sending task |
| `app/config.py` | Added email configuration settings |

---

## API Endpoints

### Upload with Email
```bash
POST /api/upload
Content-Type: multipart/form-data

Parameters:
- email: user@example.com
- file: your_data.xlsx
```

### Check Status
```bash
GET /api/status/{job_id}
```

### Dashboard Endpoints
```bash
GET  /dashboard/list-analysis-files
POST /dashboard/generate/{analysis_file}
GET  /dashboard/view/{dashboard_file}
GET  /dashboard/list
```

---

## Troubleshooting

### Email Not Received?
1. ✅ Check `ENABLE_EMAIL=True` in `.env`
2. ✅ Verify email credentials are correct
3. ✅ Check **spam folder**
4. ✅ Review **Celery worker logs** for errors
5. ✅ Test with manual Python script

### Test Email Sending
```python
# In Python terminal
from app.services.email_service import email_service

email_service.send_dashboard_email(
    recipient_email="test@gmail.com",
    file_name="test.xlsx",
    dashboard_path="outputs/test_dashboard.html",
    analysis_path="outputs/test_analysis.json"
)
```

### Gmail Authentication Failed?
- Use **App Password**, not account password
- Regenerate if older than 30 days
- Ensure 2FA is enabled on Gmail account

### SMTP Error?
- Verify port 587 is not blocked
- Check SMTP_SERVER setting matches your email provider
- Test connection:
```python
import smtplib
smtplib.SMTP("smtp.gmail.com", 587).starttls()
```

---

## Email Providers

### Gmail (Recommended)
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

### Yahoo Mail
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

---

## What Users Receive

📧 **Email Subject:** "📊 Data Analysis Report - [filename]"

📎 **Attachments:**
1. `*_dashboard.html` - Interactive dashboard with 4 tabs:
   - 📈 Numeric Columns (stats)
   - 📋 Categorical Columns (distributions)
   - 🔗 Correlations (relationships)
   - 📝 Sample Data (first 5 rows)

2. `*_analysis.json` - Complete statistical report

💬 **Email Body:**
- Instructions on opening dashboard
- File processing information
- Contact info

---

## Features

✅ Automatic dashboard generation  
✅ Email with attachments  
✅ Multiple email providers supported  
✅ HTML email template  
✅ Graceful error handling  
✅ Logging for debugging  
✅ Backward compatible (optional)  

---

## Security Considerations

- 🔒 Password stored in `.env` (gitignored)
- 🔒 Email validation on upload
- 🔒 File path validation on retrieval
- 🔒 CORS enabled for API access

---

## Next Steps

1. ✅ Configure `.env` with email credentials
2. ✅ Start Redis and Celery worker
3. ✅ Start FastAPI server
4. ✅ Test upload with valid email
5. ✅ Check inbox for dashboard

---

## Support

For detailed email configuration: See `EMAIL_SETUP.md`  
For dashboard features: See `DASHBOARD_GUIDE.md`  
For API documentation: Visit `http://localhost:8000/docs`
