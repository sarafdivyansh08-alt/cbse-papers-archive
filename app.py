"""Flask application for CBSE Papers Archive"""
import os
import io
import zipfile
import requests
import time
import re
import hashlib
from flask import Flask, render_template, jsonify, request, send_file, Response, stream_with_context
from flask_cors import CORS
from database import (
    init_db, seed_initial_data, get_all_subjects, get_all_years,
    get_all_regions, get_papers, get_paper_by_id, get_db, add_missing_years
)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['PAPERS_DIR'] = os.path.join(os.path.dirname(__file__), 'static', 'papers')
app.config['CACHE_DIR'] = os.path.join(os.path.dirname(__file__), 'cache')
app.config['ZIP_CACHE_DIR'] = os.path.join(os.path.dirname(__file__), 'zip_cache')

# Ensure directories exist
os.makedirs(app.config['PAPERS_DIR'], exist_ok=True)
os.makedirs(app.config['CACHE_DIR'], exist_ok=True)
os.makedirs(app.config['ZIP_CACHE_DIR'], exist_ok=True)

# Request headers to mimic browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
}

# CBSE Official ZIP URLs
CBSE_ZIP_URLS = {
    2024: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2024/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2024/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2024/XII/Economics.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2024/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2024/XII/English_Core.zip',
    },
        2025: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2025/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2025/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2025/XII/Economics.zip',
        'data_science': 'https://www.cbse.gov.in/cbsenew/question-paper/2025/XII/Data_Science.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2025/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2025/XII/English_Core.zip',
    },

    2023: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2023/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2023/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2023/XII/Economics.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2023/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2023/XII/English_Core.zip',
    },
    2022: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2022/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2022/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2022/XII/Economics.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2022/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2022/XII/English_Core.zip',
    },
    2021: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2021/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2021/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2021/XII/Economics.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2021/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2021/XII/English_Core.zip',
    },
    2020: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2020/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2020/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2020/XII/Economics.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2020/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2020/XII/English_Core.zip',
    },
    2018: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2018/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2018/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2018/XII/Economics.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2018/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2018/XII/English_Core.zip',
    },
    2017: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2017/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2017/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2017/XII/Economics.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2017/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2017/XII/English_Core.zip',
    },
    2016: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2016/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2016/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2016/XII/Economics.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2016/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2016/XII/English_Core.zip',
    },
    2015: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2015/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2015/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2015/XII/Economics.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2015/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2015/XII/English_Core.zip',
    },

    2019: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2019/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2019/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2019/XII/Economics.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2019/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2019/XII/English_Core.zip',
    },
}

# Subject name mapping
SUBJECT_KEY_MAP = {
    'Accountancy': 'accountancy',
    'Business Studies': 'business_studies',
    'Economics': 'economics',
    'Data Science': 'data_science',
    'Mathematics (Core)': 'mathematics',
    'English Core': 'english_core'
}

def get_cbse_zip_url(year, subject_name):
    """Get CBSE ZIP URL for a subject/year"""
    subject_key = SUBJECT_KEY_MAP.get(subject_name)
    if year in CBSE_ZIP_URLS and subject_key in CBSE_ZIP_URLS[year]:
        return CBSE_ZIP_URLS[year][subject_key]
    return None

def download_cbse_zip(url):
    """Download CBSE ZIP file and cache it"""
    # Create cache key from URL
    cache_key = hashlib.md5(url.encode()).hexdigest()
    cache_path = os.path.join(app.config['ZIP_CACHE_DIR'], f"{cache_key}.zip")
    
    # Check cache
    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            return f.read()
    
    # Download
    try:
        print(f"Downloading ZIP from {url}")
        response = requests.get(url, headers=HEADERS, timeout=120)
        if response.status_code == 200:
            # Cache the ZIP
            with open(cache_path, 'wb') as f:
                f.write(response.content)
            return response.content
    except Exception as e:
        print(f"Error downloading ZIP: {e}")
    
    return None

