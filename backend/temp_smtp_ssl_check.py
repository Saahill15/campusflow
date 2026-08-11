import ssl
import smtplib
from core.config import settings

print('host=' + str(settings.MAIL_HOST))
print('port=' + str(settings.MAIL_PORT))
print('use_tls=' + str(settings.MAIL_USE_TLS))
try:
    context = ssl.create_default_context()
    server = smtplib.SMTP_SSL(settings.MAIL_HOST, settings.MAIL_PORT, context=context, timeout=10)
    server.ehlo()
    server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
    print('smtp_ssl_auth=success')
    server.quit()
except Exception as e:
    print('smtp_ssl_auth=failure')
    print(type(e).__name__)
    print(str(e))
