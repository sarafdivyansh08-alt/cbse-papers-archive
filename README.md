# CBSE Class 12 Papers Archive

A comprehensive web application for accessing CBSE Class 12 previous year question papers from 2015-2024 across all sets and regions.

## Features

- **1080+ Papers**: Access question papers and marking schemes for 6 subjects
- **Smart Filters**: Filter by subject, year, region, and paper type
- **Multi-Select Download**: Select multiple papers and download as ZIP
- **Modern UI**: Responsive design with grid/list view options
- **Search**: Quick search across all papers

## Subjects Covered

1. **Accountancy** (Code: 055)
2. **Business Studies** (Code: 054)
3. **Economics** (Code: 030)
4. **Data Science** (Code: 844) - Available from 2020
5. **Mathematics (Core)** (Code: 041)
6. **English Core** (Code: 301)

## Regions

- All India
- Delhi
- Foreign
- Outside Delhi

## Years

2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone or download the repository:
```bash
cd cbse-papers-website
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database and populate with paper data:
```bash
python populate_papers.py
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:12000`

## Production Deployment

### Using Gunicorn (Recommended)

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python populate_papers.py

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Build and run:
```bash
docker build -t cbse-papers-archive .
docker run -p 8000:8000 cbse-papers-archive
```

## Project Structure

```
cbse-papers-website/
├── app.py                 # Flask application
├── database.py            # Database models and functions
├── populate_papers.py     # Script to populate database
├── requirements.txt       # Python dependencies
├── cbse_papers.db        # SQLite database (generated)
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   ├── js/
│   │   └── app.js        # Frontend JavaScript
│   └── papers/           # Local PDF storage (optional)
└── templates/
    └── index.html        # Main HTML template
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main page |
| `/api/subjects` | GET | List all subjects |
| `/api/years` | GET | List all years |
| `/api/regions` | GET | List all regions |
| `/api/papers` | GET | List papers with filters |
| `/api/papers/<id>` | GET | Get single paper details |
| `/api/download/<id>` | GET | Download single paper |
| `/api/download-multiple` | POST | Download multiple papers as ZIP |
| `/api/stats` | GET | Get statistics |
| `/api/search` | GET | Search papers |

### Query Parameters for `/api/papers`

- `subject_id`: Filter by subject ID
- `year_id`: Filter by year ID
- `region_id`: Filter by region ID
- `paper_type`: Filter by type (`question_paper` or `marking_scheme`)

## Paper Sources

Papers are linked from:
- [CBSE Official Website](https://cbse.gov.in)
- [Supercop](https://supercop.in)

## License

This project is for educational purposes only. All question papers are property of CBSE.

## Contributing

Feel free to submit issues and pull requests for improvements.
