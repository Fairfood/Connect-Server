import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
input_file = os.path.join(BASE_DIR, 'fixtures/entity_dump.json')
output_file = os.path.join(BASE_DIR, 'fixtures/entity_migration.json')

# Read JSON data from the file
with open(input_file, 'r') as file:
    data = json.load(file)

# Process the data
output_data = []
for item in data:
    if item['fields']['buyer'] is not None:  # Skip if buyer is null
        transformed_item = {
            "model": "supply_chains.entitybuyer",
            "pk": None,  # Set pk to None
            "fields": {
                "creator": item['fields']['creator'],
                "updater": item['fields']['updater'],
                "updated_on": item['fields']['updated_on'],
                "created_on": item['fields']['created_on'],
                "buyer": item['fields']['buyer'],
                "entity": item['pk'],  # Use the old pk value here
                "is_default": True
            }
        }
        output_data.append(transformed_item)

# Write the transformed data to a new JSON file
with open(output_file, 'w') as file:
    json.dump(output_data, file, indent=4)

print(f"Transformed data saved to {output_file}")
