# LBLOD Scraper service

Service to scrape LBLOD publication from a provided url. The URL can ei ther be an index (listing) page or an actual LBLOD publication.
The service will start downloading at the provided url and follow any links that have the following annotiations:
 - lblodBesluit:linkToPublication
 - besluit:heeftAgenda
 - besluit:heeftBesluitenlijst
 - besluit:heeftUittreksel
 - besluit:heeftNotulen
 
 For more information see https://lblod.github.io/pages-vendors/#/docs/publication-annotations
 

## Testing
the service exposes an endpoint `/scrape` that you can `POST` to. the provided URL (query param `url`) is used as the start_url to scrape from.

## Things worth mentioning
~uses pyrdfa3, which is no longer maintained. This means we're stuck on an old version of librdf (4.2.2) as well, since that's the last version pyrdfa3 works with.~
because of poor rdfa support in python, doesn't actually parse rdfa but some heuristics to find relevant links.
Testing with about 100 "gemeenten" indicates this works well enough for now

## setup 
TODO
 
 
