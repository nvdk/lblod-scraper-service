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
        print(response.url)
        # store page itself
        job = create_scrape_job(response.url, self.job)
        page = ItemLoader(item=Page(), response=response)
        page.add_value("url", response.url)
        page.add_value("contents", response.text)
        page.add_value("job", job["uri"])
        yield page.load_item()

        # follow possible links
        g = Graph()
        g.bind("besluit", BESLUIT)
        g.bind("lblodBesluit", LBBESLUIT)
        g.parse(data=response,format='rdfa')
        for s, p, o in g.triples(None, BESLUIT.heeftAgenda, None ):
            yield response.follow(o)
        for s, p, o in g.triples(None, BESLUIT.heeftNotulen, None ):
            yield response.follow(o)
        for s, p, o in g.triples(None, BESLUIT.heeftBesluitenlijst, None ):
            yield response.follow(o)
        for s, p, o in g.triples(None, BESLUIT.heeftUittreksel, None ):
            yield response.follow(o)
        for s, p, o in g.triples(None, LBBESLUIT.linkToPublicationm, None):
            yield response.follow(o)
