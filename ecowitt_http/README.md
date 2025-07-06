## Driver ecowitt_http
forked from 
https://github.com/gjr80/weewx-ecowitt_local_http/blob/master

(C) 2024-25 Gary Roderick                     gjroderick<at>gmail.com

Modified by me!

        - WH45/WH46 = co2 missed - added
        - changed some keys that are the same as my ecowittcustom driver
        - add some keys
        - completed all data from the SDcard GW3000
        - completed all data from the device 

        4 July 2025           
        - corrected radiation
        - corrected co2_Temp
        - corrected wh51 - forget to add sensors wh51 at sensors
        - corrected signal to None if signal id is "FFFFFFFE" or "FFFFFFFF"
        - add some unit-settings
        - corrected rain, piezo_rain, lightning_count for loop packets
        not yet verified: rain, piezo_rain, lightning_count from sdcard and cloud


Tested and completed:
```
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW3000% --live-data
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW3000% --weewx-fields
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW3000% --firmware
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW3000% --mac
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW3000% --system
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --discover

PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW3000% --discover
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW3000% --default-map
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW3000% --driver-map
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW3000% --service-map
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW3000% --get-services

PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW3000% --test-driver 
```
Not working:
```
PYTHONPATH=/usr/share/weewx python3 /etc/weewx/bin/user/ecowitt_http.py --ip-address=%IP-GW3000% --test-service
```
and
```
[Engine]
    [[Services]]
        data_services = user.ecowitt_http.EcowittHttpService
```

### Settings in weewx.conf

```
# Whether to try indefinitely to load the driver
loop_on_init = 1

[EcowittHttp]
    # the driver to use
    driver = user.ecowitt_http
   
    # how often to poll the device
    poll_interval = 20
    # how many attempts to contact the device before giving up
    max_tries = 3
    # wait time in seconds between retries to contact the device
    retry_wait = 2
    # max wait for device to respond to a HTTP request
    url_timeout = 3
    
    # whether to show all battery state data including nonsense data and 
    # sensors that are disabled sensors and connecting
    show_all_batt = False

    # whether to always log unknown API fields, unknown fields are always 
    # logged at the debug level, this will log them at the info level
    log_unknown_fields = True

    # How often to check for device firmware updates, 0 disables firmware 
    # update checks. Available firmware updates are logged.
    firmware_update_check_interval = 86400

    only_registered = False
    
    #wn32_indoor = True
    #wn32_outdoor = True

    #former debug_logging (here for wind) not more supported!:
    # provide additional log information to help debug wind issues
    #debug_wind = False

    #debug_logging new with list:
    #debug = rain, wind, loop, sensors, parser, catchup, collector

    debug = parser, sensors, catchup  

    catchup_grace = 0

    ip_address = 192.168.0.110
    api_key = 00000000-1111-2222-3333-444444444444
    app_key = DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
    mac = 5C:01:3B:46:C3:FF

```
All mapping and unit assignments are done now in the driver

# Problem at the moment:
## Loop packets are captured but not used
Found the problem: to use the loop packets, this setting in weewx.conf is necessary
```
[StdArchive]
    record_generation = software
```

