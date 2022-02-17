import json

import scrapy
import os
from parsel import Selector
from datetime import date
import time
import json
import datetime


def authentication_failed(response):
    pass

class StravaSpider(scrapy.Spider):

    name = "strava"

    gpx_root = "athletes"

    states = ["New Hampshire", "Maine", "Vermont", "Massachusetts"]

    start_urls = [
        'https://www.strava.com/login'
    ]

    def throttle(self, response):
        if response.status == 429:
            self.logger.info("FALLING ASLEEP...")
            time.sleep(960)
        else:
            return

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'email': self.email, 'password': self.password},
            callback=self.after_login
        )

    def after_login(self, response):

        if authentication_failed(response):
            self.logger.error("Login failed")
            return

        # continue scraping with authenticated session...

        segment_page = 'https://www.strava.com/segments/3700913/leaderboard?filter=overall&page=1&page_uses_modern_javascript=true&per_page=100&partial=true'
        request = scrapy.Request(segment_page, dont_filter=True, callback=self.parse_segment)

        yield request

    def parse_segment(self, response):

        '''
        athletes = response.css('.athlete a::attr(href)').getall()
        for athlete in athletes:
            athlete_id = athlete.split('/')[-1]
            athlete_path = f'{self.gpx_root}/{athlete_id}'
            if not os.path.exists(athlete_path):
                os.makedirs(athlete_path)
                athlete_page = 'https://www.strava.com' + athlete
                request = scrapy.Request(url=athlete_page, dont_filter=True, callback=self.parse_athlete)
                yield request
        '''

        next_page = response.xpath("//li[@class='next_page']//@href").extract()

        if len(next_page) > 0:
            next_page = next_page[0] + "&partial=true"
            yield scrapy.Request("https://www.strava.com" + next_page, dont_filter=True, callback=self.parse_segment)

    def parse_gpx(self, response, athlete_id, activity_id):

        gpx_file = f'{self.gpx_root}/{athlete_id}/{activity_id}.gpx'
        with open(gpx_file, 'wb') as f:
            f.write(response.body)

    def parse_activity(self, response):

        athlete_id = response.xpath('//span[@class="title"]//@href').extract()[0].split('/')[-1]
        activity_id = response.url.split('/')[-1]
        activity_time = response.xpath('//div[@class="details"]//time/text()').get()

        segment_efforts = 'pageView.segmentEfforts().reset('
        strip_ele = ', { parse: true }'
        segment_ids = list()

        # Get the segments
        lines = response.text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(segment_efforts):
                content = line[len(segment_efforts):-(2 + len(strip_ele))]
                efforts_json = activity_json = json.loads(content)
                for effort in efforts_json["efforts"]:
                    segment_ids.append(effort["segment_id"])
                for effort in efforts_json["hidden_efforts"]:
                    segment_ids.append(effort["segment_id"])

        # Store the segments ids for future crawling.
        self.logger.info(activity_time)
        self.logger.info(segment_ids)

        # Some messy formatting required because Python doesn't support time formats with leading zeros on Windows.
        activity_time = [s.strip() for s in activity_time.split(',')]
        activity_year = activity_time[-1]
        activity_fmonth = activity_time[1].split(' ')

        activity_month = activity_fmonth[0]
        activity_day = activity_fmonth[1].strip().zfill(2)


        activity_date = datetime.datetime.strptime(f"{activity_day} {activity_month} {activity_year}", '%d %B %Y')

        activity_json = {"activity_id" : activity_id, "athlete_id" : athlete_id, "activity_date" : activity_date.strftime("%Y%m%d")}
        if segment_ids:
            activity_json["segments"] = segment_ids
        with open(f'{self.gpx_root}/{athlete_id}/{activity_id}.json', 'w') as outfile:
            json.dump(activity_json, outfile)

        # Download the GPX track and save it as a GEOJSON
        request = scrapy.Request(url=f"https://www.strava.com/activities/{activity_id}/export_gpx", dont_filter=True,
                                 callback=self.parse_gpx)
        request.cb_kwargs['athlete_id'] = athlete_id
        request.cb_kwargs['activity_id'] = activity_id
        yield request

    def parse_interval(self, response):

        interval_rides = "jQuery('#interval-rides').html(\""

        lines = response.text.split('\n')
        for line in lines:
            if line.startswith(interval_rides):
                content = line[len(interval_rides):-3]
                content = content.replace("\\n", "")
                content = content.replace("\\'", "'")
                content = content.replace('\\"', '"')
                content = content.replace("\\\\&quot;", "'")

                selector = Selector(text=content)
                activities = selector.xpath('//div[@class="content react-feed-component"]//@data-react-props').extract()
                for activity in activities:
                    # Read the JSON representation of the activity
                    try:
                        activity = activity.replace("\\", "")
                        activity_json = json.loads(activity)
                        if "activity" in activity_json:
                            # Check if it's backcountry skiiing and located in New England.
                            if activity_json["activity"]["type"] == "BackcountrySki":
                                activity_location = activity_json["activity"]["timeAndLocation"]["location"]
                                if any(state in activity_location for state in self.states):
                                    # Get the activity ID
                                    activity_id = activity_json["activity"]["id"]
                                    request = scrapy.Request(url=f"https://www.strava.com/activities/{activity_id}",
                                                             dont_filter=True,
                                                             callback=self.parse_activity)
                                    yield request

                    except:
                        self.logger.error(activity)

    def parse_range(self, response):

        interval_date_range = 'jQuery("#interval-graph-columns").html("'

        lines = response.text.split('\n')
        for line in lines:
            if line.startswith(interval_date_range):
                content = line[len(interval_date_range):-3]
                content = content.replace("\\n", "")
                content = content.replace("\\", "")

                selector = Selector(text=content)
                intervals = selector.xpath('//a[@class="bar"]//@href').extract()
                for interval in intervals:
                    interval = 'https://www.strava.com' + interval.replace('#', '/')
                    request = scrapy.Request(url=interval, dont_filter=True,
                                             headers={'X-Requested-With': 'XMLHttpRequest',
                                                      'Content-Type': 'application/json; charset=UTF-8'},
                                             callback=self.parse_interval)
                    yield request

    def parse_athlete(self, response):

        years_active = response.xpath('//div[@id="interval-date-range"]//li//@href').extract()
        # Add the current year
        # /athletes/9728065#graph_date_range?chart_type=miles&interval_type=week&interval=202106&year_offset=1
        for index, year_active in enumerate(years_active):
            year_active = year_active.replace('#', '/')
            year_active = year_active.replace('interval_type=week',
                                              'interval_type=month')  # Switch to monthly activities
            years_active[index] = 'https://www.strava.com' + year_active

        today = date.today()
        year = today.year
        month = '{:02d}'.format(today.month)
        years_active.append(
            response.url + f'/graph_date_range?chart_type=miles&interval_type=month&interval={year}{month}&year_offset=0')

        # Build a list of pages to parse
        for year_active in years_active:
            request = scrapy.Request(url=year_active, dont_filter=True,
                                     headers={'X-Requested-With': 'XMLHttpRequest',
                                              'Content-Type': 'application/json; charset=UTF-8'},
                                     callback=self.parse_range)
            yield request
