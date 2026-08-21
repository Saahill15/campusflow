from io import BytesIO
from pathlib import Path
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
    """Insert the live QR and pass number into the master pass template."""
    if not qr_token:
        raise ValueError('A QR token is required to generate an entry pass.')
    if not QR_LIB_AVAILABLE:
        raise RuntimeError('The qrcode package is required to generate an entry pass.')

    template_path = Path(__file__).resolve().parents[1] / 'assets' / 'pass-header.png'
    if not template_path.is_file():
        raise FileNotFoundError(f'Approved pass artwork not found: {template_path}')

    image = Image.open(template_path).convert('RGB').copy()
    width, height = image.size
    draw = ImageDraw.Draw(image)

    qr_placeholder = {'x': 326, 'y': 663, 'width': 464, 'height': 424}
    pass_number_placeholder = {'x': 230, 'y': 1166, 'width': 663, 'height': 101}

    qr_inner = {'x': 329, 'y': 666, 'width': 458, 'height': 418}
    draw.rounded_rectangle(
        (
            qr_inner['x'],
            qr_inner['y'],
            qr_inner['x'] + qr_inner['width'],
            qr_inner['y'] + qr_inner['height'],
        ),
        radius=30,
        fill='#F6EEDB',
    )

    qr_size = min(qr_inner['width'], qr_inner['height']) - 28
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=16, border=4)
    qr.add_data(qr_token)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color='black', back_color='#F6EEDB').convert('RGB')
    qr_image = qr_image.resize((qr_size, qr_size), Image.Resampling.NEAREST)
    qr_x = qr_inner['x'] + (qr_inner['width'] - qr_size) // 2
    qr_y = qr_inner['y'] + (qr_inner['height'] - qr_size) // 2
    image.paste(qr_image, (qr_x, qr_y))

    font_path = Path('C:/Windows/Fonts/arialbd.ttf')
    if not font_path.is_file():
        raise FileNotFoundError(f'Pass font not found: {font_path}')
    font_size = 42
    while font_size > 12:
        font = ImageFont.truetype(str(font_path), font_size)
        bounds = draw.textbbox((0, 0), pass_number, font=font)
        if bounds[2] - bounds[0] <= pass_number_placeholder['width'] - 48 and bounds[3] - bounds[1] <= pass_number_placeholder['height'] - 24:
            break
        font_size -= 1
    bounds = draw.textbbox((0, 0), pass_number, font=font)
    text_x = pass_number_placeholder['x'] + (pass_number_placeholder['width'] - (bounds[2] - bounds[0])) // 2
    text_y = pass_number_placeholder['y'] + (pass_number_placeholder['height'] - (bounds[3] - bounds[1])) // 2 - bounds[1]
    draw.text((text_x, text_y), pass_number, font=font, fill='#F6EEDB')

    buffer = BytesIO()
    image.save(buffer, format='PNG', optimize=False)
    return buffer.getvalue()
