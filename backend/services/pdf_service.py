from io import BytesIO
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

try:
    import qrcode
    QR_LIB_AVAILABLE = True
except Exception:
    QR_LIB_AVAILABLE = False


def generate_pass_png_bytes(
    registration_number: str,
    pass_number: str,
    attendee_name: str,
    event_title: str = 'Pragyarambh 3.0',
    department: str = '',
    academic_year: str = '',
    qr_token: Optional[str] = None,
) -> bytes:
    # Portrait pass, phone-friendly
    width = 1200
    height = 1800
    background_color = 'white'
    text_color = 'black'
    padding = 60

    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)
    try:
        font_large = ImageFont.truetype('DejaVuSans-Bold.ttf', 48)
        font_med = ImageFont.truetype('DejaVuSans.ttf', 36)
        font_small = ImageFont.truetype('DejaVuSans.ttf', 28)
    except Exception:
        font_large = ImageFont.load_default()
        font_med = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Header / branding
    draw.text((padding, padding), 'Pragyarambh', font=font_large, fill=text_color)
    draw.text((padding, padding + 70), event_title, font=font_med, fill=text_color)

    # Main attendee block
    y = padding + 160
    draw.text((padding, y), f'Name: {attendee_name}', font=font_med, fill=text_color)
    y += 60
    draw.text((padding, y), f'Registration No: {registration_number}', font=font_med, fill=text_color)
    y += 50
    draw.text((padding, y), f'Pass No: {pass_number}', font=font_med, fill=text_color)
    y += 50
    if department:
        draw.text((padding, y), f'Department: {department}', font=font_small, fill=text_color)
        y += 40
    if academic_year:
        draw.text((padding, y), f'Academic Year: {academic_year}', font=font_small, fill=text_color)
        y += 40

    # Footer note
    footer_y = height - padding - 120
    draw.text((padding, footer_y), 'Please present this pass at the event entrance.', font=font_small, fill=text_color)

    # QR placement
    if qr_token:
        try:
            if QR_LIB_AVAILABLE:
                qr_img = qrcode.make(qr_token)
                # ensure QR is square and sized appropriately
                qr_size = 520
                qr_img = qr_img.resize((qr_size, qr_size))
                qr_x = width - padding - qr_size
                qr_y = padding + 200
                image.paste(qr_img, (qr_x, qr_y))
            else:
                # Fallback: draw token text in QR area if qrcode lib missing
                qr_box_x = width - padding - 520
                qr_box_y = padding + 200
                draw.rectangle([qr_box_x, qr_box_y, qr_box_x + 520, qr_box_y + 520], outline=text_color)
                draw.text((qr_box_x + 20, qr_box_y + 20), qr_token, font=font_small, fill=text_color)
        except Exception:
            # don't raise; caller will handle missing image/attachment
            raise

    buffer = BytesIO()
    image.save(buffer, format='PNG', optimize=True)
    return buffer.getvalue()
