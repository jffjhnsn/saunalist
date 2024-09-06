import requests
import time
import csv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_KEY = 'YOUR_API_KEY_HERE'
TEXTSEARCH_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'


def get_place_details(place_id):
    params = {
        'place_id': place_id,
        'fields': 'business_status,current_opening_hours,editorial_summary,international_phone_number,price_level,reservable,secondary_opening_hours,url,website',
        'key': API_KEY
    }
    response = requests.get(DETAILS_URL, params=params)
    result = response.json()

    if response.status_code != 200:
        logger.error(
            f"Place Details API request failed: {result.get('error_message', 'Unknown error')}")
        return {}

    return result.get('result', {})


def get_places(query, location):
    places = []
    next_page_token = None

    while True:
        params = {
            'query': f'{query} in {location}',
            'key': API_KEY
        }
        if next_page_token:
            params['pagetoken'] = next_page_token

        response = requests.get(TEXTSEARCH_URL, params=params)
        result = response.json()

        if response.status_code != 200:
            logger.error(
                f"Text Search API request failed: {result.get('error_message', 'Unknown error')}")
            break

        for place in result.get('results', []):
            place_id = place.get('place_id')
            details = get_place_details(place_id)

            places.append({
                'name': place.get('name'),
                'address': place.get('formatted_address'),
                'rating': place.get('rating', 'N/A'),
                'review_count': place.get('user_ratings_total', 'N/A'),
                'latitude': place['geometry']['location']['lat'],
                'longitude': place['geometry']['location']['lng'],
                'type': 'sauna' if 'sauna' in query.lower() else 'therme',
                'place_id': place_id,
                'business_status': details.get('business_status', 'N/A'),
                'current_opening_hours': details.get('current_opening_hours', {}).get(
                    'weekday_text', 'N/A'),
                'editorial_summary': details.get('editorial_summary', {}).get(
                    'overview', 'N/A'),
                'international_phone_number': details.get('international_phone_number',
                                                          'N/A'),
                'price_level': details.get('price_level', 'N/A'),
                'reservable': details.get('reservable', 'N/A'),
                'secondary_opening_hours': details.get('secondary_opening_hours',
                                                       'N/A'),
                'url': details.get('url', 'N/A'),
                'website': details.get('website', 'N/A')
            })
            logger.info(f"Found and detailed place: {place.get('name')}")

        next_page_token = result.get('next_page_token')
        if not next_page_token:
            break

        # Wait before making the next request (API requirement)
        time.sleep(2)

    return places


def save_to_csv(places, filename):
    fieldnames = ['name', 'address', 'rating', 'review_count', 'latitude', 'longitude',
                  'type',
                  'place_id', 'business_status', 'current_opening_hours',
                  'editorial_summary',
                  'international_phone_number', 'price_level', 'reservable',
                  'secondary_opening_hours', 'url', 'website']

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for place in places:
            writer.writerow(place)
    logger.info(f"Data saved to {filename}")


def main():
    queries = ['sauna', 'therme']
    location = 'Berlin, Germany'
    all_places = []

    for query in queries:
        logger.info(f"Starting API search for {query} in {location}")
        places = get_places(query, location)
        all_places.extend(places)
        time.sleep(2)  # Add a delay between queries

    save_to_csv(all_places, 'berlin_saunas_thermes_detailed.csv')
    logger.info("Data collection complete")


if __name__ == "__main__":
    main()