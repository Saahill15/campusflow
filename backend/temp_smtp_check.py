import smtplib
from core.config import settings
from services.email_service import get_email_service

svc = get_email_service()
print('service_type=' + type(svc).__name__)
print('MAIL_HOST=' + ('configured' if settings.MAIL_HOST is not None else 'missing'))
print('MAIL_PORT=' + ('configured' if settings.MAIL_PORT is not None else 'missing'))
print('MAIL_USERNAME=' + ('configured' if settings.MAIL_USERNAME is not None else 'missing'))
print('MAIL_FROM=' + ('configured' if settings.MAIL_FROM is not None else 'missing'))
print('MAIL_FROM_NAME=' + ('configured' if settings.MAIL_FROM_NAME is not None else 'missing'))
print('MAIL_USE_TLS=' + ('configured' if settings.MAIL_USE_TLS is not None else 'missing'))
print('MAIL_PASSWORD=' + ('configured' if settings.MAIL_PASSWORD is not None else 'missing'))
print('settings_host=' + str(settings.MAIL_HOST))
print('settings_port=' + str(settings.MAIL_PORT))
print('settings_use_tls=' + str(settings.MAIL_USE_TLS))

try:
    if settings.MAIL_USE_TLS:
        server = smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT, timeout=10)
        server.ehlo()
        server.starttls()
        server.ehlo()
    else:
        server = smtplib.SMTP(settings.MAIL_HOST, settings.MAIL_PORT, timeout=10)
        server.ehlo()
    server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
    print('smtp_auth=success')
    server.quit()
except Exception as e:
    print('smtp_auth=failure')
    print(type(e).__name__)
    print(str(e))
