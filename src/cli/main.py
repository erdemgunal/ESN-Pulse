#!/usr/bin/env python3
"""
ESN PULSE CLI Module

Bu modül, ESN PULSE projesinin komut satırı arayüzünü sağlar.
Scraper modüllerini yönetir ve komut satırı argümanlarını işler.

Usage:
    python run_scraper.py --module accounts
    python run_scraper.py --module activities
    python run_scraper.py --module activities --section esn-yildiz
    python run_scraper.py --module all
"""

import argparse
import asyncio
import logging
from typing import Optional
from datetime import datetime

from src.scrapers.accounts_scraper import AccountsScraper
from src.scrapers.activities_statistics_scraper import ActivitiesAndStatisticsScraper

logger = logging.getLogger(__name__)

async def run_accounts_scraper():
    """AccountsScraper'ı çalıştırır."""
    logger.info("🔄 AccountsScraper başlatılıyor...")
    
    try:
        scraper = AccountsScraper()
        await scraper.scrape()
            
        logger.info("✅ AccountsScraper tamamlandı")
        
    except Exception as e:
        logger.error(f"❌ AccountsScraper hatası: {str(e)}")
        raise

async def run_activities_scraper(section_slug: Optional[str] = None):
    """ActivitiesAndStatisticsScraper'ı çalıştırır."""
    logger.info("🔄 ActivitiesAndStatisticsScraper başlatılıyor...")
    
    try:
        scraper = ActivitiesAndStatisticsScraper()
        await scraper.scrape(section_slug=section_slug)
            
        logger.info("✅ ActivitiesAndStatisticsScraper tamamlandı")
        
    except Exception as e:
        logger.error(f"❌ ActivitiesAndStatisticsScraper hatası: {str(e)}")
        raise

def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="ESN PULSE Scraper")
    parser.add_argument(
        "--module",
        type=str,
        choices=["accounts", "activities", "all"],
        required=True,
        help="Çalıştırılacak scraper modülü"
    )
    parser.add_argument(
        "--section",
        type=str,
        help="Belirli bir şube için scraping (sadece activities modülü için)"
    )
    
    args = parser.parse_args()
    
    print("🚀 ESN PULSE - Starting...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    try:
        if args.module == "accounts":
            asyncio.run(run_accounts_scraper())
            
        elif args.module == "activities":
            asyncio.run(run_activities_scraper(args.section))
            
        elif args.module == "all":
            asyncio.run(run_accounts_scraper())
            asyncio.run(run_activities_scraper())
            
    except Exception as e:
        logger.error(f"❌ Hata: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        
    print("-" * 50)
    print(f"🏁 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("✅ ESN PULSE - Completed")

if __name__ == "__main__":
    main() 