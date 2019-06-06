import scrapy
from scrapy.crawler import CrawlerProcess, Crawler
from scrapy.utils.project import get_project_settings

import os

from .spiders.cirnopedia import CirnoSpider

config = {
    'http://fate-go.cirnopedia.org/summon.php': 'data/banners.json',
    'http://fate-go.cirnopedia.org/quest_event.php': 'data/events.json'
}


process = CrawlerProcess()
for url, out in config.items():
    try:
        os.unlink(out)
    except FileNotFoundError:
        pass
    settings = get_project_settings() 
    settings['LOG_LEVEL'] = 'INFO'
    settings['FEED_FORMAT'] = 'json'
    settings['FEED_URI'] = out

    process.crawl(Crawler(CirnoSpider, settings), url=url)

process.start()