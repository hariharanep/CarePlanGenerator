# Care Plan Generator

A production-ready web application for automatically generating pharmaceutical care plans using AI (Claude). 

---

## Setup

```bash
# 1. Clone and setup
git clone <repository-url>
cd care-plan-generator
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export ANTHROPIC_API_KEY="your-api-key-here"
export DATABASE_URL="your-postgresql-db-url-here"
export FLASK_ENV=development
export PORT=8000

# 5. Run the application
python app.py

# 6. Open in browser
open http://localhost:8000
```

---

## 📦 Prerequisites

### Required

- **Python 3.8+** (Tested on Python 3.13)
- **Anthropic API Key** - For AI-powered care plan generation
- **PostgreSQL DB URL** - For persisting orders and generated careplans in a PostgreSQL DB

---

## ⚙️ Configuration

### Required Environment Variables

Create a `.env` file in the project root:

```bash
# Anthropic API key
ANTHROPIC_API_KEY=enter your API key here

# PostgreSQL DB URL
DATABASE_URL=enter your PostgreSQL DB URL here

# Flask environment (OPTIONAL)
FLASK_ENV=development

# Flask app port (OPTIONAL)
PORT=8000
```

**Or export directly:**

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
export DATABASE_URL="your-postgresql-db-url-here"
export FLASK_ENV=development
export PORT=8000
```

---

## 📖 Usage Guide

### Creating a Care Plan

1. **Open the application** at http://localhost:8000

2. **Fill in required fields:**
   - Patient Information: First Name, Last Name, MRN (6 digits)
   - Provider Information: Name, NPI (10 digits)
   - Clinical Information: Primary Diagnosis, Medication

3. **Optional fields:**
   - Additional Diagnoses
   - Medication History
   - Patient Clinical Records (vitals, labs, notes)

4. **Validate**: Click "Validate" to check for errors and warnings before submission

5. **Generate Care Plan**: Click "Generate Care Plan"
   - Care plan generates in 10-30 seconds
   - Order is submitted
   - Download the generated plan

### Exporting Data

Click "Export All Orders" to download a CSV file containing:
- Order ID and timestamp
- Patient information
- Provider information
- Diagnoses and medications
- Care plan text