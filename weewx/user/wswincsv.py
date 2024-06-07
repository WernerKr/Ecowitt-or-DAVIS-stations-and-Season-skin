# Copyright 2021 Werner Krenn
# Distributed under terms of the GPLv3
"""
Emit archive data to wswin.csv file for WsWin automatic importing

Put this file in the weewx 'user' directory, then add the following to the
weewx configuration file:

[WswinCSV]
    filename = /path/to/wswin.csv
    binding = archive 	# or loop = not active!
    mode = append		# or overwrite
    txtheader = False	# not active !
    append_datestamp = False  # then file = 202110_wswin.csv

[Engine]
    [[Services]]
        process_services = ..., user.wswincsv.WswinCSV


"""

import time
import os
import os.path
import weewx
import weewx.wxformulas
import weeutil.weeutil
import weeutil.Sun
from weewx.engine import StdService

try:
    # WeeWX4 logging
    import logging
    from weeutil.logger import log_traceback

    log = logging.getLogger(__name__)

    def logdbg(msg):
        log.debug(msg)

    def loginf(msg):
        log.info(msg)

    def logerr(msg):
        log.error(msg)

    def log_traceback_error(prefix=''):
        log_traceback(log.error, prefix=prefix)

except ImportError:
    # WeeWX legacy (v3) logging via syslog
    import syslog
    from weeutil.weeutil import log_traceback

    def logmsg(level, msg):
        syslog.syslog(level, 'wswincsv: %s' % msg)

    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)

    def log_traceback_error(prefix=''):
        log_traceback(prefix=prefix, loglevel=syslog.LOG_ERR)

VERSION = "0.6"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("WeeWX 3 is required, found %s" %
                                   weewx.__version__)


def convert(v, metric, group, from_unit_system, to_units):
    ut = weewx.units.getStandardUnitType(from_unit_system, metric)
    vt = (v, ut[0], group)
    v = weewx.units.convert(vt, to_units)[0]
    return v


def nullproof(key, data):
    if key in data and data[key] is not None:
        return data[key]
    return 0


def testkey(key, data):
    if key in data and data[key] is not None:
       return True
    else:
       return False


def calcDayRain(dbm, ts):
    sts = weeutil.weeutil.startOfDay(ts)
    val = dbm.getSql("SELECT SUM(rain) FROM %s "
                     "WHERE dateTime>? AND dateTime<=?" % dbm.table_name,
                     (sts, ts))
    if val is None:
        return None
    return val[0]


