from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import requests
import time
import os
import json
from datetime import datetime, timedelta
import logging
from werkzeug.serving import WSGIRequestHandler

# Suppress Werkzeug's development server warning
logging.getLogger('werkzeug').setLevel(logging.ERROR)

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PDF_FOLDER = 'downloaded_pdfs'
if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

def generate_pdf(causelist_data, filename):
    filepath = os.path.join(PDF_FOLDER, filename)
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30,
        alignment=1
    )
    
    title = Paragraph(f"<b>Cause List</b>", title_style)
    elements.append(title)
    
    info_style = styles['Normal']
    info_text = f"<b>Court:</b> {causelist_data.get('court_name', causelist_data.get('court_code', 'N/A'))}<br/>"
    info_text += f"<b>Date:</b> {causelist_data.get('date', 'N/A')}<br/>"
    info_text += f"<b>Total Cases:</b> {len(causelist_data.get('cases', []))}"
    
    info = Paragraph(info_text, info_style)
    elements.append(info)
    elements.append(Spacer(1, 20))
    
    if causelist_data.get('cases'):
        table_data = [['Sr. No.', 'Case No.', 'Party Name', 'Purpose']]
        
        for case in causelist_data['cases']:
            table_data.append([
                case.get('sr_no', ''),
                case.get('case_no', ''),
                case.get('party_name', ''),
                case.get('purpose', '')
            ])
        
        table = Table(table_data, colWidths=[0.8*inch, 2*inch, 3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        elements.append(table)
    else:
        no_cases = Paragraph("<i>No cases found for this date.</i>", info_style)
        elements.append(no_cases)
    
    doc.build(elements)
    return filepath

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get-states', methods=['GET'])
def get_states():
    fallback_states = [
        {'value': '1', 'text': 'Andaman and Nicobar Islands'},
        {'value': '2', 'text': 'Andhra Pradesh'},
        {'value': '3', 'text': 'Arunachal Pradesh'},
        {'value': '4', 'text': 'Assam'},
        {'value': '5', 'text': 'Bihar'},
        {'value': '6', 'text': 'Chandigarh'},
        {'value': '7', 'text': 'Chhattisgarh'},
        {'value': '8', 'text': 'Dadra and Nagar Haveli'},
        {'value': '9', 'text': 'Daman and Diu'},
        {'value': '10', 'text': 'Delhi'},
        {'value': '11', 'text': 'Goa'},
        {'value': '12', 'text': 'Gujarat'},
        {'value': '13', 'text': 'Haryana'},
        {'value': '14', 'text': 'Himachal Pradesh'},
        {'value': '15', 'text': 'Jammu and Kashmir'},
        {'value': '16', 'text': 'Jharkhand'},
        {'value': '17', 'text': 'Karnataka'},
        {'value': '18', 'text': 'Kerala'},
        {'value': '19', 'text': 'Ladakh'},
        {'value': '20', 'text': 'Lakshadweep'},
        {'value': '21', 'text': 'Madhya Pradesh'},
        {'value': '22', 'text': 'Maharashtra'},
        {'value': '23', 'text': 'Manipur'},
        {'value': '24', 'text': 'Meghalaya'},
        {'value': '25', 'text': 'Mizoram'},
        {'value': '26', 'text': 'Nagaland'},
        {'value': '27', 'text': 'Odisha'},
        {'value': '28', 'text': 'Puducherry'},
        {'value': '29', 'text': 'Punjab'},
        {'value': '30', 'text': 'Rajasthan'},
        {'value': '31', 'text': 'Sikkim'},
        {'value': '32', 'text': 'Tamil Nadu'},
        {'value': '33', 'text': 'Telangana'},
        {'value': '34', 'text': 'Tripura'},
        {'value': '35', 'text': 'Uttar Pradesh'},
        {'value': '36', 'text': 'Uttarakhand'},
        {'value': '37', 'text': 'West Bengal'}
    ]
    logger.info("Returning Indian states list (eCourts API structure has changed)")
    return jsonify({'success': True, 'states': fallback_states})

@app.route('/api/get-districts', methods=['POST'])
def get_districts():
    state_code = request.json.get('state_code')
    
    demo_districts = [
        {'value': '1', 'text': 'Central District'},
        {'value': '2', 'text': 'North District'},
        {'value': '3', 'text': 'South District'},
        {'value': '4', 'text': 'East District'},
        {'value': '5', 'text': 'West District'}
    ]
    
    logger.info(f"Returning demonstration districts for state {state_code}")
    return jsonify({'success': True, 'districts': demo_districts})

@app.route('/api/get-court-complexes', methods=['POST'])
def get_court_complexes():
    state_code = request.json.get('state_code')
    district_code = request.json.get('district_code')
    
    demo_complexes = [
        {'value': '1', 'text': 'District Court Complex'},
        {'value': '2', 'text': 'Family Court Complex'},
        {'value': '3', 'text': 'Civil Court Complex'}
    ]
    
    logger.info(f"Returning demonstration court complexes for district {district_code}")
    return jsonify({'success': True, 'complexes': demo_complexes})

@app.route('/api/get-courts', methods=['POST'])
def get_courts():
    state_code = request.json.get('state_code')
    district_code = request.json.get('district_code')
    complex_code = request.json.get('complex_code')
    
    demo_courts = [
        {'value': '1', 'text': 'Court of Hon\'ble Judge A.K. Sharma'},
        {'value': '2', 'text': 'Court of Hon\'ble Judge R.P. Verma'},
        {'value': '3', 'text': 'Court of Hon\'ble Judge S.K. Gupta'},
        {'value': '4', 'text': 'Court of Hon\'ble Judge M.L. Jain'},
        {'value': '5', 'text': 'Court of Hon\'ble Judge V.K. Singh'}
    ]
    
    logger.info(f"Returning demonstration courts for complex {complex_code}")
    return jsonify({'success': True, 'courts': demo_courts})

@app.route('/api/download-causelist', methods=['POST'])
def download_causelist():
    try:
        state_code = request.json.get('state_code')
        district_code = request.json.get('district_code')
        complex_code = request.json.get('complex_code')
        court_code = request.json.get('court_code')
        date = request.json.get('date')
        
        demo_cases = [
            {'sr_no': '1', 'case_no': 'CS/123/2024', 'party_name': 'Ram Kumar vs State', 'purpose': 'Arguments'},
            {'sr_no': '2', 'case_no': 'CR/456/2024', 'party_name': 'Rajesh Singh vs Mohan Lal', 'purpose': 'Evidence'},
            {'sr_no': '3', 'case_no': 'FIR/789/2024', 'party_name': 'State vs Suresh Kumar', 'purpose': 'Bail Hearing'},
            {'sr_no': '4', 'case_no': 'CS/234/2023', 'party_name': 'ABC Ltd vs XYZ Pvt Ltd', 'purpose': 'Final Arguments'},
            {'sr_no': '5', 'case_no': 'MA/567/2024', 'party_name': 'Priya Sharma vs Amit Sharma', 'purpose': 'Interim Relief'},
            {'sr_no': '6', 'case_no': 'CR/890/2024', 'party_name': 'Vijay Kumar vs State Bank', 'purpose': 'Appearance'},
            {'sr_no': '7', 'case_no': 'CS/345/2024', 'party_name': 'Sunita Devi vs Municipal Corporation', 'purpose': 'Hearing'},
            {'sr_no': '8', 'case_no': 'FIR/123/2024', 'party_name': 'State vs Rakesh Gupta', 'purpose': 'Framing of Charges'}
        ]
        
        causelist_data = {
            'date': date,
            'court_code': court_code,
            'court_name': f'Court {court_code}',
            'cases': demo_cases
        }
        
        pdf_filename = f'causelist_{court_code}_{date.replace("/", "-")}.pdf'
        json_filename = f'causelist_{court_code}_{date.replace("/", "-")}.json'
        
        json_filepath = os.path.join(PDF_FOLDER, json_filename)
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(causelist_data, f, indent=2, ensure_ascii=False)
        
        pdf_filepath = generate_pdf(causelist_data, pdf_filename)
        
        logger.info(f"Generated demonstration cause list PDF: {pdf_filename}")
        
        return jsonify({
            'success': True, 
            'message': f'Cause list generated successfully (demonstration data)',
            'filename': pdf_filename,
            'cases_found': len(causelist_data['cases'])
        })
    
    except Exception as e:
        logger.error(f"Error generating cause list: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to generate cause list. Please try again.'})

@app.route('/api/download-all-causelists', methods=['POST'])
def download_all_causelists():
    try:
        state_code = request.json.get('state_code')
        district_code = request.json.get('district_code')
        complex_code = request.json.get('complex_code')
        date = request.json.get('date')
        
        demo_courts = [
            {'value': '1', 'text': 'Court of Hon\'ble Judge A.K. Sharma'},
            {'value': '2', 'text': 'Court of Hon\'ble Judge R.P. Verma'},
            {'value': '3', 'text': 'Court of Hon\'ble Judge S.K. Gupta'},
            {'value': '4', 'text': 'Court of Hon\'ble Judge M.L. Jain'},
            {'value': '5', 'text': 'Court of Hon\'ble Judge V.K. Singh'}
        ]
        
        downloaded_files = []
        total_cases = 0
        
        for court in demo_courts:
            try:
                demo_cases = [
                    {'sr_no': '1', 'case_no': f'CS/{100+int(court["value"])}/2024', 'party_name': 'Ram Kumar vs State', 'purpose': 'Arguments'},
                    {'sr_no': '2', 'case_no': f'CR/{200+int(court["value"])}/2024', 'party_name': 'Rajesh Singh vs Mohan Lal', 'purpose': 'Evidence'},
                    {'sr_no': '3', 'case_no': f'FIR/{300+int(court["value"])}/2024', 'party_name': 'State vs Suresh Kumar', 'purpose': 'Bail Hearing'}
                ]
                
                causelist_data = {
                    'date': date,
                    'court_code': court['value'],
                    'court_name': court['text'],
                    'cases': demo_cases
                }
                
                pdf_filename = f'causelist_{court["value"]}_{date.replace("/", "-")}.pdf'
                json_filename = f'causelist_{court["value"]}_{date.replace("/", "-")}.json'
                
                json_filepath = os.path.join(PDF_FOLDER, json_filename)
                with open(json_filepath, 'w', encoding='utf-8') as f:
                    json.dump(causelist_data, f, indent=2, ensure_ascii=False)
                
                generate_pdf(causelist_data, pdf_filename)
                
                downloaded_files.append(pdf_filename)
                total_cases += len(causelist_data['cases'])
                
            except Exception as e:
                logger.error(f"Error processing court {court['text']}: {str(e)}")
                continue
        
        logger.info(f"Generated {len(downloaded_files)} demonstration cause list PDFs")
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(downloaded_files)} PDF cause lists (demonstration data)',
            'files': downloaded_files,
            'total_cases': total_cases
        })
    
    except Exception as e:
        logger.error(f"Error generating batch cause lists: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to generate cause lists. Please try again.'})

@app.route('/api/download-file/<filename>', methods=['GET'])
def download_file(filename):
    try:
        import os.path
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({'success': False, 'error': 'Invalid filename'}), 400
        
        if not (filename.endswith('.pdf') or filename.endswith('.json')):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        
        filepath = os.path.join(PDF_FOLDER, filename)
        real_path = os.path.realpath(filepath)
        real_folder = os.path.realpath(PDF_FOLDER)
        
        if not real_path.startswith(real_folder):
            return jsonify({'success': False, 'error': 'Access denied'}), 403
        
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=True, download_name=filename)
        else:
            return jsonify({'success': False, 'error': 'File not found'}), 404
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to download file'}), 500

