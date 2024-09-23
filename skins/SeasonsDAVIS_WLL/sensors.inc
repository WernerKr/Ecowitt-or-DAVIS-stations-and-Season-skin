## sensors module for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights
#errorCatcher Echo
#encoding UTF-8

## this is a conditional display of sensor data, including connectivity,
## battery status, and various voltages.  if there are no data available,
## then this degenerates to nothing displayed.
## To include GW1000 sensor battery state information in the Seasons skin
## Sensor Panel list the sensor battery states to display in the
## $sensor_batt_data list. Sensors will be displayed in the order listed. Each
## entry is in the format:
##      (WeeWX sensor battery state field name, decode function name)
## where 'WeeWX sensor battery state field name' is the WeeWX field holding the
## battery state data and 'decode function name' is set as follows depending on
## the sensor type:
##      WH24: 'get_battery_status'
##      WH25: 'get_battery_status'
##      WH26: 'get_battery_status'
##      WH31: 'get_battery_status'
##      WH32: 'get_battery_status'
##      WH40: 'get_battery_status'
##      WH65: 'get_battery_status'
##      WH68: 'get_battery_status'

##      WH41/WH43 'get_multi_battery_status'
##      WH45: 'get_multi_battery_status'
##      WH55: 'get_multi_battery_status'
##      WH57: 'get_multi_battery_status'
##

#set $allways_lang = False
#set $use_lang = False
#try
 #if $SKIN_VERSION != '' or $allways_lang == True
  #set $use_lang = True
 #end if
#except
 #pass
#end try

## remember the current time - we will use it more than once.
#import time
#set $now = time.time()

## use this span to determine whether there are any data to consider.
#if $use_lang
 #set $recent=$span($day_delta=30, boundary='midnight')
#else
 #set $recent=$span($day_delta=30)
#end if

## provide an indication of how much time has passed since the last sensor
## reading.


#def get_time_deltaX($last_ts, $now)
  #if $last_ts
    #set $delta = int($now - $last_ts)
    #set $delta = 80
    #if $delta < 60
   
    #elif $delta < 3600
     #set $minutes = int($delta / 60)
$minutes $gettext('minutes ago')
    #elif $delta < 86400
      #set $hours = int($delta / 3600)
$hours $gettext('hours ago')
    #else
      #set $days = int($delta / 86400)
$days $gettext('days ago')
    #end if
  #else
$gettext('never')
  #end if
#end def
##

#def get_time_delta($last_ts, $now)
  #if $last_ts
    #set $delta = int($now - $last_ts)
    ##set $delta = 87400
    #if $delta < 60
  
#elif $delta < 3600
      #set $minutes = int($delta / 60)
$minutes minutes ago
    #elif $delta < 86400
      #set $hours = int($delta / 3600)
$hours hours ago
    #else
      #set $days = int($delta / 86400)
$days days ago
    #end if
  #else
never
  #end if
#end def

#def sig_out($sstate)
 #if $sstate != None
  #set $sh_1 = float($sstate)
  #set $x = int($sh_1 * 100) / 100
   <td class="data">$x</td>
 #end if
#end def

#set $ecowitt_hw = [('GW1000'),
                    ('GW1100'),
                    ('GW2000'),
                    ('WH2650'),
                    ('WH2680'),
                    ('WS1900'),
                    ('WN1980'),
                    ('HP2550'),
                    ('ecowitt-client'),
                    ]

#set $ecowitt = 0
#for $x in $ecowitt_hw
  #if $x in $station.hardware
        #set $ecowitt = 1
  #end if
#end for
##

#set $sensor_batt_data = [('pm25_Batt1', 'get_multi_battery_status'),
                          ('pm25_Batt2', 'get_multi_battery_status'),
                          ('pm25_Batt3', 'get_multi_battery_status'),
                          ('pm25_Batt4', 'get_multi_battery_status'),
                          ('co2_Batt', 'get_multi_battery_status'),
                          ('leak_Batt1', 'get_multi_battery_status'),
                          ('leak_Batt2', 'get_multi_battery_status'),
                          ('leak_Batt3', 'get_multi_battery_status'),
                          ('leak_Batt4', 'get_multi_battery_status'),
                          ('lightning_Batt', 'get_multi_battery_status')
                         ]
