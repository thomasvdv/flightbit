# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FlightItem(scrapy.Item):
    # define the fields for your item here like:
    airport_id = scrapy.Field()
    date = scrapy.Field()
    points = scrapy.Field()
    pilot_name = scrapy.Field()
    pilot_id = scrapy.Field()
    km = scrapy.Field()
    kph = scrapy.Field()
    club = scrapy.Field()
    aircraft = scrapy.Field()
    index = scrapy.Field()
    callsign = scrapy.Field()
    start = scrapy.Field()
    end = scrapy.Field()
    flight_info = scrapy.Field()
    flight_id = scrapy.Field()
    pass