class WswinCSV(StdService):

    def __init__(self, engine, config_dict):
        super(WswinCSV, self).__init__(engine, config_dict)
        loginf("service version is %s" % VERSION)
        h = config_dict.get('Station', {})
        self.station_type = h.get('station_type', 'None').lower()  
        if 'ecowitt' in self.station_type or 'gw1000' in self.station_type or 'interceptor' in self.station_type:
            self.leafcorr = 6.6
        else:
            self.leafcorr = 1

        d = config_dict.get('WswinCSV', {})
        self.filename = d.get('filename', '/var/tmp/wswin.csv')
        binding = d.get('binding', 'archive').lower()
        #if binding == 'loop':
        #    self.bind(weewx.NEW_LOOP_PACKET, self.handle_new_loop)
        #else:
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.handle_new_archive)
        # optionally emit a textheader line as the first line of the file
        self.header = weeutil.weeutil.to_bool(d.get('txtheader', False))
        self.append_datestamp =  weeutil.weeutil.to_bool(d.get('append_datestamp', False))
        # mode can be append or overwrite
        self.mode = d.get('mode', 'append')
        if self.mode == 'overwrite':
           self.header = False
           self.append_datestamp = False
        loginf("binding is %s" % binding)
        loginf("output goes to %s, leaf_correction=%s" % (self.filename, self.leafcorr))

    def handle_new_loop(self, event):
        self.handle_data(event.packet)

    def handle_new_archive(self, event):
        self.handle_data(event.record)

    def handle_data(self, event_data):
        try:
            dbm = self.engine.db_binder.get_manager('wx_binding')
            data, fields = self.calculate(event_data, dbm)
            self.write_data(data, fields)
        except Exception as e:
            log_traceback_error('wswincsv: **** ')

    def calculate(self, packet, archive):
        pu = packet.get('usUnits')
        data = dict(packet)
 
        fields = []
        data['dateTime'] = packet['dateTime']

        if testkey('inTemp', packet) is True:
          data['inTemp'] = convert(data['inTemp'], 'inTemp', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['inTemp']))
        else:
           fields.append(",")
        if testkey('outTemp', packet) is True:
          data['outTemp'] = convert(data['outTemp'], 'outTemp', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['outTemp']))
        else:
          fields.append(",")
        if testkey('extraTemp1', packet) is True:
          data['extraTemp1'] = convert(data['extraTemp1'], 'extraTemp1', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['extraTemp1']))
        else:
           fields.append(",")
        if testkey('extraTemp2', packet) is True:
          data['extraTemp2'] = convert(data['extraTemp2'], 'extraTemp2', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['extraTemp2']))
        else:
           fields.append(",")
        if testkey('extraTemp3', packet) is True:
          data['extraTemp3'] = convert(data['extraTemp3'], 'extraTemp3', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['extraTemp3']))
        else:
           fields.append(",")
        if testkey('extraTemp4', packet) is True:
          data['extraTemp4'] = convert(data['extraTemp4'], 'extraTemp4', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['extraTemp4']))
        else:
           fields.append(",")
        if testkey('extraTemp5', packet) is True:
          data['extraTemp5'] = convert(data['extraTemp5'], 'extraTemp5', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['extraTemp5']))
        else:
           fields.append(",")
        if testkey('extraTemp6', packet) is True:
          data['extraTemp6'] = convert(data['extraTemp6'], 'extraTemp6', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['extraTemp6']))
        else:
           fields.append(",")
#       if testkey('extraTemp7', packet) is True:
#          data['extraTemp7'] = convert(data['extraTemp7'], 'extraTemp7', 'group_temperature', pu, 'degree_C')
#          fields.append("%.1f," % float(data['extraTemp7']))
#       else:
#           fields.append(",")
#       if testkey('extraTemp8', packet) is True:
#          data['extraTemp8'] = convert(data['extraTemp8'], 'extraTemp8', 'group_temperature', pu, 'degree_C')
#          fields.append("%.1f," % float(data['extraTemp8']))
#       else:
#           fields.append(",")

        if testkey('leafTemp1', packet) is True:
          data['leafTemp1'] = convert(data['leafTemp1'], 'leafTemp1', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['leafTemp1']))
        else:
          fields.append(",")
        if testkey('leafTemp2', packet) is True:
          data['leafTemp2'] = convert(data['leafTemp2'], 'leafTemp2', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['leafTemp2']))
        else:
          fields.append(",")
        if testkey('leafTemp3', packet) is True:
          data['leafTemp3'] = convert(data['leafTemp3'], 'leafTemp3', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['leafTemp3']))
        else:
          fields.append(",")
        if testkey('leafTemp4', packet) is True:
          data['leafTemp4'] = convert(data['leafTemp4'], 'leafTemp4', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['leafTemp4']))
        else:
          fields.append(",")

        if testkey('soilTemp1', packet) is True:
          data['soilTemp1'] = convert(data['soilTemp1'], 'soilTemp1', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['soilTemp1']))
        else:
          fields.append(",")
        if testkey('soilTemp2', packet) is True:
          data['soilTemp2'] = convert(data['soilTemp2'], 'soilTemp2', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['soilTemp2']))
        else:
          fields.append(",")
        if testkey('soilTemp3', packet) is True:
          data['soilTemp3'] = convert(data['soilTemp3'], 'soilTemp3', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['soilTemp3']))
        else:
          fields.append(",")
        if testkey('soilTemp4', packet) is True:
          data['soilTemp4'] = convert(data['soilTemp4'], 'soilTemp4', 'group_temperature', pu, 'degree_C')
          fields.append("%.1f," % float(data['soilTemp4']))
        else:
          fields.append(",")

        if testkey('inHumidity', packet) is True:
          fields.append("%.0f," % float(data['inHumidity']))
        else:
          fields.append(",")
        if testkey('outHumidity', packet) is True:
          fields.append("%.0f," % float(data['outHumidity']))
        else:
          fields.append(",")
        if testkey('extraHumid1', packet) is True:
          fields.append("%.0f," % float(data['extraHumid1']))
        else:
          fields.append(",")
        if testkey('extraHumid2', packet) is True:
          fields.append("%.0f," % float(data['extraHumid2']))
        else:
          fields.append(",")
        if testkey('extraHumid3', packet) is True:
          fields.append("%.0f," % float(data['extraHumid3']))
        else:
          fields.append(",")
        if testkey('extraHumid4', packet) is True:
          fields.append("%.0f," % float(data['extraHumid4']))
        else:
          fields.append(",")
        if testkey('extraHumid5', packet) is True:
          fields.append("%.0f," % float(data['extraHumid5']))
        else:
          fields.append(",")
        if testkey('extraHumid6', packet) is True:
          fields.append("%.0f," % float(data['extraHumid6']))
        else:
          fields.append(",")
