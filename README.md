# Court Scraper

A lightweight Flask-based demonstration application that generates and serves court cause lists (PDF and JSON) using sample/demonstration data. The project includes a small web UI, API endpoints for fetching sample states/districts/courts, utilities to generate cause list PDFs, and an optional Selenium-based case lookup that attempts to query an external eCourts site.

## Features

- Web UI served by Flask (HTML, CSS, JS under `templates/` and `static/`).
- API endpoints to retrieve sample states, districts, court complexes and courts.
- Generate a PDF cause list and corresponding JSON file saved under `downloaded_pdfs/`.
- Optional Selenium-based case lookup (requires Chrome/Chromedriver).

---

## Tech stack

- Python 3.11+ (development tested on 3.13)
- Flask — web framework used to serve the UI and APIs
- Selenium + webdriver-manager — optional headless browser automation for case lookup
- BeautifulSoup (bs4) — HTML parsing when scraping
- ReportLab — PDF generation library used to produce cause list PDFs
- PyPDF2 — PDF utilities (dependency)
- Requests — HTTP client for external requests
- Frontend: vanilla HTML/CSS/JavaScript served from Flask `templates/` and `static/`


## Repository structure

Top-level files and folders (important ones):

- `app.py` - The main Flask application. Contains routes, PDF generation logic and optional Selenium-based lookup.
- `README.md` - This file.
- `static/` - Static web assets (CSS and JavaScript). Required for the frontend.
	- `css/` - Stylesheets used by the UI. (Currently styles not seperated)
	- `js/app.js` - Frontend JavaScript for communicating with the API.
- `templates/` - HTML templates used by Flask (contains `index.html`).
- `downloaded_pdfs/` - Output folder where generated PDFs and JSONs are saved. The app will create this folder if missing.

---

## Code architecture and how it works

High-level components:

- Flask app (app.py)
	- Routes serve the UI and provide JSON APIs under `/api/*`.
	- `generate_pdf(causelist_data, filename)` - Uses ReportLab to build a PDF from a causelist data structure and save it to `downloaded_pdfs/`.
	- `get_driver()` - Returns a Selenium Chrome WebDriver configured with webdriver-manager. This is only used by the `/api/lookup-case` route.

- Frontend
	- `templates/index.html` renders the UI and loads `static/js/app.js` which calls the Flask API routes.

- Data flow
	1. Client requests states/districts/courts from Flask API (demo data returned).
	2. User selects court/date and requests ‘download causelist’. Flask creates a JSON and a PDF and returns metadata about the generated file.
	3. The client can download PDFs from `/api/download-file/<filename>`.

Security and safety notes:

- The app currently uses demonstration sample data for most endpoints. The Selenium lookup navigates to an external site and runs a headless browser. That requires a compatible Chrome/Chromedriver on the system and may create `.config` files and crash reports.
- The `downloaded_pdfs` folder is used to store output files and the `/api/download-file` route sanitizes path input to avoid directory traversal.

---

## Installation

Prerequisites:

- Python 3.13.
- pip (or use the Python that points to your desired environment).
- If you plan to use the Selenium lookup feature: a compatible Chrome/Chromium binary and matching driver will be installed automatically by `webdriver-manager`, but ensure Chrome/Chromium is installed on your machine.

Recommended steps (Windows PowerShell example):

```powershell
# 1. Create and activate a virtual environment (optional, recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt
# or install from pyproject.toml deps manually:
pip install beautifulsoup4 flask flask-cors pypdf2 reportlab requests selenium webdriver-manager

# 3. Run the app
python app.py
```

Note: This repository contains a `pyproject.toml` with a dependency list. If you prefer, you can create `requirements.txt` using:

```powershell
pip freeze > requirements.txt
```

If you run into permission or browser driver issues on Windows, the easy option is to keep `get_driver()` disabled or avoid the `/api/lookup-case` endpoint.

---

## Usage

1. Start the app (example):

```powershell
python app.py
```

2. Open your browser to: http://localhost:5000/

3. Use the UI to select demo state/district/court and a date, then click to generate a cause list. The server will save a PDF and a JSON file under `downloaded_pdfs/` and return the filename.

4. You can download generated files directly via the API:

- GET `/api/download-file/<filename>` — downloads a generated PDF or JSON (the route validates the filename to reduce risk).

5. Optional: `/api/lookup-case` uses Selenium to search the eCourts website for a case number; this is experimental and may fail if the eCourts site changed or if the local browser environment is incompatible.

---

## API summary

- GET `/api/get-states` — returns demo list of Indian states.
- POST `/api/get-districts` — accepts `{ state_code }` and returns demo districts.
- POST `/api/get-court-complexes` — accepts `{ state_code, district_code }` and returns demo complexes.
- POST `/api/get-courts` — accepts `{ state_code, district_code, complex_code }` and returns demo courts.
- POST `/api/download-causelist` — accepts `{ state_code, district_code, complex_code, court_code, date }`, generates JSON + PDF for a demo causelist and saves them to `downloaded_pdfs/`.
- POST `/api/download-all-causelists` — accepts similar payload and generates PDFs for several demo courts in batch.
- GET `/api/download-file/<filename>` — downloads saved PDF/JSON (filename must end with `.pdf` or `.json`).
- POST `/api/lookup-case` — experimental Selenium-based lookup. Payload includes `cnr`, `case_type`, `case_number`, `case_year`, `state_code`, `district_code`.

---

## Troubleshooting & Tips

- If you see errors related to Chrome/Chromedriver when calling `/api/lookup-case`, either ensure Chrome is installed and up-to-date, or avoid calling this endpoint.
- To clear generated outputs, delete files inside `downloaded_pdfs/`. The folder itself should be kept.
- If you want to run the app in production, use a WSGI server (Gunicorn, uWSGI, or IIS/other Windows-friendly servers) behind a proper reverse proxy. The app is currently configured to run with Flask's builtin server.

---

## Message from the author

Thank you for using this Court Scraper demo. This project was built to demonstrate how a small Flask app can mock court cause list generation and optionally use Selenium to look up cases.

If you find it useful, please modify and extend it to integrate real data sources carefully (respecting terms of service of any external website).

— Aviral

---

## Credits

Project maintained by: Aviral Yadav

Licensed: MIT
