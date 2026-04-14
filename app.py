from flask import Flask, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import io

app = Flask(__name__)

RED          = colors.HexColor('#B01C1C')
RED_LIGHT    = colors.HexColor('#F5E0E0')
DARK         = colors.HexColor('#1A1A1A')
GRAY         = colors.HexColor('#5A5A5A')
LGRAY        = colors.HexColor('#F4F4F4')
MGRAY        = colors.HexColor('#D0D0D0')
WHITE        = colors.white
GOLD         = colors.HexColor('#D4A017')
GOLD_LIGHT   = colors.HexColor('#FDF6E3')
GREEN        = colors.HexColor('#2D6A2D')
GREEN_BG     = colors.HexColor('#EAF3DE')
GREEN_BORDER = colors.HexColor('#639922')
REDDEV_BG    = colors.HexColor('#FCEBEB')
REDDEV       = colors.HexColor('#A32D2D')
REDDEV_BORDER = colors.HexColor('#E24B4A')

def S(name, **kw):
    return ParagraphStyle(name, **kw)

def fmt_money(n):
    return '$ {:,.0f}'.format(int(n)).replace(',', '.')

def fmt_pct(n):
    if n >= 0:
        return '+' + '{:.1f}'.format(n) + '%'
    else:
        return '{:.1f}'.format(n) + '%'

