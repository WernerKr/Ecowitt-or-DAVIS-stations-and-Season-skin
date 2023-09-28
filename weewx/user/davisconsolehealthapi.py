#!/usr/bin/python3
"""
weewx module that records health information from a Davis Weatherlink Console 6313 using
the v2 API.

Modified from the davishealthapi driver by Werner Krenn

Settings in weewx.conf:

[StdReport]
    [[DavisConsoleHealth]]
        HTML_ROOT = /var/www/html/weewx/healthc
        enable = true
        skin = healthc

[DataBindings]
    [[davisconsolehealthapi_binding]]
        database = davisconsolehealthapi_sqlite
        table_name = archive
        manager = weewx.manager.DaySummaryManager
        schema = user.davisconsolehealthapi.schema

[Databases]
    [[davisconsolehealthapi_sqlite]]
        database_type = SQLite
        database_name = davisconsolehealthapi.sdb

[Engine]
    [[Services]]
        data_services = user.davisconsolehealthapi.DavisConsoleHealthAPI,

[davisconsolehealthapi]
    data_binding = davisconsolehealthapi_binding
    station_id = 123456
    api_key = abcdefghijklmnopqrstuvwzyx123456
    api_secret = 123456abcdefghijklmnopqrstuvwxyz
    max_age = None	# default = 2592000
    packet_log = 0
#packet_log = 0 -> none logging - log once: "Found current data from data ID %s Struc"
#packet_log = 1 -> "Found current data from data ID %s Sensortype %s" 
#packet_log = 3 -> Log all received packets "packet: %s" % record
#packet_log = 5 -> Log all current received Data "c_data: %s" % data

[Accumulator]
   [[consoleRadioVersionC]]
        accumulator = firstlast
        extractor = last
   [[consoleSwVersionC]]
        accumulator = firstlast
        extractor = last
   [[consoleOsVersionC]]
        accumulator = firstlast
        extractor = last

"""

from __future__ import with_statement
from __future__ import absolute_import
from __future__ import print_function

import json
import requests
import time
import hashlib
import hmac

import weewx
import weewx.units
from weewx.engine import StdService

import weeutil.weeutil

try:
    # Test for new-style weewx logging by trying to import weeutil.logger
    import weeutil.logger
    import logging

    log = logging.getLogger(__name__)

    def logdbg(msg):
        """Log debug messages"""
        log.debug(msg)

    def loginf(msg):
        """Log info messages"""
        log.info(msg)

    def logerr(msg):
        """Log error messages"""
        log.error(msg)


except ImportError:
    # Old-style weewx logging
    import syslog

    def logmsg(level, msg):
        """Log messages"""
        syslog.syslog(level, "davisconsolehealthapi: %s:" % msg)

    def logdbg(msg):
        """Log debug messages"""
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        """Log info messages"""
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        """Log error messages"""
        logmsg(syslog.LOG_ERR, msg)


DRIVER_NAME = "DavisConsoleHealthAPI"
DRIVER_VERSION = "0.3"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" % weewx.__version__)

weewx.units.USUnits["group_decibels"] = "decibels"
weewx.units.MetricUnits["group_decibels"] = "decibels"
weewx.units.MetricWXUnits["group_decibels"] = "decibels"
weewx.units.default_unit_format_dict["decibels"] = "%.1f"
weewx.units.default_unit_label_dict["decibels"] = " dBm"

weewx.units.USUnits["group_string"] = "string"
weewx.units.MetricUnits["group_string"] = "string"
weewx.units.MetricWXUnits["group_string"] = "string"
weewx.units.default_unit_label_dict["string"] = ""
weewx.units.default_unit_format_dict["string"] = "%s"

weewx.units.USUnits["group_millivolts"] = "millivolts"
weewx.units.MetricUnits["group_millivolts"] = "millivolts"
weewx.units.MetricWXUnits["group_millivolts"] = "millivolts"
weewx.units.default_unit_format_dict["millivolts"] = "%d"
weewx.units.default_unit_label_dict["millivolts"] = " mV"

weewx.units.USUnits["group_ampere"] = "ampere"
weewx.units.MetricUnits["group_ampere"] = "ampere"
weewx.units.MetricWXUnits["group_ampere"] = "ampere"
weewx.units.default_unit_format_dict["ampere"] = "%.3f"
weewx.units.default_unit_label_dict["ampere"] = " A"

