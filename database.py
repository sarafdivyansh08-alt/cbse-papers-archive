"""Database setup and models for CBSE Papers Archive"""
import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'cbse_papers.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with schema"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create subjects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            code TEXT,
            display_name TEXT NOT NULL
        )
    ''')
    
    # Create years table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS years (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year INTEGER NOT NULL UNIQUE
        )
    ''')
    
    # Create regions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL
        )
    ''')
    
    # Create papers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            year_id INTEGER NOT NULL,
            region_id INTEGER NOT NULL,
            set_code TEXT,
            paper_type TEXT DEFAULT 'question_paper',
            title TEXT NOT NULL,
            pdf_url TEXT,
            local_path TEXT,
            file_size INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (subject_id) REFERENCES subjects(id),
            FOREIGN KEY (year_id) REFERENCES years(id),
            FOREIGN KEY (region_id) REFERENCES regions(id)
        )
    ''')
    
    # Create indexes for faster queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_subject ON papers(subject_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_papers_region ON papers(region_id)')
    
    conn.commit()
    conn.close()

def seed_initial_data():
    """Seed initial data for subjects, years, and regions"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Subjects
    subjects = [
        ('accountancy', '055', 'Accountancy'),
        ('business_studies', '054', 'Business Studies'),
        ('economics', '030', 'Economics'),
        ('data_science', '844', 'Data Science'),
        ('mathematics', '041', 'Mathematics (Core)'),
        ('english_core', '301', 'English Core'),
    ]
    
    for name, code, display_name in subjects:
        cursor.execute('''
            INSERT OR IGNORE INTO subjects (name, code, display_name) 
            VALUES (?, ?, ?)
        ''', (name, code, display_name))
    
    # Years (2015-2024, 10 years)
    for year in range(2015, 2026):
        cursor.execute('INSERT OR IGNORE INTO years (year) VALUES (?)', (year,))
    
    # Regions
    regions = [
        ('all_india', 'All India'),
        ('delhi', 'Delhi'),
        ('foreign', 'Foreign'),
        ('outside_delhi', 'Outside Delhi'),
    ]
    
    for name, display_name in regions:
        cursor.execute('''
            INSERT OR IGNORE INTO regions (name, display_name) 
            VALUES (?, ?)
        ''', (name, display_name))
    
    conn.commit()
    conn.close()

def get_all_subjects():
    """Get all subjects"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects ORDER BY display_name')
    subjects = cursor.fetchall()
    conn.close()
    return [dict(s) for s in subjects]

def get_all_years():
    """Get all years"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM years ORDER BY year DESC')
    years = cursor.fetchall()
    conn.close()
    return [dict(y) for y in years]

def get_all_regions():
    """Get all regions"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM regions ORDER BY display_name')
    regions = cursor.fetchall()
    conn.close()
    return [dict(r) for r in regions]

def get_papers(subject_id=None, year_id=None, region_id=None, paper_type=None):
    """Get papers with optional filters"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = '''
        SELECT p.*, s.display_name as subject_name, y.year, r.display_name as region_name
        FROM papers p
        JOIN subjects s ON p.subject_id = s.id
        JOIN years y ON p.year_id = y.id
        JOIN regions r ON p.region_id = r.id
        WHERE 1=1
    '''
    params = []
    
    if subject_id:
        query += ' AND p.subject_id = ?'
        params.append(subject_id)
    if year_id:
        query += ' AND p.year_id = ?'
        params.append(year_id)
    if region_id:
        query += ' AND p.region_id = ?'
        params.append(region_id)
    if paper_type:
        query += ' AND p.paper_type = ?'
        params.append(paper_type)
    
    query += ' ORDER BY y.year DESC, s.display_name, r.display_name'
    
    cursor.execute(query, params)
    papers = cursor.fetchall()
    conn.close()
    return [dict(p) for p in papers]

def get_paper_by_id(paper_id):
    """Get a single paper by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, s.display_name as subject_name, y.year, r.display_name as region_name
        FROM papers p
        JOIN subjects s ON p.subject_id = s.id
        JOIN years y ON p.year_id = y.id
        JOIN regions r ON p.region_id = r.id
        WHERE p.id = ?
    ''', (paper_id,))
    paper = cursor.fetchone()
    conn.close()
    return dict(paper) if paper else None

def add_paper(subject_id, year_id, region_id, set_code, paper_type, title, pdf_url=None, local_path=None):
    """Add a new paper to the database"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO papers (subject_id, year_id, region_id, set_code, paper_type, title, pdf_url, local_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (subject_id, year_id, region_id, set_code, paper_type, title, pdf_url, local_path))
    paper_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return paper_id

def get_subject_by_name(name):
    """Get subject by name"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM subjects WHERE name = ?', (name,))
    subject = cursor.fetchone()
    conn.close()
    return dict(subject) if subject else None

def get_year_by_value(year):
    """Get year by value"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM years WHERE year = ?', (year,))
    year_row = cursor.fetchone()
    conn.close()
    return dict(year_row) if year_row else None

def get_region_by_name(name):
    """Get region by name"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM regions WHERE name = ?', (name,))
    region = cursor.fetchone()
    conn.close()
    return dict(region) if region else None

def add_missing_years():
 """Add any missing years to the database"""
 conn = get_db()
 cursor = conn.cursor()
 
 # Check which years exist
 cursor.execute('SELECT year FROM years ORDER BY year')
 existing_years = set(row['year'] for row in cursor.fetchall())
 
 # Add missing years
 for year in range(2015, 2026):  # 2015-2025
 if year not in existing_years:
 cursor.execute('INSERT INTO years (year) VALUES (?)', (year,))
 
 conn.commit()
 conn.close()

if __name__ == '__main__':
    init_db()
    seed_initial_data()
        add_missing_years()
    print("Database initialized and seeded successfully!")
