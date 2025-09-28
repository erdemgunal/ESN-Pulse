"""
CSS selectors for accounts.esn.org platform.
"""

ACCOUNT_SELECTORS = {
    'country_links': 'a[href*="/country/"]',
    'section_items': 'span.field-content',
    'section_links': '.views-view-grid a[href*="/section/"]',
    'contact_email': '.field--name-field-email .field--item',
    'contact_website': 'a[title="Website of the organisation"]',
    'university_name': '.field--name-field-university-name .field--item',
    'address': '.field--name-field-address .field--item .address',
    'coordinates': '.geolocation-location[data-lat]',
    'logo': '.center-block.img-responsive[alt*="Logo"]',
    'social_media': 'a[title*="profile"]',
    'city': '.field--name-field-city .field--item'
}