##
#set $signal_data = [('wh24_sig'),
                     ('wh25_sig'),
                     ('wh26_sig'),
                     ('wh31_ch1_sig'),
                     ('wh31_ch2_sig'),
                     ('wh31_ch3_sig'),
                     ('wh31_ch4_sig'),
                     ('wh31_ch5_sig'),
                     ('wh31_ch6_sig'),
                     ('wh31_ch7_sig'),
                     ('wh31_ch8_sig'),
                     ('wh32_sig'),                     
                     ('wn34_ch1_sig'),
                     ('wn34_ch2_sig'),
                     ('wn34_ch3_sig'),
                     ('wn34_ch4_sig'),
                     ('wn34_ch5_sig'),
                     ('wn34_ch6_sig'),
                     ('wn34_ch7_sig'),
                     ('wn34_ch8_sig'),
                     ('wn35_ch1_sig'),
                     ('wn35_ch2_sig'),
                     ('wn35_ch3_sig'),
                     ('wn35_ch4_sig'),
                     ('wn35_ch5_sig'),
                     ('wn35_ch6_sig'),
                     ('wn35_ch7_sig'),
                     ('wn35_ch8_sig'),
                     ('wh40_sig'),
                     ('wh41_ch1_sig'),
                     ('wh41_ch2_sig'),
                     ('wh41_ch3_sig'),
                     ('wh41_ch4_sig'),
                     ('wh45_sig'),
                     ('wh51_ch1_sig'),
                     ('wh51_ch2_sig'),
                     ('wh51_ch3_sig'),
                     ('wh51_ch4_sig'),
                     ('wh51_ch5_sig'),
                     ('wh51_ch6_sig'),
                     ('wh51_ch7_sig'),
                     ('wh51_ch8_sig'),
                     ('wh55_ch1_sig'),
                     ('wh55_ch2_sig'),
                     ('wh55_ch3_sig'),
                     ('wh55_ch4_sig'),
                     ('wh57_sig'),
                     ('wh68_sig'),
                     ('ws80_sig'),
                     ('ws90_sig'),
                    ]

#set $conns = [ "rxCheckPercent", "signal1", "signal1_2", "signal2", "signal3", "signal4", "signal5", "signal6", "signal7", "signal8", "signalr", "signalw", "signala" ]
##
#set $battery_statuses = [ "outTempBatteryStatus", "inTempBatteryStatus", "windBatteryStatus", "rainBatteryStatus", "hailBatteryStatus", "snowBatteryStatus", "uvBatteryStatus", "txBatteryStatus", "txBatteryStatus_2", "batteryStatus1", "batteryStatus2", "batteryStatus3", "batteryStatus4", "batteryStatus5", "batteryStatus6", "batteryStatus7", "batteryStatus8" ]
#set $battery_statuses_ecowitt = [ "wh24_batt", "wh25_batt", "wh26_batt", "wh65_batt", "wh68_batt" ]
##set $battery_statuses_check = [ "txBatteryStatus", "txBatteryStatus_2", "batteryStatus1", "batteryStatus2", "batteryStatus3", "batteryStatus4", "batteryStatus5", "batteryStatus6", "batteryStatus7", "batteryStatus8" ]
#set $battery_statuses_check = [ "txBatteryStatus", "txBatteryStatus_2", "batteryStatus2", "batteryStatus7", "batteryStatus8" ]
##
#set $voltages = [("consBatteryVoltage",2.8),
("heatingVoltage",11.8),
("supplyVoltage",11.8),
("referenceVoltage",3.3),
("windBatteryStatus",2.4),
("hailBatteryStatus",2.4),
("ws90cap_volt",2.4),
("rainBatteryStatus",1.2),
("soilMoistBatt1",1.2),
("soilMoistBatt2",1.2),
("soilMoistBatt3",1.2),
("soilMoistBatt4",1.2),
("soilMoistBatt5",1.2),
("soilMoistBatt6",1.2),
("soilMoistBatt7",1.2),
("soilMoistBatt8",1.2),
("soilTempBatt1",1.2),
("soilTempBatt2",1.2),
("soilTempBatt3",1.2),
("soilTempBatt4",1.2),
("soilTempBatt5",1.2),
("soilTempBatt6",1.2),
("soilTempBatt7",1.2),
("soilTempBatt8",1.2),
("leafTempBatt1",1.2),
("leafTempBatt2",1.2),
("leafTempBatt3",1.2),
("leafTempBatt4",1.2),
("leafTempBatt5",1.2),
("leafTempBatt6",1.2),
("leafTempBatt7",1.2),
("leafTempBatt8",1.2),
("leafWetBatt1",1.2),
("leafWetBatt2",1.2),
("leafWetBatt3",1.2),
("leafWetBatt4",1.2),
("leafWetBatt5",1.2),
("leafWetBatt6",1.2),
("leafWetBatt7",1.2),
("leafWetBatt8",1.2),
]

