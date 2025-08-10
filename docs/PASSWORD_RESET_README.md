# Password Reset Functionality Documentation

## Overview
This implementation provides a secure password reset functionality with email verification for the ALX Project Nexus backend. Users can reset their passwords by receiving a 6-digit verification code via email.

## Features
- ✅ Email-based password reset with verification codes
- ✅ Secure token generation using Python's `secrets` module
- ✅ 6-digit verification codes for easy user entry
- ✅ Token expiration (1 hour by default)
- ✅ Email notifications for both reset request and confirmation
- ✅ Protection against enumeration attacks (doesn't reveal if email exists)
- ✅ Automatic invalidation of previous tokens when new one is requested
- ✅ Admin interface for monitoring password reset tokens

## Setup Instructions

### 1. Environment Variables
Add the following email configuration to your `.env` file:

```env
# Email Settings (Gmail example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
SERVER_EMAIL=your-email@gmail.com
```

#### For Gmail Users:
1. Enable 2-factor authentication on your Google account
2. Generate an app-specific password:
   - Go to https://myaccount.google.com/security
   - Click on "2-Step Verification"
   - Scroll down to "App passwords"
   - Generate a new app password for "Mail"
   - Use this password as `EMAIL_HOST_PASSWORD`

#### For Other Email Providers:
- **Outlook/Hotmail:**
  - `EMAIL_HOST=smtp-mail.outlook.com`
  - `EMAIL_PORT=587`
  
- **Yahoo:**
  - `EMAIL_HOST=smtp.mail.yahoo.com`
  - `EMAIL_PORT=587` or `465` for SSL
  
- **Custom SMTP:**
  - Use your SMTP server details

### 2. Apply Database Migrations
Run the migrations to create the PasswordResetToken table:

```bash
python manage.py migrate authentication
```

### 3. Test Email Configuration
Test if your email configuration is working:

```bash
python manage.py shell
```

Then in the shell:
```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test email from Django.',
    settings.DEFAULT_FROM_EMAIL,
    ['test@example.com'],  # Replace with your test email
    fail_silently=False,
)
```

## API Endpoints

### 1. Request Password Reset
**POST** `/api/auth/forgot-password/`

Request Body:
```json
{
    "email": "user@example.com"
}
```

Response (200 OK):
```json
{
    "message": "Password reset code has been sent to your email",
    "email": "user@example.com",
    "token": "generated-token-string",
    "expires_in": "1 hour"
}
```

### 2. Verify Reset Code
**POST** `/api/auth/verify-reset-code/`

Request Body:
```json
{
    "token": "token-from-forgot-password",
    "code": "123456"
}
```

Response (200 OK):
```json
{
    "message": "Verification code is valid",
    "token": "token-string",
    "valid": true
}
```

### 3. Reset Password
**POST** `/api/auth/reset-password/`

Request Body:
```json
{
    "token": "token-from-forgot-password",
    "code": "123456",
    "new_password": "NewSecurePassword123",
    "confirm_password": "NewSecurePassword123"
}
```

Response (200 OK):
```json
{
    "message": "Password has been reset successfully. You can now login with your new password.",
    "success": true
}
```

### 4. Resend Reset Code
**POST** `/api/auth/resend-reset-code/`

Request Body:
```json
{
    "email": "user@example.com"
}
```

Response (200 OK):
```json
{
    "message": "A new password reset code has been sent to your email",
    "email": "user@example.com",
    "token": "new-token-string",
    "expires_in": "1 hour"
}
```

## Frontend Integration Example

### React/JavaScript Example:

```javascript
// 1. Request password reset
async function requestPasswordReset(email) {
    const response = await fetch('/api/auth/forgot-password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
    });
    
    const data = await response.json();
    if (response.ok) {
        // Store token for later use
        localStorage.setItem('resetToken', data.token);
        return data;
    }
    throw new Error(data.error);
}

// 2. Verify code
async function verifyResetCode(code) {
    const token = localStorage.getItem('resetToken');
    const response = await fetch('/api/auth/verify-reset-code/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, code })
    });
    
    const data = await response.json();
    if (response.ok) {
        return data.valid;
    }
    throw new Error(data.error);
}

// 3. Reset password
async function resetPassword(code, newPassword, confirmPassword) {
    const token = localStorage.getItem('resetToken');
    const response = await fetch('/api/auth/reset-password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            token,
            code,
            new_password: newPassword,
            confirm_password: confirmPassword
        })
    });
    
    const data = await response.json();
    if (response.ok) {
        // Clear stored token
        localStorage.removeItem('resetToken');
        return data;
    }
    throw new Error(data.error);
}
```

## Testing

### Using the Test Script
A test script is provided to test the password reset functionality:

```bash
python test_password_reset.py
```

Choose option 1 for interactive testing where you can:
1. Enter an email address
2. Check your email for the verification code
3. Enter the code to verify it
4. Set a new password

### Manual Testing with cURL

1. Request password reset:
```bash
curl -X POST http://localhost:8000/api/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```

2. Verify code:
```bash
curl -X POST http://localhost:8000/api/auth/verify-reset-code/ \
  -H "Content-Type: application/json" \
  -d '{"token":"your-token","code":"123456"}'
```

3. Reset password:
```bash
curl -X POST http://localhost:8000/api/auth/reset-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "token":"your-token",
    "code":"123456",
    "new_password":"NewPassword123",
    "confirm_password":"NewPassword123"
  }'
```

## Security Features

1. **Token Security:**
   - Tokens are generated using `secrets.token_urlsafe()` for cryptographic security
   - Each token is unique and unpredictable
   - Tokens expire after 1 hour

2. **Code Security:**
   - 6-digit numeric codes for easy user entry
   - Codes are randomly generated using `secrets.choice()`
   - Combined with token for two-factor verification

3. **Rate Limiting:**
   - Consider implementing rate limiting on password reset endpoints
   - Can be added using Django middleware or third-party packages

4. **Email Enumeration Protection:**
   - The system doesn't reveal whether an email exists in the database
   - Always returns a success message for security

5. **Token Invalidation:**
   - Previous tokens are automatically invalidated when a new one is requested
   - Tokens are marked as "used" once password is reset

## Troubleshooting

### Email Not Sending
1. Check your email credentials in `.env`
2. For Gmail, ensure you're using an app-specific password
3. Check if your firewall allows outbound connections on port 587
4. Try using `EMAIL_USE_TLS=False` and `EMAIL_USE_SSL=True` with port 465

### Token Expired Error
- Tokens expire after 1 hour by default
- Users can request a new token using the resend endpoint
- Adjust `PASSWORD_RESET_TIMEOUT` in settings.py if needed

### Invalid Code Error
- Ensure the code is entered exactly as received
- Codes are case-sensitive (though numeric)
- Check if the token hasn't expired

## Admin Interface

Access the Django admin at `/admin/` to:
- View all password reset tokens
- Check token status (used/expired)
- Monitor password reset attempts
- Manually invalidate tokens if needed

## Customization

### Change Token Expiration Time
In `settings.py`:
```python
PASSWORD_RESET_TIMEOUT = 7200  # 2 hours in seconds
```

### Customize Email Template
Modify the email content in `apps/authentication/email_utils.py`:
- `send_password_reset_email()` - Reset request email
- `send_password_reset_confirmation_email()` - Confirmation email

### Change Code Length
In `apps/authentication/models.py`, modify the `generate_code()` method:
```python
@classmethod
def generate_code(cls):
    """Generate a verification code"""
    return ''.join(secrets.choice(string.digits) for _ in range(8))  # 8-digit code
```

## Production Considerations

1. **Use HTTPS:** Always use HTTPS in production to protect tokens in transit
2. **Rate Limiting:** Implement rate limiting to prevent abuse
3. **Monitoring:** Set up logging and monitoring for password reset attempts
4. **Email Service:** Consider using a dedicated email service (SendGrid, AWS SES, etc.)
5. **Backup Codes:** Consider implementing backup codes for users without email access
6. **2FA:** Consider adding two-factor authentication for additional security

## Support

For issues or questions:
1. Check the Django logs for detailed error messages
2. Verify email configuration with your email provider
3. Test email connectivity using Django shell
4. Review the test script output for debugging information