def extract_pdf_from_zip(zip_content, paper_title, set_code):
    """Extract a specific PDF from a ZIP file based on paper title and set"""
    try:
        zip_buffer = io.BytesIO(zip_content)
        with zipfile.ZipFile(zip_buffer, 'r') as zf:
            pdf_files = [f for f in zf.namelist() if f.lower().endswith('.pdf')]
            
            # Try to find matching PDF
            # Extract set number from set_code (e.g., "Set 1" -> "1")
            set_num = set_code.replace('Set ', '') if set_code else '1'
            
            for pdf_file in pdf_files:
                pdf_name_lower = pdf_file.lower()
                # Match by set number in filename
                if f'-{set_num}-' in pdf_name_lower or f'_{set_num}_' in pdf_name_lower or f'set{set_num}' in pdf_name_lower:
                    return zf.read(pdf_file), os.path.basename(pdf_file)
            
            # If no specific match, return first PDF
            if pdf_files:
                return zf.read(pdf_files[0]), os.path.basename(pdf_files[0])
                
    except Exception as e:
        print(f"Error extracting PDF: {e}")
    
    return None, None

def get_pdf_for_paper(paper):
    """Get PDF content for a paper"""
    paper_id = paper['id']
    cache_path = os.path.join(app.config['CACHE_DIR'], f"paper_{paper_id}.pdf")
    
    # Check cache first
    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            return f.read()
    
    # Check local file
    if paper.get('local_path') and os.path.exists(paper['local_path']):
        with open(paper['local_path'], 'rb') as f:
            return f.read()
    
    # Try to get from CBSE ZIP
    year = paper.get('year')
    subject_name = paper.get('subject_name')
    set_code = paper.get('set_code')
    
    zip_url = get_cbse_zip_url(year, subject_name)
    if zip_url:
        zip_content = download_cbse_zip(zip_url)
        if zip_content:
            pdf_content, pdf_name = extract_pdf_from_zip(zip_content, paper['title'], set_code)
            if pdf_content:
                # Cache the extracted PDF
                with open(cache_path, 'wb') as f:
                    f.write(pdf_content)
                return pdf_content
    
    return None

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/subjects')
def api_subjects():
    """Get all subjects"""
    subjects = get_all_subjects()
    return jsonify(subjects)

@app.route('/api/years')
def api_years():
    """Get all years"""
    years = get_all_years()
    return jsonify(years)

@app.route('/api/regions')
def api_regions():
    """Get all regions"""
    regions = get_all_regions()
    return jsonify(regions)

@app.route('/api/papers')
def api_papers():
    """Get papers with optional filters"""
    subject_id = request.args.get('subject_id', type=int)
    year_id = request.args.get('year_id', type=int)
    region_id = request.args.get('region_id', type=int)
    paper_type = request.args.get('paper_type')
    
    papers = get_papers(subject_id, year_id, region_id, paper_type)
    return jsonify(papers)

@app.route('/api/papers/<int:paper_id>')
def api_paper_detail(paper_id):
    """Get a single paper by ID"""
    paper = get_paper_by_id(paper_id)
    if paper:
        return jsonify(paper)
    return jsonify({'error': 'Paper not found'}), 404