#        if testkey('extraHumid7', packet) is True:
#          fields.append("%.0f," % float(data['extraHumid7']))
#        else:
#          fields.append(",")
#        if testkey('extraHumid8', packet) is True:
#          fields.append("%.0f," % float(data['extraHumid8']))
#        else:
#          fields.append(",")
        if testkey('leafWet1', packet) is True:
          fields.append("%.0f," % float(data['leafWet1']/self.leafcorr))
        else:
          fields.append(",")
        if testkey('leafWet2', packet) is True:
          fields.append("%.0f," % float(data['leafWet2']/self.leafcorr))
        else:
          fields.append(",")
        if testkey('leafWet3', packet) is True:
          fields.append("%.0f," % float(data['leafWet3']/self.leafcorr))
        else:
          fields.append(",")
        if testkey('leafWet4', packet) is True:
          fields.append("%.0f," % float(data['leafWet4']/self.leafcorr))
        else:
          fields.append(",")

        if testkey('soilMoist1', packet) is True:
          fields.append("%.0f," % float(data['soilMoist1']))
        else:
          fields.append(",")        
        if testkey('soilMoist2', packet) is True:
          fields.append("%.0f," % float(data['soilMoist2']))
        else:
          fields.append(",")
        if testkey('soilMoist3', packet) is True:
          fields.append("%.0f," % float(data['soilMoist3']))
        else:
          fields.append(",")
        if testkey('soilMoist4', packet) is True:
          fields.append("%.0f," % float(data['soilMoist4']))
        else:
          fields.append(",")

        if testkey('barometer', packet) is True:
          data['barometer'] = convert(data['barometer'], 'pressure', 'group_pressure', pu, 'mbar')
          fields.append("%.1f," % float(data['barometer']))
        else:
          fields.append(",")

        v = nullproof('rain', packet)
        data['rain'] = convert(v, 'rain', 'group_rain', pu, 'mm')
        fields.append("%.3f," % float(data['rain']))

        v = nullproof('windSpeed', packet)
        data['windSpeed'] = convert(v, 'windSpeed', 'group_speed', pu, 'km_per_hour')
        fields.append("%.1f," % float(data['windSpeed']))

        v = nullproof('windDir', packet)
        data['windDir'] = v
        fields.append("%.0f," % float(data['windDir']))

        v = nullproof('ET', packet)
        data['ET'] = convert(v, 'ET', 'group_rain', pu, 'mm')
        fields.append("%.3f," % float(data['ET']))

        if testkey('UV', packet) is True:
          fields.append("%.1f," % float(data['UV']))
        else:
          fields.append(",")

        if testkey('radiation', packet) is True:
          fields.append("%.0f," % float(data['radiation']))
        else:
          fields.append(",")

        v = nullproof('windGust', packet)
        data['windGust'] = convert(v, 'windGust', 'group_speed', pu, 'km_per_hour')
        if data['windGust'] < data['windSpeed']:
          data['windGust'] = data['windSpeed'] 
        fields.append("%.1f,"  % float(data['windGust']))

        v = nullproof('rxCheckPercent', packet)
        data['rxCheckPercent'] = v
        fields.append("%.0f," % float(data['rxCheckPercent']))

        if testkey('windGustDir', packet) is True:
          if data['windGustDir'] == 0: 
            fields.append("%.0f" % float(data['windGustDir']))
          else:
            fields.append("%.0f" % float(data['windGustDir']/22.5))
        else:
          fields.append("0")

