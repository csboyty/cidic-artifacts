import random
try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from flask import Blueprint, make_response, current_app, session, request
from wheezy.captcha.image import captcha
from wheezy.captcha.image import background
from wheezy.captcha.image import curve
from wheezy.captcha.image import noise
from wheezy.captcha.image import smooth
from wheezy.captcha.image import text
from wheezy.captcha.image import offset
from wheezy.captcha.image import rotate
from wheezy.captcha.image import warp


captcha_bp = Blueprint('captcha', __name__)


def sample_chars():
    characters = current_app.config['CAPTCHA_CHARACTERS']
    char_length = current_app.config['CAPTCHA_CHARS_LENGTH']
    captcha_code = random.sample(characters, char_length)
    return captcha_code


@captcha_bp.route('/captcha', endpoint="captcha")
def captcha_view():
    out = StringIO()
    captcha_image = captcha(drawings=[
        background(),
        text(fonts=current_app.config['CAPTCHA_FONTS'],
             drawings=[warp(),rotate(), offset()]),
        curve(),
        noise(),
        smooth(),
    ], width=200, height=75)
    captcha_code = ''.join(sample_chars())
    imgfile = captcha_image(captcha_code)
    session['captcha'] = captcha_code.lower()
    imgfile.save(out, 'PNG')
    out.seek(0)
    response = make_response(out.read())
    response.content_type = 'image/png'
    return response


@captcha_bp.route('/check-captcha', methods=['GET'])
def check_captcha():
    input_captcha = request.args.get('captcha', None)
    if input_captcha:
        input_captcha = input_captcha.lower()

    if (not input_captcha) or input_captcha != session.get('captcha', ''):
        return 'false'
    else:
        return 'true'