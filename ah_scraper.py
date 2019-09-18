import json
from jsonpath_rw import jsonpath, parse
import requests
from lxml import html
import ast
import os

from utils import get_valid_filename

base_url = 'https://www.ah.nl'

category_urls = [
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Faardappel-groente-fruit&_=1562023807988',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fverse-kant-en-klaar-maaltijden-salades&_=1562023811847',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fvlees-kip-vis-vega&_=1562023818546',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fkaas-vleeswaren-delicatessen&_=1562023822248',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fzuivel-eieren&_=1562023827469',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fbakkerij&_=1562023827914',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fontbijtgranen-broodbeleg-tussendoor&_=1562023832845',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Ffrisdrank-sappen-koffie-thee&_=1562023959434',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fwijn&_=1562023841107',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fbier-sterke-drank-aperitieven&_=1562023846624',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fpasta-rijst-internationale-keuken&_=1562023844176',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fsoepen-conserven-sauzen-smaakmakers&_=1562023857533',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fsnoep-koek-chips&_=1562023853531',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fdiepvries&_=1562023857283',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fdrogisterij-baby&_=1562023860598',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fbewuste-voeding&_=1562023866150',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fhuishouden-huisdier&_=1562023875297',
    'https://www.ah.nl/service/rest/delegate?url=%2Fproducten%2Fkoken-tafelen-non-food&_=1562023878391',
]


def scrape_products():
    for category_url in category_urls:
        print(category_url)
        r = requests.get(category_url)
        category_json = r.json()

        # json_data = None
        # with open('category.json', 'r') as f:
        #     json_data = json.load(f)

        jsonpath_expr = parse('$..navItem.link.href')

        products = [match.value for match in jsonpath_expr.find(category_json)]

        products = [x for x in products if x.startswith('/producten/product')]

        all_products = {}
        for product in products:
            r = requests.get(base_url + product)
            tree = html.fromstring(r.content)
            # json_ld = tree.xpath('string(/html/head/script[7])')

            javascript = tree.xpath('string(/html/body/script/text())')[54:-14]
            javascript = ast.literal_eval(javascript)
            javascript = json.loads(javascript)

            if javascript['product']['state'] == 'ERROR':
                print('ERROR state detected:')
                print(javascript)
                continue

            product_info = javascript['product']['card']
            title = product_info['products'][0]['title']

            try:
                os.makedirs('products/ah')
            except FileExistsError:
                pass

            with open('products/ah/{}.json'.format(get_valid_filename(title)), 'w') as f:
                json.dump(product_info, f)

            all_products[title] = product_info
            print(product_info['products'][0]['title'])

    print(products)

scrape_products()
