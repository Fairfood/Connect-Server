import json

from django.core.exceptions import ValidationError


def validate_geojson_polygon(json_data):
	"""
	Validate GeoJSON Polygon.

	Example GeoJSON Polygon:
	{
		"type": "Feature",
		"properties": {},
		"geometry": {
			"type": "Polygon",
			"coordinates": [
			[
				[-122.801742, 45.48565],
				[-122.801742, 45.60491],
				[-122.584762, 45.60491],
				[-122.584762, 45.48565],
				[-122.801742, 45.48565]
			]
			]
		}
	}
	"""
	if not json_data:
		return json_data

	errors = []
	try:
		# Parse JSON data
		if isinstance(json_data, str):
			data = json.loads(json_data)
		else:
			data = json_data

		if not isinstance(data, dict):
			raise ValidationError("JSON data should be a dictionary")

		# Check if 'type' key exists and has the value 'Feature'
		if 'type' not in data or data['type'] != 'Feature':
			errors.append("Invalid type. It should be 'Feature'")

		# Check if 'geometry' key exists
		if 'geometry' not in data:
			errors.append("Missing 'geometry' key")

		# Check if 'type' within 'geometry' is 'Polygon'
		if ('type' not in data['geometry'] or
			data['geometry']['type'] != 'Polygon'):
			errors.append("Invalid type within 'geometry'. "
						  "It should be 'Polygon'")

		# Check if 'coordinates' key exists within 'geometry'
		if 'coordinates' not in data['geometry']:
			errors.append("Missing 'coordinates' key within 'geometry'")

		# Check if 'coordinates' is a list of lists
		if not isinstance(data['geometry']['coordinates'], list):
			errors.append("'coordinates' should be a list of lists")

		# Check if each coordinate is a list of length 2
		for ring in data['geometry']['coordinates']:
			if (not (isinstance(ring, list) and
					 all(isinstance(coord, list)
						 and len(coord) == 2 for coord in ring))):
				errors.append("Each coordinate should be a list of length 2")

	except json.JSONDecodeError:
		errors.append("Invalid JSON")

	if errors:
		return ValidationError(errors)

def validate_coordinates(json_data):
    """Validate coordinates."""

    if not json_data:
        return json_data

    if isinstance(json_data, str):
        json_data = json.loads(json_data)
    if not isinstance(json_data, dict):
        return json_data

    if 'geometry' not in json_data:
        return json_data
    if 'coordinates' not in json_data["geometry"]:
        return json_data

    value = json_data["geometry"]["coordinates"]

    errors = []
    for lon, lat in value[0]:
        set_error = False
        if not -90 <= lat <= 90:
            set_error = True
        if not -180 <= lon <= 180:
            set_error = True
        if set_error:
            errors.append(
                f"[{lon}, {lat}]: "
                f"Longitude must be between -180 and 180."
                f"Latitude must be between -90 and 90. "
            )
    if errors:
        raise ValidationError(errors)