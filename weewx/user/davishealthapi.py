#!/usr/bin/python3
"""
weewx module that records health information from a Davis weather station using
the v2 API.

Modified from the davishealthapi driver by uajqq

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
        syslog.syslog(level, "davishealthapi: %s:" % msg)

    def logdbg(msg):
        """Log debug messages"""
        logmsg(syslog.LOG_DEBUG, msg)

    def loginf(msg):
        """Log info messages"""
        logmsg(syslog.LOG_INFO, msg)

    def logerr(msg):
        """Log error messages"""
        logmsg(syslog.LOG_ERR, msg)


DRIVER_NAME = "DavisHealthAPI"
DRIVER_VERSION = "0.2"

if weewx.__version__ < "3":
    raise weewx.UnsupportedFeature("weewx 3 is required, found %s" % weewx.__version__)

weewx.units.USUnits["group_decibels"] = "decibels"
weewx.units.MetricUnits["group_decibels"] = "decibels"
weewx.units.MetricWXUnits["group_decibels"] = "decibels"
weewx.units.default_unit_format_dict["decibels"] = "%.1f"
weewx.units.default_unit_label_dict["decibels"] = " dBm"

weewx.units.default_unit_format_dict["volt"] = "%.3f"

weewx.units.USUnits["group_millivolts"] = "millivolts"
weewx.units.MetricUnits["group_millivolts"] = "millivolts"
weewx.units.MetricWXUnits["group_millivolts"] = "millivolts"
weewx.units.default_unit_format_dict["millivolts"] = "%d"
weewx.units.default_unit_label_dict["millivolts"] = " mV"

weewx.units.obs_group_dict["supercapVolt"] = "group_volt"
weewx.units.obs_group_dict["solarVolt"] = "group_volt"
weewx.units.obs_group_dict["txBattery"] = "group_volt"
weewx.units.obs_group_dict["solarRadVolt"] = "group_volt"
weewx.units.obs_group_dict["uvVolt"] = "group_volt"
weewx.units.obs_group_dict["consoleBattery"] = "group_millivolts"
weewx.units.obs_group_dict["consolePower"] = "group_millivolts"
weewx.units.obs_group_dict["signalQuality"] = "group_percent"
weewx.units.obs_group_dict["rssi"] = "group_decibels"
weewx.units.obs_group_dict["uptime"] = "group_deltatime"
weewx.units.obs_group_dict["linkUptime"] = "group_deltatime"
weewx.units.obs_group_dict["packetStreak"] = "group_count"
weewx.units.obs_group_dict["rainfallClicks"] = "group_count"
weewx.units.obs_group_dict["errorPackets"] = "group_count"
weewx.units.obs_group_dict["touchpadWakeups"] = "group_count"
weewx.units.obs_group_dict["localAPIQueries"] = "group_count"
weewx.units.obs_group_dict["txID"] = "group_count"
weewx.units.obs_group_dict["txBatteryFlag"] = "group_count"
#weewx.units.obs_group_dict["firmwareVersion"] = "group_count"
weewx.units.obs_group_dict["firmwareVersion"] = "group_time"
#weewx.units.obs_group_dict["bootloaderVersion"] = "group_count"
weewx.units.obs_group_dict["bootloaderVersion"] = "group_time"
weewx.units.obs_group_dict["healthVersion"] = "group_count"
weewx.units.obs_group_dict["radioVersion"] = "group_count"
#weewx.units.obs_group_dict["radioVersion"] = "group_time"
weewx.units.obs_group_dict["espressIFVersion"] = "group_count"
weewx.units.obs_group_dict["afc"] = "group_count"
weewx.units.obs_group_dict["resynchs"] = "group_count"
weewx.units.obs_group_dict["rxBytes"] = "group_data"
weewx.units.obs_group_dict["txBytes"] = "group_data"
weewx.units.obs_group_dict["rapidRecords"] = "group_data"

weewx.units.obs_group_dict["rxCheckPercent1"] = "group_percent"
weewx.units.obs_group_dict["rssi1"] = "group_decibels"
weewx.units.obs_group_dict["supercapVolt1"] = "group_volt"
weewx.units.obs_group_dict["solarVolt1"] = "group_volt"
weewx.units.obs_group_dict["packetStreak1"] = "group_count"
weewx.units.obs_group_dict["txID1"] = "group_count"
weewx.units.obs_group_dict["txBattery1"] = "group_volt"
weewx.units.obs_group_dict["rainfallClicks1"] = "group_count"
weewx.units.obs_group_dict["solarRadVolt1"] = "group_volt"
weewx.units.obs_group_dict["txBatteryFlag1"] = "group_count"
weewx.units.obs_group_dict["signalQuality1"] = "group_percent"
weewx.units.obs_group_dict["errorPackets1"] = "group_count"
weewx.units.obs_group_dict["afc1"] = "group_count"
weewx.units.obs_group_dict["resynchs1"] = "group_count"
weewx.units.obs_group_dict["uvVolt1"] = "group_volt"

weewx.units.obs_group_dict["rxCheckPercent2"] = "group_percent"
weewx.units.obs_group_dict["rssi2"] = "group_decibels"
weewx.units.obs_group_dict["supercapVolt2"] = "group_volt"
weewx.units.obs_group_dict["solarVolt2"] = "group_volt"
weewx.units.obs_group_dict["packetStreak2"] = "group_count"
weewx.units.obs_group_dict["txID2"] = "group_count"
weewx.units.obs_group_dict["txBattery2"] = "group_volt"
weewx.units.obs_group_dict["rainfallClicks2"] = "group_count"
weewx.units.obs_group_dict["solarRadVolt2"] = "group_volt"
weewx.units.obs_group_dict["txBatteryFlag2"] = "group_count"
weewx.units.obs_group_dict["signalQuality2"] = "group_percent"
weewx.units.obs_group_dict["errorPackets2"] = "group_count"
weewx.units.obs_group_dict["afc2"] = "group_count"
weewx.units.obs_group_dict["resynchs2"] = "group_count"
weewx.units.obs_group_dict["uvVolt2"] = "group_volt"

weewx.units.obs_group_dict["rxCheckPercent3"] = "group_percent"
weewx.units.obs_group_dict["rssi3"] = "group_decibels"
weewx.units.obs_group_dict["supercapVolt3"] = "group_volt"
weewx.units.obs_group_dict["solarVolt3"] = "group_volt"
weewx.units.obs_group_dict["packetStreak3"] = "group_count"
weewx.units.obs_group_dict["txID3"] = "group_count"
weewx.units.obs_group_dict["txBattery3"] = "group_volt"
weewx.units.obs_group_dict["rainfallClicks3"] = "group_count"
weewx.units.obs_group_dict["solarRadVolt3"] = "group_volt"
weewx.units.obs_group_dict["txBatteryFlag3"] = "group_count"
weewx.units.obs_group_dict["signalQuality3"] = "group_percent"
weewx.units.obs_group_dict["errorPackets3"] = "group_count"
weewx.units.obs_group_dict["afc3"] = "group_count"
weewx.units.obs_group_dict["resynchs3"] = "group_count"
weewx.units.obs_group_dict["uvVolt3"] = "group_volt"

weewx.units.obs_group_dict["rxCheckPercent4"] = "group_percent"
weewx.units.obs_group_dict["rssi4"] = "group_decibels"
weewx.units.obs_group_dict["supercapVolt4"] = "group_volt"
weewx.units.obs_group_dict["solarVolt4"] = "group_volt"
weewx.units.obs_group_dict["packetStreak4"] = "group_count"
weewx.units.obs_group_dict["txID4"] = "group_count"
weewx.units.obs_group_dict["txBattery4"] = "group_volt"
weewx.units.obs_group_dict["rainfallClicks4"] = "group_count"
weewx.units.obs_group_dict["solarRadVolt4"] = "group_volt"
weewx.units.obs_group_dict["txBatteryFlag4"] = "group_count"
weewx.units.obs_group_dict["signalQuality4"] = "group_percent"
weewx.units.obs_group_dict["errorPackets4"] = "group_count"
weewx.units.obs_group_dict["afc4"] = "group_count"
weewx.units.obs_group_dict["resynchs4"] = "group_count"
weewx.units.obs_group_dict["uvVolt4"] = "group_volt"

weewx.units.obs_group_dict["rxCheckPercent5"] = "group_percent"
weewx.units.obs_group_dict["rssi5"] = "group_decibels"
weewx.units.obs_group_dict["supercapVolt5"] = "group_volt"
weewx.units.obs_group_dict["solarVolt5"] = "group_volt"
weewx.units.obs_group_dict["packetStreak5"] = "group_count"
weewx.units.obs_group_dict["txID5"] = "group_count"
weewx.units.obs_group_dict["txBattery5"] = "group_volt"
weewx.units.obs_group_dict["rainfallClicks5"] = "group_count"
weewx.units.obs_group_dict["solarRadVolt5"] = "group_volt"
weewx.units.obs_group_dict["txBatteryFlag5"] = "group_count"
weewx.units.obs_group_dict["signalQuality5"] = "group_percent"
weewx.units.obs_group_dict["errorPackets5"] = "group_count"
weewx.units.obs_group_dict["afc5"] = "group_count"
weewx.units.obs_group_dict["resynchs5"] = "group_count"
weewx.units.obs_group_dict["uvVolt5"] = "group_volt"

weewx.units.obs_group_dict["rxCheckPercent6"] = "group_percent"
weewx.units.obs_group_dict["rssi6"] = "group_decibels"
weewx.units.obs_group_dict["supercapVolt6"] = "group_volt"
weewx.units.obs_group_dict["solarVolt6"] = "group_volt"
weewx.units.obs_group_dict["packetStreak6"] = "group_count"
weewx.units.obs_group_dict["txID6"] = "group_count"
weewx.units.obs_group_dict["txBattery6"] = "group_volt"
weewx.units.obs_group_dict["rainfallClicks6"] = "group_count"
weewx.units.obs_group_dict["solarRadVolt6"] = "group_volt"
weewx.units.obs_group_dict["txBatteryFlag6"] = "group_count"
weewx.units.obs_group_dict["signalQuality6"] = "group_percent"
weewx.units.obs_group_dict["errorPackets6"] = "group_count"
weewx.units.obs_group_dict["afc6"] = "group_count"
weewx.units.obs_group_dict["resynchs6"] = "group_count"
weewx.units.obs_group_dict["uvVolt6"] = "group_volt"

weewx.units.obs_group_dict["rxCheckPercent7"] = "group_percent"
weewx.units.obs_group_dict["rssi7"] = "group_decibels"
weewx.units.obs_group_dict["supercapVolt7"] = "group_volt"
weewx.units.obs_group_dict["solarVolt7"] = "group_volt"
weewx.units.obs_group_dict["packetStreak7"] = "group_count"
weewx.units.obs_group_dict["txID7"] = "group_count"
weewx.units.obs_group_dict["txBattery7"] = "group_volt"
weewx.units.obs_group_dict["rainfallClicks7"] = "group_count"
weewx.units.obs_group_dict["solarRadVolt7"] = "group_volt"
weewx.units.obs_group_dict["txBatteryFlag7"] = "group_count"
weewx.units.obs_group_dict["signalQuality7"] = "group_percent"
weewx.units.obs_group_dict["errorPackets7"] = "group_count"
weewx.units.obs_group_dict["afc7"] = "group_count"
weewx.units.obs_group_dict["resynchs7"] = "group_count"
weewx.units.obs_group_dict["uvVolt7"] = "group_volt"

weewx.units.obs_group_dict["rssiA"] = "group_decibels"
weewx.units.obs_group_dict["firmwareVersionA"] = "group_time"
#weewx.units.obs_group_dict["bootloaderVersionA"] = "group_count"
weewx.units.obs_group_dict["bootloaderVersionA"] = "group_time"
weewx.units.obs_group_dict["localAPIQueriesA"] = "group_count"
weewx.units.obs_group_dict["healthVersionA"] = "group_count"
weewx.units.obs_group_dict["uptimeA"] = "group_deltatime"
weewx.units.obs_group_dict["linkUptimeA"] = "group_deltatime"
weewx.units.obs_group_dict["rxPacketsA"] = "group_count"
weewx.units.obs_group_dict["txPacketsA"] = "group_count"
weewx.units.obs_group_dict["errorPacketsA"] = "group_count"
weewx.units.obs_group_dict["droppedPacketsA"] = "group_count"
weewx.units.obs_group_dict["recordWriteCountA"] = "group_count"
weewx.units.obs_group_dict["iFreeMemChunkA"] = "group_data"
weewx.units.obs_group_dict["iFreeMemWatermA"] = "group_data"
weewx.units.obs_group_dict["iUsedMemA"] = "group_data"
weewx.units.obs_group_dict["iFreeMemA"] = "group_data"
weewx.units.obs_group_dict["tUsedMemA"] = "group_data"
weewx.units.obs_group_dict["tFreeMemA"] = "group_data"

schema = [
    ("dateTime", "INTEGER NOT NULL PRIMARY KEY"),  # seconds
    ("usUnits", "INTEGER NOT NULL"),
    ("interval", "INTEGER NOT NULL"),  # seconds
    ("supercapVolt", "REAL"),  # volts
    ("solarVolt", "REAL"),  # volts
    ("packetStreak", "INTEGER"),
    ("txID", "INTEGER"),
    ("txBattery", "REAL"),  # volts
    ("rainfallClicks", "INTEGER"),
    ("solarRadVolt", "REAL"),  # volts
    ("txBatteryFlag", "INTEGER"),
    ("signalQuality", "INTEGER"),  # percent
    ("errorPackets", "INTEGER"),
    ("afc", "REAL"),
    ("rssi", "REAL"),  # decibel-milliwats
    ("resynchs", "INTEGER"),
    ("uvVolt", "REAL"),  # volts
    ("consoleBattery", "REAL"),  # millivolts
    ("rapidRecords", "INTEGER"),
    ("firmwareVersion", "REAL"),
    ("uptime", "REAL"),  # seconds
    ("touchpadWakeups", "INTEGER"),
    ("bootloaderVersion", "REAL"),
    ("localAPIQueries", "INTEGER"),
    ("rxBytes", "INTEGER"),  # bytes
    ("healthVersion", "REAL"),
    ("radioVersion", "REAL"),
    ("espressIFVersion", "REAL"),
    ("linkUptime", "REAL"),  # seconds
    ("consolePower", "REAL"),  # millivolts
    ("txBytes", "INTEGER"),  # bytes
    ("rxCheckPercent1", "INTEGER"),  # percent
    ("rssi1", "REAL"),  # decibel-milliwats
    ("supercapVolt1", "REAL"),  # volts
    ("solarVolt1", "REAL"),  # volts
    ("packetStreak1", "REAL"),  # volts
    ("txID1", "INTEGER"),
    ("txBattery1", "REAL"),  # volts
    ("rainfallClicks1", "INTEGER"),
    ("solarRadVolt1", "REAL"),  # volts
    ("txBatteryFlag1", "INTEGER"),
    ("signalQuality1", "INTEGER"),  # percent
    ("errorPackets1", "INTEGER"),
    ("afc1", "REAL"),
    ("resynchs1", "INTEGER"),
    ("uvVolt1", "REAL"),  # volts
    ("rssi2", "REAL"),
    ("supercapVolt2", "REAL"),
    ("solarVolt2", "REAL"),
    ("packetStreak2", "REAL"),
    ("txID2", "INTEGER"),
    ("txBattery2", "REAL"),
    ("rainfallClicks2", "INTEGER"),
    ("solarRadVolt2", "REAL"),
    ("txBatteryFlag2", "INTEGER"),
    ("signalQuality2", "INTEGER"),
    ("errorPackets2", "INTEGER"),
    ("afc2", "REAL"),
    ("resynchs2", "INTEGER"),
    ("uvVolt2", "REAL"),
    ("rssi3", "REAL"),
    ("supercapVolt3", "REAL"),
    ("solarVolt3", "REAL"),
    ("packetStreak3", "REAL"),
    ("txID3", "INTEGER"),
    ("txBattery3", "REAL"),
    ("rainfallClicks3", "INTEGER"),
    ("solarRadVolt3", "REAL"),
    ("txBatteryFlag3", "INTEGER"),
    ("signalQuality3", "INTEGER"),
    ("errorPackets3", "INTEGER"),
    ("afc3", "REAL"),
    ("resynchs3", "INTEGER"),
    ("uvVolt3", "REAL"),
    ("rssi4", "REAL"),
    ("supercapVolt4", "REAL"),
    ("solarVolt4", "REAL"),
    ("packetStreak4", "REAL"),
    ("txID4", "INTEGER"),
    ("txBattery4", "REAL"),
    ("rainfallClicks4", "INTEGER"),
    ("solarRadVolt4", "REAL"),
    ("txBatteryFlag4", "INTEGER"),
    ("signalQuality4", "INTEGER"),
    ("errorPackets4", "INTEGER"),
    ("afc4", "REAL"),
    ("resynchs4", "INTEGER"),
    ("uvVolt4", "REAL"),
    ("rssi5", "REAL"),
    ("supercapVolt5", "REAL"),
    ("solarVolt5", "REAL"),
    ("packetStreak5", "REAL"),
    ("txID5", "INTEGER"),
    ("txBattery5", "REAL"),
    ("rainfallClicks5", "INTEGER"),
    ("solarRadVolt5", "REAL"),
    ("txBatteryFlag5", "INTEGER"),
    ("signalQuality5", "INTEGER"),
    ("errorPackets5", "INTEGER"),
    ("afc5", "REAL"),
    ("resynchs5", "INTEGER"),
    ("uvVolt5", "REAL"),
    ("rssi6", "REAL"),
    ("supercapVolt6", "REAL"),
    ("solarVolt6", "REAL"),
    ("packetStreak6", "REAL"),
    ("txID6", "INTEGER"),
    ("txBattery6", "REAL"),
    ("rainfallClicks6", "INTEGER"),
    ("solarRadVolt6", "REAL"),
    ("txBatteryFlag6", "INTEGER"),
    ("signalQuality6", "INTEGER"),
    ("errorPackets6", "INTEGER"),
    ("afc6", "REAL"),
    ("resynchs6", "INTEGER"),
    ("uvVolt6", "REAL"),
    ("rssi7", "REAL"),
    ("supercapVolt7", "REAL"),
    ("solarVolt7", "REAL"),
    ("packetStreak7", "REAL"),
    ("txID7", "INTEGER"),
    ("txBattery7", "REAL"),
    ("rainfallClicks7", "INTEGER"),
    ("solarRadVolt7", "REAL"),
    ("txBatteryFlag7", "INTEGER"),
    ("signalQuality7", "INTEGER"),
    ("errorPackets7", "INTEGER"),
    ("afc7", "REAL"),
    ("resynchs7", "INTEGER"),
    ("uvVolt7", "REAL"),
    ("rssiA", "REAL"),
    ("firmwareVersionA", "REAL"),
    ("bootloaderVersionA", "REAL"),
    ("localAPIQueriesA", "INTEGER"),
    ("healthVersionA", "REAL"),
    ("uptimeA", "REAL"),
    ("linkUptimeA", "REAL"),
    ("rxPacketsA", "INTEGER"),
    ("txPacketsA", "INTEGER"),
    ("errorPacketsA", "INTEGER"),
    ("droppedPacketsA", "INTEGER"),
    ("recordWriteCountA", "INTEGER"),
    ("iFreeMemChunkA", "INTEGER"),
    ("iFreeMemWatermA", "INTEGER"),
    ("iUsedMemA", "INTEGER"),
    ("iFreeMemA", "INTEGER"),
    ("tUsedMemA", "INTEGER"),
    ("tFreeMemA", "INTEGER"),
]



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

        if self.sensor_tx2 != 0:
          for i in range(self.max_count):
            tx_id = None
            if historical_data[i]["data"] and (
                historical_data[i]["data_structure_type"] == 13
                or historical_data[i]["data_structure_type"] == 11):
               values = historical_data[i]["data"][0]

               tx_id = values.get("tx_id")
               if self.sensor_tx2 == tx_id:
                  if self.packet_log >= 2:
                    loginf("Use historical data from data ID %s Struc: %s Sensortype %s tx_id %s" % (i, historical_data[i]["data_structure_type"], historical_data[i]["sensor_type"], tx_id) )

                  h_packet["rxCheckPercent1"] = values.get("reception")
                  h_packet["rssi1"] = values.get("rssi")
                  h_packet["supercapVolt1"] = values.get("supercap_volt_last")
                  h_packet["solarVolt1"] = values.get("solar_volt_last")
                  h_packet["packetStreak1"] = values.get("good_packets_streak")
                  h_packet["txID1"] = values.get("tx_id")
                  h_packet["txBattery1"] = values.get("trans_battery")
                  h_packet["rainfallClicks1"] = values.get("rainfall_clicks")
                  h_packet["solarRadVolt1"] = values.get("solar_rad_volt_last")
                  h_packet["txBatteryFlag1"] = values.get("trans_battery_flag")
                  h_packet["signalQuality1"] = values.get("reception")
                  h_packet["errorPackets1"] = values.get("error_packets")
                  h_packet["afc1"] = values.get("afc")
                  h_packet["resynchs1"] = values.get("resynchs")
                  h_packet["uvVolt1"] = values.get("uv_volt_last")
                  found1 = True
                  break

        if self.sensor_tx3 != 0: #and found1:
          for i in range(self.max_count):
            tx_id = None
            if historical_data[i]["data"] and (
                historical_data[i]["data_structure_type"] == 13
                or historical_data[i]["data_structure_type"] == 11):
               values = historical_data[i]["data"][0]

               tx_id = values.get("tx_id")
               if self.sensor_tx3 == tx_id:
                  if self.packet_log >= 2:
                    loginf("Use historical data from data ID %s Struc: %s Sensortype %s tx_id %s" % (i, historical_data[i]["data_structure_type"], historical_data[i]["sensor_type"], tx_id) )

                  h_packet["rxCheckPercent2"] = values.get("reception")
                  h_packet["rssi2"] = values.get("rssi")
                  h_packet["supercapVolt2"] = values.get("supercap_volt_last")
                  h_packet["solarVolt2"] = values.get("solar_volt_last")
                  h_packet["packetStreak2"] = values.get("good_packets_streak")
                  h_packet["txID2"] = values.get("tx_id")
                  h_packet["txBattery2"] = values.get("trans_battery")
                  h_packet["rainfallClicks2"] = values.get("rainfall_clicks")
                  h_packet["solarRadVolt2"] = values.get("solar_rad_volt_last")
                  h_packet["txBatteryFlag2"] = values.get("trans_battery_flag")
                  h_packet["signalQuality2"] = values.get("reception")
                  h_packet["errorPackets2"] = values.get("error_packets")
                  h_packet["afc2"] = values.get("afc")
                  h_packet["resynchs2"] = values.get("resynchs")
                  h_packet["uvVolt2"] = values.get("uv_volt_last")
                  found2 = True
                  break

        if self.sensor_tx4 != 0:  # and found2:
          for i in range(self.max_count):
            tx_id = None
            if historical_data[i]["data"] and (
                historical_data[i]["data_structure_type"] == 13
                or historical_data[i]["data_structure_type"] == 11):
               values = historical_data[i]["data"][0]

               tx_id = values.get("tx_id")
               if self.sensor_tx4 == tx_id:
                  if self.packet_log >= 2:
                    loginf("Use historical data from data ID %s Struc: %s Sensortype %s tx_id %s" % (i, historical_data[i]["data_structure_type"], historical_data[i]["sensor_type"], tx_id) )

                  h_packet["rxCheckPercent3"] = values.get("reception")
                  h_packet["rssi3"] = values.get("rssi")
                  h_packet["supercapVolt3"] = values.get("supercap_volt_last")
                  h_packet["solarVolt3"] = values.get("solar_volt_last")
                  h_packet["packetStreak3"] = values.get("good_packets_streak")
                  h_packet["txID3"] = values.get("tx_id")
                  h_packet["txBattery3"] = values.get("trans_battery")
                  h_packet["rainfallClicks3"] = values.get("rainfall_clicks")
                  h_packet["solarRadVolt3"] = values.get("solar_rad_volt_last")
                  h_packet["txBatteryFlag3"] = values.get("trans_battery_flag")
                  h_packet["signalQuality3"] = values.get("reception")
                  h_packet["errorPackets3"] = values.get("error_packets")
                  h_packet["afc3"] = values.get("afc")
                  h_packet["resynchs3"] = values.get("resynchs")
                  h_packet["uvVolt3"] = values.get("uv_volt_last")
                  found3 = True
                  break

        if self.sensor_tx5 != 0: # and found3:
          for i in range(self.max_count):
            tx_id = None
            if historical_data[i]["data"] and (
                historical_data[i]["data_structure_type"] == 13
                or historical_data[i]["data_structure_type"] == 11):
               values = historical_data[i]["data"][0]

               tx_id = values.get("tx_id")
               if self.sensor_tx5 == tx_id:
                  if self.packet_log >= 2:
                    loginf("Use historical data from data ID %s Struc: %s Sensortype %s tx_id %s" % (i, historical_data[i]["data_structure_type"], historical_data[i]["sensor_type"], tx_id) )

                  h_packet["rxCheckPercent4"] = values.get("reception")
                  h_packet["rssi4"] = values.get("rssi")
                  h_packet["supercapVolt4"] = values.get("supercap_volt_last")
                  h_packet["solarVolt4"] = values.get("solar_volt_last")
                  h_packet["packetStreak4"] = values.get("good_packets_streak")
                  h_packet["txID4"] = values.get("tx_id")
                  h_packet["txBattery4"] = values.get("trans_battery")
                  h_packet["rainfallClicks4"] = values.get("rainfall_clicks")
                  h_packet["solarRadVolt4"] = values.get("solar_rad_volt_last")
                  h_packet["txBatteryFlag4"] = values.get("trans_battery_flag")
                  h_packet["signalQuality4"] = values.get("reception")
                  h_packet["errorPackets4"] = values.get("error_packets")
                  h_packet["afc4"] = values.get("afc")
                  h_packet["resynchs4"] = values.get("resynchs")
                  h_packet["uvVolt4"] = values.get("uv_volt_last")
                  found4 = True
                  break

        if self.sensor_tx6 != 0: # and found4:
          for i in range(self.max_count):
            tx_id = None
            if historical_data[i]["data"] and (
                historical_data[i]["data_structure_type"] == 13
                or historical_data[i]["data_structure_type"] == 11):
               values = historical_data[i]["data"][0]

               tx_id = values.get("tx_id")
               if self.sensor_tx6 == tx_id:
                  if self.packet_log >= 2:
                    loginf("Use historical data from data ID %s Struc: %s Sensortype %s tx_id %s" % (i, historical_data[i]["data_structure_type"], historical_data[i]["sensor_type"], tx_id) )

                  h_packet["rxCheckPercent5"] = values.get("reception")
                  h_packet["rssi5"] = values.get("rssi")
                  h_packet["supercapVolt5"] = values.get("supercap_volt_last")
                  h_packet["solarVolt5"] = values.get("solar_volt_last")
                  h_packet["packetStreak5"] = values.get("good_packets_streak")
                  h_packet["txID5"] = values.get("tx_id")
                  h_packet["txBattery5"] = values.get("trans_battery")
                  h_packet["rainfallClicks5"] = values.get("rainfall_clicks")
                  h_packet["solarRadVolt5"] = values.get("solar_rad_volt_last")
                  h_packet["txBatteryFlag5"] = values.get("trans_battery_flag")
                  h_packet["signalQuality5"] = values.get("reception")
                  h_packet["errorPackets5"] = values.get("error_packets")
                  h_packet["afc5"] = values.get("afc")
                  h_packet["resynchs5"] = values.get("resynchs")
                  h_packet["uvVolt5"] = values.get("uv_volt_last")
                  found5 = True
                  break

        if self.sensor_tx7 != 0: # and found5:
          for i in range(self.max_count):
            tx_id = None
            if historical_data[i]["data"] and (
                historical_data[i]["data_structure_type"] == 13
                or historical_data[i]["data_structure_type"] == 11):
               values = historical_data[i]["data"][0]

               tx_id = values.get("tx_id")
               if self.sensor_tx7 == tx_id:
                  if self.packet_log >= 2:
                    loginf("Use historical data from data ID %s Struc: %s Sensortype %s tx_id %s" % (i, historical_data[i]["data_structure_type"], historical_data[i]["sensor_type"], tx_id) )

                  h_packet["rxCheckPercent6"] = values.get("reception")
                  h_packet["rssi6"] = values.get("rssi")
                  h_packet["supercapVolt6"] = values.get("supercap_volt_last")
                  h_packet["solarVolt6"] = values.get("solar_volt_last")
                  h_packet["packetStreak6"] = values.get("good_packets_streak")
                  h_packet["txID6"] = values.get("tx_id")
                  h_packet["txBattery6"] = values.get("trans_battery")
                  h_packet["rainfallClicks6"] = values.get("rainfall_clicks")
                  h_packet["solarRadVolt6"] = values.get("solar_rad_volt_last")
                  h_packet["txBatteryFlag6"] = values.get("trans_battery_flag")
                  h_packet["signalQuality6"] = values.get("reception")
                  h_packet["errorPackets6"] = values.get("error_packets")
                  h_packet["afc6"] = values.get("afc")
                  h_packet["resynchs6"] = values.get("resynchs")
                  h_packet["uvVolt6"] = values.get("uv_volt_last")
                  found6 = True
                  break

        if self.sensor_tx8 != 0: # and found6:
          for i in range(self.max_count):
            tx_id = None
            if historical_data[i]["data"] and (
                historical_data[i]["data_structure_type"] == 13
                or historical_data[i]["data_structure_type"] == 11):
               values = historical_data[i]["data"][0]

               tx_id = values.get("tx_id")
               if self.sensor_tx8 == tx_id:
                  if self.packet_log >= 2:
                    loginf("Use historical data from data ID %s Struc: %s Sensortype %s tx_id %s" % (i, historical_data[i]["data_structure_type"], historical_data[i]["sensor_type"], tx_id) )

                  h_packet["rxCheckPercent7"] = values.get("reception")
                  h_packet["rssi7"] = values.get("rssi")
                  h_packet["supercapVolt7"] = values.get("supercap_volt_last")
                  h_packet["solarVolt7"] = values.get("solar_volt_last")
                  h_packet["packetStreak7"] = values.get("good_packets_streak")
                  h_packet["txID7"] = values.get("tx_id")
                  h_packet["txBattery7"] = values.get("trans_battery")
                  h_packet["rainfallClicks7"] = values.get("rainfall_clicks")
                  h_packet["solarRadVolt7"] = values.get("solar_rad_volt_last")
                  h_packet["txBatteryFlag7"] = values.get("trans_battery_flag")
                  h_packet["signalQuality7"] = values.get("reception")
                  h_packet["errorPackets7"] = values.get("error_packets")
                  h_packet["afc7"] = values.get("afc")
                  h_packet["resynchs7"] = values.get("resynchs")
                  h_packet["uvVolt7"] = values.get("uv_volt_last")
                  found7 = True
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
                current_data[i]["data_structure_type"] == 15
                 or current_data[i]["data_structure_type"] == 18):
             loginf("Found current data from data ID %s Struc: %s Sensortype %s" % (i, current_data[i]["data_structure_type"], current_data[i]["sensor_type"]) )
             max_ccount = i+1
             self.foundc = True
         except IndexError as error:
          i == 13

       if self.max_ccount == 0 or max_ccount > self.max_ccount:
          self.max_ccount = max_ccount
       
       for i in range(self.max_ccount):
            if current_data[i]["data"] and current_data[i]["data_structure_type"] == 15:
                logdbg("Found current data from data ID %s" % i)
                if self.packet_log >= 1:
                   loginf("Found current data from data ID %s Sensortype %s" % (i,current_data[i]["sensor_type"]) )

                values = current_data[i]["data"][0]

                c_packet["consoleBattery"] = values.get("battery_voltage")
                c_packet["rapidRecords"] = values.get("rapid_records_sent")
                c_packet["firmwareVersion"] = values.get("firmware_version")
                c_packet["uptime"] = values.get("uptime")
                c_packet["touchpadWakeups"] = values.get("touchpad_wakeups")
                c_packet["bootloaderVersion"] = values.get("bootloader_version")
                c_packet["localAPIQueries"] = values.get("local_api_queries")
                c_packet["rxBytes"] = values.get("rx_bytes")
                c_packet["healthVersion"] = values.get("health_version")
                #test = values.get("radio_version")
                #if test != None:
                #   if test < 1000000000:
                #      test = test + 1000000000
                #c_packet["radioVersion"] = test
                c_packet["radioVersion"] = values.get("radio_version")
                c_packet["espressIFVersion"] = values.get("espressif_version")
                c_packet["linkUptime"] = values.get("link_uptime")
                c_packet["consolePower"] = values.get("input_voltage")
                c_packet["txBytes"] = values.get("tx_bytes")

                break

       for i in range(self.max_ccount):
            if current_data[i]["data"] and current_data[i]["data_structure_type"] == 18:
                logdbg("Found current data from data ID %s" % i)
                if self.packet_log >= 1:
                   loginf("Found current data from data ID %s Sensortype %s" % (i,current_data[i]["sensor_type"]) )

                values = current_data[i]["data"][0]

                c_packet["rssiA"] = values.get("wifi_rssi")
                c_packet["firmwareVersionA"] = values.get("firmware_version")
                #test = values.get("bootloader_version")
                #if test != None:
                #   if test < 1000000000:
                #      test = test + 1000000000
                #c_packet["bootloaderVersionA"] = test
                c_packet["bootloaderVersionA"] = values.get("bootloader_version")
                c_packet["iFreeMemChunkA"] = values.get("internal_free_mem_chunk_size")
                c_packet["iUsedMemA"] = values.get("internal_used_mem")
                c_packet["iFreeMemA"] = values.get("internal_free_mem")
                c_packet["tUsedMemA"] = values.get("total_used_mem")
                c_packet["tFreeMemA"] = values.get("total_free_mem")
                c_packet["iFreeMemWatermA"] = values.get("internal_free_mem_watermark")
                c_packet["errorPacketsA"] = values.get("packet_errors")
                c_packet["droppedPacketsA"] = values.get("dropped_packets")
                c_packet["rxPacketsA"] = values.get("rx_packets")
                c_packet["txPacketsA"] = values.get("tx_packets")
                c_packet["recordWriteCountA"] = values.get("record_write_count")
                c_packet["localAPIQueriesA"] = values.get("local_api_queries")
                c_packet["uptimeA"] = values.get("uptime")
                c_packet["linkUptimeA"] = values.get("link_uptime")
                c_packet["healthVersionA"] = values.get("health_version")
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


class DavisHealthAPI(StdService):
    """Collect Davis sensor health information."""

    def __init__(self, engine, config_dict):
        super(DavisHealthAPI, self).__init__(engine, config_dict)
        self.polling_interval = 360  # FIX THIS - was 360
        loginf("service version is %s" % DRIVER_VERSION)
        loginf("archive interval is %s" % self.polling_interval)

        options = config_dict.get("davishealthapi", {})
        self.max_age = weeutil.weeutil.to_int(options.get("max_age", 2592000))
        self.api_key = options.get("api_key", None)
        self.api_secret = options.get("api_secret", None)
        self.station_id = options.get("station_id", None)
        self.packet_log = weeutil.weeutil.to_int(options.get("packet_log", 0))
        self.sensor_tx1 = weeutil.weeutil.to_int(options.get("sensor_tx1", 0))
        self.sensor_tx2 = weeutil.weeutil.to_int(options.get("sensor_tx2", 0))
        self.sensor_tx3 = weeutil.weeutil.to_int(options.get("sensor_tx3", 0))
        self.sensor_tx4 = weeutil.weeutil.to_int(options.get("sensor_tx4", 0))
        self.sensor_tx5 = weeutil.weeutil.to_int(options.get("sensor_tx5", 0))
        self.sensor_tx6 = weeutil.weeutil.to_int(options.get("sensor_tx6", 0))
        self.sensor_tx7 = weeutil.weeutil.to_int(options.get("sensor_tx7", 0))
        self.sensor_tx8 = weeutil.weeutil.to_int(options.get("sensor_tx8", 0))
 
        self.max_count = weeutil.weeutil.to_int(options.get("max_count", 0))
        self.max_ccount = weeutil.weeutil.to_int(options.get("max_ccount", 0))

        self.found = False
        self.foundc = False


        # get the database parameters we need to function
        binding = options.get("data_binding", "davishealthapi_binding")
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
                "davishealthapi schema mismatch: %s != %s" % (dbcol, memcol)
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
                "DavisHealthAPI is missing a required parameter. "
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
        
        url = get_historical_url(parameters, self.api_secret)

        uerror = False
        h_error = False
        logdbg("Historical data url is %s" % url)
        data = get_json(url, uerror)
        if uerror == False: 
          if self.packet_log >= 4:
            loginf("h_data: %s" % data)
          if self.packet_log >= 3:
             test = ("h_data: %s" % data)
             loginf("h_data_len: %s" % len(test))
          h_packet = decode_historical_json(data, self)
        else:
          h_error = True 
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
        if not h_error:
           packet.update(h_packet)
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
        logdbg("davishealthapi packet: %s" % record)
        if self.packet_log >= 3:
           loginf("packet: %s" % record)
        return record
