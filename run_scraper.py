#!/usr/bin/env python3
import os
import sys
import argparse
from esn_scraper import ESNScraper

def main():
    parser = argparse.ArgumentParser(description="Scrape ESN countries and branches data from the ESN Accounts website")
    parser.add_argument("--output", default="esn_data.json",
                       help="Output JSON file path")
    parser.add_argument("--skip-details", action="store_true",
                       help="Skip scraping detailed branch information")
    parser.add_argument("--country-code", default=None,
                       help="Only scrape a specific country (e.g., 'de' for Germany)")
    parser.add_argument("--delay", type=float, default=1.0,
                       help="Delay between requests in seconds (default: 1.0)")
    
    args = parser.parse_args()
    
    print(f"Output will be saved to: {args.output}")
    print(f"Request delay: {args.delay} seconds")
    
    scraper = ESNScraper(delay=args.delay)
    
    if args.country_code:
        print(f"Scraping only country with code: {args.country_code}")
        countries = scraper.scrape_countries()
        country = next((c for c in countries if c['code'] == args.country_code), None)
        
        if not country:
            print(f"Country with code '{args.country_code}' not found")
            return
            
        print(f"Scraping branches for {country['name']}...")
        branches = scraper.scrape_branches_for_country(country)
        
        if not args.skip_details:
            for i, branch in enumerate(branches):
                print(f"  Scraping details for {branch['name']} ({i+1}/{len(branches)})...")
                scraper.scrape_branch_details(branch)
                
        data = {
            "metadata": {
                "country": country['name'],
                "total_branches": len(branches)
            },
            "country": country
        }
    else:
        print("Scraping all countries and branches...")
        data = scraper.scrape_all(with_branch_details=not args.skip_details)
    
    scraper.save_to_json(data, args.output)
    
    if args.country_code:
        print(f"Scraped {len(data['country']['branches'])} branches for {data['country']['name']}.")
    else:
        print(f"Scraped {len(data['countries'])} countries with {data['metadata']['total_branches']} branches.")

if __name__ == "__main__":
    main()