#set $testvoltage = False
#if $testvoltage
#set $voltagesno = [("ws1900batt",2.4),
("ws80_batt",2.4),
("ws80batt",2.4),
("ws90_batt",2.4),
("ws90batt",2.4),
("ws90cap_volt",2.4),
]
#end if

#def get_battery_status($x)
#if $x is None
 <span class="status_unknown">N/A</span>
#elif $x == 1
 <span class="status_low">LOW</span>
#else
<span class="status_ok">OK</span>
#end if
#end def
##
#def get_multi_battery_status($x)
 ##if $x is None
 ##<span class="status_unknown">N/A</span>
  #if $x <= 1
<span class="status_low">LOW</span>
  #elif $x <= 5
<span class="status_ok">OK</span>
  #elif $x == 6
<span class="status_dc">DC</span>
  #end if
#end def
##
#def get_conn_status($x)
#if $x == 0
<span class="status_ok">OK</span>
#elif $x ==2
<span class="status_low">Scanning</span>
#else
<span class="status_dc">Synched</span>
#end if
#end def


## first see what sensor data are available

#set $have_conn = 0
#for $x in $conns
  #if $getattr($current, $x).has_data
    #set $have_conn = 1
  #end if
#end for


#set $have_battery_status = 0
#for $x in $battery_statuses
  #if $getattr($current, $x).has_data
    #set $have_battery_status = 1
  #end if
#end for

#for $x in $sensor_batt_data
  #try
      #if getattr($current, $x[0]).has_data
        #set $have_battery_status = 1
      #end if
  #except (AttributeError, TypeError)
    ## there is no battery state data for that sensor
    #pass
  #end try
#end for
##
#set $have_voltage = 0
#for $x in $voltages
  #if $getattr($current, $x[0]).has_data
    #set $have_voltage = 1
  #end if
#end for

#set $_state = 1
#if $station.hardware == "WeatherLinkLiveUDP"
 #set $have_voltage = 0
 #set $_state = 0
#end if

#set $have_signal = 0
#for $x in $signal_data
  #if $getattr($current, $x).has_data
    #set $have_signal = 1
  #end if
#end for

## now display the available data only


#if $have_conn or $have_battery_status or $have_voltage
<div id='sensors_widget' class="widget">

  <div class="widget_title">
    #if $_state
    #if $use_lang
    <a href="telemetry.html">$gettext("Sensor Status")</a>
    #else
    <a href="telemetry.html">Sensor Status</a>
    #end if
    <a class="widget_control"
      onclick="toggle_widget('sensors')">&diams;</a>
    #else
    #if $use_lang
      $gettext("Sensor Status")
    #else
      Sensor Status
    #end if
    #end if 
  </div>
  <div class="widget_contents">
  <table>