@app.route('/api/download/<int:paper_id>')
def download_paper(paper_id):
    """Download a single paper PDF directly"""
    paper = get_paper_by_id(paper_id)
    if not paper:
        return jsonify({'error': 'Paper not found'}), 404
    
    # Generate filename
    safe_title = paper['title'].replace(' ', '_').replace('/', '-').replace('(', '').replace(')', '')
    filename = f"{safe_title}.pdf"
    
    # Try to get PDF content
    pdf_content = get_pdf_for_paper(paper)
    
    if pdf_content:
        return send_file(
            io.BytesIO(pdf_content),
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    
    # If direct download fails, return error with source URL
    zip_url = get_cbse_zip_url(paper.get('year'), paper.get('subject_name'))
    return jsonify({
        'error': 'Direct PDF download not available',
        'source_url': zip_url or paper.get('pdf_url'),
        'message': 'Please visit the source URL to download the paper'
    }), 404

def download_paper_task(paper_id):
    """Task to download a single paper - used for parallel downloads"""
    paper = get_paper_by_id(paper_id)
    if not paper:
        return None, None, None
    
    safe_title = paper['title'].replace(' ', '_').replace('/', '-').replace('(', '').replace(')', '')
    filename = f"{safe_title}.pdf"
    
    # Try to get PDF content
    pdf_content = get_pdf_for_paper(paper)
    
    if pdf_content:
        return filename, pdf_content, None
    else:
        zip_url = get_cbse_zip_url(paper.get('year'), paper.get('subject_name'))
        return filename, None, {
            'title': paper['title'],
            'url': zip_url or paper.get('pdf_url', 'N/A')
        }

@app.route('/api/download-multiple', methods=['POST'])
def download_multiple():
    """Download multiple papers as a ZIP file with actual PDFs using parallel downloads"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    data = request.get_json()
    paper_ids = data.get('paper_ids', [])
    
    if not paper_ids:
        return jsonify({'error': 'No papers selected'}), 400
    
    # Create a ZIP file in memory
    memory_file = io.BytesIO()
    downloaded_count = 0
    failed_papers = []
    results = {}
    
    # Use ThreadPoolExecutor for parallel downloads
    # Limit to 5 concurrent downloads to avoid overwhelming the server
    max_workers = min(5, len(paper_ids))
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_paper = {executor.submit(download_paper_task, pid): pid for pid in paper_ids}
        
        # Collect results as they complete
        for future in as_completed(future_to_paper):
            paper_id = future_to_paper[future]
            try:
                filename, pdf_content, error = future.result()
                if filename:
                    results[paper_id] = (filename, pdf_content, error)
            except Exception as e:
                print(f"Error downloading paper {paper_id}: {e}")
    
    # Create ZIP file with results
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        for paper_id in paper_ids:
            if paper_id in results:
                filename, pdf_content, error = results[paper_id]
                if pdf_content:
                    zf.writestr(filename, pdf_content)
                    downloaded_count += 1
                elif error:
                    failed_papers.append(error)
        
        # Add a readme if some downloads failed
        if failed_papers:
            readme_content = "Some papers could not be downloaded directly.\n"
            readme_content += "Please download them manually from the following URLs:\n\n"
            for fp in failed_papers:
                readme_content += f"- {fp['title']}\n  URL: {fp['url']}\n\n"
            zf.writestr("README_failed_downloads.txt", readme_content)
    
    memory_file.seek(0)
    
    if downloaded_count == 0 and failed_papers:
        return jsonify({
            'error': 'Could not download any papers directly',
            'failed_papers': failed_papers
        }), 500
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='cbse_papers.zip'
    )

@app.route('/api/stats')
def api_stats():
    """Get statistics about the papers"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Total papers
    cursor.execute('SELECT COUNT(*) as count FROM papers')
    total_papers = cursor.fetchone()['count']
    
    # Papers by subject
    cursor.execute('''
        SELECT s.display_name, COUNT(*) as count 
        FROM papers p 
        JOIN subjects s ON p.subject_id = s.id 
        GROUP BY s.id
    ''')
    by_subject = {row['display_name']: row['count'] for row in cursor.fetchall()}
    
    # Papers by year
    cursor.execute('''
        SELECT y.year, COUNT(*) as count 
        FROM papers p 
        JOIN years y ON p.year_id = y.id 
        GROUP BY y.id
        ORDER BY y.year DESC
    ''')
    by_year = {row['year']: row['count'] for row in cursor.fetchall()}
    
    conn.close()
    
    return jsonify({
        'total_papers': total_papers,
        'by_subject': by_subject,
        'by_year': by_year
    })

@app.route('/api/search')
def api_search():
    """Search papers by title"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, s.display_name as subject_name, y.year, r.display_name as region_name
        FROM papers p
        JOIN subjects s ON p.subject_id = s.id
        JOIN years y ON p.year_id = y.id
        JOIN regions r ON p.region_id = r.id
        WHERE p.title LIKE ?
        ORDER BY y.year DESC, s.display_name
        LIMIT 50
    ''', (f'%{query}%',))
    papers = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(p) for p in papers])

def initialize_app():
    """Initialize the application"""
    init_db()
    seed_initial_data()
        add_missing_years()

if __name__ == '__main__':
    initialize_app()
    app.run(host='0.0.0.0', port=12000, debug=False, threaded=True)
