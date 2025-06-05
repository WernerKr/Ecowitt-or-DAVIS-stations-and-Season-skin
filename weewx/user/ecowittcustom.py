#!/usr/bin/env python
# Copyright 2016-2020 Matthew Wall
# Distributed under the terms of the GNU Public License (GPLv3)
# Modified 2025 - now only Ecowitt client Werner Krenn

"""
This driver runs a simple web server or sniffs network traffic in order to
capture data directly from an internet weather reporting device including:

  - Fine Offset GW1000,1100,1200,2000,3000 and more (ecowitt protocol or wu protocol)

===============================================================================
SniffServer vs TCPServer

The driver can obtain packets by sniffing network traffic using pcap, or by
listening for TCP/IP requests.  The pcap approach requires the python pypcap
module, which in turn requires libpcap.  This means a separate installation
on most platforms.

https://github.com/pynetwork/pypcap

To run a listener, specify an address and port.  This is the default mode.
For example:

[Ecowittcustom]
    mode = listen
    address = localhost
    port = 9999

To run a sniffer, specify an interface and filter.  For example:

[Ecowittcustom]
    mode = sniff
    iface = eth0
    pcap_filter = src host 192.168.1.5 && dst port 80

The following sections provide some details about each type of hardware.


===============================================================================
EcowittClient - Fine Offset

The Fine Offset gateway collects data from Fine Offset sensors using 915MHz
(and other?) unlicensed frequencies, then transmits the data via Wifi to
various services.  As of dec2019 these include ecowitt.net, wunderground.com,
weathercloud, weatherobservationswebsite, and metoffice.gov.uk.

Note that there are
variants of the Fine Offset GW1000, including:

  GW1000 - 433MHz	Australia
  GW1000A - 868MHz	Europe
  GW1000B - 915MHz	US
  GW1000BU - 915MHz with better rang

Also valid for GW1100, GW1200, GW2000, GW3000, WS39xx, WS38xx, wN1980, WN1900, HP2550, HP2560, HP3500 and so much more

The transmission to wunderground can be captured using the 'wu-client' mode.
The transmission using ecowitt protocol (see the 'customize' page in the WSView Plus
application) can be captured using the 'ecowitt-client' mode.

As of firmware 1.5.5, the device will attempt to upload to ecowitt servers,
even when nothing has been configured.  It is possible to turn this off using
the WSView Plus app.

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Settings WSView Plus app:
ecowitt-client:

Weather Services
Customized
Enable
Protocol Type Same As: Ecowitt
Server IP / Hostname: %your device-Ip or Name running WeeWx%
Path: /data/report/
Port: %your choosen Port% # maybe 8080 
Upload Intervall: 20 seconds (or what you prefer)

Settings weeWx.conf
[Ecowittcustom]
    # iface = wlan0
    iface = eth0
    device_type = ecowitt-client	# but not needed = default 
    port = 8080			# what used in WSView Plus app
    driver = user.ecowittcustom

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Settings WSView Plus app:
wu-client:

Weather Services
Customized
Enable
Protocol Type Same As: Wunderground
Server IP / Hostname: %your device-Ip or Name running WeeWx%
Path: /weatherstation/updateweatherstation.php?
Station ID: %your Station ID%
Station Key: %your Station Key%
Port: %your choosen Port% # maybe 8080 
Upload Intervall: 20 seconds (or what you prefer)

Settings weeWx.conf
[Ecowittcustom]
    # iface = wlan0
    iface = eth0
    device_type = wu-client
    port = 8080
    driver = user.ecowittcustom


"""

# FIXME: do a single mapping from GET/POST args to weewx schema names
# FIXME: specify by protocol, not by hardware device
# FIXME: automatically detect the protocol?
# FIXME: add code to skip duplicate and out-of-order packets

from __future__ import with_statement

# support both python2 and python3.  attempt the python3 import first, then
# fallback to python2.
try:
    from http.server import BaseHTTPRequestHandler
    from socketserver import TCPServer
    import queue as Queue
    import urllib.parse as urlparse
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler
    from SocketServer import TCPServer
    import Queue
    import urlparse

import binascii
import calendar
import fnmatch
import re
import string
import sys
import threading
import time

try:
    # weewx4 logging
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
    # old-style weewx logging
    import syslog
    def logmsg(level, msg):
        syslog.syslog(level, 'ecowittcustom: %s: %s' %
                      (threading.currentThread().getName(), msg))
    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)
    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)
    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)

import weewx.drivers
import weeutil.weeutil
import weewx.units

DRIVER_NAME = 'Ecowittcustom'
DRIVER_VERSION = '0.1.0'

DEFAULT_ADDR = ''
DEFAULT_PORT = 80
DEFAULT_IFACE = 'eth0'
DEFAULT_FILTER = 'dst port 80'
DEFAULT_DEVICE_TYPE = 'ecowitt-client'

weewx.units.obs_group_dict['co2'] = 'group_fraction'
weewx.units.obs_group_dict['co2_Temp'] = 'group_temperature'
weewx.units.obs_group_dict['co2_Hum'] = 'group_percent'
weewx.units.obs_group_dict['co2_24h'] = 'group_fraction'

weewx.units.obs_group_dict['co2in'] = 'group_fraction'
weewx.units.obs_group_dict['co2in_24h'] = 'group_fraction'

weewx.units.obs_group_dict['pm1_0'] = 'group_concentration'
weewx.units.obs_group_dict['pm4_0'] = 'group_concentration'
weewx.units.obs_group_dict['pm2_5'] = 'group_concentration'
weewx.units.obs_group_dict['pm10_0'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_1'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_2'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_3'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_4'] = 'group_concentration'

