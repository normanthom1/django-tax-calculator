# Django Tax Estimator Tool

## Overview
The **Django Tax Estimator Tool** is a web application that helps New Zealand freelancers and business owners estimate their tax obligations. With features for tracking earnings, expenses, GST, and asset depreciation, this tool provides a straightforward way to manage tax records and estimate tax owed.

> **Disclaimer**: This application is a tax estimation tool only. Results are intended as a guide and may not accurately reflect actual tax obligations. Please consult a qualified tax professional for precise tax advice.

## Features
- Calculates tax owed based on New Zealand tax brackets.
- Tracks GST for registered users.
- Calculates depreciation for assets over multiple years.
- Manages earnings and expenses with a user-friendly dashboard.

## Setup Instructions
Follow these steps to set up the Django Tax Estimator Tool on your local environment.

### Prerequisites
- **Python** 3.8+
- **Django** 4.0+
- **Git**

### Installation

1. **Clone the Repository**
   Clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/tax-estimator.git
   cd tax-estimator

2. **Set up virtual environment**
    ```python3 -m venv venv
    source venv/bin/activate  # For macOS/Linux
    venv\Scripts\activate     # For Windows

3. **Install Requirements**
    ```bash
    pip install -r requirements.txt

4. **Run Migrations**
    ```bash
    python manage.py migrate

5. **Create a superuser**
    ```bash
    python manage.py createsuperuser

6. **Run the Development Server**
    ```bash
    python manage.py runserver

