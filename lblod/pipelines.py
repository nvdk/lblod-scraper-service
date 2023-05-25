import datetime
import os
import uuid
from string import Template

from itemadapter import ItemAdapter
from constants import EXTRACTION_GRAPH

from escape_helpers import sparql_escape_uri
from sudo_query import update_sudo
from helpers import logger

from .job import STATUS_STARTED, STATUS_FAILED, STATUS_SUCCESS
from .job import create_job, update_job_status, attach_job_results
from .file import construct_insert_file_query, STORAGE_PATH
from constants import EXTRACTION_GRAPH, SCRAPE_CAMPAIGN_JOB_TYPE, SCRAPE_JOB_TYPE, RESOURCE_BASE

DEFAULT_GRAPH = os.getenv("DEFAULT_GRAPH", "http://mu.semte.ch/graphs/scraper-graph")

class Pipeline:
    timestamp = datetime.datetime.now()

    def __init__(self):
        self.storage_path = os.path.join(STORAGE_PATH, self.timestamp.isoformat())
        if not os.path.exists(self.storage_path):
            os.mkdir(self.storage_path)

    def open_spider(self, spider):
        (query, job) = create_job(
            SCRAPE_CAMPAIGN_JOB_TYPE,
            RESOURCE_BASE,
            EXTRACTION_GRAPH
        )
        update_sudo(query)
        spider.job = job

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        contents = adapter.get("contents")
        job = adapter["job"]
        if not job:
            return

        if isinstance(contents, (bytes, bytearray)):
            write_mode = "wb"
        elif isinstance(contents, str):
            write_mode = "w"
        else:
            # Can't write a file that isn't a (byte)string
            self.set_job_status_to_failed(job)
            return item

        _uuid = str(uuid.uuid4())
        physical_file_name = f"{_uuid}.html"
        physical_file_path = os.path.join(self.storage_path, physical_file_name)
        with open(physical_file_path, write_mode) as f:
            f.write(contents)
            f.seek(0, os.SEEK_END) # TODO: check if this can be replaced by return value of write
            size = f.tell()
            file_created = datetime.datetime.now()

        adapter["uuid"] = _uuid
        adapter["size"] = size
        adapter["file_created"] = file_created
        adapter["extension"] = "html"
        adapter["format"] = "text/html; charset=utf-8"
        adapter["physical_file_name"] = physical_file_name
        adapter["physical_file_path"] = physical_file_path

        try:
            self.push_item_to_triplestore(adapter)
        except Exception as e:
            logger.error(f"Encountered exception while trying to write data to triplestore for item generated by scraping {adapter['url']}")
            self.set_job_status_to_failed(job)
            raise e from None

        return item

    def push_item_to_triplestore(self, item):
        virtual_resource_uuid = str(uuid.uuid4())
        virtual_resource_uri = f"http://data.lblod.info/files/{virtual_resource_uuid}"
        virtual_resource_name = f"{virtual_resource_uuid}.{item['extension']}"
        file = {
            "uri": virtual_resource_uri,
            "uuid": virtual_resource_uuid,
            "name": virtual_resource_name,
            "mimetype": item["format"],
            "created": item["file_created"],
            "modified": item["file_created"], # currently unused
            "size": item["size"],
            "extension": item["extension"],
        }
        physical_resource_uri = item["physical_file_path"].replace("/share/", "share://") # TODO: use file lib function to construct share uri
        physical_file = {
            "uuid": item["uuid"],
            "uri": physical_resource_uri,
            "name": item["physical_file_name"]
        }

        ins_file_q_string = construct_insert_file_query(file,
                                                        physical_file,
                                                        DEFAULT_GRAPH)
        update_sudo(ins_file_q_string)

        add_url_q_string = add_url_to_file(virtual_resource_uri, item["url"], DEFAULT_GRAPH)
        update_sudo(add_url_q_string)

        # Set scrape job status to success & attach results
        q_attach_res = attach_job_results(item["job"], [virtual_resource_uri], EXTRACTION_GRAPH)
        update_sudo(q_attach_res)
        q_update_status = update_job_status(item["job"], STATUS_SUCCESS, EXTRACTION_GRAPH)
        update_sudo(q_update_status)

    def set_job_status_to_failed(self, job):
        q_update_status = update_job_status(job, STATUS_FAILED, EXTRACTION_GRAPH)
        update_sudo(q_update_status)


def add_url_to_file(file, url, graph):
    query_template = Template("""
PREFIX nfo: <http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#>
PREFIX nie: <http://www.semanticdesktop.org/ontologies/2007/01/19/nie#>

INSERT {
    GRAPH $graph {
        $file
            a nfo:RemoteDataObject ;
            nie:url $url .
    }
}
WHERE {
    GRAPH $graph {
        $file a nfo:FileDataObject .
    }
}
""")
    return query_template.substitute(
        graph=sparql_escape_uri(graph),
        file=sparql_escape_uri(file),
        url=sparql_escape_uri(url))
