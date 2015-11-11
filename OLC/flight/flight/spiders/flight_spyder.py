import scrapy

from flight.items import FlightItem

class FlightSpider(scrapy.Spider):

    name = "flight"
    allowed_domains = ["onlinecontest.org"]
    airports = ["ARLIW1", "TWISP1", "WINTH1", "RICLW1", "EPHRA1", "BOULD1", "DEERP1", "VANCV1", "WENAT1", "DAVEW1", "DARRI1"]
    years = range(2007,2016)
    start_urls = []

    def __init__(self):
        for y in self.years:
            for airport in self.airports:
                url = "http://www.onlinecontest.org/olc-2.0/gliding/flightsOfAirfield.html?c=US&sc=8&rt=olc&aa=%s&st=olcp&sp=%s&paging=100000" % (airport, y)
                self.start_urls.append(url)

    def parse(self, response):
        for tr in response.xpath('//table[@id="dailyScore"]//tr'):
            flight_info = tr.xpath('td[10]//@href').extract()
            if flight_info:
                item = FlightItem()
                item['airport_id'] = response.url.split('&')[3].split('=')[-1]
                item['date'] = tr.xpath('td[1]/text()').extract()
                item['points'] = tr.xpath('td[2]/text()').extract()[0].strip()
                item['pilot_name'] = tr.xpath('td[3]/a/text()').extract()[0].strip()
                item['pilot_id'] = tr.xpath('td[3]//@href').extract()[0].split('=')[-1]
                item['km'] = tr.xpath('td[4]/text()').extract()[0].strip()
                item['kph'] = tr.xpath('td[5]/text()').extract()[0].strip()
                item['club'] = tr.xpath('td[6]/text()').extract()
                item['aircraft'] = tr.xpath('td[7]/text()').extract()
                item['start'] = tr.xpath('td[8]/text()').extract()[0].strip()
                item['end'] = tr.xpath('td[9]/text()').extract()[0].strip()
                item['flight_info'] = tr.xpath('td[10]//@href').extract()[0].split('=')[-1]

                info_page = "http://www.onlinecontest.org/olc-2.0/gliding/flightinfo.html?dsId=%s" % (item['flight_info'])
                request = scrapy.Request(info_page, dont_filter=True, callback=self.parse_info)
                request.meta['item'] = item

                yield request

    def parse_info(self, response):
        item = response.meta['item']
        item['flight_id'] = response.xpath('//meta[@name="og:image"]/@content').extract()[0].split('=')[-1]
        dds = response.xpath('//div[@id="aircraftinfo"]//dd/text()')
        item['index'] = dds[-1].extract()
        item['callsign'] = dds[1].extract()
        yield item

