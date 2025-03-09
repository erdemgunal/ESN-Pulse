import json
with open('/Users/erdemgunal/Desktop/sites/esn/esn.json') as f:
    file = json.load(f)

country_codes = [s for s in file]
print([s.lower().replace(' ', '-') for p in country_codes for s in file[p]])

# print([s.lower().replace(' ', '-') for s in file['gr']])