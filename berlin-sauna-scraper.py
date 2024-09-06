import requests
import time
import csv
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
BASE_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'


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

        response = requests.get(BASE_URL, params=params)
        result = response.json()

        if response.status_code != 200:
            logger.error(
                f"API request failed: {result.get('error_message', 'Unknown error')}")
            break

        for place in result.get('results', []):
            places.append({
                'name': place.get('name'),
                'address': place.get('formatted_address'),
                'rating': place.get('rating', 'N/A'),
                'review_count': place.get('user_ratings_total', 'N/A'),
                'latitude': place['geometry']['location']['lat'],
                'longitude': place['geometry']['location']['lng']
            })
            logger.info(f"Found place: {place.get('name')}")

        next_page_token = result.get('next_page_token')
        if not next_page_token:
            break

        # Wait before making the next request (API requirement)
        time.sleep(2)

    return places


def save_to_csv(places, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'address', 'rating', 'review_count', 'latitude',
                      'longitude']
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

    save_to_csv(all_places, 'berlin_saunas_thermes.csv')
    logger.info("Data collection complete")


if __name__ == "__main__":
    main()