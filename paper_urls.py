"""
Direct PDF URLs for CBSE Class 12 Papers
URLs sourced from CBSE official website and verified mirrors
"""

# CBSE Official ZIP URLs (contain all sets for each subject/year)
CBSE_OFFICIAL_ZIPS = {
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
}

# Direct PDF URLs from various verified sources
# Format: {year: {subject: {region: {set: {type: url}}}}}
DIRECT_PDF_URLS = {}

# Supercop.in base URLs for individual papers
SUPERCOP_BASE = "https://supercop.in/cbse-board-papers/class12"

# Subject codes used by CBSE
SUBJECT_CODES = {
    'accountancy': '055',
    'business_studies': '054', 
    'economics': '030',
    'data_science': '844',
    'mathematics': '041',
    'english_core': '301'
}

# Paper code patterns by subject
# CBSE uses codes like 67-1-1, 67-1-2, etc. for Accountancy
PAPER_CODES = {
    'accountancy': {
        2024: ['67-1-1', '67-1-2', '67-1-3', '67-2-1', '67-2-2', '67-2-3', '67-3-1', '67-3-2', '67-3-3',
               '67-4-1', '67-4-2', '67-4-3', '67-5-1', '67-5-2', '67-5-3'],
        2023: ['67-1-1', '67-1-2', '67-1-3', '67-2-1', '67-2-2', '67-2-3', '67-3-1', '67-3-2', '67-3-3'],
    },
    'business_studies': {
        2024: ['66-1-1', '66-1-2', '66-1-3', '66-2-1', '66-2-2', '66-2-3', '66-3-1', '66-3-2', '66-3-3'],
        2023: ['66-1-1', '66-1-2', '66-1-3', '66-2-1', '66-2-2', '66-2-3', '66-3-1', '66-3-2', '66-3-3'],
    },
    'economics': {
        2024: ['58-1-1', '58-1-2', '58-1-3', '58-2-1', '58-2-2', '58-2-3', '58-3-1', '58-3-2', '58-3-3'],
        2023: ['58-1-1', '58-1-2', '58-1-3', '58-2-1', '58-2-2', '58-2-3', '58-3-1', '58-3-2', '58-3-3'],
    },
    'mathematics': {
        2024: ['65-1-1', '65-1-2', '65-1-3', '65-2-1', '65-2-2', '65-2-3', '65-3-1', '65-3-2', '65-3-3'],
        2023: ['65-1-1', '65-1-2', '65-1-3', '65-2-1', '65-2-2', '65-2-3', '65-3-1', '65-3-2', '65-3-3'],
    },
    'english_core': {
        2024: ['1-1-1', '1-1-2', '1-1-3', '1-2-1', '1-2-2', '1-2-3', '1-3-1', '1-3-2', '1-3-3'],
        2023: ['1-1-1', '1-1-2', '1-1-3', '1-2-1', '1-2-2', '1-2-3', '1-3-1', '1-3-2', '1-3-3'],
    },
}

def get_cbse_zip_url(year, subject):
    """Get CBSE official ZIP URL for a subject/year"""
    if year in CBSE_OFFICIAL_ZIPS and subject in CBSE_OFFICIAL_ZIPS[year]:
        return CBSE_OFFICIAL_ZIPS[year][subject]
    return None

def get_supercop_page_url(subject, year):
    """Get Supercop page URL for a subject/year"""
    subject_names = {
        'accountancy': 'Accountancy',
        'business_studies': 'Business-Studies',
        'economics': 'Economics',
        'data_science': 'Data-Science',
        'mathematics': 'Mathematics',
        'english_core': 'English-Core'
    }
    if subject in subject_names:
        return f"{SUPERCOP_BASE}/{subject_names[subject]}-{year}/"
    return None
