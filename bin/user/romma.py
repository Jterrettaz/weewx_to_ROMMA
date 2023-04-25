#!/usr/bin/env python
# Copyright 2016-2017 Matthew Wall
# Licensed under the terms of the GPLv3

try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    import Queue as queue
from distutils.version import StrictVersion
import sys
import syslog
import time
try:
    # Python 3
    from urllib.parse import urlencode
except ImportError:
    # Python 2
    from urllib import urlencode


import weewx
import weewx.restx
import weewx.units
from weeutil.weeutil import to_bool, list_as_string

VERSION = "2.0"

REQUIRED_WEEWX = "3.5.0"
if StrictVersion(weewx.__version__) < StrictVersion(REQUIRED_WEEWX):
    raise weewx.UnsupportedFeature("weewx %s or greater is required, found %s"
                                   % (REQUIRED_WEEWX, weewx.__version__))

try:
    # Test for new-style weewx logging by trying to import weeutil.logger
    import weeutil.logger
    import logging
    log = logging.getLogger(__name__)

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

except ImportError:
    # Old-style weewx logging
    import syslog

    def logmsg(level, msg):
        syslog.syslog(level, 'meteotemplate: %s' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)

class Romma(weewx.restx.StdRESTbase):
    DEFAULT_URL = 'https://www.romma.fr/donneesdeweewx.php'

    def __init__(self, engine, cfg_dict):
        """This service recognizes standard restful options plus the following:

        Parameters:

        password: the shared key for uploading data

        server_url: full URL to the meteotemplate ingest script
        """
        super(Romma, self).__init__(engine, cfg_dict)
        loginf("service version is %s" % VERSION)

        site_dict = weewx.restx.get_site_dict(cfg_dict, 'Romma', 'password', 'id')
        if site_dict is None:
            logerr("Data will not be uploaded: Missing password and/or id")
            return

        site_dict.get('server_url', Romma.DEFAULT_URL)
        binding = list_as_string(site_dict.pop('binding', 'archive').lower())

        try:
            _mgr_dict = weewx.manager.get_manager_dict_from_config(
                cfg_dict, 'wx_binding')
            site_dict['manager_dict'] = _mgr_dict
        except weewx.UnknownBinding:
            pass

        self._queue = queue.Queue()
        self._thread = RommaThread(self._queue, **site_dict)
        self._thread.start()
        if 'loop' in binding:
            self.bind(weewx.NEW_LOOP_PACKET, self.handle_new_loop)
        if 'archive' in binding:
            self.bind(weewx.NEW_ARCHIVE_RECORD, self.handle_new_archive)
        loginf("Data will be uploaded to %s" % site_dict['server_url'])

    def handle_new_loop(self, event):
        self._queue.put(event.packet)

    def handle_new_archive(self, event):
        self._queue.put(event.record)


class RommaThread(weewx.restx.RESTThread):

    def __init__(self, q, password, id, server_url, skip_upload=False,
                 manager_dict=None,
                 post_interval=None, max_backlog=sys.maxsize, stale=None,
                 log_success=True, log_failure=True,
                 timeout=60, max_tries=3, retry_wait=5):
        super(RommaThread, self).__init__(
            q, protocol_name='Romma', manager_dict=manager_dict,
            post_interval=post_interval, max_backlog=max_backlog, stale=stale,
            log_success=log_success, log_failure=log_failure,
            max_tries=max_tries, timeout=timeout, retry_wait=retry_wait)
        self.server_url = server_url
        self.password = password
        self.id = id
        self.skip_upload = to_bool(skip_upload)
        self.field_map = self.create_default_field_map()
        # FIXME: make field map changes available via config file


    def check_response(self, response):
        txt = response.read().decode()
        if txt != 'Success':
            raise weewx.restx.FailedPost("Server returned '%s'" % txt)

    def format_url(self, record):
        record = weewx.units.to_std_system(record, weewx.METRIC)
        if 'dayRain' in record and record['dayRain'] is not None:
            record['dayRain'] *= 10.0 # convert to mm
        if 'rain' in record and record['rain'] is not None:
            record['rain'] *= 10.0  # convert to mm
        if 'rainRate' in record and record['rainRate'] is not None:
            record['rainRate'] *= 10.0 # convert to mm/h 
        parts = dict()
        parts['date'] = record['dateTime']
        parts['pwd'] = self.password
        parts['id'] = self.id
        for k in self.field_map:
            if self.field_map[k][0] in record and record[self.field_map[k][0]] is not None:
                parts[k] = self._fmt(record.get(self.field_map[k][0]), self.field_map[k][1])
        return "%s?%s" % (self.server_url, urlencode(parts))

    @staticmethod
    def _fmt(x, places=3):
        fmt = "%%.%df" % places
        try:
            return fmt % x
        except TypeError:
            pass
        return x



    @staticmethod
    def create_default_field_map():
        fm = {
            'temp_e': ('outTemp', 1),  # degree_C
            'mintemp_e': ('lowOutTemp', 1),  # degree_C
            'maxtemp_e': ('highOutTemp', 1),  # degree_C
            'hum_e': ('outHumidity', 0),
            'baro': ('barometer', 1),  # mbar
            'pluie': ('rain', 1),  # mm
            'pluiejour': ('dayRain', 1),  # mm
            'ipluie': ('rainRate', 1),  # mm/h
            'vent': ('windSpeed', 1),  # km/h
            'direction': ('windDir', 0),  # degree_compass
            'solaire': ('radiation', 0),  # W/m^2
            'dew_point': ('dewpoint', 1),
            'windchill': ('windchill', 1),
            'humidex': ('humidex', 1),
            'rafale': ('windGust', 1),  # km/h
            'rafale_dir': ('windGustDir', 0),  # degree compass
            'solaire_max': ('highRadiation', 1),
            'temp_p1': ('extraTemp1', 1),  # degree_C
            'temp_p2': ('extraTemp2', 1),  # degree_C
            'temp_p3': ('extraTemp3', 1),  # degree_C
            'tempsoil1': ('soilTemp1', 1),  # degree_C
            'tempsoil2': ('soilTemp2', 1),  # degree_C
            'tempsoil3': ('soilTemp3', 1),  # degree_C
            'humsoil1': ('soilMoist1', 0),
            'humsoil2': ('soilMoist2', 0),
            'humsoil3': ('soilMoist3', 0)
            }

        return fm


# Do direct testing of this extension like this:
#   PYTHONPATH=WEEWX_BINDIR python WEEWX_BINDIR/user/meteotemplate.py

if __name__ == "__main__":
    import optparse

    usage = """%prog [--url URL] [--version] [--help]"""
    try:
        # WeeWX V4 logging
        weeutil.logger.setup('romma', {})
    except NameError:
        # WeeWX V3 logging
        syslog.openlog('romma', syslog.LOG_PID | syslog.LOG_CONS)
        syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--version', dest='version', action='store_true',
                      help='display driver version')
    parser.add_option('--url', dest='url', default=Romma.DEFAULT_URL,
                      help='full URL to the server script')
    (options, args) = parser.parse_args()

    if options.version:
        print("romma uploader version %s" % VERSION)
        exit(0)

    print ("uploading to %s" % options.url)
    weewx.debug = 2
    q = ueue.Queue()
    t = RommaThread(
        q, manager_dict=None, password=options.pw, server_url=options.url)
    t.start()
    q.put({'dateTime': int(time.time() + 0.5),
           'usUnits': weewx.US,
           'outTemp': 32.5,
           'inTemp': 75.8,
           'outHumidity': 24})
    q.put(None)
    t.join(20)