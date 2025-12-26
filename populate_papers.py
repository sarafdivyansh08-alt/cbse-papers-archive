"""Script to populate the database with CBSE paper metadata"""
import os
from database import (
    get_db, init_db, seed_initial_data, add_paper,
    get_subject_by_name, get_year_by_value, get_region_by_name
)

# Define subjects and their URL patterns
SUBJECTS = {
    'accountancy': {
        'display': 'Accountancy',
        'supercop_name': 'Accountancy',
        'cbse_code': '055'
    },
    'business_studies': {
        'display': 'Business Studies',
        'supercop_name': 'Business-Studies',
        'cbse_code': '054'
    },
    'economics': {
        'display': 'Economics',
        'supercop_name': 'Economics',
        'cbse_code': '030'
    },
    'data_science': {
        'display': 'Data Science',
        'supercop_name': 'Data-Science',
        'cbse_code': '844'
    },
    'mathematics': {
        'display': 'Mathematics',
        'supercop_name': 'Maths',
        'cbse_code': '041'
    },
    'english_core': {
        'display': 'English Core',
        'supercop_name': 'English-Core',
        'cbse_code': '301'
    }
}

REGIONS = {
    'all_india': {'display': 'All India', 'supercop': 'All-India'},
    'delhi': {'display': 'Delhi', 'supercop': 'Delhi'},
    'foreign': {'display': 'Foreign', 'supercop': 'Foreign'},
    'outside_delhi': {'display': 'Outside Delhi', 'supercop': 'Outside-Delhi'}
}

YEARS = list(range(2015, 2025))

# CBSE paper code patterns by subject
PAPER_CODES = {
    'accountancy': '67',
    'business_studies': '66',
    'economics': '58',
    'data_science': '844',
    'mathematics': '65',
    'english_core': '301'
}

def get_supercop_url(subject_key, year, region_key, set_num):
    """Generate supercop URL for a paper"""
    subject_info = SUBJECTS[subject_key]
    return f"https://supercop.in/cbse-board-papers/class12/{subject_info['supercop_name']}-{year}"

def get_educart_url(subject_key, year):
    """Generate educart URL for a paper"""
    subject_names = {
        'accountancy': 'accountancy',
        'business_studies': 'business-studies',
        'economics': 'economics',
        'data_science': 'data-science',
        'mathematics': 'mathematics',
        'english_core': 'english-core'
    }
    return f"https://www.educart.co/previous-year-question-paper/cbse-class-12-{subject_names[subject_key]}-previous-year-question-paper-{year}"

def get_vedantu_url(subject_key, year):
    """Generate vedantu URL for a paper"""
    return f"https://www.vedantu.com/cbse/previous-year-question-paper-for-class-12-{subject_key.replace('_', '-')}"

def generate_paper_entries():
    """Generate paper entries for all subjects, years, and regions"""
    papers = []
    
    for subject_key, subject_info in SUBJECTS.items():
        for year in YEARS:
            # Data Science started in 2020
            if subject_key == 'data_science' and year < 2020:
                continue
                
            for region_key, region_info in REGIONS.items():
                # Generate set codes based on year
                if year >= 2020:
                    # Multiple sets for recent years
                    set_configs = [
                        ('Set 1', '1-1'),
                        ('Set 2', '1-2'),
                        ('Set 3', '1-3'),
                    ]
                elif year >= 2018:
                    set_configs = [
                        ('Set 1', '1'),
                        ('Set 2', '2'),
                        ('Set 3', '3'),
                    ]
                else:
                    # Single set for older years
                    set_configs = [('Set 1', '1')]
                
                for set_name, set_code in set_configs:
                    # Question Paper
                    title = f"{subject_info['display']} {year} - {region_info['display']} - {set_name}"
                    
                    # Primary URL from supercop
                    pdf_url = get_supercop_url(subject_key, year, region_key, set_code)
                    
                    papers.append({
                        'subject': subject_key,
                        'year': year,
                        'region': region_key,
                        'set_code': set_name,
                        'paper_type': 'question_paper',
                        'title': title,
                        'pdf_url': pdf_url
                    })
                    
                    # Marking Scheme / Solution
                    solution_title = f"{subject_info['display']} {year} - {region_info['display']} - {set_name} (Marking Scheme)"
                    papers.append({
                        'subject': subject_key,
                        'year': year,
                        'region': region_key,
                        'set_code': set_name,
                        'paper_type': 'marking_scheme',
                        'title': solution_title,
                        'pdf_url': pdf_url
                    })
    
    return papers

def populate_database():
    """Populate the database with paper entries"""
    # Initialize database
    init_db()
    seed_initial_data()
    
    papers = generate_paper_entries()
    added_count = 0
    
    for paper in papers:
        subject = get_subject_by_name(paper['subject'])
        year = get_year_by_value(paper['year'])
        region = get_region_by_name(paper['region'])
        
        if subject and year and region:
            add_paper(
                subject_id=subject['id'],
                year_id=year['id'],
                region_id=region['id'],
                set_code=paper['set_code'],
                paper_type=paper['paper_type'],
                title=paper['title'],
                pdf_url=paper['pdf_url']
            )
            added_count += 1
    
    print(f"Added {added_count} paper entries to the database")

if __name__ == '__main__':
    populate_database()
