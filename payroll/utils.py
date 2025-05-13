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

    # Create a BytesIO object to store the PDF
    buffer = io.BytesIO()
    
    # Create the PDF object with landscape orientation
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []
    
    # Add title with smaller font
    from reportlab.platypus import Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.fontSize = 14  # Reduce title font size
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph("<br/>", styles['Normal']))  # Reduce space after title
    
    # Convert DataFrame to list of lists for the table
    table_data = [df.columns.tolist()] + df.values.tolist()
    
    # Create the table
    table = Table(table_data)
    
    # Add style to the table with smaller fonts and reduced padding
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),  # Reduce header font size
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  # Reduce header padding
        ('TOPPADDING', (0, 0), (-1, 0), 6),  # Reduce header padding
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),  # Reduce content font size
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Thinner grid lines
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Reduce cell padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Reduce cell padding
        ('TOPPADDING', (0, 1), (-1, -1), 3),  # Reduce cell padding
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),  # Reduce cell padding
    ])
    table.setStyle(style)
    
    # Add the table to the elements
    elements.append(table)
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create the HttpResponse
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
    response.write(pdf)
    
    return response 