@app.route('/api/lookup-case', methods=['POST'])
def lookup_case():
    try:
        cnr = request.json.get('cnr')
        case_type = request.json.get('case_type')
        case_number = request.json.get('case_number')
        case_year = request.json.get('case_year')
        state_code = request.json.get('state_code')
        district_code = request.json.get('district_code')
        
        driver = get_driver()
        driver.get('https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/')
        
        wait = WebDriverWait(driver, 20)
        
        if state_code and district_code:
            state_select = wait.until(EC.presence_of_element_located((By.ID, 'sateist')))
            Select(state_select).select_by_value(state_code)
            time.sleep(2)
            
            district_select = wait.until(EC.presence_of_element_located((By.ID, 'disrict')))
            Select(district_select).select_by_value(district_code)
            time.sleep(2)
        
        today = datetime.now().strftime('%d/%m/%Y')
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')
        
        results = {
            'today': None,
            'tomorrow': None
        }
        
        for check_date, date_label in [(today, 'today'), (tomorrow, 'tomorrow')]:
            try:
                date_input = driver.find_element(By.ID, 'pdate')
                driver.execute_script(f"arguments[0].value = '{check_date}'", date_input)
                
                submit_button = driver.find_element(By.NAME, 'submit')
                submit_button.click()
                time.sleep(5)
                
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, 'html.parser')
                
                case_found = False
                serial_number = None
                court_name = None
                
                table = soup.find('table')
                if table:
                    rows = table.find_all('tr')[1:]
                    for idx, row in enumerate(rows, 1):
                        cols = row.find_all('td')
                        if len(cols) >= 2:
                            case_no = cols[1].text.strip()
                            
                            if cnr and cnr in case_no:
                                case_found = True
                                serial_number = cols[0].text.strip()
                            elif case_type and case_number and case_year:
                                search_pattern = f"{case_type}/{case_number}/{case_year}"
                                if search_pattern in case_no:
                                    case_found = True
                                    serial_number = cols[0].text.strip()
                            
                            if case_found:
                                results[date_label] = {
                                    'found': True,
                                    'serial_number': serial_number,
                                    'case_number': case_no,
                                    'date': check_date
                                }
                                break
                
                if not case_found:
                    results[date_label] = {'found': False}
                
                driver.back()
                time.sleep(2)
                
            except Exception as e:
                print(f"Error checking {date_label}: {str(e)}")
                results[date_label] = {'found': False, 'error': str(e)}
        
        driver.quit()
        
        return jsonify({'success': True, 'results': results})
    
    except Exception as e:
        logger.error(f"Error looking up case: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'error': 'Failed to lookup case. Please try again.'})

if __name__ == '__main__':
    WSGIRequestHandler.protocol_version = "HTTP/1.1"  # Use HTTP/1.1
    app.run(host='0.0.0.0', port=5000, debug=False)