weewx.units.obs_group_dict['pm1_24h_co2'] = 'group_concentration'
weewx.units.obs_group_dict['pm4_24h_co2'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_24h_co2'] = 'group_concentration'
weewx.units.obs_group_dict['pm10_24h_co2'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_avg_24h_ch1'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_avg_24h_ch2'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_avg_24h_ch3'] = 'group_concentration'
weewx.units.obs_group_dict['pm25_avg_24h_ch4'] = 'group_concentration'

weewx.units.obs_group_dict['soilTemp1'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp2'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp3'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp4'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp5'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp6'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp7'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp8'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp9'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp10'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp11'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp12'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp13'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp14'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp15'] = 'group_temperature'
weewx.units.obs_group_dict['soilTemp16'] = 'group_temperature'

weewx.units.obs_group_dict['leafWet1'] = 'group_percent'
weewx.units.obs_group_dict['leafWet2'] = 'group_percent'
weewx.units.obs_group_dict['leafWet3'] = 'group_percent'
weewx.units.obs_group_dict['leafWet4'] = 'group_percent'
weewx.units.obs_group_dict['leafWet5'] = 'group_percent'
weewx.units.obs_group_dict['leafWet6'] = 'group_percent'
weewx.units.obs_group_dict['leafWet7'] = 'group_percent'
weewx.units.obs_group_dict['leafWet8'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist1'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist2'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist3'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist4'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist5'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist6'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist7'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist8'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist9'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist10'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist11'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist12'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist13'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist14'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist15'] = 'group_percent'
weewx.units.obs_group_dict['soilMoist16'] = 'group_percent'

weewx.units.obs_group_dict['lightning_distance'] = 'group_count'
weewx.units.obs_group_dict['lightning_disturber_count'] = 'group_time'
weewx.units.obs_group_dict['lightning_strike_count'] = 'group_count'
weewx.units.obs_group_dict['lightning_num'] = 'group_count'
weewx.units.obs_group_dict['runtime'] = 'group_deltatime'

weewx.units.obs_group_dict['rainrate'] = 'group_rainrate'
weewx.units.obs_group_dict['eventRain'] = 'group_rain'
weewx.units.obs_group_dict['weekRain'] = 'group_rain'
weewx.units.obs_group_dict['raintotal'] = 'group_rain'
weewx.units.obs_group_dict['rainBatteryStatus'] = 'group_volt'
weewx.units.obs_group_dict['hailBatteryStatus'] = 'group_volt'
weewx.units.obs_group_dict['windBatteryStatus'] = 'group_volt'
weewx.units.obs_group_dict['ws80_batt'] = 'group_volt'
weewx.units.obs_group_dict['ws90_batt'] = 'group_volt'
weewx.units.obs_group_dict['ws1900batt'] = 'group_volt'
weewx.units.obs_group_dict['console_batt'] = 'group_volt'
weewx.units.obs_group_dict['ws85_batt'] = 'group_volt'
weewx.units.obs_group_dict['wh85_batt'] = 'group_volt'

weewx.units.obs_group_dict['rrain_piezo'] = 'group_rainrate'
weewx.units.obs_group_dict['erain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['hrain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['drain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['wrain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['mrain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['yrain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['rain_piezo'] = 'group_rain'
weewx.units.obs_group_dict['p_rain'] = 'group_rain'
weewx.units.obs_group_dict['p_rainrate'] = 'group_rainrate'

weewx.units.obs_group_dict['ws90cap_volt'] = 'group_volt'
weewx.units.obs_group_dict['ws85cap_volt'] = 'group_volt'
weewx.units.obs_group_dict['ws90_ver'] = 'group_count'
weewx.units.obs_group_dict['ws85_ver'] = 'group_count'

weewx.units.obs_group_dict['soilMoistBatt1'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt2'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt3'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt4'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt5'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt6'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt7'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt8'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt9'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt10'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt11'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt12'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt13'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt14'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt15'] = 'group_volt'
weewx.units.obs_group_dict['soilMoistBatt16'] = 'group_volt'

weewx.units.obs_group_dict['soilTempBatt1'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt2'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt3'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt4'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt5'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt6'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt7'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt8'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt9'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt10'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt11'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt12'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt13'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt14'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt15'] = 'group_volt'
weewx.units.obs_group_dict['soilTempBatt16'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt1'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt2'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt3'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt4'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt5'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt6'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt7'] = 'group_volt'
weewx.units.obs_group_dict['leafWetBatt8'] = 'group_volt'

weewx.units.obs_group_dict['maxdailygust'] = 'group_speed2'
weewx.units.obs_group_dict['winddir_avg10m'] = 'group_direction'
weewx.units.obs_group_dict['windspdmph_avg10m'] = 'group_speed2'

weewx.units.obs_group_dict['co2_Batt'] = 'group_count'
weewx.units.obs_group_dict['pm25_Batt1'] = 'group_count'
weewx.units.obs_group_dict['pm25_Batt2'] = 'group_count'
weewx.units.obs_group_dict['pm25_Batt3'] = 'group_count'
weewx.units.obs_group_dict['pm25_Batt4'] = 'group_count'
weewx.units.obs_group_dict['leak_1'] = 'group_count'
weewx.units.obs_group_dict['leak_2'] = 'group_count'
weewx.units.obs_group_dict['leak_3'] = 'group_count'
weewx.units.obs_group_dict['leak_4'] = 'group_count'
weewx.units.obs_group_dict['leak_Batt1'] = 'group_count'
weewx.units.obs_group_dict['leak_Batt2'] = 'group_count'
weewx.units.obs_group_dict['leak_Batt3'] = 'group_count'
weewx.units.obs_group_dict['leak_Batt4'] = 'group_count'
weewx.units.obs_group_dict['lightning_Batt'] = 'group_count'
weewx.units.obs_group_dict['wh24_batt'] = 'group_count'
weewx.units.obs_group_dict['wh25_batt'] = 'group_count'
weewx.units.obs_group_dict['wh26_batt'] = 'group_count'
weewx.units.obs_group_dict['wh65_batt'] = 'group_count'
weewx.units.obs_group_dict['wh68_batt'] = 'group_count'

weewx.units.obs_group_dict['soilad1'] = 'group_count'
weewx.units.obs_group_dict['soilad2'] = 'group_count'
weewx.units.obs_group_dict['soilad3'] = 'group_count'
weewx.units.obs_group_dict['soilad4'] = 'group_count'
weewx.units.obs_group_dict['soilad5'] = 'group_count'
weewx.units.obs_group_dict['soilad6'] = 'group_count'
weewx.units.obs_group_dict['soilad7'] = 'group_count'
weewx.units.obs_group_dict['soilad8'] = 'group_count'
weewx.units.obs_group_dict['soilad9'] = 'group_count'
weewx.units.obs_group_dict['soilad10'] = 'group_count'
weewx.units.obs_group_dict['soilad11'] = 'group_count'
weewx.units.obs_group_dict['soilad12'] = 'group_count'
weewx.units.obs_group_dict['soilad13'] = 'group_count'
weewx.units.obs_group_dict['soilad14'] = 'group_count'
weewx.units.obs_group_dict['soilad15'] = 'group_count'
weewx.units.obs_group_dict['soilad16'] = 'group_count'

"""
weewx.units.obs_group_dict['wh24_sig'] = 'group_count'
weewx.units.obs_group_dict['wh25_sig'] = 'group_count'
weewx.units.obs_group_dict['wh26_sig'] = 'group_count'
weewx.units.obs_group_dict['wh31_ch1_sig'] = 'group_count'
weewx.units.obs_group_dict['wh31_ch2_sig'] = 'group_count'
weewx.units.obs_group_dict['wh31_ch3_sig'] = 'group_count'
weewx.units.obs_group_dict['wh31_ch4_sig'] = 'group_count'
weewx.units.obs_group_dict['wh31_ch5_sig'] = 'group_count'
weewx.units.obs_group_dict['wh31_ch6_sig'] = 'group_count'
weewx.units.obs_group_dict['wh31_ch7_sig'] = 'group_count'
weewx.units.obs_group_dict['wh31_ch8_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch1_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch2_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch3_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch4_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch5_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch6_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch7_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch8_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch9_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch10_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch11_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch12_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch13_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch14_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch15_sig'] = 'group_count'
weewx.units.obs_group_dict['wn34_ch16_sig'] = 'group_count'
weewx.units.obs_group_dict['wn35_ch1_sig'] = 'group_count'
weewx.units.obs_group_dict['wn35_ch2_sig'] = 'group_count'
weewx.units.obs_group_dict['wn35_ch3_sig'] = 'group_count'
weewx.units.obs_group_dict['wn35_ch4_sig'] = 'group_count'
weewx.units.obs_group_dict['wn35_ch5_sig'] = 'group_count'
weewx.units.obs_group_dict['wn35_ch6_sig'] = 'group_count'
weewx.units.obs_group_dict['wn35_ch7_sig'] = 'group_count'
weewx.units.obs_group_dict['wn35_ch8_sig'] = 'group_count'
weewx.units.obs_group_dict['wh40_sig'] = 'group_count'
weewx.units.obs_group_dict['wh41_ch1_sig'] = 'group_count'
weewx.units.obs_group_dict['wh41_ch2_sig'] = 'group_count'
weewx.units.obs_group_dict['wh41_ch3_sig'] = 'group_count'
weewx.units.obs_group_dict['wh41_ch4_sig'] = 'group_count'
weewx.units.obs_group_dict['wh45_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch1_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch2_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch3_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch4_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch5_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch6_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch7_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch8_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch9_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch10_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch11_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch12_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch13_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch14_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch15_sig'] = 'group_count'
weewx.units.obs_group_dict['wh51_ch16_sig'] = 'group_count'

weewx.units.obs_group_dict['wh54_ch1_sig'] = 'group_count'
weewx.units.obs_group_dict['wh54_ch2_sig'] = 'group_count'
weewx.units.obs_group_dict['wh54_ch3_sig'] = 'group_count'
weewx.units.obs_group_dict['wh54_ch4_sig'] = 'group_count'

weewx.units.obs_group_dict['wh55_ch1_sig'] = 'group_count'
weewx.units.obs_group_dict['wh55_ch2_sig'] = 'group_count'
weewx.units.obs_group_dict['wh55_ch3_sig'] = 'group_count'
weewx.units.obs_group_dict['wh55_ch4_sig'] = 'group_count'
weewx.units.obs_group_dict['wh57_sig'] = 'group_count'
weewx.units.obs_group_dict['wh65_sig'] = 'group_count'
weewx.units.obs_group_dict['wh68_sig'] = 'group_count'
weewx.units.obs_group_dict['wh69_sig'] = 'group_count'
weewx.units.obs_group_dict['ws80_sig'] = 'group_count'
weewx.units.obs_group_dict['ws90_sig'] = 'group_count'
weewx.units.obs_group_dict['ws85_sig'] = 'group_percent'
weewx.units.obs_group_dict['wh85_sig'] = 'group_count'
"""

weewx.units.obs_group_dict['ldsbatt1'] = 'group_volt'
weewx.units.obs_group_dict['ldsbatt2'] = 'group_volt'
weewx.units.obs_group_dict['ldsbatt3'] = 'group_volt'
weewx.units.obs_group_dict['ldsbatt4'] = 'group_volt'
weewx.units.obs_group_dict['ldsheat_ch1'] = 'group_count'
weewx.units.obs_group_dict['ldsheat_ch2'] = 'group_count'
weewx.units.obs_group_dict['ldsheat_ch3'] = 'group_count'
weewx.units.obs_group_dict['ldsheat_ch4'] = 'group_count'

weewx.units.obs_group_dict['srain_piezo'] = 'group_count'

weewx.units.obs_group_dict['heap'] = 'group_data'


weewx.units.obs_group_dict['fdewptf'] = 'group_temperature'
weewx.units.obs_group_dict['fwindchillf'] = 'group_temperature'
weewx.units.obs_group_dict['ffeelslikef'] = 'group_temperature'
weewx.units.obs_group_dict['fheatindexf'] = 'group_temperature'
weewx.units.obs_group_dict['fwindspdmph_avg10m'] = 'group_speed2'
weewx.units.obs_group_dict['fwinddir_avg10m'] = 'group_direction'
weewx.units.obs_group_dict['fwindgustmph_max10m'] = 'group_speed2'
weewx.units.obs_group_dict['fwindrun'] = 'group_distance'
weewx.units.obs_group_dict['fpm25_AQI_ch1'] = 'group_count'
weewx.units.obs_group_dict['fpm25_AQI_ch2'] = 'group_count'
weewx.units.obs_group_dict['fpm25_AQI_ch3'] = 'group_count'
weewx.units.obs_group_dict['fpm25_AQI_ch4'] = 'group_count'
weewx.units.obs_group_dict['fpm25_AQI_co2'] = 'group_count'
weewx.units.obs_group_dict['fpm10_AQI_co2'] = 'group_count'
weewx.units.obs_group_dict['fpm25_AQI_avg_24h_ch1'] = 'group_count'
weewx.units.obs_group_dict['fpm25_AQI_avg_24h_ch2'] = 'group_count'
weewx.units.obs_group_dict['fpm25_AQI_avg_24h_ch3'] = 'group_count'
weewx.units.obs_group_dict['fpm25_AQI_avg_24h_ch4'] = 'group_count'
weewx.units.obs_group_dict['fpm25_AQI_24h_co2'] = 'group_count'
weewx.units.obs_group_dict['fpm10_AQI_24h_co2'] = 'group_count'
weewx.units.obs_group_dict['fsunshine'] = 'group_count'

weewx.units.obs_group_dict['radcompensation'] = 'group_count'
weewx.units.obs_group_dict['upgrade'] = 'group_count'
weewx.units.obs_group_dict['newVersion'] = 'group_count'
weewx.units.obs_group_dict['rainFallPriority'] = 'group_count'
weewx.units.obs_group_dict['rainGain'] = 'group_count'
weewx.units.obs_group_dict['piezo'] = 'group_count'
weewx.units.obs_group_dict['rain1_gain'] = 'group_count'
weewx.units.obs_group_dict['rain2_gain'] = 'group_count'
weewx.units.obs_group_dict['rain3_gain'] = 'group_count'
weewx.units.obs_group_dict['rain4_gain'] = 'group_count'
weewx.units.obs_group_dict['rain5_gain'] = 'group_count'

weewx.units.USUnits["group_sunhours"] = "sunhours"
weewx.units.MetricUnits["group_sunhours"] = "sunhours"
weewx.units.MetricWXUnits["group_sunhours"] = "sunhours"
weewx.units.default_unit_format_dict["sunhours"] = "%.2f"
weewx.units.default_unit_label_dict["sunhours"] = " h"
weewx.units.obs_group_dict['fsunhours'] = 'group_sunhours'

weewx.units.default_unit_format_dict["microgram_per_meter_cubed"] = "%.1f"
weewx.units.default_unit_format_dict["volt"] = "%.2f"

weewx.units.obs_group_dict['thi_ch1'] = 'group_lengthmm'
weewx.units.obs_group_dict['thi_ch2'] = 'group_lengthmm'
weewx.units.obs_group_dict['thi_ch3'] = 'group_lengthmm'
weewx.units.obs_group_dict['thi_ch4'] = 'group_lengthmm'
weewx.units.obs_group_dict['depth_ch1'] = 'group_lengthmm'
weewx.units.obs_group_dict['depth_ch2'] = 'group_lengthmm'
weewx.units.obs_group_dict['depth_ch3'] = 'group_lengthmm'
weewx.units.obs_group_dict['depth_ch4'] = 'group_lengthmm'
weewx.units.obs_group_dict['air_ch1'] = 'group_lengthmm'
weewx.units.obs_group_dict['air_ch2'] = 'group_lengthmm'
weewx.units.obs_group_dict['air_ch3'] = 'group_lengthmm'
weewx.units.obs_group_dict['air_ch4'] = 'group_lengthmm'

weewx.units.USUnits["group_lengthmm"] = "mm"
weewx.units.MetricUnits["group_lengthmm"] = "mm"
weewx.units.MetricWXUnits["group_lengthmm"] = "mm"
weewx.units.default_unit_label_dict["thi_ch1"] = "mm"
weewx.units.default_unit_label_dict["thi_ch2"] = "mm"
weewx.units.default_unit_label_dict["thi_ch3"] = "mm"
weewx.units.default_unit_label_dict["thi_ch4"] = "mm"
weewx.units.default_unit_label_dict["depth_ch1"] = "mm"
weewx.units.default_unit_label_dict["depth_ch2"] = "mm"
weewx.units.default_unit_label_dict["depth_ch3"] = "mm"
weewx.units.default_unit_label_dict["depth_ch4"] = "mm"
weewx.units.default_unit_label_dict["air_ch1"] = "mm"
weewx.units.default_unit_label_dict["air_ch2"] = "mm"
weewx.units.default_unit_label_dict["air_ch3"] = "mm"
weewx.units.default_unit_label_dict["air_ch4"] = "mm"


"""
weewx.units.USUnits["group_lengthmm"] = "lmm"
weewx.units.MetricUnits["group_lengthmm"] = "lmm"
weewx.units.MetricWXUnits["group_lengthmm"] = "lmm"
weewx.units.default_unit_label_dict["lmm"] = "mm"
weewx.units.default_unit_format_dict["lmm"] = "%.0f"
"""

weewx.units.obs_group_dict['vpd'] = 'group_pressurevpd'
weewx.units.USUnits["group_pressurevpd"] = "inHg"
weewx.units.MetricUnits["group_pressurevpd"] = "kPa"
weewx.units.MetricWXUnits["group_pressurevpd"] = "kPa"


def loader(config_dict, _):
    return EcowittcustomDriver(**config_dict[DRIVER_NAME])

def confeditor_loader():
    return EcowittcustomConfigurationEditor()


def _to_bytes(data):
    if sys.version_info < (3, 0):
        return bytes(data)
    return bytes(data, 'utf8')

def _bytes_to_str(data):
    if sys.version_info < (3, 0):
        return data
    return str(data, 'utf-8')

def _obfuscate_passwords(msg):
    return re.sub(r'(PASSWORD|PASSKEY)=[^&]+', r'\1=XXXX', msg)

def _fmt_bytes(data):
    if not data:
        return ''
    return ' '.join(['%02x' % ord(x) for x in data])

def _cgi_to_dict(s):
    if '=' in s:
        return dict([y.strip() for y in x.split('=')] for x in s.split('&'))
    return dict()


class Consumer(object):
    """The Consumer contains two primary parts - a Server and a Parser.  The
    Server can be a sniff server or a TCP server.  Either type of server
    is a data sink.  When it receives data, it places a string on a queue.
    The driver then pops items of the queue and hands them over to the parser.
    The Parser processes each string and spits out a dictionary that contains
    the parsed data.

    The handler is only used by the TCP server.  It provides the response to
    the client requests.

    Sniffing is not available for every type of hardware.
    """

    queue = Queue.Queue()

    # the default sensor map associates database field names with generic
    # observation names.  each derived parser should map observation names
    # to these generic names, or define a new default sensor map that is
    # appropriate for the observation names from the derived output.
    #
    # the default mapping is for the wview schema plus a few extensions.

    DEFAULT_SENSOR_MAP = {
        #to weewx : from station
        'pressure': 'pressure',
        'barometer': 'barometer',
        'outHumidity': 'humidity_out',
        'inHumidity': 'humidity_in',
        'outTemp': 'temperature_out',
        'inTemp': 'temperature_in',
        'windSpeed': 'wind_speed',
        'windGust': 'wind_gust',
        'windDir': 'wind_dir',
        'windGustDir': 'wind_gust_dir',
        'radiation': 'solar_radiation',
        'dewpoint': 'dewpoint',
        'windchill': 'windchill',
        'rain': 'rain',
        'rainRate': 'rain_rate',
        'UV': 'uv',
        'txBatteryStatus': 'battery',
        'extraTemp1': 'temperature_1',
        'extraTemp2': 'temperature_2',
        'extraTemp3': 'temperature_3',
        'extraTemp4': 'temperature_4',
        'extraTemp5': 'temperature_5',
        'extraTemp6': 'temperature_6',
        'extraTemp7': 'temperature_7',
        'extraTemp8': 'temperature_8',
        'extraHumid1': 'humidity_1',
        'extraHumid2': 'humidity_2',
        'extraHumid3': 'humidity_3',
        'extraHumid4': 'humidity_4',
        'extraHumid5': 'humidity_5',
        'extraHumid6': 'humidity_6',
        'extraHumid7': 'humidity_7',
        'extraHumid8': 'humidity_8',
        #'soilTemp1': 'soil_temperature_1',
        #'soilTemp2': 'soil_temperature_2',
        #'soilTemp3': 'soil_temperature_3',
        #'soilTemp4': 'soil_temperature_4',
        'soilTemp1': 'tf_ch1',
        'soilTemp2': 'tf_ch2',
        'soilTemp3': 'tf_ch3',
        'soilTemp4': 'tf_ch4',
        'soilTemp5': 'tf_ch5',
        'soilTemp6': 'tf_ch6',
        'soilTemp7': 'tf_ch7',
        'soilTemp8': 'tf_ch8',
        'soilMoist1': 'soil_moisture_1',
        'soilMoist2': 'soil_moisture_2',
        'soilMoist3': 'soil_moisture_3',
        'soilMoist4': 'soil_moisture_4',
        'soilMoist5': 'soil_moisture_5',
        'soilMoist6': 'soil_moisture_6',
        'soilMoist7': 'soil_moisture_7',
        'soilMoist8': 'soil_moisture_8',
        'soilMoist9': 'soil_moisture_9',
        'soilMoist10': 'soil_moisture_10',
        'soilMoist11': 'soil_moisture_11',
        'soilMoist12': 'soil_moisture_12',
        'soilMoist13': 'soil_moisture_13',
        'soilMoist14': 'soil_moisture_14',
        'soilMoist15': 'soil_moisture_15',
        'soilMoist16': 'soil_moisture_16',
        #these are ecowitt client schema
        'co2': 'co2',
        'co2_24h': 'co2_24h',
        'co2in': 'co2in',
        'co2in_24h': 'co2in_24h',
        'co2_Temp': 'tf_co2',
        'co2_Hum': 'humi_co2',
        'co2_Batt': 'co2_batt',
        'pm1_0': 'pm1_co2',
        'pm4_0': 'pm4_co2',
        'pm10_0': 'pm10_co2',
        'pm2_5': 'pm25_co2',
        'pm25_1': 'pm25_ch1',
        'pm25_2': 'pm25_ch2',
        'pm25_3': 'pm25_ch3',
        'pm25_4': 'pm25_ch4',
        'pm25_Batt1': 'pm25batt1',
        'pm25_Batt2': 'pm25batt2',
        'pm25_Batt3': 'pm25batt3',
        'pm25_Batt4': 'pm25batt4',
        'batteryStatus1': 'battery_1',
        'batteryStatus2': 'battery_2',
        'batteryStatus3': 'battery_3',
        'batteryStatus4': 'battery_4',
        'batteryStatus5': 'battery_5',
        'batteryStatus6': 'battery_6',
        'batteryStatus7': 'battery_7',
        'batteryStatus8': 'battery_8',
        'soilMoistBatt1': 'soilbatt1',
        'soilMoistBatt2': 'soilbatt2',
        'soilMoistBatt3': 'soilbatt3',
        'soilMoistBatt4': 'soilbatt4',
        'soilMoistBatt5': 'soilbatt5',
        'soilMoistBatt6': 'soilbatt6',
        'soilMoistBatt7': 'soilbatt7',
        'soilMoistBatt8': 'soilbatt8',
        'soilMoistBatt9': 'soilbatt9',
        'soilMoistBatt10': 'soilbatt10',
        'soilMoistBatt11': 'soilbatt11',
        'soilMoistBatt12': 'soilbatt12',
        'soilMoistBatt13': 'soilbatt13',
        'soilMoistBatt14': 'soilbatt14',
        'soilMoistBatt15': 'soilbatt15',
        'soilMoistBatt16': 'soilbatt16',
        'soilTempBatt1': 'tf_batt1',
        'soilTempBatt2': 'tf_batt2',
        'soilTempBatt3': 'tf_batt3',
        'soilTempBatt4': 'tf_batt4',
        'soilTempBatt5': 'tf_batt5',
        'soilTempBatt6': 'tf_batt6',
        'soilTempBatt7': 'tf_batt7',
        'soilTempBatt8': 'tf_batt8',
        'soilTempBatt9': 'tf_batt9',
        'soilTempBatt10': 'tf_batt10',
        'soilTempBatt11': 'tf_batt11',
        'soilTempBatt12': 'tf_batt12',
        'soilTempBatt13': 'tf_batt13',
        'soilTempBatt14': 'tf_batt14',
        'soilTempBatt15': 'tf_batt15',
        'soilTempBatt16': 'tf_batt16',
        'leafWet1': 'leafwetness_ch1',
        'leafWet2': 'leafwetness_ch2',
        'leafWet3': 'leafwetness_ch3',
        'leafWet4': 'leafwetness_ch4',
        'leafWet5': 'leafwetness_ch5',
        'leafWet6': 'leafwetness_ch6',
        'leafWet7': 'leafwetness_ch7',
        'leafWet8': 'leafwetness_ch8',
        'leafWetBatt1': 'leaf_batt1',
        'leafWetBatt2': 'leaf_batt2',
        'leafWetBatt3': 'leaf_batt3',
        'leafWetBatt4': 'leaf_batt4',
        'leafWetBatt5': 'leaf_batt5',
        'leafWetBatt6': 'leaf_batt6',
        'leafWetBatt7': 'leaf_batt7',
        'leafWetBatt8': 'leaf_batt8',
        'leak_1': 'leak_ch1',
        'leak_2': 'leak_ch2',
        'leak_3': 'leak_ch3',
        'leak_4': 'leak_ch4',
        'leak_Batt1': 'leakbatt1',
        'leak_Batt2': 'leakbatt2',
        'leak_Batt3': 'leakbatt3',
        'leak_Batt4': 'leakbatt4',
        'lightning_distance': 'lightning',
        'lightning_disturber_count': 'lightning_time',
        'lightning_num': 'lightning_num',
        'lightning_strike_count': 'lightning_strike_count',
        'lightning_Batt': 'wh57batt',
        'maxdailygust': 'maxdailygust',
        'winddir_avg10m': 'winddir_avg10m',
        'windspdmph_avg10m': 'windspdmph_avg10m',
        'pm1_24h_co2': 'pm1_24h_co2',
        'pm4_24h_co2': 'pm4_24h_co2',
        'pm25_24h_co2': 'pm25_24h_co2',
        'pm10_24h_co2': 'pm10_24h_co2',
        'pm25_avg_24h_ch1': 'pm25_avg_24h_ch1',
        'pm25_avg_24h_ch2': 'pm25_avg_24h_ch2',
        'pm25_avg_24h_ch3': 'pm25_avg_24h_ch3',
        'pm25_avg_24h_ch4': 'pm25_avg_24h_ch4',
        'consBatteryVoltage': 'console_batt',
        'rainBatteryStatus': 'wh40batt',
        'hailBatteryStatus': 'wh90batt',
        'windBatteryStatus': 'wh80batt',
        'ws90_batt': 'wh90batt',
        'ws80_batt': 'wh80batt',
        'ws85_batt': 'wh85batt',
        'wh24_batt': 'wh24batt',
        'wh25_batt': 'wh25batt',
        'wh26_batt': 'wh26batt',
        'wh65_batt': 'wh65batt',
        'wh68_batt': 'wh68batt',
        'wh69_batt': 'wh69batt',
        'outTempBatteryStatus': 'wh65batt',
        'inTempBatteryStatus': 'wh25batt',
        'rainrate': 'rainratein',
        'totalRain': 'rain_total',
        'eventRain': 'rainevent',
        'hourRain': 'hourlyrainin',
        'dayRain': 'dailyrainin',
        'weekRain': 'weeklyrainin',
        'monthRain': 'monthlyrainin',
        'yearRain': 'rainyear',
        'p_rain': 'rain_piezo',
        'p_rainrate': 'rrain_piezo',
        'hail': 'rain_piezo',
        'hailRate': 'rrain_piezo',
        #'rain_piezo': 'rain_piezo',
        #'rrain_piezo': 'rrain_piezo',
        'erain_piezo': 'erain_piezo',
        'hrain_piezo': 'hrain_piezo',
        'drain_piezo': 'drain_piezo',
        'wrain_piezo': 'wrain_piezo',
        'mrain_piezo': 'mrain_piezo',
        'yrain_piezo': 'yrain_piezo',
        'srain_piezo': 'srain_piezo',
        'ws90cap_volt': 'ws90cap_volt',
        'ws85cap_volt': 'ws85cap_volt',
        'ws90_ver': 'ws90_ver',
        'ws85_ver': 'ws85_ver',
        'runtime': 'runtime',
        'ws_interval': 'interval',
        'model': 'model',
        'stationtype': 'stationtype',
        'gain0': 'gain0',
        'gain1': 'gain1',
        'gain2': 'gain2',
        'gain3': 'gain3',
        'gain4': 'gain4',
        'gain5': 'gain5',
        'gain6': 'gain6',
        'gain7': 'gain7',
        'gain8': 'gain8',
        'gain9': 'gain9',
        'soilad1': 'soilad1',
        'soilad2': 'soilad2',
        'soilad3': 'soilad3',
        'soilad4': 'soilad4',
        'soilad5': 'soilad5',
        'soilad6': 'soilad6',
        'soilad7': 'soilad7',
        'soilad8': 'soilad8',
        'soilad9': 'soilad9',
        'soilad10': 'soilad10',
        'soilad11': 'soilad11',
        'soilad12': 'soilad12',
        'soilad13': 'soilad13',
        'soilad14': 'soilad14',
        'soilad15': 'soilad15',
        'soilad16': 'soilad16',
        'heap': 'heap',
        'wh24_sig': 'wh24sig',
        'wh25_sig': 'wh25sig',
        'wh26_sig': 'wh26sig',
        'wh31_ch1_sig': 'wh31sig1',
        'wh31_ch2_sig': 'wh31sig2',
        'wh31_ch3_sig': 'wh31sig3',
        'wh31_ch4_sig': 'wh31sig4',
        'wh31_ch5_sig': 'wh31sig5',
        'wh31_ch6_sig': 'wh31sig6',
        'wh31_ch7_sig': 'wh31sig7',
        'wh31_ch8_sig': 'wh31sig8',
        'wn34_ch1_sig': 'wh34sig1',
        'wn34_ch2_sig': 'wh34sig2',
        'wn34_ch3_sig': 'wh34sig3',
        'wn34_ch4_sig': 'wh34sig4',
        'wn34_ch5_sig': 'wh34sig5',
        'wn34_ch6_sig': 'wh34sig6',
        'wn34_ch7_sig': 'wh34sig7',
        'wn34_ch8_sig': 'wh34sig8',
        'wn34_ch9_sig': 'wh34sig9',
        'wn34_ch10_sig': 'wh34sig10',
        'wn34_ch11_sig': 'wh34sig11',
        'wn34_ch12_sig': 'wh34sig12',
        'wn34_ch13_sig': 'wh34sig13',
        'wn34_ch14_sig': 'wh34sig14',
        'wn34_ch15_sig': 'wh34sig15',
        'wn34_ch16_sig': 'wh34sig16',
        'wn35_ch1_sig': 'wh35sig1',
        'wn35_ch2_sig': 'wh35sig2',
        'wn35_ch3_sig': 'wh35sig3',
        'wn35_ch4_sig': 'wh35sig4',
        'wn35_ch5_sig': 'wh35sig5',
        'wn35_ch6_sig': 'wh35sig6',
        'wn35_ch7_sig': 'wh35sig7',
        'wn35_ch8_sig': 'wh35sig8',
        'wh40_sig': 'wh40sig',
        'wh41_ch1_sig': 'wh41sig1',
        'wh41_ch2_sig': 'wh41sig2',
        'wh41_ch3_sig': 'wh41sig3',
        'wh41_ch4_sig': 'wh41sig4',
        'wh45_sig': 'wh45sig',
        'wh51_ch1_sig': 'wh51sig1',
        'wh51_ch2_sig': 'wh51sig2',
        'wh51_ch3_sig': 'wh51sig3',
        'wh51_ch4_sig': 'wh51sig4',
        'wh51_ch5_sig': 'wh51sig5',
        'wh51_ch6_sig': 'wh51sig6',
        'wh51_ch7_sig': 'wh51sig7',
        'wh51_ch8_sig': 'wh51sig8',
        'wh51_ch9_sig': 'wh51sig9',
        'wh51_ch10_sig': 'wh51sig10',
        'wh51_ch11_sig': 'wh51sig11',
        'wh51_ch12_sig': 'wh51sig12',
        'wh51_ch13_sig': 'wh51sig13',
        'wh51_ch14_sig': 'wh51sig14',
        'wh51_ch15_sig': 'wh51sig15',
        'wh51_ch16_sig': 'wh51sig16',
        'wh55_ch1_sig': 'wh55sig1',
        'wh55_ch2_sig': 'wh55sig2',
        'wh55_ch3_sig': 'wh55sig3',
        'wh55_ch4_sig': 'wh55sig4',
        'wh57_sig': 'wh57sig',
        'wh65_sig': 'wh65sig',
        'wh68_sig': 'wh68sig',
        'wh69_sig': 'wh69sig',
        'ws80_sig': 'wh80sig',
        'ws90_sig': 'wh90sig',
        'ws85_sig': 'wh85sig',
        'wh54_ch1_sig': 'wh54sig1',
        'wh54_ch2_sig': 'wh54sig2',
        'wh54_ch3_sig': 'wh54sig3',
        'wh54_ch4_sig': 'wh54sig4',
        'thi_ch1': 'thi_ch1',
        'thi_ch2': 'thi_ch2',
        'thi_ch3': 'thi_ch3',
        'thi_ch4': 'thi_ch4',
        'depth_ch1': 'depth_ch1',
        'depth_ch2': 'depth_ch2',
        'depth_ch3': 'depth_ch3',
        'depth_ch4': 'depth_ch4',
        'air_ch1': 'air_ch1',
        'air_ch2': 'air_ch2',
        'air_ch3': 'air_ch3',
        'air_ch4': 'air_ch4',
        'ldsbatt1': 'ldsbatt1',
        'ldsbatt2': 'ldsbatt2',
        'ldsbatt3': 'ldsbatt3',
        'ldsbatt4': 'ldsbatt4',
        'ldsheat_ch1': 'ldsheat_ch1',
        'ldsheat_ch2': 'ldsheat_ch2',
        'ldsheat_ch3': 'ldsheat_ch3',
        'ldsheat_ch4': 'ldsheat_ch4',
        'noise_ch1': 'noise_ch1',
        'noise_ch2': 'noise_ch2',
        'noise_ch3': 'noise_ch3',
        'noise_ch4': 'noise_ch4',
        'peak_ch1': 'peak_ch1',
        'peak_ch2': 'peak_ch2',
        'peak_ch3': 'peak_ch3',
        'peak_ch4': 'peak_ch4',
        'ldspw_ch1': 'ldspw_ch1',
        'ldspw_ch2': 'ldspw_ch2',
        'ldspw_ch3': 'ldspw_ch3',
        'ldspw_ch4': 'ldspw_ch4',
        'vpd': 'vpd',
        'fdewptf': 'dewptf',
        'fwindchillf': 'windchillf',
        'ffeelslikef': 'feelslikef',
        'fheatindexf': 'heatindexf',
        'fwindspdmph_avg10m': 'windspdmph_avg10m',
        'fwinddir_avg10m': 'winddir_avg10m',
        'fwindgustmph_max10m': 'windgustmph_max10m',
        'fwindrun': 'windrun',
        'fpm25_AQI_ch1': 'pm25_AQI_ch1',
        'fpm25_AQI_ch2': 'pm25_AQI_ch2',
        'fpm25_AQI_ch3': 'pm25_AQI_ch3',
        'fpm25_AQI_ch4': 'pm25_AQI_ch4',
        'fpm25_AQI_co2': 'pm25_AQI_co2',
        'fpm10_AQI_co2': 'pm10_AQI_co2',
        'fpm25_AQI_avg_24h_ch1': 'pm25_AQI_avg_24h_ch1',
        'fpm25_AQI_avg_24h_ch2': 'pm25_AQI_avg_24h_ch2',
        'fpm25_AQI_avg_24h_ch3': 'pm25_AQI_avg_24h_ch3',
        'fpm25_AQI_avg_24h_ch4': 'pm25_AQI_avg_24h_ch4',
        'fpm25_AQI_24h_co2': 'pm25_AQI_24h_co2',
        'fpm10_AQI_24h_co2': 'pm10_AQI_24h_co2',
        'fsunhours': 'sunhours',
        'fsunshine': 'sunshine',
        'radcompensation': 'radcompensation',
        'newVersion': 'newVersion',
        'upgrade': 'upgrade',
        'rain_source': 'rainFallPriority',
        'rain_day_reset': 'rstRainDay',
        'rain_week_reset': 'rstRainWeek',
        'rain_annual_reset': 'rstRainYear',
        'raingain': 'rainGain',
        'piezo': 'piezo',
        'gain0': 'rain1_gain',
        'gain1': 'rain2_gain',
        'gain2': 'rain3_gain',
        'gain3': 'rain4_gain',
        'gain4': 'rain5_gain',
    }

    def default_sensor_map(self):
        return Consumer.DEFAULT_SENSOR_MAP

    def __init__(self, parser, mode='listen',
                 address=DEFAULT_ADDR, port=DEFAULT_PORT, handler=None,
                 iface=DEFAULT_IFACE, pcap_filter=DEFAULT_FILTER,
                 promiscuous=0):
        self.parser = parser
        loginf("mode is %s" % mode)
        if mode == 'sniff':
            self._server = Consumer.SniffServer(
                iface, pcap_filter, promiscuous)
        elif mode == 'listen':
            self._server = Consumer.TCPServer(address, port, handler)
        else:
            raise TypeError("unrecognized mode '%s'" % mode)

    def run_server(self):
        self._server.run()

    def stop_server(self):
        self._server.stop()
        self._server = None

    def get_queue(self):
        return Consumer.queue

    class Server(object):
        def run(self):
            pass
        def stop(self):
            pass

    class SniffServer(Server):
        """
        Abstraction to deal with the two different python pcap implementations,
        pylibpcap and pypcap.
        """
        def __init__(self, iface, pcap_filter, promiscuous):
            self.running = False
            self.data_buffer = ''
            self.sniffer_type = None
            self.sniffer_version = 'unknown'
            self.sniffer = None
            snaplen = 1600
            timeout_ms = 100
            pval = 1 if weeutil.weeutil.to_bool(promiscuous) else 0
            loginf("sniff iface=%s promiscuous=%s" % (iface, pval))
            loginf("sniff filter '%s'" % pcap_filter)
            import pcap
            try:
                # try pylibpcap
                self.sniffer = pcap.pcapObject()
                self.sniffer.open_live(iface, snaplen, pval, timeout_ms)
                self.sniffer.setfilter(pcap_filter, 0, 0)
                self.sniffer_type = 'pylibpcap'
            except AttributeError:
                # try pypcap
                self.sniffer = pcap.pcap(iface, snaplen, pval)
                self.sniffer.setfilter(pcap_filter)
                self.sniffer_type = 'pypcap'
                self.sniffer_version = pcap.__version__.lower()
            loginf("%s (%s)" % (self.sniffer_type, self.sniffer_version))

        def run(self):
            logdbg("start sniff server")
            self.running = True
            if self.sniffer_type == 'pylibpcap':
                while self.running:
                    self.sniffer.dispatch(1, self.decode_ip_packet)
            elif self.sniffer_type == 'pypcap':
                for ts, pkt in self.sniffer:
                    if not self.running:
                        break
                    self.decode_ip_packet(0, pkt, ts)

        def stop(self):
            logdbg("stop sniff server")
            self.running = False
            if self.sniffer_type == 'pylibpcap':
                self.sniffer.close()
            self.packet_sniffer = None

        def decode_ip_packet(self, _pktlen, data, _timestamp):
            # i would like to queue up each packet so we do not have to
            # maintain state.  unfortunately, sometimes we get data spread
            # across multiple packets, so we have to reassemble them.
            #
             #
            # examples:
            # POST /update HTTP/1.0\r\nHost: gateway.oregonscientific.com\r\n
            # mac=0004a36903fe&id=84&rid=f3&pwr=0&htr=0&cz=1&oh=41&...
            # GET /weatherstation/updateweatherstation?dateutc=now&rssi=2&...
            # &sensor=00003301&windspeedmph=5&winddir=113&rainin=0.00&...
            if not data:
                return
            logdbg("sniff: timestamp=%s pktlen=%s data=%s" %
                   (_timestamp, _pktlen, _fmt_bytes(data)))
            # FIXME: generalize the packet type detection
            header_len = 0
            idx = 0
            if len(data) >= 15 and data[12:14] == '\x08\x00':
                # this is standard IP packet
                header_len = ord(data[14]) & 0x0f
                idx = 4 * header_len + 34
            elif (len(data) >= 70 and
                data[12:14] == '\x81\x00' and data[16:18] == '\x08\x00'):
                # this is 802.1Q tagged IP packet
                header_len = ord(data[18]) & 0x0f
                idx = 4 * header_len + 38
            if idx and len(data) >= idx:
                _data = data[idx:]
                if 'GET' in _data:
                    self.flush()
                    logdbg("sniff: start GET")
                    self.data_buffer = _data
                elif 'POST' in _data:
                    self.flush()
                    logdbg("sniff: start POST")
                    self.data_buffer = 'POST?' # start buffer with dummy
                elif len(self.data_buffer):
                    if 'HTTP' in data:
                        # looks like the end of a multi-packet GET
                        self.flush()
                    else:
                        printable = set(string.printable)
                        fdata = filter(lambda x: x in printable, _data)
                        if fdata == _data:
                            logdbg("sniff: append %s" % _fmt_bytes(_data))
                            self.data_buffer += _data
                        else:
                            logdbg("sniff: skip %s" % _fmt_bytes(_data))
                else:
                    logdbg("sniff: ignore %s" % _fmt_bytes(_data))
            else:
                logdbg("sniff: unrecognized packet header")

        def flush(self):
            logdbg("sniff: flush %s" % _fmt_bytes(self.data_buffer))
            if not self.data_buffer:
                return
            data = self.data_buffer
            # if this is a query string, parse it
            if '?' in data:
                data = urlparse.urlparse(data).query
            # trim any dangling HTTP/x.x and connection info
            idx = data.find(' HTTP')
            if idx >= 0:
                data = data[:idx]
            if len(data):
                logdbg("SNIFF: %s" % _obfuscate_passwords(data))
                Consumer.queue.put(data)
            # clear the data buffer
            self.data_buffer = ''


    class TCPServer(Server, TCPServer):
        daemon_threads = True
        allow_reuse_address = True

        def __init__(self, address, port, handler):
            if handler is None:
                handler = Consumer.Handler
            loginf("listen on %s:%s" % (address, port))
            TCPServer.__init__(self, (address, int(port)), handler)

        def run(self):
            logdbg("start tcp server")
            self.serve_forever()

        def stop(self):
            logdbg("stop tcp server")
            self.shutdown()
            self.server_close()

    class Handler(BaseHTTPRequestHandler):

        def get_response(self):
            # default reply is a simple 'OK' string
            return 'OK'

        def reply(self):
            # standard reply is HTTP code of 200 and the response string
            response = _to_bytes(self.get_response())
            self.send_response(200)
            self.send_header("Content-Length", str(len(response)))
            self.end_headers()
            self.wfile.write(response)            

        def do_POST(self):
            # get the payload from an HTTP POST
            length = int(self.headers["Content-Length"])
            #data = str(self.rfile.read(length))
            data = self.rfile.read(length).decode('utf-8')
            logdbg('POST: %s' % _obfuscate_passwords(data))
            Consumer.queue.put(data)
            self.reply()

        def do_PUT(self):
            pass

        def do_GET(self):
            # get the query string from an HTTP GET
            data = urlparse.urlparse(self.path).query
            logdbg('GET: %s' % _obfuscate_passwords(data))
            Consumer.queue.put(data)
            self.reply()

        # do not spew messages on every connection
        def log_message(self, _format, *_args):
            pass

    class Parser(object):

        def parse(self, s):
            return dict()

        @staticmethod
        def parse_identifiers(s):
            return dict()

        @staticmethod
        def map_to_fields(pkt, sensor_map):
            # the sensor map is a dictionary of database field names as keys,
            # each with an associated observation identifier.
            if sensor_map is None:
                return pkt
            packet = dict()
            if 'dateTime' in pkt:
                packet['dateTime'] = pkt['dateTime']
            if 'usUnits' in pkt:
                packet['usUnits'] = pkt['usUnits']
            for n in sensor_map:
                label = Consumer.Parser._find_match(sensor_map[n], pkt.keys())
                if label:
                    packet[n] = pkt.get(label)
            return packet

        @staticmethod
        def _find_match(pattern, keylist):
            # pattern can be a simple label, or an identifier pattern.
            # keylist is an array of observations, each of which is either
            # a simple label, or an identifier tuple.
            match = None
            pparts = pattern.split('.')
            if len(pparts) == 3:
                for k in keylist:
                    kparts = k.split('.')
                    if (len(kparts) == 3 and
                        Consumer.Parser._part_match(pparts[0], kparts[0]) and
                        Consumer.Parser._part_match(pparts[1], kparts[1]) and
                        Consumer.Parser._part_match(pparts[2], kparts[2])):
                        match = k
                    elif pparts[0] == k:
                        match = k
            else:
                for k in keylist:
                    if pattern == k:
                        match = k
            return match

        @staticmethod
        def _part_match(pattern, value):
            # use glob matching for parts of the tuple
            matches = fnmatch.filter([value], pattern)
            return True if matches else False

        @staticmethod
        def _delta_rain(rain, last_rain):
            if last_rain is None:
                #loginf("skipping rain measurement of %s: no last rain" % rain)
                loginf("skipping rain measurement of %sin/%.1fmm: no last rain" % (rain, rain*25.4))
                return None
            if rain < last_rain:
                loginf("rain counter wraparound detected: new=%sin/%.1fmm last=%sin/%.1fmm" %
                       (rain, rain*25.4, last_rain, last_rain*25.4))
                return rain
            return rain - last_rain

        @staticmethod
        def _delta_rain_piezo(rain_piezo, last_rain_piezo):
            if last_rain_piezo is None:
                #loginf("skipping rain_piezo measurement of %s: no last rain_piezo" % rain_piezo)
                loginf("skipping rain_piezo measurement of %sin/%.1fmm: no last rain_piezo" % (rain_piezo, rain_piezo*25.4))
                return None
            if rain_piezo < last_rain_piezo:
                loginf("rain_piezo counter wraparound detected: new=%sin/%.1fmm last=%sin/%.1fmm" %
                       (rain_piezo, rain_piezo*25.4, last_rain_piezo, last_rain_piezo*25.4))
                return rain_piezo
            return rain_piezo - last_rain_piezo

        @staticmethod
        #def _delta_lightning_num(lightning_num, last_lightning_num):
        def _delta_lightning_num(lightning_num, last_lightning_num, lightning_time, last_lightning_time):
            if last_lightning_num is None:
                loginf("skipping lightning_strike_count measurement of %s: no last lightning_strike_count" % last_lightning_num)
                return None
            if lightning_num < last_lightning_num:
                loginf("lightning_strike_count counter wraparound detected: new=%s last=%s" %
                       (lightning_num, last_lightning_num))
                return lightning_num
            if lightning_time != last_lightning_time:
                return lightning_num - last_lightning_num
            else:
                return 0


        @staticmethod
        def decode_float(x):
            return None if x is None else float(x)

        @staticmethod
        def decode_int(x):
            return None if x is None else int(x)

        @staticmethod
        def decode_datetime(s):
            if isinstance(s, int):
                return s
            if s == 'now':
                return int(time.time() + 0.5)
            s = s.replace("%20", " ")
            s = s.replace("%3A", ":")
            if '+' in s:
                # this is a fine offset (ambient, ecowitt) timestamp
                ts = time.strptime(s, "%Y-%m-%d+%H:%M:%S")
            else:
                # this is a weather underground timestamp
                ts = time.strptime(s, "%Y-%m-%d %H:%M:%S")
            return calendar.timegm(ts)


# capture data from hardware that sends using the weather underground protocol

class WUClient(Consumer):

    def __init__(self, **stn_dict):
        super(WUClient, self).__init__(
            WUClient.Parser(), handler=WUClient.Handler, **stn_dict)

    class Handler(Consumer.Handler):

        def get_response(self):
            return 'success'

    class Parser(Consumer.Parser):

        # map labels to observation names
        LABEL_MAP = {
            'winddir': 'wind_dir',
            'windspeedmph': 'wind_speed',
            'windgustmph': 'wind_gust',
            'windgustdir': 'wind_gust_dir',
            'humidity': 'humidity_out',
            'dewptf': 'dewpoint',
            'tempf': 'temperature_out',
            #'temp1f': 'temperature_0',
            'temp2f': 'temperature_1',
            'temp3f': 'temperature_2',
            'temp4f': 'temperature_3',
            'temp5f': 'temperature_4',
            'temp6f': 'temperature_5',
            'temp7f': 'temperature_6',
            'temp8f': 'temperature_7',
            'temp9f': 'temperature_8',
            #'humidity1': 'humidity_0',
            'humidity2': 'humidity_1',
            'humidity3': 'humidity_2',
            'humidity4': 'humidity_3',
            'humidity5': 'humidity_4',
            'humidity6': 'humidity_5',
            'humidity7': 'humidity_6',
            'humidity8': 'humidity_7',
            'humidity9': 'humidity_8',
            'baromin': 'barometer',
            'soiltempf': 'soil_temperature_1',
            'soiltemp2f': 'soil_temperature_2',
            'soiltemp3f': 'soil_temperature_3',
            'soiltemp4f': 'soil_temperature_4',
            'soiltemp5f': 'soil_temperature_5',
            'soiltemp6f': 'soil_temperature_6',
            'soiltemp7f': 'soil_temperature_7',
            'soiltemp8f': 'soil_temperature_8',
            'soilmoisture': 'soil_moisture_1',
            'soilmoisture2': 'soil_moisture_2',
            'soilmoisture3': 'soil_moisture_3',
            'soilmoisture4': 'soil_moisture_4',
            'soilmoisture5': 'soil_moisture_5',
            'soilmoisture6': 'soil_moisture_6',
            'soilmoisture7': 'soil_moisture_7',
            'soilmoisture8': 'soil_moisture_8',
            'leafwetness': 'leafwetness_ch1',
            'leafwetness2': 'leafwetness_ch2',
            'leafwetness3': 'leafwetness_ch3',
            'leafwetness4': 'leafwetness_ch4',
            'solarradiation': 'solar_radiation',
            'UV': 'uv',
            'visibility': 'visibility',
            'indoortempf': 'temperature_in',
            'indoorhumidity': 'humidity_in',
            'rainin': 'rainin',
            'dailyrainin': 'dailyrainin',
            'weeklyrainin': 'weeklyrainin',
            'monthlyrainin': 'monthlyrainin',
            'yearlyrainin': 'yearlyrainin',
            'softwaretype': 'stationtype',
            'rtfreq': 'rtfreq',
            'AqNO': 'no',
            'AqNO2T': 'no2T',
            'AqNO2': 'no2',
            'AqNO2Y': 'no2Y',
            'AqNOX': 'noX',
            'AqNOY': 'noY',
            'AqNO3': 'no3',
            'AqSO4': 'so4',
            'AqSO2': 'so',
            'AqSO2T': 'so2T',
            'AqCO': 'co',
            'AqCOT': 'coT',
            'AqEC': 'ec',
            'AqOC': 'oc',
            'AqBC': 'bc',
            'AqUV-AETH': 'uv_aeth',
            'AqPM2_5': 'pm2_5',
            'AqPM2.5': 'pm2_5',
            'AqPM10': 'pm10_0',
            'AqOZONE': 'ozone',
            # these have been observed, but apparently are unsupported?
            'windchillf': 'windchill',
            'lowbatt': 'battery',
        }

        IGNORED_LABELS = [
            'ID', 'PASSWORD', 'dateutc',
            'action', 'realtime',
            'weather', 'clouds',
            'windspdmph_avg2m', 'winddir_avg2m',
            'windgustmph_10m', 'windgustdir_10m',
        ]

        def __init__(self):
            self._last_rain = None
            self._stationtype = None

        def parse(self, s):
            pkt = dict()
            try:
                data = _cgi_to_dict(s)
                pkt['dateTime'] = self.decode_datetime(
                    data.pop('dateutc', int(time.time() + 0.5)))
                pkt['usUnits'] = weewx.US

                if 'softwaretype' in data:
                    pkt['stationtype'] = data['softwaretype']
                    if self._stationtype != data['softwaretype']:
                       self._stationtype = data['softwaretype']
                       loginf("Station_type: %s" % (data['softwaretype']))

                # different firmware seems to report rain in different ways.
                # prefer to get rain total from the yearly count, but if
                # that is not available, get it from the daily count.
                rain_total = None
                field = None
                if 'dailyrainin' in data:
                    rain_total = self.decode_float(data.pop('dailyrainin', None))
                    field = 'dailyrainin'
                    year_total = self.decode_float(data.pop('yearlyrainin', None))
                    if year_total is not None:
                        rain_total = year_total
                        field = 'yearlyrainin'
                elif 'dailyrain' in data:
                    rain_total = self.decode_float(data.pop('dailyrain', None))
                    field = 'dailyrain'
                    year_total = self.decode_float(data.pop('yearlyrain', None))
                    if year_total is not None:
                        rain_total = year_total
                        field = 'yearlyrain'
                if rain_total is not None:
                    pkt['rain_total'] = rain_total
                    logdbg("using rain_total %s from %s" % (rain_total, field))

                # get all of the other parameters
                for n in data:
                    if n in self.LABEL_MAP:
                        #pkt[self.LABEL_MAP[n]] = self.decode_float(data[n])
                        if n != 'stationtype' and n != 'softwaretype':
                           pkt[self.LABEL_MAP[n]] = self.decode_float(data[n]) if data[n] != '' else 0
                    elif n in self.IGNORED_LABELS:
                        val = data[n]
                        if n == 'PASSWORD':
                            val = 'X' * len(data[n])
                        logdbg("ignored parameter %s=%s" % (n, val))
                    else:
                        loginf("unrecognized parameter %s=%s" % (n, data[n]))

                # get the rain this period from total
                if 'rain_total' in pkt:
                    newtot = pkt['rain_total']
                    pkt['rain'] = self._delta_rain(newtot, self._last_rain)
                    self._last_rain = newtot

            except ValueError as e:
                logerr("parse failed for %s: %s" % (s, e))
            return pkt

        @staticmethod
        def decode_float(x):
            # these stations send a value of -9999 to indicate no value, so
            # convert that to a proper None.
            x = Consumer.Parser.decode_float(x)
            return None if x == -9999 else x


class EcowittClient(Consumer):
    """Use the ecowitt protocol (not WU protocol) to capture data"""

    def __init__(self, **stn_dict):
        super(EcowittClient, self).__init__(
            EcowittClient.Parser(), handler=EcowittClient.Handler, **stn_dict)

    class Handler(Consumer.Handler):

        def get_response(self):
            return '{"errcode":"0","errmsg":"ok","UTC_offset":"-18000"}'

    class Parser(Consumer.Parser):

        # map labels to observation names
        LABEL_MAP = {
            #from station : to weewx
            'baromrelin': 'barometer',
            'baromabsin': 'pressure',
            'humidity': 'humidity_out',
            'humidityin': 'humidity_in',
            'tempf': 'temperature_out',
            'tempinf': 'temperature_in',
            'temp1f': 'temperature_1',
            'temp2f': 'temperature_2',
            'temp3f': 'temperature_3',
            'temp4f': 'temperature_4',
            'temp5f': 'temperature_5',
            'temp6f': 'temperature_6',
            'temp7f': 'temperature_7',
            'temp8f': 'temperature_8',
            'humidity1': 'humidity_1',
            'humidity2': 'humidity_2',
            'humidity3': 'humidity_3',
            'humidity4': 'humidity_4',
            'humidity5': 'humidity_5',
            'humidity6': 'humidity_6',
            'humidity7': 'humidity_7',
            'humidity8': 'humidity_8',
            'batt1': 'battery_1',
            'batt2': 'battery_2',
            'batt3': 'battery_3',
            'batt4': 'battery_4',
            'batt5': 'battery_5',
            'batt6': 'battery_6',
            'batt7': 'battery_7',
            'batt8': 'battery_8',
            'soilmoisture1': 'soil_moisture_1',
            'soilmoisture2': 'soil_moisture_2',
            'soilmoisture3': 'soil_moisture_3',
            'soilmoisture4': 'soil_moisture_4',
            'soilmoisture5': 'soil_moisture_5',
            'soilmoisture6': 'soil_moisture_6',
            'soilmoisture7': 'soil_moisture_7',
            'soilmoisture8': 'soil_moisture_8',
            'soilmoisture9': 'soil_moisture_9',
            'soilmoisture10': 'soil_moisture_10',
            'soilmoisture11': 'soil_moisture_11',
            'soilmoisture12': 'soil_moisture_12',
            'soilmoisture13': 'soil_moisture_13',
            'soilmoisture14': 'soil_moisture_14',
            'soilmoisture15': 'soil_moisture_15',
            'soilmoisture16': 'soil_moisture_16',
            'soilbatt1': 'soilbatt1',
            'soilbatt2': 'soilbatt2',
            'soilbatt3': 'soilbatt3',
            'soilbatt4': 'soilbatt4',
            'soilbatt5': 'soilbatt5',
            'soilbatt6': 'soilbatt6',
            'soilbatt7': 'soilbatt7',
            'soilbatt8': 'soilbatt8',
            'soilbatt9': 'soilbatt9',
            'soilbatt10': 'soilbatt10',
            'soilbatt11': 'soilbatt11',
            'soilbatt12': 'soilbatt12',
            'soilbatt13': 'soilbatt13',
            'soilbatt14': 'soilbatt14',
            'soilbatt15': 'soilbatt15',
            'soilbatt16': 'soilbatt16',
            'windspeedmph': 'wind_speed',
            'windgustmph': 'wind_gust',
            'winddir': 'wind_dir',
            'solarradiation': 'solar_radiation',
            'uv': 'uv',
            'totalrainin': 'rain_total',
            #'totalainin': 'rain_total',
            'rainratein': 'rain_rate',
            'wh25batt': 'wh25batt',
            'wh26batt': 'wh26batt',
            'wh40batt': 'wh40batt',
            'wh57batt': 'wh57batt',
            'wh65batt': 'wh65batt',
            'wh68batt': 'wh65batt',
            'wh80batt': 'wh80batt',
            'wh90batt': 'wh90batt',
            'wh85batt': 'wh85batt',
            'pm25_ch1': 'pm25_ch1',
            'pm25_ch2': 'pm25_ch2',
            'pm25_ch3': 'pm25_ch3',
            'pm25_ch4': 'pm25_ch4',
            'pm25batt1': 'pm25batt1',
            'pm25batt2': 'pm25batt2',
            'pm25batt3': 'pm25batt3',
            'pm25batt4': 'pm25batt4',
            'lightning': 'lightning',
            'lightning_time': 'lightning_time',
            'lightning_num': 'lightning_num',
            'leak_ch1': 'leak_ch1',
            'leak_ch2': 'leak_ch2',
            'leak_ch3': 'leak_ch3',
            'leak_ch4': 'leak_ch4',
            'leakbatt1': 'leakbatt1',
            'leakbatt2': 'leakbatt2',
            'leakbatt3': 'leakbatt3',
            'leakbatt4': 'leakbatt4',
            'co2': 'co2',
            'co2_24h': 'co2_24h',
            'co2in': 'co2in',
            'co2in_24h': 'co2in_24h',
            'co2_batt': 'co2_batt',
            'tf_co2': 'tf_co2',
            'humi_co2': 'humi_co2',
            'pm1_co2': 'pm1_co2',
            'pm1_24h_co2': 'pm1_24h_co2',
            'pm4_co2': 'pm4_co2',
            'pm4_24h_co2': 'pm4_24h_co2',
            'pm25_co2': 'pm25_co2',
            'pm25_24h_co2': 'pm25_24h_co2',
            'pm10_co2': 'pm10_co2',
            'pm10_24h_co2': 'pm10_24h_co2',
            'tf_ch1': 'tf_ch1',
            'tf_ch2': 'tf_ch2',
            'tf_ch3': 'tf_ch3',
            'tf_ch4': 'tf_ch4',
            'tf_ch5': 'tf_ch5',
            'tf_ch6': 'tf_ch6',
            'tf_ch7': 'tf_ch7',
            'tf_ch8': 'tf_ch8',
            'tf_ch9': 'tf_ch9',
            'tf_ch10': 'tf_ch10',
            'tf_ch11': 'tf_ch11',
            'tf_ch12': 'tf_ch12',
            'tf_ch13': 'tf_ch13',
            'tf_ch14': 'tf_ch14',
            'tf_ch15': 'tf_ch15',
            'tf_ch16': 'tf_ch16',
            'tf_batt1': 'tf_batt1',
            'tf_batt2': 'tf_batt2',
            'tf_batt3': 'tf_batt3',
            'tf_batt4': 'tf_batt4',
            'tf_batt5': 'tf_batt5',
            'tf_batt6': 'tf_batt6',
            'tf_batt7': 'tf_batt7',
            'tf_batt8': 'tf_batt8',
            'tf_batt9': 'tf_batt9',
            'tf_batt10': 'tf_batt10',
            'tf_batt11': 'tf_batt11',
            'tf_batt12': 'tf_batt12',
            'tf_batt13': 'tf_batt13',
            'tf_batt14': 'tf_batt14',
            'tf_batt15': 'tf_batt15',
            'tf_batt16': 'tf_batt16',
            'leafwetness_ch1': 'leafwetness_ch1',
            'leafwetness_ch2': 'leafwetness_ch2',
            'leafwetness_ch3': 'leafwetness_ch3',
            'leafwetness_ch4': 'leafwetness_ch4',
            'leafwetness_ch5': 'leafwetness_ch5',
            'leafwetness_ch6': 'leafwetness_ch6',
            'leafwetness_ch7': 'leafwetness_ch7',
            'leafwetness_ch8': 'leafwetness_ch8',
            'leaf_batt1': 'leaf_batt1',
            'leaf_batt2': 'leaf_batt2',
            'leaf_batt3': 'leaf_batt3',
            'leaf_batt4': 'leaf_batt4',
            'leaf_batt5': 'leaf_batt5',
            'leaf_batt6': 'leaf_batt6',
            'leaf_batt7': 'leaf_batt7',
            'leaf_batt8': 'leaf_batt8',
            'maxdailygust': 'maxdailygust',
            'winddir_avg10m': 'winddir_avg10m',
            'windspdmph_avg10m': 'windspdmph_avg10m',
            'pm25_avg_24h_ch1' : 'pm25_avg_24h_ch1',
            'pm25_avg_24h_ch2' : 'pm25_avg_24h_ch2',
            'pm25_avg_24h_ch3' : 'pm25_avg_24h_ch3',
            'pm25_avg_24h_ch4' : 'pm25_avg_24h_ch4',
            'eventrainin' : 'eventrainin',
            'hourlyrainin' : 'hourlyrainin',
            'dailyrainin' : 'dailyrainin',
            'weeklyrainin' : 'weeklyrainin',
            'monthlyrainin' : 'monthlyrainin',
            'yearlyrainin' : 'yearlyrainin',
            'rainyear' : 'rainyear',
            'rrain_piezo' : 'rrain_piezo',
            'erain_piezo' : 'erain_piezo',
            'hrain_piezo' : 'hrain_piezo',
            'drain_piezo' : 'drain_piezo',
            'wrain_piezo' : 'wrain_piezo',
            'mrain_piezo' : 'mrain_piezo',
            'yrain_piezo' : 'yrain_piezo',
            'srain_piezo': 'srain_piezo',
            'ws90_ver' : 'ws90_ver',
            'ws85_ver' : 'ws85_ver',
            'ws1900batt' : 'console_batt',
            'console_batt' : 'console_batt',
            'ws90cap_volt' : 'ws90cap_volt',
            'ws85cap_volt' : 'ws85cap_volt',
            'gain10_piezo' : 'gain0',
            'gain20_piezo' : 'gain1',
            'gain30_piezo' : 'gain2',
            'gain40_piezo' : 'gain3',
            'gain50_piezo' : 'gain4',
            'runtime' : 'runtime',
            'interval' : 'interval',
            'stationtype' :  'stationtype',
            'model': 'model',
            'soilad1': 'soilad1',
            'soilad2': 'soilad2',
            'soilad3': 'soilad3',
            'soilad4': 'soilad4',
            'soilad5': 'soilad5',
            'soilad6': 'soilad6',
            'soilad7': 'soilad7',
            'soilad8': 'soilad8',
            'soilad9': 'soilad9',
            'soilad10': 'soilad10',
            'soilad11': 'soilad11',
            'soilad12': 'soilad12',
            'soilad13': 'soilad13',
            'soilad14': 'soilad14',
            'soilad15': 'soilad15',
            'soilad16': 'soilad16',
            'heap': 'heap',
            'wh24sig': 'wh24sig',
            'wh25sig': 'wh25sig',
            'wh26sig': 'wh26sig',
            'wh31sig1': 'wh31sig1',
            'wh31sig2': 'wh31sig2',
            'wh31sig3': 'wh31sig3',
            'wh31sig4': 'wh31sig4',
            'wh31sig5': 'wh31sig5',
            'wh31sig6': 'wh31sig6',
            'wh31sig7': 'wh31sig7',
            'wh31sig8': 'wh31sig8',
            'wh34sig1': 'wh34sig1',
            'wh34sig2': 'wh34sig2',
            'wh34sig3': 'wh34sig3',
            'wh34sig4': 'wh34sig4',
            'wh34sig5': 'wh34sig5',
            'wh34sig6': 'wh34sig6',
            'wh34sig7': 'wh34sig7',
            'wh34sig8': 'wh34sig8',
            'wh34sig9': 'wh34sig9',
            'wh34sig10': 'wh34sig10',
            'wh34sig11': 'wh34sig10',
            'wh34sig12': 'wh34sig11',
            'wh34sig13': 'wh34sig13',
            'wh34sig14': 'wh34sig14',
            'wh34sig15': 'wh34sig15',
            'wh34sig16': 'wh34sig16',
            'wh35sig1': 'wh35sig1',
            'wh35sig2': 'wh35sig2',
            'wh35sig3': 'wh35sig3',
            'wh35sig4': 'wh35sig4',
            'wh35sig5': 'wh35sig5',
            'wh35sig6': 'wh35sig6',
            'wh35sig7': 'wh35sig7',
            'wh35sig8': 'wh35sig8',
            'wh40sig': 'wh40sig',
            'wh41sig1': 'wh41sig1',
            'wh41sig2': 'wh41sig2',
            'wh41sig3': 'wh41sig3',
            'wh41sig4': 'wh41sig4',
            'wh45sig': 'wh45sig',
            'wh51sig1': 'wh51sig1',
            'wh51sig2': 'wh51sig2',
            'wh51sig3': 'wh51sig3',
            'wh51sig4': 'wh51sig4',
            'wh51sig5': 'wh51sig5',
            'wh51sig6': 'wh51sig6',
            'wh51sig7': 'wh51sig7',
            'wh51sig8': 'wh51sig8',
            'wh51sig9': 'wh51sig9',
            'wh51sig10': 'wh51sig10',
            'wh51sig11': 'wh51sig11',
            'wh51sig12': 'wh51sig12',
            'wh51sig13': 'wh51sig13',
            'wh51sig14': 'wh51sig14',
            'wh51sig15': 'wh51sig15',
            'wh51sig16': 'wh51sig16',
            'wh55sig1': 'wh55sig1',
            'wh55sig2': 'wh55sig2',
            'wh55sig3': 'wh55sig3',
            'wh55sig4': 'wh55sig4',
            'wh57sig': 'wh57sig',
            'wh65sig': 'wh65sig',
            'wh68sig': 'wh68sig',
            'wh69sig': 'wh69sig',
            'wh80sig': 'wh80sig',
            'wh90sig': 'wh90sig',
            'wh85sig': 'wh85sig',
            'wh54sig1': 'wh54sig1',
            'wh54sig2': 'wh54sig2',
            'wh54sig3': 'wh54sig3',
            'wh54sig4': 'wh54sig4',
            'dewptf': 'dewptf',
            'windchillf': 'windchillf',
            'feelslikef': 'feelslikef',
            'heatindexf': 'heatindexf',
            'windspdmph_avg10m': 'windspdmph_avg10m',
            'winddir_avg10m': 'winddir_avg10m',
            'windgustmph_max10m': 'windgustmph_max10m',
            'windrun': 'windrun',
            'pm25_AQI_ch1': 'pm25_AQI_ch1',
            'pm25_AQI_ch2': 'pm25_AQI_ch2',
            'pm25_AQI_ch3': 'pm25_AQI_ch3',
            'pm25_AQI_ch4': 'pm25_AQI_ch4',
            'pm25_AQI_co2': 'pm25_AQI_co2',
            'pm10_AQI_co2': 'pm10_AQI_co2',
            'pm25_AQI_avg_24h_ch1': 'pm25_AQI_avg_24h_ch1',
            'pm25_AQI_avg_24h_ch2': 'pm25_AQI_avg_24h_ch2',
            'pm25_AQI_avg_24h_ch3': 'pm25_AQI_avg_24h_ch3',
            'pm25_AQI_avg_24h_ch4': 'pm25_AQI_avg_24h_ch4',
            'pm25_AQI_24h_co2': 'pm25_AQI_24h_co2',
            'pm10_AQI_24h_co2': 'pm10_AQI_24h_co2',
            'sunhours': 'sunhours',
            'sunshine': 'sunshine',
            'radcompensation': 'radcompensation',
            'newVersion': 'newVersion',
            'upgrade': 'upgrade',
            'rainFallPriority': 'rainFallPriority',
            'rstRainDay': 'rstRainDay',
            'rstRainWeek': 'rstRainWeek',
            'rstRainYear': 'rstRainYear',
            'rainGain': 'rainGain',
            'piezo': 'piezo',
            'rain1_gain': 'rain1_gain',
            'rain2_gain': 'rain2_gain',
            'rain3_gain': 'rain3_gain',
            'rain4_gain': 'rain4_gain',
            'rain5_gain': 'rain5_gain',
            'wh54_ch1_sig': 'wh54sig1',
            'wh54_ch2_sig': 'wh54sig2',
            'wh54_ch3_sig': 'wh54sig3',
            'wh54_ch4_sig': 'wh54sig4',
            'thi_ch1': 'thi_ch1',
            'thi_ch2': 'thi_ch2',
            'thi_ch3': 'thi_ch3',
            'thi_ch4': 'thi_ch4',
            'depth_ch1': 'depth_ch1',
            'depth_ch2': 'depth_ch2',
            'depth_ch3': 'depth_ch3',
            'depth_ch4': 'depth_ch4',
            'air_ch1': 'air_ch1',
            'air_ch2': 'air_ch2',
            'air_ch3': 'air_ch3',
            'air_ch4': 'air_ch4',
            'ldsbatt1': 'ldsbatt1',
            'ldsbatt2': 'ldsbatt2',
            'ldsbatt3': 'ldsbatt3',
            'ldsbatt4': 'ldsbatt4',
            'ldsheat_ch1': 'ldsheat_ch1',
            'ldsheat_ch2': 'ldsheat_ch2',
            'ldsheat_ch3': 'ldsheat_ch3',
            'ldsheat_ch4': 'ldsheat_ch4',
            'noise_ch1': 'noise_ch1',
            'noise_ch2': 'noise_ch2',
            'noise_ch3': 'noise_ch3',
            'noise_ch4': 'noise_ch4',
            'peak_ch1': 'peak_ch1',
            'peak_ch2': 'peak_ch2',
            'peak_ch3': 'peak_ch3',
            'peak_ch4': 'peak_ch4',
            'ldspw_ch1': 'ldspw_ch1',
            'ldspw_ch2': 'ldspw_ch2',
            'ldspw_ch3': 'ldspw_ch3',
            'ldspw_ch4': 'ldspw_ch4',
            'vpd': 'vpd',
       }

        IGNORED_LABELS = [
            'PASSKEY', 'dateutc', 'freq', 'rfdata', 'isintvl','isintvl10',
            #'dewptf','windchillf','feelslikef','heatindexf',
            'pm25_AQIlvl_ch1','pm25_AQIlvl_avg_24h_ch1',
            'pm25_AQIlvl_ch2','pm25_AQIlvl_avg_24h_ch2',
            'pm25_AQIlvl_ch3','pm25_AQIlvl_avg_24h_ch3',
            'pm25_AQIlvl_ch4','pm25_AQIlvl_avg_24h_ch4',
            'co2lvl',
            'pm25_AQIlvl_co2','pm25_AQIlvl_24h_co2',
            'pm10_AQIlvl_co2','pm10_AQIlvl_24h_co2',
            #'windspdmph_avg10m','winddir_avg10m','windgustmph_max10m','windrun',
            'brightness','cloudf','srsum',
            #'sunhours','sunshine',
            'ptrend1','pchange1','ptrend3','pchange3',
            'running','wswarning','sensorwarning','batterywarning','stormwarning','tswarning','updatewarning','leakwarning','co2warning','intvlwarning','time',
        ]

        def __init__(self):
            self._last_rain = None
            self._rain_mapping_confirmed = False
            self._last_rain_piezo = None
            self._rain_piezo_mapping_confirmed = False
            self._last_lightning_num = None
            self._last_lightning_time = None
            self._last_lightning_confirmed = False
            self._model = None
            self._stationtype = None


        def parse(self, s):
            pkt = dict()
            try:
                data = _cgi_to_dict(s)
                pkt['dateTime'] = self.decode_datetime(
                    data.pop('dateutc', int(time.time() + 0.5)))
                pkt['usUnits'] = weewx.US

                # some devices (e.g., HP2551_V1.5.7) emit something that looks
                # a lot like ecowitt protocol, but not quite.  one thing that
                # they get wrong is the rain - that have no totalrainin.  so
                # for those devices, substitute a different cumulative rain
                # measurement.  do this only once, and do not be fooled by
                # partial packets.
                if 'stationtype' in data:
                    pkt['stationtype'] = data['stationtype']
                    if self._stationtype != data['stationtype']:
                       self._stationtype = data['stationtype']
                       loginf("Station_type: %s" % (data['stationtype']))

                if 'model' in data:
                    pkt['model'] = data['model']
                    if self._model != data['model']:
                       self._model = data['model']  
                       loginf("Hardware_model: %s" % (data['model']))

                if 'totalrainin' not in data and 'yearlyrainin' in data:
                    pkt['rainyear'] = self.decode_float(data['yearlyrainin']) if data['yearlyrainin'] != '' else 0

                if 'yrain_piezo' in data:
                    pkt['yrain_piezo'] = self.decode_float(data['yrain_piezo']) if data['yrain_piezo'] != '' else 0

                if not self._rain_mapping_confirmed:
                    if 'totalrainin' not in data and 'yearlyrainin' in data:
                        self.LABEL_MAP.pop('totalrainin')
                        self.LABEL_MAP['yearlyrainin'] = 'rain_total'
                        self._rain_mapping_confirmed = True
                        loginf("using 'yearlyrainin' for rain_total")
                    elif 'totalrainin' in data:
                        self._rain_mapping_confirmed = True
                        loginf("using 'totalrainin' for rain_total")

                if not self._rain_piezo_mapping_confirmed:
                    if 'yrain_piezo' in data:
                        #self.LABEL_MAP.pop('totalrainin_piezo')
                        self.LABEL_MAP['yrain_piezo'] = 'rain_total_piezo'
                        self._rain_piezo_mapping_confirmed = True
                        loginf("using 'yrain_piezo' for rain_total_piezo")

                #if not self._last_lightning_confirmed:
                #    if 'lightning_num' in data:
                #        #self.LABEL_MAP.pop('lightning_strike_count')
                #        self.LABEL_MAP['lightning_strike_count'] = 'lightning_num'
                #        #self._last_lightning_num = data['lightning_num']
                #        self._last_lightning_confirmed = True


                # get all of the other parameters
                for n in data:
                    if n in self.LABEL_MAP:
                        #pkt[self.LABEL_MAP[n]] = self.decode_float(data[n])
                        #pkt[self.LABEL_MAP[n]] = self.decode_float(data[n]) if data[n] != '' else ''
                        if n != 'model' and n != 'stationtype':
                           pkt[self.LABEL_MAP[n]] = self.decode_float(data[n]) if data[n] != '' else 0
                    elif n in self.IGNORED_LABELS:
                        val = data[n]
                        if n == 'PASSKEY':
                            val = 'X' * len(data[n])
                        logdbg("ignored parameter %s=%s" % (n, val))
                    else:
                        if n != 'totalrainin':
                          loginf("unrecognized parameter %s=%s" % (n, data[n]))

                # get the rain this period from total
                if 'rain_total' in pkt:
                    newtot = pkt['rain_total']
                    pkt['rain'] = self._delta_rain(newtot, self._last_rain)
                    self._last_rain = newtot
                # get the rain_piezo (WS90) this period from total
                if 'rain_total_piezo' in pkt:
                    newtot = pkt['rain_total_piezo']
                    pkt['rain_piezo'] = self._delta_rain_piezo(newtot, self._last_rain_piezo)
                    self._last_rain_piezo = newtot
                if 'lightning_num' and 'lightning_time'in pkt:
                    if not self._last_lightning_confirmed:                        
                       self._last_lightning_num = pkt['lightning_num']
                       self._last_lightning_time = pkt['lightning_time']
                       self._last_lightning_confirmed = True
                    newtot = pkt['lightning_num']
                    newtime = pkt['lightning_time']
                    #pkt['lightning_strike_count'] = self._delta_lightning_num(newtot, self._last_lightning_num)
                    pkt['lightning_strike_count'] = self._delta_lightning_num(newtot, self._last_lightning_num, newtime, self._last_lightning_time)
                    self._last_lightning_num = newtot
                    self._last_lightning_time = newtime


            except ValueError as e:
                logerr("parse failed for %s: %s" % (s, e))
            return pkt

        @staticmethod
        def decode_float(x):
            # these stations send a value of -9999 to indicate no value, so
            # convert that to a proper None.
            x = Consumer.Parser.decode_float(x)
            return None if x == -9999 else x


class EcowittcustomConfigurationEditor(weewx.drivers.AbstractConfEditor):
    @property
    def default_stanza(self):
        return """
[Ecowittcustom]
    # This section is for the network traffic ecowittclient driver.

    # The driver to use:
    driver = user.ecowittcustom

    # Specify the hardware device to capture.  Options include:
    #   ecowitt-client - any hardware that uses the ecowitt protocol
    #   wu-client - any hardware that uses the weather underground protocol
    device_type = ecowitt-client

    # For acurite, fine offset, and oregon scientific hardware, the driver
    # can sniff packets directly or run a socket server that listens for
    # connections.  Packet sniffing requires the installation of the pcap
    # python module.  The default mode is to listen using a socket server.
    # Options are 'listen' and 'sniff'.
    #mode = listen

    # When listening, specify at least a port on which to bind.
    #address = 127.0.0.1
    #port = 80

    # When sniffing, specify a network interface and a pcap filter.
    #iface = eth0
    #pcap_filter = src 192.168.4.12 and dst port 80
    # If your interface requires promiscuous mode, then set this to True.
    #promiscuous = False

    # Specify a sensor map to associate sensor observations with fields in
    # the database.  This is most appropriate for hardware that supports
    # a variable number of sensors.  The values in the tuple on the right
    # side are hardware-specific, but follow the pattern:
    #
    #  <observation_name>.<hardware_id>.<bridge_id>
    #
    #[[sensor_map]]
    #    inTemp = temperature_in.*.*
    #    inHumidity = humidity_in.*.*
    #    outTemp = temperature.?*.*
    #    outHumidity = humidity.?*.*
    #
    # Optionally specify a sensor map extensions.  The fields in this stanza
    # will override any defined in the sensor_map.  The values have the same
    # format as those in the sensor_map.
    #
    #[[sensor_map_extensions]]
    #    extraTemp1 = temperature_1.*.*
"""

    def prompt_for_settings(self):
        print("Specify the type of device whose data will be captured")
        device_type = self._prompt(
            'device_type', 'ecowitt-client',
            ['wu-client', 'ecowitt-client'])
        return {'device_type': device_type}


class EcowittcustomDriver(weewx.drivers.AbstractDevice):
    DEVICE_TYPES = {
        'ecowitt-client': EcowittClient,
        'wu-client': WUClient
    }

    def __init__(self, **stn_dict):
        loginf('driver version is %s' % DRIVER_VERSION)
        stn_dict.pop('driver')
        self._device_type = stn_dict.pop('device_type', 'ecowitt-client')
        if not self._device_type in self.DEVICE_TYPES:
            raise TypeError("unsupported device type '%s'" % self._device_type)
        loginf('device type: %s' % self._device_type)
        self._queue_timeout = int(stn_dict.pop('queue_timeout', 10))
        obs_map = stn_dict.pop('sensor_map', None)
        obs_map_ext = stn_dict.pop('sensor_map_extensions', {})
        self._device = self.DEVICE_TYPES.get(self._device_type)(**stn_dict)
        if obs_map is None:
            obs_map = self._device.default_sensor_map()
        obs_map.update(obs_map_ext)
        self._obs_map = obs_map
        loginf('sensor map: %s' % self._obs_map)
        self._server_thread = threading.Thread(target=self._device.run_server)
        self._server_thread.setDaemon(True)
        self._server_thread.setName('ServerThread')
        self._server_thread.start()

    def closePort(self):
        loginf('shutting down server thread')
        self._device.stop_server()
        self._server_thread.join(20.0)
        if self._server_thread.isAlive():
            logerr('unable to shut down server thread')

    @property
    def hardware_name(self):
        return self._device_type

    def genLoopPackets(self):
        last_ts = 0
        while True:
            try:
                data = self._device.get_queue().get(True, self._queue_timeout)
                logdbg('raw data: %s' % data)
                pkt = self._device.parser.parse(data)
                logdbg('raw packet: %s' % pkt)
                pkt = self._device.parser.map_to_fields(pkt, self._obs_map)
                logdbg('mapped packet: %s' % pkt)
                if pkt and 'dateTime' in pkt and 'usUnits' in pkt:
                    if pkt['dateTime'] >= last_ts:
                        last_ts = pkt['dateTime']
                        yield pkt
                    else:
                        loginf("skipping out-of-order packet %s ('%s')" %
                               (pkt, data))
                else:
                    logdbg("skipping bogus packet %s ('%s')" % (pkt, data))
            except Queue.Empty:
                logdbg('empty queue')


# define a main entry point for determining sensor identifiers.
# invoke this as follows from the weewx root dir:
#
# PYTHONPATH=bin python bin/user/ecowittclient.py

if __name__ == '__main__':
    import optparse

    usage = """%prog [options] [--debug] [--help]"""

    parser = optparse.OptionParser(usage=usage)
    parser.add_option('--version', dest='version', action='store_true',
                      help='display driver version')
    parser.add_option('--debug', dest='debug', action='store_true',
                      default=False,
                      help='display diagnostic information while running')
    parser.add_option('--mode', dest='mode', metavar='MODE',
                      default='listen',
                      help='how to capture traffic: listen or sniff')
    parser.add_option('--port', dest='port', metavar='PORT', type=int,
                      default=DEFAULT_PORT,
                      help='port on which to listen')
    parser.add_option('--address', dest='addr', metavar='ADDRESS',
                      default=DEFAULT_ADDR,
                      help='address on which to bind')
    parser.add_option('--iface', dest='iface', metavar='IFACE',
                      default=DEFAULT_IFACE,
                      help='network interface to sniff')
    parser.add_option('--filter', dest='filter', metavar='FILTER',
                      default=DEFAULT_FILTER,
                      help='pcap filter for sniffing')
    parser.add_option('--device', dest='device_type', metavar='DEVICE_TYPE',
                      default=DEFAULT_DEVICE_TYPE,
                      help='type of device for which to listen')
    parser.add_option('--data', dest='data', metavar='DATA',
                      default='',
                      help='data string for parse testing')
    parser.add_option('--no-obfuscate', action='store_true', default=False,
                      help='do not obfuscate passkeys/passwords')

    (options, args) = parser.parse_args()

    if options.version:
        print("driver version is %s" % DRIVER_VERSION)
        exit(0)

    if options.debug:
        weewx.debug = 1

    #    weeutil.logger.setup('ecowittcustom', {})

    if options.data:
        options.data = options.data.replace(' ', '')

    if not options.device_type in EcowittcustomDriver.DEVICE_TYPES:
        raise TypeError("unsupported device type '%s'.  options include %s" %
                        (options.device_type,
                         ', '.join(EcowittcustomDriver.DEVICE_TYPES.keys())))

    device = EcowittcustomDriver.DEVICE_TYPES.get(options.device_type)(
        mode=options.mode,
        iface=options.iface, pcap_filter=options.filter,
        address=options.addr, port=options.port)

    server_thread = threading.Thread(target=device.run_server)
    server_thread.setDaemon(True)
    server_thread.setName('ServerThread')
    server_thread.start()

    while True:
        try:
            _data = device.get_queue().get(True, 1)
            ids = device.parser.parse_identifiers(_data)
            if ids:
                print('identifiers: %s' % ids)
            if options.debug:
                s = '%s' % _data
                if not options.no_obfuscate:
                    s = _obfuscate_passwords(s)
                print('raw data: %s' % s)
            _pkt = device.parser.parse(_data)
            if options.debug:
                s = '%s' % _pkt
                if not options.no_obfuscate:
                    s = _obfuscate_passwords(s)
                print('raw packet: %s' % s)
            _pkt = device.parser.map_to_fields(_pkt, device.default_sensor_map())
            s = '%s' % _pkt
            if not options.no_obfuscate:
                s = _obfuscate_passwords(s)
            print('mapped packet: %s' % s)
        except Queue.Empty:
            pass
        except KeyboardInterrupt:
            break