weewx.units.obs_group_dict["consoleBatteryC"] = "group_millivolts"
weewx.units.obs_group_dict["rssiC"] = "group_decibels"
weewx.units.obs_group_dict["consoleApiLevelC"] = "group_count"
weewx.units.obs_group_dict["queueKilobytesC"] = "group_count"
weewx.units.obs_group_dict["freeMemC"] = "group_count"
weewx.units.obs_group_dict["systemFreeSpaceC"] = "group_count"
weewx.units.obs_group_dict["chargerPluggedC"] = "group_count"
weewx.units.obs_group_dict["batteryPercentC"] = "group_percent"
weewx.units.obs_group_dict["localAPIQueriesC"] = "group_count"
weewx.units.obs_group_dict["healthVersionC"] = "group_count"
weewx.units.obs_group_dict["linkUptimeC"] = "group_deltatime"
weewx.units.obs_group_dict["rxKilobytesC"] = "group_count"

weewx.units.obs_group_dict["connectionUptimeC"] = "group_deltatime"
weewx.units.obs_group_dict["osUptimeC"] = "group_deltatime"
weewx.units.obs_group_dict["batteryConditionC"] = "group_count"
weewx.units.obs_group_dict["iFreeSpaceC"] = "group_count"
weewx.units.obs_group_dict["batteryCurrentC"] = "group_ampere"
weewx.units.obs_group_dict["batteryStatusC"] = "group_count"
weewx.units.obs_group_dict["databaseKilobytesC"] = "group_count"
weewx.units.obs_group_dict["batteryCycleCountC"] = "group_count"
weewx.units.obs_group_dict["bootloaderVersionC"] = "group_count"
weewx.units.obs_group_dict["clockSourceC"] = "group_count"
weewx.units.obs_group_dict["appUptimeC"] = "group_deltatime"
weewx.units.obs_group_dict["batteryTempC"] = "group_count"
weewx.units.obs_group_dict["txKilobytesC"] = "group_count"

weewx.units.obs_group_dict["consoleRadioVersionC"] = "group_string"
weewx.units.obs_group_dict["consoleSwVersionC"] = "group_string"
weewx.units.obs_group_dict["consoleOsVersionC"] = "group_string"

schema = [
    ("dateTime", "INTEGER NOT NULL PRIMARY KEY"),  # seconds
    ("usUnits", "INTEGER NOT NULL"),
    ("interval", "INTEGER NOT NULL"),  # seconds
    ("consoleBatteryC", "REAL"),
    ("rssiC", "REAL"),
    ("consoleApiLevelC", "INTEGER"),
    ("queueKilobytesC", "INTEGER"),
    ("freeMemC", "INTEGER"),
    ("systemFreeSpaceC", "INTEGER"),
    ("chargerPluggedC", "INTEGER"),
    ("batteryPercentC", "INTEGER"),
    ("localAPIQueriesC", "INTEGER"),
    ("healthVersionC", "INTEGER"),
    ("linkUptimeC", "INTEGER"),
    ("rxKilobytesC", "INTEGER"),
    ("connectionUptimeC", "INTEGER"),
    ("osUptimeC", "INTEGER"),
    ("batteryConditionC", "INTEGER"),
    ("iFreeSpaceC", "INTEGER"),
    ("batteryCurrentC", "REAL"),
    ("batteryStatusC", "INTEGER"),
    ("databaseKilobytesC", "INTEGER"),
    ("batteryCycleCountC", "INTEGER"),
    ("bootloaderVersionC", "INTEGER"),
    ("clockSourceC", "INTEGER"),
    ("appUptimeC", "INTEGER"),
    ("batteryTempC", "INTEGER"),
    ("txKilobytesC", "INTEGER"),
    ("consoleRadioVersionC", "TEXT"),
    ("consoleSwVersionC", "TEXT"),
    ("consoleOsVersionC", "TEXT"),
]

"""
"battery_voltage":4226,
"wifi_rssi":-56,
"console_radio_version":"10.3.2.90",
"console_api_level":28,
"queue_kilobytes":4,
"free_mem":699453,
"system_free_space":747118,
"charger_plugged":1,
"battery_percent":100,
"local_api_queries":null,
"health_version":1,
"link_uptime":31130,
"rx_kilobytes":20465563,
"console_sw_version":"1.2.13",
"connection_uptime":31113,
"os_uptime":1187518,
"battery_condition":2,
"internal_free_space":2215120,
"battery_current":0.003,
"battery_status":5,
"database_kilobytes":108347,
"battery_cycle_count":1,
"console_os_version":"1.2.11",
"bootloader_version":2,
"clock_source":2,
"app_uptime":1186355,
"battery_temp":33,
"tx_kilobytes":181662,
"""


