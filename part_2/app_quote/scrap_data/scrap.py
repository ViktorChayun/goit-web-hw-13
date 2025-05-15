import json
from pathlib import Path
import scrapy
import sys
from scrapy.crawler import CrawlerProcess
from scrapy.item import Item, Field
from itemadapter import ItemAdapter

from .db import (
    insert_data,
    upload_author_if_not_exist,
    insert_quote_if_not_exist,
    insert_tag_if_not_exist,
    insert_quote_to_tag,
    find_author_id,
)


BASE_DIR = dir = Path(__file__).resolve().parent / "output"
FILE_QUOTES = BASE_DIR / 'quotes.json'
FILE_AUTHORS = BASE_DIR / 'authors.json'


class QuoteItem(Item):
    quote = Field()
    author = Field()
    tags = Field()


class AuthorItem(Item):
    fullname = Field()
    born_date = Field()
    born_location = Field()
    description = Field()


class DataPipeline:
    quotes = []
    authors = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if 'fullname' in adapter.keys():
            self.authors.append(dict(adapter))
        if 'quote' in adapter.keys():
            self.quotes.append(dict(adapter))

    def close_spider(self, spider):
        with open(FILE_QUOTES, mode='w+', encoding='utf-8') as file:
            json.dump(self.quotes, file, ensure_ascii=False, indent=4)
        with open(FILE_AUTHORS, mode='w+', encoding='utf-8') as file:
            json.dump(self.authors, file, ensure_ascii=False, indent=4)


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]
    custom_settings = {"ITEM_PIPELINES": {DataPipeline: 300}}
    visited_authors = set()

    def parse(self, response):
        for q in response.xpath("/html//div[@class='quote']"):
            author = q.xpath("span/small/text()").get().strip()
            author_url = q.xpath("span/a/@href").get().strip()
            quote = q.xpath("span[@class='text']/text()").get().strip()
            tags = q.xpath("div[@class='tags']/a/text()").extract()

            yield QuoteItem(
                quote=quote,
                author=author,
                tags=[t.strip() for t in tags]
            )

            yield response.follow(
                url=self.start_urls[0] + author_url,
                callback=self.parse_author
            )

        next_page_link = response.xpath("/html//li[@class='next']/a/@href").get()
        if next_page_link:
            url = self.start_urls[0] + next_page_link
            yield scrapy.Request(url=url)

    @classmethod
    def parse_author(self, response, **kwarg):
        content = response.xpath("/html//div[@class='author-details']")
        fullname = content.xpath("h3[@class='author-title']/text()").get().strip()
        born_date = content.xpath("p/span[@class='author-born-date']/text()").get().strip()
        born_location = content.xpath("p/span[@class='author-born-location']/text()").get().strip()
        description = content.xpath("div[@class='author-description']/text()").get().strip()
        yield AuthorItem(
            fullname=fullname,
            born_date=born_date,
            born_location=born_location,
            description=description
        )


def scrap_data():
    # run spider
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.start()


def upload_authors(authors_data, user_id):
    for author in authors_data:
        name = author['fullname']
        borndate = author['born_date']
        bornlocation = author['born_location']
        description = author['description']
        upload_author_if_not_exist(name, borndate, bornlocation, description, user_id)


def uopload_quotes(quotes_data, user_id):
    for quote in quotes_data:
        quote_text = quote['quote']
        author_id = find_author_id(quote.get('author'))
        try:
            quote_id = insert_quote_if_not_exist(quote_text, author_id, user_id)
            for tag in quote['tags']:
                tag_name = tag.strip()
                tag_id = insert_tag_if_not_exist(tag_name, user_id)
                insert_quote_to_tag(quote_id, tag_id)
        except ValueError as err:
            print(f"{quote} triggered error: {err}")


def upload_to_postgres(user_id):
    # Read data from JSON files
    with open(FILE_QUOTES, 'r', encoding='utf-8') as file:
        quotes_data = json.load(file)

    with open(FILE_AUTHORS, 'r', encoding='utf-8') as file:
        authors_data = json.load(file)

    # insert_data(authors_data, quotes_data)
    upload_authors(authors_data, user_id)
    uopload_quotes(quotes_data, user_id)


def scrap_and_upload_data(user_id=1):
    # scrap_data()
    upload_to_postgres(user_id)


if __name__ == "__main__":
    scrap_and_upload_data()
