from datetime import datetime, timedelta


class Nomads():
    '''
    Generates NOMADS GRIB download URL

    The archive is a mess with missing files and different formats. Files represent end of time period.

    https://nomads.ncdc.noaa.gov/data/rucanl/200612/20061231/ruc2_252_20061231_2300_000.grb
    https://nomads.ncdc.noaa.gov/data/rucanl/200712/20071231/ruc2anl_130_20071231_2300_000.grb2
    https://nomads.ncdc.noaa.gov/data/rucanl/200810/20081029/ruc2_252_20081029_2300_000.grb
    https://nomads.ncdc.noaa.gov/data/rucanl/201106/20110620/ruc2anl_130_20110620_2300_000.grb2
    https://nomads.ncdc.noaa.gov/data/rucanl/201610/20161001/rap_130_20161001_2300_000.grb2
    https://nomads.ncdc.noaa.gov/data/ruc130/201701/20170113/rap_130_20170113_0000_000.grb2
    '''

    repos = [
        (datetime(2006, 12, 31), "rucanl", "ruc2_252", "grb"),
        (datetime(2007, 12, 31), "rucanl", "ruc2anl_130", "grb2"),
        (datetime(2008, 10, 29), "rucanl", "ruc2_252", "grb"),
        (datetime(2012, 5, 1), "rucanl", "ruc2anl_130", "grb2"),
        (datetime(2016, 10, 1), "rucanl", "rap_130", "grb2")
    ]

    def __init__(self, t_time):
        self.t_time = t_time
        self.dir = "ruc130"
        self.model = "rap_130"
        self.ext = "grb2"
        self.year = t_time.year
        self.month = t_time.strftime('%m')
        self.day = t_time.strftime('%d')
        self.hour = t_time.strftime('%H')
        for repo in self.repos:
            if t_time <= repo[0]:
                self.dir = repo[1]
                self.model = repo[2]
                self.ext = repo[3]
                break

    def grib_file(self):
        return "%s_%s%s%s_%s00_000.%s" % (
            self.model, self.year, self.month, self.day, self.hour, self.ext)

    def grib_url(self):
        grib_file = self.grib_file()
        grib_url = "https://nomads.ncdc.noaa.gov/data/%s/%s%s/%s%s%s/%s" % (self.dir,
                                                                            self.year, self.month,
                                                                            self.year, self.month,
                                                                            self.day, grib_file)
        return grib_url

    def grib_model(self):
        return self.model
