import os
RESOURCE_BASE = "http://data.lblod.info/id/"
SCRAPE_JOB_TYPE = "http://lblod.data.gift/ns/ScrapeJob"
SCRAPE_CAMPAIGN_JOB_TYPE = "http://lblod.data.gift/ns/ScrapeCampaignJob"
SCRAPE_GRAPH = "http://mu.semte.ch/graphs/jobs-graph"
DEFAULT_GRAPH = os.environ['DEFAULT_GRAPH'] or 'http://mu.semte.ch/graphs/public'
STATUSES =  {
    'READY': 'http://lblod.data.gift/file-download-statuses/ready-to-be-cached',
    'ONGOING': 'http://lblod.data.gift/file-download-statuses/ongoing',
    'SUCCESS': 'http://lblod.data.gift/file-download-statuses/success',
    'FAILURE': 'http://lblod.data.gift/file-download-statuses/failure'
}

OPERATIONS = {
    'COLLECTING': 'http://lblod.data.gift/id/jobs/concept/TaskOperation/collecting'
}
