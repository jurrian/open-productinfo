import requests
import os
import json
import time

from utils import get_valid_filename, requests_retry_session

api_base = 'https://mobileapi.jumbo.com/v5'
jumbo_products_path = 'products/jumbo'

session = requests_retry_session()


def fetch_product(product_id):
    url = '{}/products/{}'.format(api_base, product_id)

    r = session.get(url)
    r.raise_for_status()

    return r.json()['product']['data']


def fetch_products(size=100):
    offset = 0

    products = []
    while True:
        url = '{}/products?count={}&offset={}'.format(api_base, size, offset)
        try:
            r = session.get(url)
            r.raise_for_status()
        except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
            print(e)
            print('Skipping {}, waiting 60 before continuing'.format(url))
            time.sleep(60)
            continue

        response_json = r.json()

        for product in response_json['products']['data']:
            try:
                detail_product = fetch_product(product['id'])
            except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
                print(e)
                print('Skipping product {}'.format(product['id']))
                continue

            if detail_product:
                save_product(detail_product)
                products.append(detail_product)

        if offset >= response_json['products']['total']:
            break

        offset += size

    return products


def save_product(product):
    os.makedirs(jumbo_products_path, exist_ok=True)
    try:
        with open(
                os.path.join(
                    jumbo_products_path,
                    get_valid_filename(product['title']) + '.json')
                , 'w') as f:
            json.dump(product, f)
    except KeyError:
        print('Could not save product with id: {}'.format(product['id']))


if __name__ == "__main__":
    fetch_products()