#if $have_conn
    #if $use_lang
     <tr><th>$gettext("Connectivity")</th><th></th></tr>
    #else
     <tr><th>Connectivity</th><th></th></tr>
    #end if

    #try
      #set $test = 'signalQuality'
      #if $getattr($current($max_delta=3600,$data_binding='davishealthapi_binding'), $test).has_data
       <tr>
       #set $xv = $getattr($current($max_delta=3600,$data_binding='davishealthapi_binding'), $test)
       <td class="label">$obs.label[$test]</td>
       <td class="data">$xv</td>
       </tr>  
      #end if
    #except (AttributeError, TypeError)
      ## there is no data for that sensor
      #pass
    #end try

    #try
      #set $test = 'signalQuality1'
      #if $getattr($current($max_delta=3600,$data_binding='davishealthapi_binding'), $test).has_data
        <tr>
        #set $xv = $getattr($current($max_delta=3600,$data_binding='davishealthapi_binding'), $test)
        <td class="label">$obs.label[$test]</td>
        <td class="data">$xv</td>
        </tr> 
      #end if
    #except (AttributeError, TypeError)
      ## there is no data for that sensor
      #pass
    #end try

 #for $x in $conns
  #if $getattr($recent, $x).has_data or $getattr($current, $x).has_data
    <tr>
      <td class="label">$obs.label[$x]</td>
      #set $xv = $getattr($current, $x) 
      #if $x == 'rxCheckPercent'
       <td class="data">$xv</td> 
      #elif $ecowitt == 0
       <td class="data">$get_conn_status($xv.raw)</td>
      #else
       #set $xv = getattr($current, $x).format("%.0f")
       <td class="data">$xv</td>
      #end if
      #if $x != 'signal1_2' 
       #set $lasttime = $getattr($recent, $x).lasttime.raw
       <td class="timestamp">$get_time_delta($lasttime, $now)</td>
      #end if
    </tr>
  #end if
 #end for
#end if

#if $have_battery_status
    #if $use_lang
     <tr><th>$gettext("Battery Status")</th><th></th></tr>
    #else
     <tr><th>Battery Status</th><th></th></tr>
    #end if
 #for $x in $battery_statuses
  #if $getattr($recent, $x).has_data or $getattr($current, $x).has_data
    #if ( ( (($x != 'windBatteryStatus') and ($x != 'rainBatteryStatus') and ($x != 'hailBatteryStatus')) ) and $ecowitt == 1 ) or $ecowitt == 0
    ##if ( ( (($x != 'windBatteryStatus') and ($x != 'rainBatteryStatus') and ($x != 'hailBatteryStatus')) or ($x == 'wh24_batt') or ($x == 'wh25_batt') or ($x == 'wh26_batt')) and $ecowitt == 1 ) or $ecowitt == 0
    ##if ( (($x == 'wh24_batt') or ($x == 'wh25_batt') or ($x == 'wh26_batt')) and $ecowitt == 1 ) or $ecowitt == 0
    <tr>
      <td class="label">$obs.label[$x]</td>
      #set $xv = $getattr($current, $x) 
      <td class="data">$get_battery_status($xv.raw)</td>
      #if $x != 'txBatteryStatus_2'
       #set $lasttime = $getattr($recent, $x).lasttime.raw
       <td class="timestamp">$get_time_delta($lasttime, $now)</td>
      #end if
    </tr>
    #end if
  #else
   #if $station.hardware == "WeatherLinkLiveUDP"
    #for $xx in $battery_statuses_check
    #if $x == $xx
    <tr>
      <td class="label"><font color='red'>$obs.label[$xx]</font></td>
      <td class="data"><font color='red'>N/A</font></td>
    </tr>
    #end if
    #end for   
   #end if

  #end if
 #end for

 #for $x in $battery_statuses_ecowitt
   #if ($getattr($recent, $x).has_data or $getattr($current, $x).has_data) and $ecowitt == 1 
    <tr>
      <td class="label">$obs.label[$x]</td>
      #set $xv = $getattr($current, $x) 
      <td class="data">$get_battery_status($xv.raw)</td>
    </tr>
   #end if
 #end for

 #for $battery in $sensor_batt_data
    #try
      #if getattr($recent, $battery[0]).has_data
        #set $state = getattr(self, $battery[1])(getattr($current, $battery[0]).raw)
        #set $vstate = getattr($current, $battery[0]).format("%.0f")
        #if $vstate == '6'
           #set $vstate = ""
           #set $graf = "Batt6x.png"
        #elif $vstate == '5'
         #set $graf = "Batt5.png"
        #elif $vstate == '4'
         #set $graf = "Batt4.png"
        #elif $vstate == '3'
         #set $graf = "Batt3.png"
        #elif $vstate == '2'
         #set $graf = "Batt2.png"
        #elif $vstate == '1'
         #set $graf = "Batt1.png"
        #else
         #set $graf = "Batt0.png"
        #end if
        <tr>
          <td class="label">$obs.label[$battery[0]]</td>
          #if $graf == "Batt6.png"
           <td class="data">$state  <font color=#dfdfdf>$vstate</font></td>
          #else
           <td class="data"><img src=$graf style="height: 10px; width: 6px;" > $state  <font color=#dfdfdf>$vstate</font></td>
          #end if
          #set $lasttime = $getattr($recent, $battery[0]).lasttime.raw
          <td class="timestamp"> $get_time_delta($lasttime, $now)</td>
        </tr>
      #end if
    #except (AttributeError, TypeError)
      ## there is no battery state data for that sensor
      #pass
    #end try
 #end for

