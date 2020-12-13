#!/usr/bin/env python3

import requests
from lxml import etree

import re
import csv

product_count = 943
products_per_page = 12

unicode_parser = etree.HTMLParser(encoding="utf-8")

results = [['nazev', 'cena bez dph', 'vaha v kg']]

def scrape_product_list(page):
    page = requests.get('https://www.mp-eshop.cz/hutni-material?page={}'.format(page))
    tree = etree.HTML(page.content, parser=unicode_parser)

    # select HTML elements which have URL of products
    product_urls = tree.xpath('//div[@class="productList__inner"]/a/@href')


    for product_url in product_urls:
        result = scrape_product(product_url)
        results.append(result)

def scrape_product(url):
    page = requests.get(url)
    tree = etree.HTML(page.content, parser=unicode_parser)

    # product title
    title = tree.xpath('//h1[@class="product__title"]/text()')[0]

    # price excl. vat
    price_messy = tree.xpath('//div[@class="price price--excVat"]/text()')[0]

    # features
    table_features = tree.xpath('//table[@class="table table--features m-b-0"]/tr/td/text()')
    
    weight_messy = ""

    for i in range(0, len(table_features), 2):
        feat_name = table_features[i].strip()

        if feat_name == u"Váha":
            weight_messy = table_features[i+1]

    price = re.sub("[^0-9\,]", "", price_messy)
    weight = re.sub("[^0-9\.]", "", weight_messy)

    return [title, price, weight]

last_page = product_count // products_per_page + 1
for page in range(1, last_page + 1):
    scrape_product_list(page)

print(results)

with open('result.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter='|',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in results:
         spamwriter.writerow(row)