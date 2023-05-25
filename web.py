import os
from multiprocessing import Process

from flask import jsonify, request
from werkzeug.exceptions import NotFound

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from lblod.spiders.lblod import LBLODSpider

AUTO_RUN = os.getenv("AUTO_RUN") in ["yes", "on", "true", True, "1", 1]
DEFAULT_GRAPH = os.getenv("DEFAULT_GRAPH", "http://mu.semte.ch/graphs/scraper-graph")
MU_APPLICATION_FILE_STORAGE_PATH = os.getenv("MU_APPLICATION_FILE_STORAGE_PATH", "")


def run_spider(spider, **kwargs):
    def _run():
        crawler_process = CrawlerProcess(get_project_settings())
        crawler_process.crawl(spider, **kwargs)
        crawler_process.start()

    process = Process(target=_run)
    process.start()
    return process
@app.route("/scrape", methods=["POST"])
def scrape():
    if "url" in request.args:
        start_urls = [request.args["url"]]
        run_spider(LBLODSpider, start_urls=start_urls)
        return jsonify({"message": "Scraping started"})
    else:
        return jsonify({"error": "URL parameter is missing"})