#end if

#if $have_voltage
    #if $use_lang
     <tr><th>$gettext("Voltage")</th><th></th></tr>
    #else
     <tr><th>Voltage</th><th></th></tr>
    #end if
#for $x in $voltages
  #if $getattr($recent, $x[0]).has_data
    #if ((($x[0] == 'windBatteryStatus') or ($x[0] == 'rainBatteryStatus') or ($x[0] == 'hailBatteryStatus')) and $ecowitt == 1 ) or $x[0] not in $battery_statuses
    <tr>
      <td class="label">$obs.label[$x[0]]</td>
      #set $xv = $getattr($current, $x[0])
      #set $xx = getattr($current, $x[0]).raw
      #if  $xx == None
        <td class="data"><span class="status_unknown">N/A</span></td>
      ##elif $xx <= $x[1]
      ##  <td class="data"><span class="status_low">$xv.format("%.2f") <font color=#dfdfdf>0</font></span></td>
      #else
        #if $xx > 2.0
         #set $xxv = float($xx/2)
        #else
         #set $xxv = float($xx)
        #end if
        #set $xxv = round($xxv, 4)
        #if $xxv > 1.45
         #set $vv = 5
         #set $graf = "Batt5.png"
        #elif $xxv >= 1.4
         #set $vv = 4
         #set $graf = "Batt4.png"
        #elif $xxv > 1.3
         #set $vv = 3
         #set $graf = "Batt3.png"
        #elif $xxv > 1.2
         #set $vv = 2
         #set $graf = "Batt2.png"
        #elif $xxv >= 0.1
         #set $vv = 1
         #set $graf = "Batt1.png"
        #else
         #set $vv = 0
         #set $graf = "Batt0.png"
        #end if
        ##if $xx <= $x[1]
        #if $xx == 0
         <td class="data"><span class="status_low">$xv.format("%.2f") <font color=#dfdfdf>$vv</font></span></td>
        #else
         ##<td class="data">$xv.format("%.2f") <font color=#dfdfdf>$vv</font></td>
         <td class="data"><img src=$graf style="height: 10px; width: 6px;" > $xv.format("%.2f") <font color=#dfdfdf>$vv</font></td>
         ##<td class="data">$xv.format("%.2f")</td>
        #end if 
      #end if
      #if $ecowitt == 1
       #set $lasttime = $getattr($recent, $battery[0]).lasttime.raw
       <td class="timestamp">$get_time_delta($lasttime, $now)</td>
      #end if
    </tr>
    #end if
  #end if
#end for

