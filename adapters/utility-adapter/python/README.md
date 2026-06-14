# EFN Utility Adapter - Python SDK

A FastAPI implementation of the EFN Utility Provider Adapter.

## Quickstart
1. Install dependencies: `pip install -r requirements.txt`
2. Set your secret: `export EFN_API_SECRET="your_secret"`
3. Run the server: `uvicorn main:app --port 8000`

## Customization
Open `main.py` and replace the `TODO` sections in `/validate` and `/dispense` with your actual database queries and token generation logic.
