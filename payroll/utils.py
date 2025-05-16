import pandas as pd
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch
import io

def export_to_excel(data, filename, sheet_name='Sheet1'):
    """
    Export data to Excel file
    data: List of dictionaries or DataFrame
    filename: Name of the file to be downloaded
    sheet_name: Name of the Excel sheet
    """
    if not isinstance(data, pd.DataFrame):
        df = pd.DataFrame(data)
    else:
        df = data

    # Create a BytesIO object to store the Excel file
    output = io.BytesIO()
    
    # Create Excel writer object
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Get the workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        
        # Add some formatting
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'bg_color': '#D9E1F2',
            'border': 1
        })
        
        # Write the column headers with the defined format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, 15)  # Set column width

    # Set the response headers
    output.seek(0)
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}.xlsx"'
    return response

def export_to_pdf(data, filename, title):
    """
    Export data to PDF file
    data: List of dictionaries or DataFrame
    filename: Name of the file to be downloaded
    title: Title of the PDF document
    """
    if not isinstance(data, pd.DataFrame):
        df = pd.DataFrame(data)
    else:
        df = data

    from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, landscape

    buffer = io.BytesIO()
    page_width, _ = landscape(letter)
    margin = 40
    available_width = page_width - 2 * margin
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    normal_style.fontSize = 7
    normal_style.leading = 8
    header_style = styles['Heading5']
    header_style.fontSize = 8
    header_style.leading = 9
    header_style.alignment = 1  # center

    # Abbreviate headers for clarity
    header_map = {
        'DESIGNATION': 'DESIG',
        'PROCESS_CYCLE': 'CYCLE',
        'EMPLOYEE_CODE': 'EMP CODE',
        'EMP_NAME': 'NAME',
        'A_BASIC': 'A_BASIC',
        'A_ALLOW': 'A_ALLOW',
        'PROCESS_COMP_FLAG': 'COMP_FLG',
        'PRESENT': 'PRES',
        'ABSENT': 'ABS',
        'WDAYS': 'WDAYS',
        'OT1_HOURS': 'OT1 HRS',
        'OT2_HOURS': 'OT2 HRS',
        'BASIC': 'BASIC',
        'ALLOWANCE': 'ALLOW',
        'OT1': 'OT1',
        'OT2': 'OT2',
        'G_PAY': 'G_PAY',
        'G_DED': 'G_DED',
        'NET': 'NET',
    }
    columns = df.columns.tolist()
    display_headers = [header_map.get(col, col) for col in columns]

    # Calculate column widths: EMP_NAME and DESIGNATION get 1.5x, others share the rest
    n_cols = len(columns)
    min_col_width = 35
    special_cols = ['EMP_NAME', 'DESIGNATION']
    special_weight = 1.5
    weights = []
    for col in columns:
        if col in special_cols:
            weights.append(special_weight)
        else:
            weights.append(1)
    total_weight = sum(weights)
    col_widths = [max(min_col_width, available_width * w / total_weight) for w in weights]

    # If total width is still too large, scale down proportionally
    total_width = sum(col_widths)
    if total_width > available_width:
        scale = available_width / total_width
        col_widths = [w * scale for w in col_widths]

    # Header row with Paragraphs
    table_data = [[Paragraph(str(col), header_style) for col in display_headers]]
    # Data rows with Paragraphs
    for row in df.values.tolist():
        table_data.append([Paragraph(str(cell), normal_style) for cell in row])

    table = Table(table_data, colWidths=col_widths)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('TOPPADDING', (0, 0), (-1, 0), 4),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 1), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 1),
    ])
    table.setStyle(style)

    elements = []
    title_style = styles['Title']
    title_style.fontSize = 14
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph("<br/>", styles['Normal']))
    elements.append(table)
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=margin, rightMargin=margin)
    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    response.write(pdf)
    return response 