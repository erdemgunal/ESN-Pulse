from src.scraping.statistics_scraper import StatisticsScraper
from src.scraping.organisations_scraper import OrganisationsScraper
from src.scraping.activities_scraper import ActivitiesScraper

organisation_id = 'esn-catania'

# scraper = OrganisationsScraper()
# organisation_data = scraper.scrape_organisation_details(organisation_id)
# print(organisation_data)

# scraper = StatisticsScraper()
# statistics_data = scraper.scrape_statistics(organisation_id)
# print(statistics_data)

scraper = ActivitiesScraper()
activities = scraper.get_all_organisation_activities(organisation_id)
print(activities)