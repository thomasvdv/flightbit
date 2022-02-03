import scrapy

class StravaSpider(scrapy.Spider):
    name = "strava"

    def start_requests(self):
        # The list of segment URLs that will be crawled for athletes.
        urls = [
            'https://www.strava.com/segments/3700913'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f'quotes-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')