#if $testvoltage
 #for $x in $voltagesno
 #try
  #if $getattr($current, $x[0]).has_data
    <tr>
      <td class="label">$obs.label[$x[0]]</td>
      #set $xv = $getattr($current, $x[0])
      #set $xx = getattr($current, $x[0]).raw
      #if  $xx == None
        <td class="data"><span class="status_unknown">N/A</span></td>
      #elif $xx <= $x[1]
        <td class="data"><span class="status_low">$xv.format("%.2f")</span></td>
      #else
        <td class="data">$xv.format("%.2f")</td>
      #end if
    </tr>
  #end if
 #except
  #pass
 #end try
 #end for
#end if

#end if


#if $have_signal and $ecowitt == 1
 #if $use_lang
   <tr><th>$gettext("Signal")</th><th></th></tr>
 #else
   <tr><th>Signal</th><th></th></tr>
 #end if
 #for $signal in $signal_data
    #try
      #if getattr($current, $signal).has_data
        #set $sstate = getattr($current, $signal).raw
        <tr>
         <td class="label">$obs.label[$signal]</td>
         $sig_out($sstate)
         ##<td class="data">$sstate</td>
        </tr>
      #end if
    #except (AttributeError, TypeError)
      ## there is no signal state data for that sensor
      #pass
    #end try
 #end for

#end if


