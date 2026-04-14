from flask import Flask, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import io

app = Flask(__name__)

RED        = colors.HexColor('#B01C1C')
RED_LIGHT  = colors.HexColor('#F5E0E0')
DARK       = colors.HexColor('#1A1A1A')
GRAY       = colors.HexColor('#5A5A5A')
LGRAY      = colors.HexColor('#F4F4F4')
MGRAY      = colors.HexColor('#D0D0D0')
WHITE      = colors.white
GOLD       = colors.HexColor('#D4A017')
GOLD_LIGHT = colors.HexColor('#FDF6E3')
GREEN      = colors.HexColor('#2D6A2D')
GREEN_BG   = colors.HexColor('#EAF3DE')
GREEN_BORDER = colors.HexColor('#639922')
REDDEV_BG  = colors.HexColor('#FCEBEB')
REDDEV     = colors.HexColor('#A32D2D')
REDDEV_BORDER = colors.HexColor('#E24B4A')

def S(name, **kw):
    return ParagraphStyle(name, **kw)

def fmt_money(n):
    return '$ {:,.0f}'.format(int(n)).replace(',', '.')

def fmt_pct(n):
    sign = '+' if n >= 0 else ''
    return f'{sign}{n:.1f}%'

@app.route('/generar-pdf', methods=['POST'])
def generar_pdf():
    data = request.json

    totalTx              = data.get('totalTx', 0)
    totalMonto           = data.get('totalMonto', 0)
    gmvBackwards         = data.get('gmvBackwards', None)
    gmvForecast          = data.get('gmvForecast', None)
    desvioBackwards      = data.get('desvioBackwards
