import requests
from bs4 import BeautifulSoup
from requests.exceptions import Timeout, ConnectionError
from .exceptions import APIBrokenError
import re
import abc


class Site:
    __metaclass__ = abc.ABCMeta

    def __init__(self, url, search_url, name=None, headers=None):
        self.url = url
        self.name = name
        self.search_url = search_url
        self.result_pattern = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}

        if headers:
            self.headers.update(headers)

    def search(self, item, category):
        pass

    def extract(self, page):
        pass

    def concatKeyWord(self, word):
        if type(word) is str:
            return word
        return '+'.join(word.split())

    def getDOM(self, url):
        try:
            page = requests.get(url, headers=self.headers)
            page_object = BeautifulSoup(page.content, "lxml")
            return page_object

        except Timeout:
            raise TimeoutError()
        except ConnectionError:
            raise ConnectionRefusedError()


class Amazon(Site):

    def __init__(self):
        super().__init__('https://www.amazon.com/', 'https://www.amazon.com/s/', 'Amazon')
        self.result_pattern = re.compile(r'result_\d+')
        self.detail_pattern = re.compile(r'access-detail-page')
        self.ad = re.compile(r'\[\s*sponsored\s*\]', re.I)
    
    def search(self, item, category='aps'):

        try:
            page = requests.get(self.search_url, {'field-keywords': self.concatKeyWord(item),
                                                  'url': 'search-alias%3D{}'.format(category)}, headers=self.headers)
            page_object = BeautifulSoup(page.content, "lxml")

            return (page['href'] if 'amazon.com' in page['href'] else 'https://amazon.com' + page['href']
                    for page in page_object.find(id='pagn').find_all('a')), page_object

        except Timeout:
            raise TimeoutError()
        except ConnectionError:
            raise ConnectionRefusedError()
        except Exception:
            raise APIBrokenError()

    def extract(self, page):
        try:
            for item in page.find_all(id=self.result_pattern):
                try:
                    image = item.find('img')['src']
                    item_info = item.find('a', class_=self.detail_pattern)
                    link = item_info['href']
                    name = item_info.h2.get_text()

                    if not self.ad.match(name):
                        price_info = item.find(class_='sx-price')
                        price_curr = price_info.find(class_='sx-price-currency')
                        if price_curr:
                            price_curr = price_curr.get_text()

                        price = float(''.join(dig for dig in price_info.find(class_='sx-price-whole').get_text()
                                            if dig != ',') + '.' + price_info.find(class_='sx-price-fractional').get_text())

                        # need fixing
                        try:
                            rating = item.find(class_='a-icon-star').get_text()
                        except AttributeError:
                            rating = None

                        # (name, price currency, price, shipping cost, rating, image, details page link)
                        yield (name, price_curr, price, None, rating, image, link)
                except:
                    continue

        except Exception:
            raise APIBrokenError()


class Ebay(Site):
    def __init__(self):
        super().__init__('https://www.ebay.com/', 'https://www.ebay.com/sch/i.html', 'Ebay')
        self.result_pattern = re.compile(r'item\w+')
        self.price_parser = re.compile(r'([^\s])\s*([\d,]+(?:\.\d+)?)', re.M)

    def search(self, item, category=None):
        try:
            page = requests.get(self.search_url, {'_nkw': self.concatKeyWord(item)}, headers=self.headers)
            page_object = BeautifulSoup(page.content, "lxml")

            return (page['href'] for page in page_object.find(id='Pagination').find_all('a')
                    if 'javascript' not in page['href']), page_object

        except Timeout:
            raise TimeoutError()
        except ConnectionError:
            raise ConnectionRefusedError()
        except Exception:
            raise APIBrokenError()

    def extract(self, page):
        try:
            for item in page.find_all(id=self.result_pattern):
                image = item.find('img')['src']
                item_info = item.find(class_='lvtitle').find('a')
                link = item_info['href']
                name = item_info.get_text()

                price_info = item.find(class_='lvprices')
                price_cost = self.price_parser.match(price_info.find(class_='prc').get_text().strip())
                price_curr = price_cost.group(1)
                price = float(''.join(dig for dig in price_cost.group(2) if dig != ','))

                # needs fixing
                try:
                    shipping_match = self.price_parser.match(
                        price_info.find(class_='lvshipping').find(class_='fee').get_text().strip())
                    shipping = shipping_match.group(2)

                except Exception:
                    shipping = None

                # (name, price currency, price, shipping cost, rating, image, details page link)
                yield (name, price_curr, price, shipping, None, image, link)

        except Exception:
            raise APIBrokenError()