#if ($ecowitt == 1) and (($getattr($current, 'rain_source').has_data) or ($getattr($current, 'gain0').has_data))
 #if $use_lang
   <tr><th>$gettext("Rain")</th><th></th></tr>
 #else
   <tr><th>Rain</th><th></th></tr>
 #end if

    #try
      #set $test = 'rain_source'
      #if $getattr($current, $test).has_data
        <tr>
        #set $xv = $getattr($current, $test).raw
        ##set $xx = int($xv) 
        #if $xv == 2
          #if $use_lang
           #set $txt=$gettext("Piezoelectric")
          #else
           #set $txt = "Piezoelectric"
          #end if
        #elif $xv == 1
          #if $use_lang
           #set $txt=$gettext("Tratitional")
          #else
           #set $txt = "Tratitional"
          #end if
        #else
          #if $use_lang
           #set $txt=$gettext("No rain gauge")
          #else
           #set $txt = "No rain gauge"
          #end if
        #end if 
        <td class="label">$obs.label[$test]</td>
        <td class="data">$txt</td>
        </tr> 
      #end if
    #except (AttributeError, TypeError)
      ## there is no data for that sensor
      #pass
    #end try

    #try
      #set $test = 'rain_day_reset'
      #if $getattr($current, $test).has_data
        <tr>
        #set $xv = $getattr($current, $test).raw
        #if $xv == 0
            #set $txt = "00:00"
        #elif $xv == 1
            #set $txt = "01:00"
        #elif $xv == 2
            #set $txt = "02:00"
        #elif $xv == 3
            #set $txt = "03:00"
        #elif $xv == 4
            #set $txt = "04:00"
        #elif $xv == 5
            #set $txt = "05:00"
        #elif $xv == 6
            #set $txt = "06:00"
        #elif $xv == 7
            #set $txt = "07:00"
        #elif $xv == 8
            #set $txt = "08:00"
        #elif $xv == 9
            #set $txt = "09:00"
        #else
            #set $txt = "??:??"
        #end if
        <td class="label">$obs.label[$test]</td>
        <td class="data">$txt</td>
        </tr> 
      #end if
    #except (AttributeError, TypeError)
      ## there is no data for that sensor
      #pass
    #end try

    #try
      #set $test = 'rain_week_reset'
      #if $getattr($current, $test).has_data
        <tr>
        #set $xv = $getattr($current, $test).raw
        #if $xv == 0
          #if $use_lang
           #set $txt=$gettext("Sunday")
          #else
           #set $txt = "Sunday"
          #end if
        #elif $xv == 1
          #if $use_lang
           #set $txt=$gettext("Monday")
          #else
           #set $txt = "Monday"
          #end if
        #else
            #set $txt = "??????"
        #end if
        <td class="label">$obs.label[$test]</td>
        ##<td class="data">$xv</td>
        <td class="data">$txt</td>
        </tr> 
      #end if
    #except (AttributeError, TypeError)
      ## there is no data for that sensor
      #pass
    #end try

    #try
      #set $test = 'rain_annual_reset'
      #if $getattr($current, $test).has_data
        <tr>
        #set $xv = $getattr($current, $test).raw
        #if $xv == 0
          #if $use_lang
           #set $txt=$gettext("January")
          #else
           #set $txt = "January"
          #end if
        #elif $xv == 1
          #if $use_lang
           #set $txt=$gettext("February")
          #else
           #set $txt = "February"
          #end if
        #elif $xv == 2
          #if $use_lang
           #set $txt=$gettext("March")
          #else
           #set $txt = "March"
          #end if
        #elif $xv == 3
          #if $use_lang
           #set $txt=$gettext("April")
          #else
           #set $txt = "April"
          #end if
        #elif $xv == 4
          #if $use_lang
           #set $txt=$gettext("May")
          #else
           #set $txt = "May"
          #end if
        #elif $xv == 5
          #if $use_lang
           #set $txt=$gettext("June")
          #else
           #set $txt = "June"
          #end if
        #elif $xv == 6
          #if $use_lang
           #set $txt=$gettext("July")
          #else
           #set $txt = "July"
          #end if
        #elif $xv == 11
          #if $use_lang
           #set $txt=$gettext("December")
          #else
           #set $txt = "December"
          #end if
        #else
            #set $txt = "??????"
        #end if
        <td class="label">$obs.label[$test]</td>
        <td class="data">$txt</td>
        </tr> 
      #end if
    #except (AttributeError, TypeError)
      ## there is no data for that sensor
      #pass
    #end try

    #try
      #set $test = 'raingain'
      #if $getattr($current, $test).has_data
        <tr>
        #set $xv = $getattr($current, $test)
        <td class="label">$obs.label[$test]</td>
        <td class="data">$xv.format("%.2f")</td>
        </tr> 
      #end if
    #except (AttributeError, TypeError)
      ## there is no data for that sensor
      #pass
    #end try
    #try
      #set $test = 'gain0'
      #if $getattr($current, $test).has_data
        <tr>
        #set $xv = $getattr($current, $test)
        <td class="label">$obs.label[$test]</td>
        <td class="data">$xv.format("%.2f")</td>
        </tr> 
      #end if
    #except (AttributeError, TypeError)
      ## there is no data for that sensor
      #pass
    #end try
    #try
      #set $test = 'gain1'
      #if $getattr($current, $test).has_data
        <tr>
        #set $xv = $getattr($current, $test)
        <td class="label">$obs.label[$test]</td>
        <td class="data">$xv.format("%.2f")</td>
        </tr> 
      #end if
    #except (AttributeError, TypeError)
      ## there is no data for that sensor
      #pass
    #end try
    #try
      #set $test = 'gain2'
      #if $getattr($current, $test).has_data
        <tr>
        #set $xv = $getattr($current, $test)
        <td class="label">$obs.label[$test]</td>
        <td class="data">$xv.format("%.2f")</td>
        </tr> 
      #end if
    #except (AttributeError, TypeError)
      ## there is no data for that sensor
      #pass
    #end try
    #try
      #set $test = 'gain3'
      #if $getattr($current, $test).has_data
        <tr>
        #set $xv = $getattr($current, $test)
        <td class="label">$obs.label[$test]</td>
        <td class="data">$xv.format("%.2f")</td>
        </tr> 
      #end if
    #except (AttributeError, TypeError)
      ## there is no data for that sensor
      #pass
    #end try
    #try
      #set $test = 'gain4'
      #if $getattr($current, $test).has_data
        <tr>
        #set $xv = $getattr($current, $test)
        <td class="label">$obs.label[$test]</td>
        <td class="data">$xv.format("%.2f")</td>
        </tr> 
      #end if
    #except (AttributeError, TypeError)
      ## there is no data for that sensor
      #pass
    #end try

#end if


  </table>
  </div>

</div>
#end if