def get_historical_url(parameters, api_secret):
    """Construct a valid v2 historical API URL"""

    # Get historical API data
    # Now concatenate all parameters into a string
    urltext = ""
    for key in parameters:
        urltext = urltext + key + str(parameters[key])
    # Now calculate the API signature using the API secret
    api_signature = hmac.new(
        api_secret.encode("utf-8"), urltext.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    # Finally assemble the URL
    apiurl = (
        "https://api.weatherlink.com/v2/historic/%s?api-key=%s&start-timestamp=%s&end-timestamp=%s&api-signature=%s&t=%s"
        % (
            parameters["station-id"],
            parameters["api-key"],
            parameters["start-timestamp"],
            parameters["end-timestamp"],
            api_signature,
            parameters["t"],
        )
    )
    # loginf("apiurl %s" % apiurl)
    return apiurl


def get_current_url(parameters, api_secret):
    """Construct a valid v2 current API URL"""

    # Remove parameters the current API does not require
    parameters.pop("start-timestamp", None)
    parameters.pop("end-timestamp", None)
    urltext = ""
    for key in parameters:
        urltext = urltext + key + str(parameters[key])
    api_signature = hmac.new(
        api_secret.encode("utf-8"), urltext.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    apiurl = (
        "https://api.weatherlink.com/v2/current/%s?api-key=%s&api-signature=%s&t=%s"
        % (
            parameters["station-id"],
            parameters["api-key"],
            api_signature,
            parameters["t"],
        )
    )
    return apiurl

def get_json(url, uerror):
    """Retrieve JSON data from the API"""
    uerror = False
    timeout = 10

    try:
        response = requests.get(url, timeout=timeout)
    except requests.Timeout as error:
        logerr("Message: %s" % error)
        uerror = True
    except requests.RequestException as error:
        logerr("RequestException: %s" % error)
        uerror = True
    except:
        logerr("Error at get_json")
        uerror = True
    if not uerror:
     return response.json()
    else:
     return
   

def decode_historical_json(data, self):
    """Read the historical API JSON data"""

    h_packet = dict()
    found0 = False
    found1 = False
    found2 = False
    found3 = False
    found4 = False
    found5 = False
    found6 = False
    found7 = False
    max_count = 0

    try:
        historical_data = data["sensors"]
        if ((self.packet_log >= 0) or (self.max_count == 0)) and not self.found:
         try:  
          for i in range(13):
            tx_id = None
            if historical_data[i]["data"] and (
                historical_data[i]["data_structure_type"] == 13
                 or historical_data[i]["data_structure_type"] == 11
                 or historical_data[i]["data_structure_type"] == 17):
                values = historical_data[i]["data"][0]
                tx_id = values.get("tx_id")
                loginf("Found historical data from data ID %s Struc: %s Sensortype %s tx_id %s" % (i, historical_data[i]["data_structure_type"], historical_data[i]["sensor_type"], tx_id) )
            self.found = True
            max_count = i+1
         except IndexError as error:
            i == 13

        if self.max_count == 0 or max_count > self.max_count:
           self.max_count = max_count
 
        for i in range(self.max_count):
            tx_id = None
            if historical_data[i]["data"] and (
                historical_data[i]["data_structure_type"] == 13
                or historical_data[i]["data_structure_type"] == 11):
                logdbg("Found historical data from data ID %s" % i)
                values = historical_data[i]["data"][0]

                tx_id = values.get("tx_id")
                if self.sensor_tx1 == 0 or self.sensor_tx1 == tx_id:
                  if self.packet_log >= 1:
                    loginf("Use historical data from data ID %s Struc: %s Sensortype %s tx_id %s" % (i, historical_data[i]["data_structure_type"], historical_data[i]["sensor_type"], tx_id) )

                  h_packet["rxCheckPercent"] = values.get("reception")
                  h_packet["rssi"] = values.get("rssi")
                  h_packet["supercapVolt"] = values.get("supercap_volt_last")
                  h_packet["solarVolt"] = values.get("solar_volt_last")
                  h_packet["packetStreak"] = values.get("good_packets_streak")
                  h_packet["txID"] = values.get("tx_id")
                  h_packet["txBattery"] = values.get("trans_battery")
                  h_packet["rainfallClicks"] = values.get("rainfall_clicks")
                  h_packet["solarRadVolt"] = values.get("solar_rad_volt_last")
                  h_packet["txBatteryFlag"] = values.get("trans_battery_flag")
                  h_packet["signalQuality"] = values.get("reception")
                  h_packet["errorPackets"] = values.get("error_packets")
                  h_packet["afc"] = values.get("afc")
                  h_packet["resynchs"] = values.get("resynchs")
                  h_packet["uvVolt"] = values.get("uv_volt_last")
                  found0 = True
                  break

    except KeyError as error:
        logerr(
            "No valid historical  API data recieved. Double-check API "
            "key/secret and station id. Error is: %s" % error
        )
        logerr("The API data returned was: %s" % data)
    except IndexError as error:
        logerr(
            "No valid historical data structure types found in API data. "
            "Error is: %s" % error
        )
        logerr("The API data returned was: %s" % data)
    except:
        logerr("No historical data.")
  
    return h_packet


def decode_current_json(data, self):
    """Read the current API JSON data"""
    max_ccount = 0
 
    c_packet = dict()
    try:
       current_data = data["sensors"]
       if ((self.packet_log >= 0) or (self.max_ccount == 0)) and not self.foundc:
         try:  
          for i in range(13):
            if current_data[i]["data"] and (
                current_data[i]["data_structure_type"] == 27):
             loginf("Found current data from data ID %s Struc: %s Sensortype %s" % (i, current_data[i]["data_structure_type"], current_data[i]["sensor_type"]) )
             max_ccount = i+1
             self.foundc = True
         except IndexError as error:
          i == 13

       if self.max_ccount == 0 or max_ccount > self.max_ccount:
          self.max_ccount = max_ccount
       

       for i in range(self.max_ccount):
            if current_data[i]["data"] and current_data[i]["data_structure_type"] == 27:
                logdbg("Found current data from data ID %s" % i)
                if self.packet_log >= 1:
                   loginf("Found current data from data ID %s Sensortype %s" % (i,current_data[i]["sensor_type"]) )

                values = current_data[i]["data"][0]
                c_packet["consoleBatteryC"] = values.get("battery_voltage")
                c_packet["rssiC"] = values.get("wifi_rssi")
                c_packet["consoleRadioVersionC"] = values.get("console_radio_version")
                c_packet["consoleApiLevelC"] = values.get("console_api_level")
                c_packet["queueKilobytesC"] = values.get("queue_kilobytes")
                c_packet["freeMemC"] = values.get("free_mem")
                c_packet["systemFreeSpaceC"] = values.get("system_free_space")
                c_packet["chargerPluggedC"] = values.get("charger_plugged")
                c_packet["batteryPercentC"] = values.get("battery_percent")
                c_packet["localAPIQueriesC"] = values.get("local_api_queries")
                c_packet["healthVersionC"] = values.get("health_version")
                c_packet["linkUptimeC"] = values.get("link_uptime")
                c_packet["rxKilobytesC"] = values.get("rx_kilobytes")
                c_packet["consoleSwVersionC"] = values.get("console_sw_version")
                c_packet["connectionUptimeC"] = values.get("connection_uptime")
                c_packet["osUptimeC"] = values.get("os_uptime")
                c_packet["batteryConditionC"] = values.get("battery_condition")
                c_packet["iFreeSpaceC"] = values.get("internal_free_space")
                c_packet["batteryCurrentC"] = values.get("battery_current")
                c_packet["batteryStatusC"] = values.get("battery_status")
                c_packet["databaseKilobytesC"] = values.get("database_kilobytes")
                c_packet["batteryCycleCountC"] = values.get("battery_cycle_count")
                c_packet["consoleOsVersionC"] = values.get("console_os_version")
                c_packet["bootloaderVersionC"] = values.get("bootloader_version")
                c_packet["clockSourceC"] = values.get("clock_source")
                c_packet["appUptimeC"] = values.get("app_uptime")
                c_packet["batteryTempC"] = values.get("battery_temp")
                c_packet["txKilobytesC"] = values.get("tx_kilobytes")
                break

    except KeyError as error:
        logerr(
            "No valid current API data recieved. Double-check API "
            "key/secret and station id. Error is: %s" % error
        )
        logerr("The API data returned was: %s" % data)
    except IndexError as error:
        logerr(
            "No valid current data structure types found in API data. "
            "Error is: %s" % error
        )
        logerr("The API data returned was: %s" % data)
    except:
        logerr("No current data.")

    return c_packet


class DavisConsoleHealthAPI(StdService):
    """Collect Davis sensor health information."""

    def __init__(self, engine, config_dict):
        super(DavisConsoleHealthAPI, self).__init__(engine, config_dict)
        self.polling_interval = 360  # FIX THIS - was 360
        loginf("service version is %s" % DRIVER_VERSION)
        loginf("archive interval is %s" % self.polling_interval)

        options = config_dict.get("davisconsolehealthapi", {})
        self.max_age = weeutil.weeutil.to_int(options.get("max_age", 2592000))
        self.api_key = options.get("api_key", None)
        self.api_secret = options.get("api_secret", None)
        self.station_id = options.get("station_id", None)
        self.packet_log = weeutil.weeutil.to_int(options.get("packet_log", 0))
 
        self.max_count = weeutil.weeutil.to_int(options.get("max_count", 0))
        self.max_ccount = weeutil.weeutil.to_int(options.get("max_ccount", 0))

        self.found = False
        self.foundc = False


        # get the database parameters we need to function
        binding = options.get("data_binding", "davisconsolehealthapi_binding")
        self.dbm = self.engine.db_binder.get_manager(
            data_binding=binding, initialize=True
        )

        # be sure schema in database matches the schema we have
        dbcol = self.dbm.connection.columnsOf(self.dbm.table_name)
        dbm_dict = weewx.manager.get_manager_dict(
            config_dict["DataBindings"], config_dict["Databases"], binding
        )
        memcol = [x[0] for x in dbm_dict["schema"]]
        if dbcol != memcol:
            raise Exception(
                "davisconsolehealthapi schema mismatch: %s != %s" % (dbcol, memcol)
            )

        self.last_ts = None
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.new_archive_record)

    @staticmethod
    def get_data(self):
        """Make an API call and process the data"""
        packet = dict()
        packet["dateTime"] = int(time.time())
        packet["usUnits"] = weewx.US

        if not self.api_key or not self.station_id or not self.api_secret:
            logerr(
                "DavisConsoleHealthAPI is missing a required parameter. "
                "Double-check your configuration file. key: %s"
                "secret: %s station ID: %s" % (self.api_key, self.api_secret, self.station_id)
            )
            return packet

        # WL API expects all of the components of the API call to be in
        # alphabetical order before the signature is calculated
        parameters = {
            "api-key": self.api_key,
            "end-timestamp": int(time.time()),
            "start-timestamp": int(time.time() - self.polling_interval),
            "station-id": self.station_id,
            "t": int(time.time()),
        }
        
        uerror = False
        c_error = False
        url = get_current_url(parameters, self.api_secret)
        logdbg("Current data url is %s" % url)
        data = get_json(url, uerror)
        if uerror == False: 
          if self.packet_log >= 5:
            loginf("c_data: %s" % data)
          c_packet = decode_current_json(data, self)
        else:
          c_error = True  
        #if not h_error:
        #   packet.update(h_packet)
        if not c_error:
           packet.update(c_packet)

        return packet

    def shutDown(self):
        """close database"""
        try:
            self.dbm.close()
        except Exception as error:
            logerr("Database exception: %s" % error)

    def new_archive_record(self, event):
        """save data to database then prune old records as needed"""
        now = int(time.time() + 0.5)
        delta = now - event.record["dateTime"]
        self.last_ts = event.record["dateTime"]
        if delta > event.record["interval"] * 60:
            loginf("Skipping record: time difference %s too big" % delta)
            return
        if self.last_ts is not None:
            self.save_data(self.get_packet(now, self.last_ts))
        self.last_ts = now
        if self.max_age is not None:
            self.prune_data(now - self.max_age)

    def save_data(self, record):
        """save data to database"""
        self.dbm.addRecord(record)

    def prune_data(self, timestamp):
        """delete records with dateTime older than ts"""
        sql = "delete from %s where dateTime < %d" % (self.dbm.table_name, timestamp)
        self.dbm.getSql(sql)
        try:
            # sqlite databases need some help to stay small
            self.dbm.getSql("vacuum")
        except Exception as error:
            logerr("Prune data error: %s" % error)

    def get_packet(self, now_ts, last_ts):
        """Retrieves and assembles the final packet"""
        record = self.get_data(self)
        # calculate the interval (an integer), and be sure it is non-zero
        record["interval"] = max(1, int((now_ts - last_ts) / 60))
        logdbg("davisconsolehealthapi packet: %s" % record)
        if self.packet_log >= 3:
           loginf("packet: %s" % record)
        return record
