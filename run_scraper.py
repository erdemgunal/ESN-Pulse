#!/usr/bin/env python3
"""
ESN PULSE - Main Scraper Orchestration Script

Bu script ESN PULSE projesinin ana orkestrasyon noktasıdır.
Scraper modüllerini koordine eder ve bağımlılıkları yönetir.

Usage:
    python run_scraper.py --module all
    python run_scraper.py --module accounts  
    python run_scraper.py --module activities
    python run_scraper.py --module activities --section esn-metu
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.cli.main import main

if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🚀 ESN PULSE - Starting...")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    try:
        # Run the main CLI
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
    finally:
        print("-" * 50)
        print(f"🏁 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("✅ ESN PULSE - Completed") 