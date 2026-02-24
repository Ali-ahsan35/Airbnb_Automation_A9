# Airbnb End-to-End Automation

Automated end-to-end user journey testing for the Airbnb web platform
built with Django and Playwright.

## Project Structure
```
airbnb_automation/
├── config/                         # Django project settings
├── automation/                     # Django app (models, admin)
│   ├── models.py                   # Database models
│   ├── admin.py                    # Django admin configuration
│   └── management/
│       └── commands/
│           └── run_airbnb_journey.py  # Entry point command
├── journey/                       # Automation step files
│   ├── base_step.py               # Abstract base class for all steps
│   ├── browser.py                 # Browser manager (Playwright)
│   ├── step01_landing.py          # Step 1: Landing + Search + Dates + Guests
│   ├── step02_autosuggest.py      # Step 2: Auto suggestion verification
│   ├── step03_datepicker.py       # Step 3: Date picker verification
│   ├── step04_guestpicker.py      # Step 4: Guest picker verification
│   ├── step05_search_results.py   # Step 5: Search results scraping
│   └── step06_listing_detail.py   # Step 6: Listing detail page
├── utils/
│   └── db_logger.py               # Database logging utility
├── screenshots/                   # Auto-generated screenshots
├── .env                           # Environment variables (never commit)
├── .env.example                   # Example environment variables
├── .gitignore
└── requirements.txt
```

## Requirements

- Python 3.12+
- Django 5.x
- Playwright
- SQLite (default)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Ali-ahsan35/Airbnb_Automation_A9
cd Airbnb_Automation_A9
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Configure Environment Variables
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True
AIRBNB_URL=https://www.airbnb.com/
SCREENSHOTS_DIR=screenshots
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Create Admin User
```bash
python manage.py createsuperuser
```

### 7. Run the Automation
```bash
# Run with browser visible (default)
python manage.py run_airbnb_journey

# Run in headless mode (no browser UI)
python manage.py run_airbnb_journey --headless
```

## What the Automation Does

| Step | Description |
|------|-------------|
| Step 1 | Opens Airbnb, types a random country, selects suggestion, picks dates and guests, clicks search |
| Step 2 | Verifies auto-suggestions were relevant and saves them to DB |
| Step 3 | Verifies selected dates appear in the URL |
| Step 4 | Verifies guest count appears in the URL |
| Step 5 | Scrapes all listing titles, prices, and image URLs from results page |
| Step 6 | Opens a random listing, captures title, subtitle, and all gallery images |

## Database Models

| Model | Description |
|-------|-------------|
| JourneyRun | One record per full automation run |
| StepResult | One record per step with pass/fail status |
| AutoSuggestion | Captured search suggestions |
| ListingData | Scraped listings from search results |
| ListingDetail | Detail page data for selected listing |
| NetworkLog | Console and network logs per step |

## Viewing Results

Start the Django development server:
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` and log in with your superuser credentials.

## Screenshots

Screenshots are automatically saved to the `screenshots/` folder after each step:
```
screenshots/
├── step_01_website_landing_and_initial_search_setup.png
├── step_02_search_auto_suggestion_verification.png
├── step_03_date_picker_interaction.png
├── step_04_guest_picker_interaction.png
├── step_05_refine_search_and_item_list_verification.png
└── step_06_item_details_page_verification.png
```

## Generate Requirements File
```bash
pip freeze > requirements.txt
```