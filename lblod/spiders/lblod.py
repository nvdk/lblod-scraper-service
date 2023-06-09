from scrapy import Spider
from scrapy.loader import ItemLoader
from rdflib import Graph, Namespace
from helpers import logger

from lblod.items import Page
from lblod.job import create_scrape_job


BESLUIT = Namespace("http://data.vlaanderen.be/ns/besluit#")
LBBESLUIT = Namespace("http://lblod.data.gift/vocabularies/besluit/")

class LBLODSpider(Spider):
    name = "LBLODSpider"
    job = None 
    def parse(self, response):
        # store page itself
        job = create_scrape_job(response.url, self.job)
        page = ItemLoader(item=Page(), response=response)
        page.add_value("url", response.url)
        page.add_value("contents", response.text)
        page.add_value("job", job["uri"])
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
                url = response.urljoin(href)
                yield response.follow(url)
