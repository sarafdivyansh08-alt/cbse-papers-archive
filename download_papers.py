"""Script to download CBSE papers from official sources and store locally"""
import os
import io
import zipfile
import requests
import time
import re
from database import get_db, init_db, seed_initial_data

# Configuration
PAPERS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'papers')
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': '*/*',
}

# CBSE Official ZIP URLs
CBSE_URLS = {
    2024: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2024/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2024/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2024/XII/Economics.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2024/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2024/XII/English_Core.zip',
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
    2019: {
        'accountancy': 'https://www.cbse.gov.in/cbsenew/question-paper/2019/XII/Accountancy.zip',
        'business_studies': 'https://www.cbse.gov.in/cbsenew/question-paper/2019/XII/Business_Studies.zip',
        'economics': 'https://www.cbse.gov.in/cbsenew/question-paper/2019/XII/Economics.zip',
        'mathematics': 'https://www.cbse.gov.in/cbsenew/question-paper/2019/XII/Math.zip',
        'english_core': 'https://www.cbse.gov.in/cbsenew/question-paper/2019/XII/English_Core.zip',
    },
}

# Subject display names
SUBJECT_DISPLAY = {
    'accountancy': 'Accountancy',
    'business_studies': 'Business Studies',
    'economics': 'Economics',
    'data_science': 'Data Science',
    'mathematics': 'Mathematics',
    'english_core': 'English Core'
}

def ensure_dirs():
    """Ensure required directories exist"""
    os.makedirs(PAPERS_DIR, exist_ok=True)
    for year in range(2015, 2025):
        year_dir = os.path.join(PAPERS_DIR, str(year))
        os.makedirs(year_dir, exist_ok=True)

def download_and_extract_zip(url, year, subject):
    """Download a ZIP file and extract PDFs"""
    print(f"Downloading {subject} {year} from {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=120, stream=True)
        if response.status_code != 200:
            print(f"  Failed to download: HTTP {response.status_code}")
            return []
        
        # Extract ZIP contents
        zip_content = io.BytesIO(response.content)
        extracted_files = []
        
        with zipfile.ZipFile(zip_content, 'r') as zf:
            for file_info in zf.filelist:
                if file_info.filename.lower().endswith('.pdf'):
                    # Extract PDF
                    pdf_content = zf.read(file_info.filename)
                    
                    # Generate clean filename
                    original_name = os.path.basename(file_info.filename)
                    clean_name = f"{subject}_{year}_{original_name}"
                    clean_name = re.sub(r'[^\w\-_\.]', '_', clean_name)
                    
                    # Save to papers directory
                    save_path = os.path.join(PAPERS_DIR, str(year), clean_name)
                    with open(save_path, 'wb') as f:
                        f.write(pdf_content)
                    
                    extracted_files.append({
                        'original_name': original_name,
                        'saved_path': save_path,
                        'size': len(pdf_content)
                    })
                    print(f"  Extracted: {clean_name} ({len(pdf_content)} bytes)")
        
        return extracted_files
        
    except Exception as e:
        print(f"  Error: {e}")
        return []

def update_database_with_local_files():
    """Update database entries with local file paths"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all papers
    cursor.execute('SELECT id, title, year_id FROM papers')
    papers = cursor.fetchall()
    
    # Get year mapping
    cursor.execute('SELECT id, year FROM years')
    years = {row['id']: row['year'] for row in cursor.fetchall()}
    
    updated_count = 0
    
    for paper in papers:
        year = years.get(paper['year_id'])
        if not year:
            continue
        
        year_dir = os.path.join(PAPERS_DIR, str(year))
        if not os.path.exists(year_dir):
            continue
        
        # Find matching PDF file
        title_lower = paper['title'].lower()
        for filename in os.listdir(year_dir):
            if filename.lower().endswith('.pdf'):
                file_path = os.path.join(year_dir, filename)
                
                # Update database with local path
                cursor.execute('''
                    UPDATE papers SET local_path = ? WHERE id = ?
                ''', (file_path, paper['id']))
                updated_count += 1
                break
    
    conn.commit()
    conn.close()
    print(f"Updated {updated_count} papers with local file paths")

def download_all_papers():
    """Download all available papers from CBSE"""
    ensure_dirs()
    
    total_files = 0
    
    for year, subjects in CBSE_URLS.items():
        print(f"\n=== Year {year} ===")
        for subject, url in subjects.items():
            files = download_and_extract_zip(url, year, subject)
            total_files += len(files)
            time.sleep(2)  # Be nice to the server
    
    print(f"\n=== Download Complete ===")
    print(f"Total files extracted: {total_files}")
    
    # Update database
    update_database_with_local_files()

if __name__ == '__main__':
    download_all_papers()
