# Email Configuration Guide for Password Reset

## Quick Setup

### Step 1: Create .env file
Copy `env.example` to `.env` and add email configuration:

```bash
cp env.example .env
```

### Step 2: Add Email Configuration to .env
Add these lines to your `.env` file:

```env
# Email Configuration for Password Reset
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@zimmerai.com
APP_URL=http://localhost:3000
```

## Gmail Setup Instructions

### 1. Enable 2-Factor Authentication
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click on "Security"
3. Enable "2-Step Verification"

### 2. Generate App Password
1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Click on "Security"
3. Under "2-Step Verification", click "App passwords"
4. Select "Mail" and "Other (Custom name)"
5. Name it "Zimmer Password Reset"
6. Copy the generated 16-character password

### 3. Configure .env File
Replace the placeholders in your `.env` file:

```env
SMTP_USERNAME=your-actual-gmail@gmail.com
SMTP_PASSWORD=abcd efgh ijkl mnop  # Your 16-character app password
```

## Alternative Email Providers

### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

### Custom SMTP Server
```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

## Testing Email Configuration

### 1. Start the Backend
```bash
cd zimmer-backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Test Password Reset
1. Go to `http://localhost:3000/login`
2. Click "فراموشی رمز عبور"
3. Enter your email address
4. Check your email for the reset link

### 3. Check Console Output
If email fails, check the backend console for error messages.

## Troubleshooting

### Common Issues:

1. **"Authentication failed"**
   - Make sure you're using an App Password, not your regular password
   - Ensure 2-factor authentication is enabled

2. **"Connection refused"**
   - Check your firewall settings
   - Verify SMTP server and port are correct

3. **"Email not received"**
   - Check spam folder
   - Verify email address is correct
   - Check backend console for errors

### Testing Without Email (Development)
If you don't want to configure email yet, the system will:
- Print email content to console
- Still generate valid reset tokens
- Allow you to copy tokens from console for testing

## Security Notes

- Never commit your `.env` file to version control
- Use App Passwords instead of regular passwords
- Consider using environment variables in production
- Regularly rotate your app passwords 