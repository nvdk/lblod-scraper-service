from scrapy import Spider
from scrapy.loader import ItemLoader
from scrapy.http.response.text import TextResponse
from scrapy.exceptions import IgnoreRequest
from rdflib import Graph, Namespace
from helpers import logger

from lblod.items import Page
from lblod.harvester import ensure_remote_data_object

BESLUIT = Namespace("http://data.vlaanderen.be/ns/besluit#")
LBBESLUIT = Namespace("http://lblod.data.gift/vocabularies/besluit/")

class LBLODSpider(Spider):
    name = "LBLODSpider"
    def parse(self, response):
        if not isinstance(response, TextResponse):
            raise IgnoreRequest("ignoring non text response")
        # store page itself
        rdo = ensure_remote_data_object(self.collection, response.url)
        page = ItemLoader(item=Page(), response=response)
        page.add_value("url", response.url)
        page.add_value("contents", response.text)
        page.add_value("rdo", rdo)
        yield page.load_item()
        interesting_properties = [
            'heeftNotulen',
            'heeftAgenda',
            'heeftBesluitenlijst',
            'heeftUittreksel',
            'linkToPublication'
        ]
        for element in response.xpath('//a[@href and @property]'):
            href = element.xpath('@href').get()
            property_value = element.xpath('@property').get()
            if any(value in property_value for value in interesting_properties):
                if not href.endswith('.pdf'):
                    url = response.urljoin(href)
                    ensure_remote_data_object(self.collection, url)
                    yield response.follow(url)
                else:
                    logger.info(f'ignoring pdf link {href}')
