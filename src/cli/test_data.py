"""
Test verilerini veritabanına eklemek için script.
"""

import asyncio
import json
import logging
from typing import Dict, Any

from src.database.operations import DatabaseOperations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def insert_test_data():
    """Test verilerini veritabanına ekler."""
    
    # ESN Lille test verisi
    section_data = {
        'country_code': 'FR',
        'name': 'ESN Lille',
        'accounts_platform_slug': 'fr-lill-esl',
        'activities_platform_slug': 'esn-lille',
        'accounts_url': 'https://accounts.esn.org/section/fr-lill-esl',
        'activities_url': 'https://activities.esn.org/organisation/esn-lille',
        'city': 'Lille',
        'address': "Maison Des Etudiants Université de Lille 1 Cité Scientifique, 59650, Villeneuve d'Ascq, France",
        'email': 'president@esnlille.fr',
        'website': 'http://www.esnlille.fr/satellite',
        'university_name': 'Université de Lille',
        'longitude': 3.140041,
        'latitude': 50.609753,
        'social_media': json.dumps({
            'facebook': 'https://www.facebook.com/ESNLillePage/',
            'instagram': 'https://www.instagram.com/esn_lille/'
        }),
        'logo_url': 'https://accounts.esn.org/sites/default/files/styles/medium/module/esn_accounts_groups/images/logos/FR/FR-LILL-ESL.png?itok=SYO5ksRO',
        'can_scrape_activities': True,
        'last_validated_activities_slug': None
    }
    
    try:
        async with DatabaseOperations() as db:
            # Şube verisini ekle
            result = await db.insert_section(section_data)
            logger.info(f"Şube eklendi: {result}")
            
    except Exception as e:
        logger.error(f"Hata oluştu: {str(e)}")

if __name__ == "__main__":
    asyncio.run(insert_test_data())