#        if 'dayRain' in packet:
#            v = nullproof('dayRain', packet)
#        else:
#            v = calcDayRain(archive, data['dateTime'])
#            v = 0 if v is None else v
#        data['dayRain'] = convert(v, 'rain', 'group_rain', pu, 'mm')
#       fields.append("%.2f," % float(data['dayRain']))

        return data, fields


    def write_data(self, data, fields):
        flag = "a" if self.mode == 'append' else "w"
        filename = self.filename
        if self.append_datestamp:
            basename = filename
            tstr = time.strftime("%Y%m",
                                 time.localtime(data['dateTime']))
            filename = "%s_%s" % (tstr, basename)

        txtheader = None
        header = None
        if (not os.path.exists(filename) or flag == "w"):
           header = True
           headertxt = ",,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,133,34,35,36,40,41,42,45,46,96\r\n"
     
        if self.header and flag == "a" and (not os.path.exists(filename)):
           txtheader = True
        #  hfields = []
           hfields = ['date']
           hfields.append('time')
           hfields.append('inTemp')
           hfields.append('outTemp')
           hfields.append('extraTemp1')
           hfields.append('extraTemp2')
           hfields.append('extraTemp3')
           hfields.append('extraTemp4')
           hfields.append('extraTemp5')
           hfields.append('extraTemp6')
        #  hfields.append('extraTemp7')
        #  hfields.append('extraTemp8')
           hfields.append('leafTemp1')
           hfields.append('leafTemp2')
           hfields.append('leafTemp3')
           hfields.append('leafTemp4')
           hfields.append('soilTemp1')
           hfields.append('soilTemp2')
           hfields.append('soilTemp3')
           hfields.append('soilTemp4')
           hfields.append('inHumidity')
           hfields.append('outHumidity')
           hfields.append('extraHumid1')
           hfields.append('extraHumid2')
           hfields.append('extraHumid3')
           hfields.append('extraHumid4')
           hfields.append('extraHumid5')
           hfields.append('extraHumid6')
        #  hfields.append('extraHumid7')
        #  hfields.append('extraHumid8')
           hfields.append('leafWet1')
           hfields.append('leafWet2')
           hfields.append('leafWet3')
           hfields.append('leafWet4')
           hfields.append('soilMoist1')
           hfields.append('soilMoist2')
           hfields.append('soilMoist3')
           hfields.append('soilMoist4')
           hfields.append('barometer')
           hfields.append('rain')
           hfields.append('windSpeed')
           hfields.append('windDir')
           hfields.append('ET')
           hfields.append('UV')
           hfields.append('radiation')
           hfields.append('windGust')
           hfields.append('rxCheckPercent')
           hfields.append('windGustDir\r\n')

        with open(self.filename, flag) as f:
            if txtheader:
               f.write(''.join(hfields))
            if header:
              f.write(headertxt)
            f.write(time.strftime("%d.%m.%Y,%H:%M,",
                                  time.localtime(data['dateTime'])))
            f.write(''.join(fields))
            f.write("\r\n")