#### log from this driver:
```
weewxd[647056]: INFO __main__: Initializing weewxd version 5.1.0
weewxd[647056]: INFO __main__: Command line: /usr/share/weewx/weewxd.py --daemon --pidfile=/var/run/weewx4.pid /etc/weewx/weewx4.conf
weewxd[647056]: INFO __main__: Using Python: 3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0]
weewxd[647056]: INFO __main__: Located at:   /bin/python3
weewxd[647056]: INFO __main__: Platform:     Linux-6.12.25+rpt-rpi-2712-aarch64-with-glibc2.36
weewxd[647056]: INFO __main__: Locale:       'de_DE.UTF-8'
weewxd[647056]: INFO __main__: Entry path:   /usr/share/weewx/weewxd.py
weewxd[647056]: INFO __main__: WEEWX_ROOT:   /etc/weewx
weewxd[647056]: INFO __main__: Config file:  /etc/weewx/weewx4.conf
weewxd[647056]: INFO __main__: User module:  /etc/weewx/bin/user
weewxd[647056]: INFO __main__: Debug:        0
weewxd[647056]: INFO __main__: User:         root
weewxd[647056]: INFO __main__: Group:        root
weewxd[647056]: INFO __main__: Groups:       
weewxd[647056]: INFO __main__: PID file is /var/run/weewx4.pid
weewxd[647060]: INFO weewx.engine: Loading station type EcowittHttp (user.ecowitt_http)
weewxd[647060]: INFO user.ecowitt_http: EcowittHttpDriver: version is 0.1.0_test
weewxd[647060]: INFO user.ecowitt_http: unit_system: 17
weewxd[647060]: INFO user.ecowitt_http:      field map is {'appTemp': 'common_list.4.val', 'barometer': 'wh25.rel', 'batteryStatus1': 'wn31.ch1.battery', 'batteryStatus2': 'wn31.ch2.battery', 'batteryStatus3': 'wn31.ch3.battery', 'batteryStatus4': 'wn31.ch4.battery', 'batteryStatus5': 'wn31.ch5.battery', 'batteryStatus6': 'wn31.ch6.battery', 'batteryStatus7': 'wn31.ch7.battery', 'batteryStatus8': 'wn31.ch8.battery', 'co2': 'co2.CO2', 'co2_24h': 'co2.CO2_24H', 'co2_Batt': 'co2.battery', 'co2_Hum': 'co2.humidity', 'co2_Temp': 'co2.temperature', 'co2in': 'wh25.CO2', 'co2in_24h': 'wh25.CO2_24H', 'dateTime': 'datetime', 'daymaxwind': 'common_list.0x19.val', 'depth_ch1': 'ch_lds.1.depth', 'depth_ch2': 'ch_lds.2.depth', 'depth_ch3': 'ch_lds.3.depth', 'depth_ch4': 'ch_lds.4.depth', 'dewpoint': 'common_list.0x03.val', 'extraHumid1': 'ch_aisle.1.humidity', 'extraHumid2': 'ch_aisle.2.humidity', 'extraHumid3': 'ch_aisle.3.humidity', 'extraHumid4': 'ch_aisle.4.humidity', 'extraHumid5': 'ch_aisle.5.humidity', 'extraHumid6': 'ch_aisle.6.humidity', 'extraHumid7': 'ch_aisle.7.humidity', 'extraHumid8': 'ch_aisle.8.humidity', 'extraTemp1': 'ch_aisle.1.temp', 'extraTemp2': 'ch_aisle.2.temp', 'extraTemp3': 'ch_aisle.3.temp', 'extraTemp4': 'ch_aisle.4.temp', 'extraTemp5': 'ch_aisle.5.temp', 'extraTemp6': 'ch_aisle.6.temp', 'extraTemp7': 'ch_aisle.7.temp', 'extraTemp8': 'ch_aisle.8.temp', 'feelslike': 'common_list.3.val', 'heap': 'debug.heap', 'inHumidity': 'wh25.inhumi', 'inTemp': 'wh25.intemp', 'is_raining': 'piezoRain.srain_piezo.val', 'ldsbatt1': 'ch_lds.1.voltage', 'ldsbatt2': 'ch_lds.2.voltage', 'ldsbatt3': 'ch_lds.3.voltage', 'ldsbatt4': 'ch_lds.4.voltage', 'ldsheat_ch1': 'ch_lds.1.heat', 'ldsheat_ch2': 'ch_lds.2.heat', 'ldsheat_ch3': 'ch_lds.3.heat', 'ldsheat_ch4': 'ch_lds.4.heat', 'leafWet1': 'ch_leaf.1.humidity', 'leafWet2': 'ch_leaf.2.humidity', 'leafWet3': 'ch_leaf.3.humidity', 'leafWet4': 'ch_leaf.4.humidity', 'leafWet5': 'ch_leaf.5.humidity', 'leafWet6': 'ch_leaf.6.humidity', 'leafWet7': 'ch_leaf.7.humidity', 'leafWet8': 'ch_leaf.8.humidity', 'leak Batt3': 'wh55.ch3.battery', 'leak_1': 'ch_leak.1.status', 'leak_2': 'ch_leak.2.status', 'leak_3': 'ch_leak.3.status', 'leak_4': 'ch_leak.4.status', 'leak_Batt1': 'wh55.ch1.battery', 'leak_Batt2': 'wh55.ch2.battery', 'leak_Batt4': 'wh55.ch4.battery', 'lightning_Batt': 'wh57.battery', 'lightning_distance': 'lightning.distance', 'lightning_disturber_count': 'lightning.timestamp', 'lightning_strike_count': 'lightning.count', 'outHumidity': 'common_list.0x07.val', 'outTemp': 'common_list.0x02.val', 'p_rain': 'piezoRain.0x0D.val', 'p_rainday': 'piezoRain.0x10.val', 'p_rainhour': 'p_rainhour', 'p_rainmonth': 'piezoRain.0x12.val', 'p_rainrate': 'piezoRain.0x0E.val', 'p_rainweek': 'piezoRain.0x11.val', 'p_rainyear': 'piezoRain.0x13.val', 'pm1_0': 'co2.PM1', 'pm1_24h_co2': 'co2.PM1_24H', 'pm1_24hAQI_co2': 'co2.PM1_24HAQI', 'pm1_RealAQI_co2': 'co2.PM1_RealAQI', 'pm2_5': 'co2.PM25', 'pm4_0': 'co2.PM4', 'pm4_24h_co2': 'co2.PM4_24H', 'pm4_24hAQI_co2': 'co2.PM4_24HAQI', 'pm4_RealAQI_co2': 'co2.PM4_RealAQI', 'pm10_0': 'co2.PM10', 'pm10_24h_co2': 'co2.PM10_24H', 'pm10_24hAQI_co2': 'co2.PM10_24HAQI', 'pm10_RealAQI_co2': 'co2.PM10_RealAQI', 'pm25_1': 'ch_pm25.1.PM25', 'pm25_2': 'ch_pm25.2.PM25', 'pm25_3': 'ch_pm25.3.PM25', 'pm25_4': 'ch_pm25.4.PM25', 'pm25_24h_co2': 'co2.PM25_24H', 'pm25_24hAQI_co2': 'co2.PM25_24HAQI', 'pm25_AQI_24h_ch1': 'ch_pm25.1.PM25_24HAQI', 'pm25_AQI_24h_ch2': 'ch_pm25.2.PM25_24HAQI', 'pm25_AQI_24h_ch3': 'ch_pm25.3.PM25_24HAQI', 'pm25_AQI_24h_ch4': 'ch_pm25.4.PM25_24HAQI', 'pm25_avg_24h_ch1': 'ch_pm25.1.PM25_24H', 'pm25_avg_24h_ch2': 'ch_pm25.2.PM25_24H', 'pm25_avg_24h_ch3': 'ch_pm25.3.PM25_24H', 'pm25_avg_24h_ch4': 'ch_pm25.4.PM25_24H', 'pm25_Batt1': 'wh41.ch1.battery', 'pm25_Batt2': 'wh41.ch2.battery', 'pm25_Batt3': 'wh41.ch3.battery', 'pm25_Batt4': 'wh41.ch4.battery', 'pm25_RealAQI_ch1': 'ch_pm25.1.PM25_RealAQI', 'pm25_RealAQI_ch2': 'ch_pm25.2.PM25_RealAQI', 'pm25_RealAQI_ch3': 'ch_pm25.3.PM25_RealAQI', 'pm25_RealAQI_ch4': 'ch_pm25.4.PM25_RealAQI', 'pm25_RealAQI_co2': 'co2.PM25_RealAQI', 'pressure': 'wh25.abs', 'radiation': 'common_list.0x15.val', 'runtime': 'debug.runtime', 'soilMoist1': 'ch_soil.1.humidity', 'soilMoist2': 'ch_soil.2.humidity', 'soilMoist3': 'ch_soil.3.humidity', 'soilMoist4': 'ch_soil.4.humidity', 'soilMoist5': 'ch_soil.5.humidity', 'soilMoist6': 'ch_soil.6.humidity', 'soilMoist7': 'ch_soil.7.humidity', 'soilMoist8': 'ch_soil.8.humidity', 'soilMoist9': 'ch_soil.9.humidity', 'soilMoist10': 'ch_soil.10.humidity', 'soilMoist11': 'ch_soil.11.humidity', 'soilMoist12': 'ch_soil.12.humidity', 'soilMoist13': 'ch_soil.13.humidity', 'soilMoist14': 'ch_soil.14.humidity', 'soilMoist15': 'ch_soil.15.humidity', 'soilMoist16': 'ch_soil.16.humidity', 'soilMoistBatt1': 'ch_soil.1.voltage', 'soilMoistBatt1s': 'wh51.ch1.battery', 'soilMoistBatt2': 'ch_soil.2.voltage', 'soilMoistBatt2s': 'wh51.ch2.battery', 'soilMoistBatt3': 'ch_soil.3.voltage', 'soilMoistBatt3s': 'wh51.ch3.battery', 'soilMoistBatt4': 'ch_soil.4.voltage', 'soilMoistBatt4s': 'wh51.ch4.battery', 'soilMoistBatt5': 'ch_soil.5.voltage', 'soilMoistBatt5s': 'wh51.ch5.battery', 'soilMoistBatt6': 'ch_soil.6.voltage', 'soilMoistBatt6s': 'wh51.ch6.battery', 'soilMoistBatt7': 'ch_soil.7.voltage', 'soilMoistBatt7s': 'wh51.ch7.battery', 'soilMoistBatt8': 'ch_soil.8.voltage', 'soilMoistBatt8s': 'wh51.ch8.battery', 'soilMoistBatt9': 'ch_soil.9.voltage', 'soilMoistBatt9s': 'wh51.ch9.battery', 'soilMoistBatt10': 'ch_soil.10.voltage', 'soilMoistBatt10s': 'wh51.ch10.battery', 'soilMoistBatt11': 'ch_soil.11.voltage', 'soilMoistBatt11s': 'wh51.ch11.battery', 'soilMoistBatt12': 'ch_soil.12.voltage', 'soilMoistBatt12s': 'wh51.ch12.battery', 'soilMoistBatt13': 'ch_soil.13.voltage', 'soilMoistBatt13s': 'wh51.ch13.battery', 'soilMoistBatt14': 'ch_soil.14.voltage', 'soilMoistBatt14s': 'wh51.ch14.battery', 'soilMoistBatt15': 'ch_soil.15.voltage', 'soilMoistBatt15s': 'wh51.ch15.battery', 'soilMoistBatt16': 'ch_soil.16.voltage', 'soilMoistBatt16s': 'wh51.ch16.battery', 'soilTemp1': 'ch_temp.1.temp', 'soilTemp2': 'ch_temp.2.temp', 'soilTemp3': 'ch_temp.3.temp', 'soilTemp4': 'ch_temp.4.temp', 'soilTemp5': 'ch_temp.5.temp', 'soilTemp6': 'ch_temp.6.temp', 'soilTemp7': 'ch_temp.7.temp', 'soilTemp8': 'ch_temp.8.temp', 'soilTempBatt1': 'ch_temp.1.voltage', 'soilTempBatt1s': 'wn34.ch1.battery', 'soilTempBatt2': 'ch_temp.2.voltage', 'soilTempBatt2s': 'wn34.ch2.battery', 'soilTempBatt3': 'ch_temp.3.voltage', 'soilTempBatt3s': 'wn34.ch3.battery', 'soilTempBatt4': 'ch_temp.4.voltage', 'soilTempBatt4s': 'wn34.ch4.battery', 'soilTempBatt5': 'ch_temp.5.voltage', 'soilTempBatt5s': 'wn34.ch5.battery', 'soilTempBatt6': 'ch_temp.6.voltage', 'soilTempBatt6s': 'wn34.ch6.battery', 'soilTempBatt7': 'ch_temp.7.voltage', 'soilTempBatt7s': 'wn34.ch7.battery', 'soilTempBatt8': 'ch_temp.8.voltage', 'soilTempBatt8s': 'wn34.ch8.battery', 't_rainday': 'rain.0x10.val', 't_rainevent': 'rain.0x0D.val', 't_rainhour': 't_rainhour', 't_rainmonth': 'rain.0x12.val', 't_rainRate': 'rain.0x0E.val', 't_rainweek': 'rain.0x11.val', 't_rainyear': 'rain.0x13.val', 'thi_ch1': 'ch_lds.1.air', 'thi_ch2': 'ch_lds.2.air', 'thi_ch3': 'ch_lds.3.air', 'thi_ch4': 'ch_lds.4.air', 'UV': 'common_list.0x17.val', 'uvradiation': 'common_list.0x16.val', 'vpd': 'common_list.5.val', 'wh25_batt': 'wh25.battery', 'wh25_sig': 'wh25.signal', 'wh26_batt': 'wh26.battery', 'wh26_sig': 'wh26.signal', 'wh41_ch1_sig': 'wh41.ch1.signal', 'wh41_ch2_sig': 'wh41.ch2.signal', 'wh41_ch3_sig': 'wh41.ch3.signal', 'wh41_ch4_sig': 'wh41.ch4.signal', 'wh45_sig': 'co2.signal', 'wh51_ch1_sig': 'wh51.ch1.signal', 'wh51_ch2_sig': 'wh51.ch2.signal', 'wh51_ch3_sig': 'wh51.ch3.signal', 'wh51_ch4_sig': 'wh51.ch4.signal', 'wh51_ch5_sig': 'wh51.ch5.signal', 'wh51_ch6_sig': 'wh51.ch6.signal', 'wh51_ch7_sig': 'wh51.ch7.signal', 'wh51_ch8_sig': 'wh51.ch8.signal', 'wh51_ch9_sig': 'wh51.ch9.signal', 'wh51_ch10_sig': 'wh51.ch10.signal', 'wh51_ch11_sig': 'wh51.ch11.signal', 'wh51_ch12_sig': 'wh51.ch12.signal', 'wh51_ch13_sig': 'wh51.ch13.signal', 'wh51_ch14_sig
weewxd[647060]: INFO user.ecowitt_http:      device IP address is 192.168.0.110
weewxd[647060]: INFO user.ecowitt_http:      poll interval is 20 seconds
weewxd[647060]: INFO user.ecowitt_http:      Max tries is 3 URL retry wait is 2 seconds
weewxd[647060]: INFO user.ecowitt_http:      URL timeout is 3 seconds
weewxd[647060]: INFO user.ecowitt_http:       any debug is set
weewxd[647060]: INFO user.ecowitt_http:      rain debug is not set
weewxd[647060]: INFO user.ecowitt_http:      wind debug is not set
weewxd[647060]: INFO user.ecowitt_http:      loop debug is not set
weewxd[647060]: INFO user.ecowitt_http:   sensors debug is set
weewxd[647060]: INFO user.ecowitt_http:   catchup debug is set
weewxd[647060]: INFO user.ecowitt_http:    parser debug is set
weewxd[647060]: INFO user.ecowitt_http: collector debug is not set
weewxd[647060]: INFO user.ecowitt_http:     cloud debug is not set
weewxd[647060]: INFO user.ecowitt_http:    wn32_indoor: sensor ID decoding will use 'WH26'
weewxd[647060]: INFO user.ecowitt_http:   wn32_outdoor: sensor ID decoding will use 'WH26'
weewxd[647060]: INFO user.ecowitt_http:      device firmware update checks will occur every 86400 seconds
weewxd[647060]: INFO user.ecowitt_http:      available device firmware updates will be logged
weewxd[647060]: INFO user.ecowitt_http:      battery state will not be reported for sensors with no signal data
weewxd[647060]: INFO user.ecowitt_http:      unknown fields will be reported
weewxd[647060]: INFO user.ecowitt_http: catchup source: None
weewxd[647060]: INFO user.ecowitt_http: EcowittHttpCollector startup
weewxd[647060]: INFO weewx.engine: StdConvert target unit is 0x1
weewxd[647060]: INFO weewx.wxservices: StdWXCalculate will use data binding wx_binding
weewxd[647060]: INFO user.GTS: Version 1.1
weewxd[647060]: INFO user.GTS: Local mean time (LMT) UTC offset 0:55:16.533360
weewxd[647060]: INFO user.GTS: PressureCooker True
weewxd[647060]: INFO user.GTS: PressureCooker <user.barometer.PressureCooker object at 0x7fff3d4c9590> 
weewxd[647060]: INFO weewx.engine: Archive will use data binding wx_binding
weewxd[647060]: INFO weewx.engine: Record generation will be attempted in 'hardware'
weewxd[647060]: INFO weewx.engine: Using archive interval of 300 seconds (specified in weewx configuration)
weewxd[647060]: INFO weewx.restx: StationRegistry: Registration not requested.
weewxd[647060]: INFO weewx.restx: Wunderground: Posting not enabled.
weewxd[647060]: INFO weewx.restx: PWSweather: Posting not enabled.
weewxd[647060]: INFO weewx.restx: CWOP: Posting not enabled.
weewxd[647060]: INFO weewx.restx: WOW: Posting not enabled.
weewxd[647060]: INFO weewx.restx: AWEKAS: Posting not enabled.
weewxd[647060]: INFO weewx.engine: 'pyephem' detected, extended almanac data is available
weewxd[647060]: INFO __main__: Starting up weewx version 5.1.0
weewxd[647060]: INFO weewx.engine: Using binding 'wx_binding' to database 'weewx_ecowitt_http.sdb'
weewxd[647060]: INFO weewx.manager: Starting backfill of daily summaries
weewxd[647060]: INFO weewx.manager: Daily summaries up to date
weewxd[647060]: INFO user.ecowitt_http: genArchiveRecords: Using MAC address: 5C:01:3B:46:C3:FF
weewxd[647060]: INFO user.ecowitt_http: Processing history file '202507A.csv' from  GW3000A_V1.0.9 at 192.168.0.110
weewxd[647060]: INFO user.ecowitt_http: Problem with key Time
weewxd[647060]: INFO user.ecowitt_http: Problem with key Timestamp
weewxd[647060]: INFO user.ecowitt_http: Processing history file '202507Allsensors_A.csv' from  GW3000A_V1.0.9 at 192.168.0.110
weewxd[647060]: INFO user.ecowitt_http: Problem with key Time
weewxd[647060]: INFO user.ecowitt_http: Problem with key Timestamp
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH2hum
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH3hum
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH4hum
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH5hum
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH6hum
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH7hum
weewxd[647060]: INFO user.ecowitt_http: no Data field WH35 CH8hum
weewxd[647060]: INFO user.ecowitt_http: no Data field SoilMoisture CH11
weewxd[647060]: INFO user.ecowitt_http: no Data field SoilMoisture CH12
weewxd[647060]: INFO user.ecowitt_http: no Data field SoilMoisture CH13
weewxd[647060]: INFO user.ecowitt_http: no Data field SoilMoisture CH14
weewxd[647060]: INFO user.ecowitt_http: no Data field SoilMoisture CH15
weewxd[647060]: INFO user.ecowitt_http: no Data field SoilMoisture CH16
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Air CH2
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Depth CH2
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Heat CH2
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Air CH3
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Depth CH3
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Heat CH3
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Air CH4
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Depth CH4
weewxd[647060]: INFO user.ecowitt_http: no Data field LDS_Heat CH4
weewxd[647060]: INFO user.ecowitt_http: Problem with key 
weewxd[647060]: INFO user.ecowitt_http: genArchiveRecords: Yielding archive record 2025-07-03 15:56:00 CEST (1751550960)
weewxd[647060]: INFO user.sunrainduration: Archiv-Record-Interval=300 sec
weewxd[647060]: INFO weewx.engine: Starting main packet loop.
weewxd[647060]: INFO user.ecowitt_http: genArchiveRecords: Using MAC address: 5C:01:3B:46:C3:FF
weewxd[647060]: INFO user.ecowitt_http: Processing history file '202507A.csv' from  GW3000A_V1.0.9 at 192.168.0.110
weewxd[647060]: INFO user.ecowitt_http: Processing history file '202507Allsensors_A.csv' from  GW3000A_V1.0.9 at 192.168.0.110
weewxd[647060]: INFO user.ecowitt_http: genArchiveRecords: Using MAC address: 5C:01:3B:46:C3:9F
weewxd[647060]: INFO user.ecowitt_http: Processing history file '202507A.csv' from  GW3000A_V1.0.9 at 192.168.0.110
weewxd[647060]: INFO user.ecowitt_http: Problem with key Time
weewxd[647060]: INFO user.ecowitt_http: Problem with key Timestamp
weewxd[647060]: INFO user.ecowitt_http: Processing history file '202507Allsensors_A.csv' from  GW3000A_V1.0.9 at 192.168.0.110
new:
weewxd[790259]: INFO user.ecowitt_http: Using 'rain.0x13.val' for rain total
weewxd[790259]: INFO user.ecowitt_http: Using 'piezoRain.0x13.val' for piezo rain total
weewxd[790259]: INFO user.ecowitt_http: skipping rain measurement of 353.3: no last rain
weewxd[790259]: INFO user.ecowitt_http: skipping piezo rain measurement of 345.9: no last rain
weewxd[790259]: INFO user.ecowitt_http: Skipping lightning count of 11: no last count


```
None of the provided configuration options (weectl station reconfigure --driver=user.ecowitt_http --config=/etc/weewx/weewx4.conf) have been tested!
