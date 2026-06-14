import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from pprint import pprint

# Add src to path so we can import helpers
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'G:\\GB\\src'))

try:
    from helpers.config import get_settings
except ImportError:
    # fallback
    class Settings:
        MONGODB_URL = "mongodb://localhost:27017"
        MONGODB_DATABASE = "ai_career_coach"
    def get_settings():
        return Settings()

async def main():
    settings = get_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    
    collection = db['interviews'] # DataBaseEnum.COLLECTION_INTERVIEW_NAME.value
    
    print("Latest 3 interviews:")
    cursor = collection.find().sort("created_at", -1).limit(3)
    async for doc in cursor:
        print(f"\n--- Interview ID: {doc.get('interview_id')} ---")
        print(f"Status: {doc.get('status')}")
        print(f"Email Sent: {doc.get('email_sent')}")
        print(f"Email Sent At: {doc.get('email_sent_at')}")
        print(f"Candidate Email: {doc.get('candidate_email')}")
        print(f"From Email: {doc.get('from_email')}")
        print(f"Current Step: {doc.get('current_step')}")
        print(f"Last Error: {doc.get('last_error')}")
        
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
