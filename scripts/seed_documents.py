"""
Seed Documents Script

Uploads sample test documents to the RAG Document Assistant API.
Make sure the server is running on http://localhost:8000 before running this script.

Usage:
    python scripts/seed_documents.py
"""

import os
import requests

API_URL = "http://localhost:8000/api/documents/upload"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_FILE = os.path.join(SCRIPT_DIR, "company_policy.txt")

def seed():
    print(f"📄 Uploading seed document: {SAMPLE_FILE} to {API_URL}...")
    
    if not os.path.exists(SAMPLE_FILE):
        print(f"❌ Error: Sample file {SAMPLE_FILE} not found!")
        return

    with open(SAMPLE_FILE, "rb") as f:
        files = {"file": ("company_policy.txt", f, "text/plain")}
        try:
            response = requests.post(API_URL, files=files)
            if response.status_code == 200:
                print("✅ Successfully seeded document!")
                print("Response:", response.json())
            else:
                print(f"❌ Failed to seed document. Status Code: {response.status_code}")
                print("Detail:", response.text)
        except requests.exceptions.ConnectionError:
            print("❌ Error: Could not connect to FastAPI server. Make sure 'uvicorn app.main:app --reload' is running on http://localhost:8000!")

if __name__ == "__main__":
    seed()