@app.route('/generar-pdf', methods=['POST'])
def generar_pdf():
    data = request.json

    totalTx            = data.get('totalTx', 0)
    totalMonto         = data.get('totalMonto', 0)
    gmvBackwards       = data.get('gmvBackwards', None)
    gmvForecast        = data.get('gmvForecast', None)
    desvioBackwards    = data.get('desvioBackwards', None)
    desvioBackwardsPct = data.get('desvioBackwardsPct', None)
    desvioForecast     = data.get('desvioForecast', None)
    desvioForecastPct  = data.get('desvioForecastPct', None)
    destacadoNombre    = data.get('destacadoNombre', '')
    destacadoTx        = data.get('destacadoTx', 0)
    destacadoMonto     = data.get('destacadoMonto', 0)
    cat1Name           = data.get('cat1Name', '')
    cat1Tx             = data.get('cat1Tx', 0)
    cat1Monto          = data.get('cat1Monto', 0)
    cat2Name           = data.get('cat2Name', '')
    cat2Tx             = data.get('cat2Tx', 0)
    cat2Monto          = data.get('cat2Monto', 0)
    topCats            = data.get('topCats', [])
    topProds           = data.get('topProds', [])
    fecha              = data.get('fecha', '')

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=14*mm, bottomMargin=14*mm)

    sTitle    = S('title',  fontName='Helvetica-Bold', fontSize=22, textColor=WHITE, alignment=TA_LEFT,   leading=26)
    sSection  = S('sec',    fontName='Helvetica-Bold', fontSize=10, textColor=RED,   alignment=TA_LEFT,   leading=14)
    sGray     = S('gray',   fontName='Helvetica',       fontSize=9,  textColor=GRAY,  alignment=TA_LEFT,   leading=13)
    sTH       = S('th',     fontName='Helvetica-Bold', fontSize=8,  textColor=WHITE, alignment=TA_CENTER, leading=11)
    sTD       = S('td',     fontName='Helvetica',       fontSize=8,  textColor=DARK,  alignment=TA_LEFT,   leading=11)
    sTDR      = S('tdr',    fontName='Helvetica',       fontSize=8,  textColor=DARK,  alignment=TA_RIGHT,  leading=11)
    sTDB      = S('tdb',    fontName='Helvetica-Bold', fontSize=8,  textColor=DARK,  alignment=TA_LEFT,   leading=11)
    sTDBR     = S('tdbr',   fontName='Helvetica-Bold', fontSize=8,  textColor=DARK,  alignment=TA_RIGHT,  leading=11)
    sMetricN  = S('mn',     fontName='Helvetica-Bold', fontSize=20, textColor=DARK,  alignment=TA_CENTER, leading=24)
    sMetricL  = S('ml',     fontName='Helvetica',       fontSize=8,  textColor=GRAY,  alignment=TA_CENTER, leading=10)
    sHighN    = S('hn',     fontName='Helvetica-Bold', fontSize=14, textColor=GOLD,  alignment=TA_CENTER, leading=18)
    sHighTx   = S('htx',   fontName='Helvetica-Bold', fontSize=20, textColor=GOLD,  alignment=TA_CENTER, leading=24)
    sHighL    = S('hl',     fontName='Helvetica',       fontSize=8,  textColor=GRAY,  alignment=TA_CENTER, leading=10)
    sPname    = S('pname',  fontName='Helvetica-Bold', fontSize=11, textColor=DARK,  alignment=TA_LEFT,   leading=14)
    sRK       = S('rk',     fontName='Helvetica',       fontSize=8,  textColor=GRAY,  alignment=TA_CENTER, leading=11)
    sFooter   = S('footer', fontName='Helvetica',       fontSize=7,  textColor=GRAY,  alignment=TA_CENTER, leading=10)
    sDevLabel = S('devlbl', fontName='Helvetica',       fontSize=8,  textColor=GRAY,  alignment=TA_LEFT,   leading=11)
    sDevPos   = S('devpos', fontName='Helvetica-Bold', fontSize=9,  textColor=GREEN,  alignment=TA_RIGHT,  leading=11)
    sDevNeg   = S('devneg', fontName='Helvetica-Bold', fontSize=9,  textColor=REDDEV, alignment=TA_RIGHT,  leading=11)
    sDevNeu   = S('devneu', fontName='Helvetica-Bold', fontSize=9,  textColor=DARK,   alignment=TA_RIGHT,  leading=11)

    story = []

    # HEADER
    ht = Table([[
        Paragraph('Reporte diario', sTitle),
        Paragraph('ICBC Mall<br/><font size="9">' + fecha + '</font>',
                  S('h2', fontName='Helvetica-Bold', fontSize=14, textColor=WHITE, alignment=TA_RIGHT, leading=18))
    ]], colWidths=[110*mm, 64*mm])
    ht.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),RED),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),8),
        ('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),10),
        ('BOTTOMPADDING',(0,0),(-1,-1),10),
    ]))
    story.append(ht)
    story.append(Spacer(1,8))

    # KPIs
    kt = Table([[
        Table([[Paragraph(str(totalTx), sMetricN)],[Paragraph('Transacciones totales', sMetricL)]]),
        Table([[Paragraph(fmt_money(totalMonto), sMetricN)],[Paragraph('Monto total', sMetricL)]]),
    ]], colWidths=[87*mm, 87*mm])
    kt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),LGRAY),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),10),
        ('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('LINEAFTER',(0,0),(0,-1),0.5,MGRAY),
    ]))
    story.append(kt)
    story.append(Spacer(1,8))

    # DESVIO VS OBJETIVO
    if gmvBackwards or gmvForecast:
        story.append(Paragraph('Desvio vs objetivo', sSection))
        story.append(Spacer(1,4))

        def desvio_block(label_obj, val_obj, label_dev, pct, abs_val):
            is_pos = pct is not None and pct >= 0
            sVal = sDevPos if is_pos else sDevNeg
            bg = GREEN_BG if is_pos else REDDEV_BG
            border = GREEN_BORDER if is_pos else REDDEV_BORDER
            pct_str = fmt_pct(pct) if pct is not None else '--'
            abs_str = fmt_money(abs(abs_val)) if abs_val is not None else '--'
            sign = '+' if is_pos else '-'
            dev_str = pct_str + '  (' + sign + abs_str + ')'
            obj_str = fmt_money(val_obj) if val_obj else '--'
            t = Table([[
                Paragraph(label_obj, sDevLabel),
                Paragraph(obj_str, sDevNeu),
            ],[
                Paragraph(label_dev, sDevLabel),
                Paragraph(dev_str, sVal),
            ]], colWidths=[120*mm, 54*mm])
            t.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,-1),bg),
                ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                ('TOPPADDING',(0,0),(-1,-1),7),
                ('BOTTOMPADDING',(0,0),(-1,-1),7),
                ('LEFTPADDING',(0,0),(0,-1),10),
                ('RIGHTPADDING',(-1,0),(-1,-1),10),
                ('LINEBEFORE',(0,0),(0,-1),3,border),
                ('BOX',(0,0),(-1,-1),0.3,MGRAY),
            ]))
            return t

        if gmvBackwards:
            story.append(desvio_block(
                'Backwards - objetivo del dia', gmvBackwards,
                'Desvio vs Backwards', desvioBackwardsPct, desvioBackwards
            ))
            story.append(Spacer(1,5))

        if gmvForecast:
            story.append(desvio_block(
                'Forecast - objetivo del dia', gmvForecast,
                'Desvio vs Forecast', desvioForecastPct, desvioForecast
            ))
            story.append(Spacer(1,5))

        story.append(Spacer(1,5))

    # DESTACADO
    story.append(Paragraph('Producto destacado de la semana', sSection))
    story.append(Spacer(1,4))
    hl = Table([[
        Table([[Paragraph(destacadoNombre, sPname)],[Paragraph('Producto estrella - destacado grande de la semana', sGray)]]),
        Table([[Paragraph(str(destacadoTx), sHighTx)],[Paragraph('Transacciones', sHighL)]]),
        Table([[Paragraph(fmt_money(destacadoMonto), sHighN)],[Paragraph('Monto total', sHighL)]]),
    ]], colWidths=[88*mm, 43*mm, 43*mm])
    hl.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),GOLD_LIGHT),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),10),
        ('BOTTOMPADDING',(0,0),(-1,-1),10),
        ('LEFTPADDING',(0,0),(0,-1),10),
        ('LINEAFTER',(0,0),(0,-1),0.5,MGRAY),
        ('LINEAFTER',(1,0),(1,-1),0.5,MGRAY),
        ('BOX',(0,0),(-1,-1),1,GOLD),
    ]))
    story.append(hl)
    story.append(Spacer(1,10))

    # CATEGORIAS A POTENCIAR
    story.append(Paragraph('Categorias a potenciar de la semana', sSection))
    story.append(Spacer(1,4))
    cr = [
        [Paragraph('Categoria',sTH), Paragraph('Transacciones',sTH), Paragraph('Monto total',sTH)],
        [Paragraph(cat1Name,sTD),    Paragraph(str(cat1Tx),sTDR),    Paragraph(fmt_money(cat1Monto),sTDR)],
        [Paragraph(cat2Name,sTDB),   Paragraph(str(cat2Tx),sTDBR),   Paragraph(fmt_money(cat2Monto),sTDBR)],
    ]
    ct = Table(cr, colWidths=[88*mm, 43*mm, 43*mm])
    ct.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),RED),
        ('BACKGROUND',(0,1),(-1,1),LGRAY),
        ('BACKGROUND',(0,2),(-1,2),WHITE),
        ('ALIGN',(1,0),(-1,-1),'RIGHT'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),7),
        ('BOTTOMPADDING',(0,0),(-1,-1),7),
        ('LEFTPADDING',(0,0),(0,-1),10),
        ('RIGHTPADDING',(-1,0),(-1,-1),10),
        ('LINEBELOW',(0,0),(-1,-2),0.3,MGRAY),
        ('BOX',(0,0),(-1,-1),0.5,MGRAY),
    ]))
    story.append(ct)
    story.append(Spacer(1,10))

    # TOP 10 CATEGORIAS
    story.append(Paragraph('Top 10 categorias por transacciones', sSection))
    story.append(Spacer(1,4))
    tcr = [[Paragraph('#',sTH), Paragraph('Categoria',sTH), Paragraph('Transacc.',sTH), Paragraph('Monto total',sTH)]]
    for i, c in enumerate(topCats):
        tcr.append([Paragraph(str(i+1),sRK), Paragraph(c['name'],sTD), Paragraph(str(c['tx']),sTDR), Paragraph(fmt_money(c['monto']),sTDR)])
    tct = Table(tcr, colWidths=[12*mm, 88*mm, 28*mm, 46*mm])
    tct.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),RED),
        ('ALIGN',(0,0),(0,-1),'CENTER'),
        ('ALIGN',(2,0),(-1,-1),'RIGHT'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(1,0),(1,-1),8),
        ('RIGHTPADDING',(-1,0),(-1,-1),8),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[LGRAY,WHITE]),
        ('LINEBELOW',(0,0),(-1,-2),0.3,MGRAY),
        ('BOX',(0,0),(-1,-1),0.5,MGRAY),
    ]))
    story.append(tct)
    story.append(Spacer(1,10))

    # TOP 10 PRODUCTOS
    story.append(Paragraph('Top 10 productos por transacciones', sSection))
    story.append(Spacer(1,4))
    tpr = [[Paragraph('#',sTH), Paragraph('Producto',sTH), Paragraph('Transacc.',sTH), Paragraph('Monto total',sTH)]]
    for i, p in enumerate(topProds):
        tpr.append([Paragraph(str(i+1),sRK), Paragraph(p['name'],sTD), Paragraph(str(p['tx']),sTDR), Paragraph(fmt_money(p['monto']),sTDR)])
    tpt = Table(tpr, colWidths=[12*mm, 108*mm, 20*mm, 34*mm])
    tpt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),RED),
        ('ALIGN',(0,0),(0,-1),'CENTER'),
        ('ALIGN',(2,0),(-1,-1),'RIGHT'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),5),
        ('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(1,0),(1,-1),8),
        ('RIGHTPADDING',(-1,0),(-1,-1),8),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[LGRAY,WHITE]),
        ('LINEBELOW',(0,0),(-1,-2),0.3,MGRAY),
        ('BOX',(0,0),(-1,-1),0.5,MGRAY),
    ]))
    story.append(tpt)

    # FOOTER
    story.append(Spacer(1,12))
    story.append(HRFlowable(width='100%', thickness=0.5, color=MGRAY))
    story.append(Spacer(1,4))
    story.append(Paragraph('Reporte generado el ' + fecha + ' - ICBC Mall - Datos internos', sFooter))

    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, mimetype='application/pdf',
                     as_attachment=True,
                     download_name='reporte_icbc_' + fecha + '.pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
