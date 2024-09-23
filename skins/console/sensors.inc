#errorCatcher Echo
## sensors module for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights
#encoding UTF-8

## remember the current time - we will use it more than once.
#import time
#set $now = time.time()

#set $recent=$span($day_delta=30, boundary='midnight')

## provide an indication of how much time has passed since the last sensor
## reading.


#def get_time_delta($last_ts, $now)
  #if $last_ts
    #set $delta = int($now - $last_ts)
    ##set $delta = 87400
    #if $delta < 360
  
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

#set $ecowitt = 0

##

#set $signal_data = [ "rssiC", "signal1", "rxCheckPercent", "rssi",
                "signal_2", "rxCheckPercent_2", "rssi_2",
                "signal2", "rxCheckPercent2", "rssi2",
                "signal3", "rxCheckPercent3", "rssi3",
                "signal4", "rxCheckPercent4", "rssi4",
                "signal5", "rxCheckPercent5", "rssi5",
                "signal6", "rxCheckPercent6", "rssi6",
                "signal7", "rxCheckPercent7", "rssi7", 
                "signal8", "rxCheckPercent8", "rssi8",
                "signalr", "rxCheckPercentr", "rssir",
                "signalw", "rxCheckPercentw", "rssiw",
]

#set $volt = [ "txBatteryVolt", "supercapVolt", "solarVolt", "txBatteryVolt_2", "supercapVolt_2", "solarVolt_2", ]
##
#set $battery_statuses = [ "batteryStatusC", "txBatteryStatus", "txBatteryStatus_2", "batteryStatus1", "batteryStatus2", "batteryStatus3", "batteryStatus4", "batteryStatus5", "batteryStatus6", "batteryStatus7", "batteryStatus8", "rainBatteryStatus_2",  ]
##set $battery_statuses_check = [ "txBatteryStatus", "txBatteryStatus_2", "batteryStatus1", "batteryStatus2", "batteryStatus3", "batteryStatus4", "batteryStatus5", "batteryStatus6", "batteryStatus7", "batteryStatus8" ]
#set $battery_statuses_check = [ "txBatteryStatus", "txBatteryStatus_2", "batteryStatus2", "batteryStatus7", "batteryStatus8" ]
##
#set $testvoltage = False


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
#for $x in $signal_data
  #if $getattr($latest, $x).has_data
    #set $have_conn = 1
  #end if
#end for


#set $have_battery_status = 0
#for $x in $battery_statuses
  #if $getattr($latest, $x).has_data
    #set $have_battery_status = 1
  #end if
#end for


##
#set $have_voltage = 1


#set $_state = 1
#if $station.hardware == "WeatherLinkLiveUDP"
 #set $have_voltage = 0
 #set $_state = 0
#end if

#set $have_signal = 0
#for $x in $signal_data
  #if $getattr($latest, $x).has_data
    #set $have_signal = 1
  #end if
#end for

## now display the available data only


#if $have_conn or $have_battery_status or $have_voltage
<div id='sensors_widget' class="widget">

  <div class="widget_title">
    #if $_state
    <a href="telemetry.html">$gettext("Sensor Status")</a>
    <a class="widget_control"
      onclick="toggle_widget('sensors')">&diams;</a>
    #else
      $gettext("Sensor Status")
    #end if 
  </div>
  <div class="widget_contents">
  <table>

#if $have_voltage
     <tr><th>$gettext("Voltage")</th><th></th></tr>

#set $x = 'consoleBatteryC'
#if $getattr($latest, $x).has_data
    <tr>
      ##<td class="label">$obs.label.consoleBatteryC</td>
      ##<td class="data">$current($max_delta=3600,$data_binding='wx_binding').consoleBatteryC</td>
      <td class="label"><font color=$color>$obs.label[$x]</font></td>
      #set $xv = $getattr($latest, $x) 
      <td class="data">$xv</td>
    </tr>
#end if

#for $x in $volt
 #if $getattr($latest, $x).has_data
  <tr>
      <td class="label"><font color=$color>$obs.label[$x]</font></td>
      ##<td class="data">$latest.uvVolt1.format("%.3f")</td>
      #set $xv = $getattr($latest, $x).format("%.3f") 
      <td class="data">$xv</td>
  </tr>
 #end if 
#end for

#end if


#if $have_battery_status
     <tr><th>$gettext("Battery Status")</th><th></th></tr>
 #for $x in $battery_statuses
  #if $getattr($recent, $x).has_data or $getattr($current, $x).has_data
    #if $ecowitt == 0
    <tr>
      <td class="label">$obs.label[$x]</td>
      #set $xv = $getattr($latest, $x) 
      <td class="data">$get_battery_status($xv.raw)</td>
       #set $lasttime = $getattr($recent, $x).lasttime.raw
       <td class="timestamp">$get_time_delta($lasttime, $now)</td>
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

#end if



##if $have_signal
<tr><th>$gettext("Connectivity")</th><th></th></tr>
 #for $x in $signal_data
  #if $getattr($latest, $x).has_data
    <tr>
      #set $xv = $getattr($latest, $x) 
      #if 'signal' in $x
       #set $color = 'blue'
      <td class="label"><font color=$color>$obs.label[$x]</font></td>
       <td class="data">$get_conn_status($xv.raw)</td>
      #elif 'rssiC' in $x
       #set $color = 'black'
      <td class="labelbold"><font color=$color>$obs.label[$x]</font></td>
       <td class="data">$xv</td>
      #else
       #set $color = 'black'
      <td class="label"><font color=$color>$obs.label[$x]</font></td>
      #set $xv = $getattr($latest, $x) 
      <td class="data">$xv</td>
      #end if
    </tr>
  #end if
 #end for
##end if




  </table>
  </div>

</div>
#end if
