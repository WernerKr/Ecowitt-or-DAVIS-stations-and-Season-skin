## sensors module for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights

## Modified to work with the DavisConsoleHealthAPI extension to display device info

#errorCatcher Echo
#encoding UTF-8

## this is a conditional display of sensor data, including connectivity,
## battery status, and various voltages.  if there are no data available,
## then this degenerates to nothing displayed.

#def get_battery_status($x)
#if $x == 0
<span class="status_ok">$gettext("OK")</span>
#else
<span class="status_low">$gettext("LOW")</span>
#end if
#end def

#set $conns = ["signalQuality", "rssiC",
                "rxCheckPercent", "rssi", "afc", "txID", "packets_received", "packets_missed", "crc_error", "resyncs",
                "rxCheckPercent_2", "rssi_2", "afc_2", "txID_2", "packets_received_2", "packets_missed_2", "crc_error_2", "resyncs_2",
                "rxCheckPercent2", "rssi2", "afc2", "txID2", "packets_received2", "packets_missed2", "crc_error2", "resyncs2",
                "rxCheckPercent3", "rssi3", "afc3", "txID3", "packets_received3", "packets_missed3", "crc_error3", "resyncs3",
                "rxCheckPercent4", "rssi4", "afc4", "txID4", "packets_received4", "packets_missed4", "crc_error4", "resyncs4",
                "rxCheckPercent5", "rssi5", "afc5", "txID5", "packets_received5", "packets_missed5", "crc_error5", "resyncs5",
                "rxCheckPercent6", "rssi6", "afc6", "txID6", "packets_received6", "packets_missed6", "crc_error6", "resyncs6",
                "rxCheckPercent7", "rssi7", "afc7", "txID7", "packets_received7", "packets_missed7", "crc_error7", "resyncs7",
                "rxCheckPercent8", "rssi8", "afc8", "txID8", "packets_received8", "packets_missed8", "crc_error8", "resyncs8", 
                "rxCheckPercentr", "rssir", "afcr", "txIDr", "packets_receivedr", "packets_missedr", "crc_errorr", "resyncsr", 
                "rxCheckPercentw", "rssiw", "afcw", "txIDw", "packets_receivedw", "packets_missedw", "crc_errorw", "resyncsw", 
]

#set $volt = [ "txBatteryVolt", "supercapVolt", "solarVolt", "txBatteryVolt_2", "supercapVolt_2", "solarVolt_2", ]

#set $battery_statuses = [ "txBatteryFlag" ]
#set $max_battery_statuses = 5

#set $transm = [ "freeMemC", "systemFreeSpaceC", "iFreeSpaceC", "queueKilobytesC", "databaseKilobytesC" ]

##

<div id='sensors_widget' class="widget">
  <div class="widget_title">
    $gettext("Status Davis Console")
    <a class="widget_control"
      onclick="toggle_widget('sensors')">&diams;</a>
  </div>
  <div class="widget_contents">
  <table>

    <tr><th>$gettext("Connectivity")</th><th></th></tr>
 #for $x in $conns
  #if $getattr($latest, $x).has_data
    <tr>
      #if "rxCheckPercent" in $x
       #set $color = 'blue'
      #else
       #set $color = 'black'
      #end if
      <td class="label"><font color=$color>$obs.label[$x]</font></td>
      #set $xv = $getattr($latest, $x) 
      <td class="data">$xv</td>
    </tr>
  #end if
 #end for

    <tr><th>$gettext("Power Status")</th><th></th></tr>
#if $current($max_delta=3600).consoleBatteryC.has_data
    <tr>
      <td class="label">$obs.label.consoleBatteryC</td>
      <td class="data">$current($max_delta=3600).consoleBatteryC.format("%.0f")</td>
    </tr>
#end if
#if $current($max_delta=3600).batteryPercentC.has_data
    <tr>
      <td class="label">$obs.label.batteryPercentC</td>
      <td class="data">$current($max_delta=3600).batteryPercentC</td>
    </tr>
    <tr>
      <td class="label">$obs.label.batteryCurrentC</td>
      <td class="data">$current($max_delta=3600).batteryCurrentC.format("%.3f")</td>
    </tr>
#end if
#if $current($max_delta=3600).batteryConditionC.has_data
    <tr>
      <td class="label">$obs.label.batteryConditionC</td>
      <td class="data">$current($max_delta=3600).batteryConditionC</td>
    </tr>
#end if
#if $current($max_delta=3600).batteryStatusC.has_data
    <tr>
      <td class="label">$obs.label.batteryStatusC</td>
      <td class="data">$current($max_delta=3600).batteryStatusC</td>
    </tr>
#end if
#if $current($max_delta=3600).batteryTempC.has_data
    <tr>
      <td class="label">$obs.label.batteryTempC</td>
      <td class="data">$current($max_delta=3600).batteryTempC</td>
    </tr>
#end if
#if $current($max_delta=3600).chargerPluggedC.has_data
    <tr>
      <td class="label">$obs.label.chargerPluggedC</td>
      <td class="data">$current($max_delta=3600).chargerPluggedC</td>
    </tr>
#end if
#if $current($max_delta=3600).batteryCycleCountC.has_data
    <tr>
      <td class="label">$obs.label.batteryCycleCountC</td>
      <td class="data">$current($max_delta=3600).batteryCycleCountC</td>
    </tr>
#end if

#set $count = 0
 #if $count != 0
 #for $x in $battery_statuses 
  #set $count = $count + 1  
  #if $getattr($current($max_delta=3600), $x).has_data
    <tr>
      <td class="label">$obs.label[$x]</td>
      #set $xv = $getattr($current($max_delta=3600), $x) 
      <td class="data">$get_battery_status($xv.raw)</td>
    </tr>
  #else
   #if $count <= $max_battery_statuses
    <tr>
      <td class="label"><font color='red'>$obs.label[$x]</font></td>
      <td class="data"><font color='red'>N/A</font></td>
    </tr>
   #end if
  #end if
 #end for
 #end if

<tr><th>$gettext("Voltage")</th><th></th></tr>
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

 <tr><th>$gettext("Data Transmission")</th><th></th></tr>

 #for $x in $transm
  #if $getattr($current($max_delta=3600), $x).has_data
    <tr>
      #if 'packetStreak' in $x
       #set $color = 'green'
      #else
       #set $color = 'black'
      #end if
      <td class="label"><font color=$color>$obs.label[$x]</font></td>
      #set $xv = $getattr($current($max_delta=3600), $x) 
      <td class="data">$xv</td>
    </tr>
  #end if
 #end for

    <tr>
      <td class="label">$obs.label.rxKilobytesC</td>
      <td class="data">$current($max_delta=3600).rxKilobytesC</td>
    </tr>
    <tr>
      <td class="label">$obs.label.txKilobytesC</td>
      <td class="data">$current($max_delta=3600).txKilobytesC</td>
    </tr>

    <tr>
      <td class="label">$obs.label.localAPIQueriesC</td>
      <td class="data">$current($max_delta=3600).localAPIQueriesC</td>
    </tr>
    <tr>
      <td class="label">$obs.label.consoleApiLevelC</td>
      <td class="data">$current($max_delta=3600).consoleApiLevelC</td>
    </tr>

    <tr><th>$gettext("Information Console")</th><th></th></tr>

    <tr>
      <td class="label">$obs.label.appUptimeC</td>
      <td class="data">$current($max_delta=3600).appUptimeC.long_form(format_string="%(day)d%(day_label)s, %(hour)d:%(minute)02d:%(second)02d")</td>
    </tr>
    <tr>
      <td class="label">$obs.label.linkUptimeC</td>
      <td class="data">$current($max_delta=3600).linkUptimeC.long_form(format_string="%(day)d%(day_label)s, %(hour)d:%(minute)02d:%(second)02d")</td>
    </tr>
    <tr>
      <td class="label">$obs.label.connectionUptimeC</td>
      <td class="data">$current($max_delta=3600).connectionUptimeC.long_form(format_string="%(day)d%(day_label)s, %(hour)d:%(minute)02d:%(second)02d")</td>
    </tr>
    <tr>
      <td class="label">$obs.label.osUptimeC</td>
      <td class="data">$current($max_delta=3600).osUptimeC.long_form(format_string="%(day)d%(day_label)s, %(hour)d:%(minute)02d:%(second)02d")</td>
    </tr>

    <tr>
      <td class="label">$obs.label.consoleRadioVersionC</td>
      <td class="data">$current($max_delta=3600).consoleRadioVersionC</td>
    </tr>
    <tr>
      <td class="label">$obs.label.consoleSwVersionC</td>
      <td class="data">$current($max_delta=3600).consoleSwVersionC</td>
    </tr>
    <tr>
      <td class="label">$obs.label.consoleOsVersionC</td>
      <td class="data">$current($max_delta=3600).consoleOsVersionC</td>
    </tr>

    <tr>
      <td class="label">$obs.label.bootloaderVersionC</td>
      <td class="data">$current($max_delta=3600).bootloaderVersionC</td>
    </tr>
    <tr>
      <td class="label">$obs.label.clockSourceC</td>
      <td class="data">$current($max_delta=3600).clockSourceC</td>
    </tr>
    <tr>
      <td class="label">$obs.label.healthVersionC</td>
      <td class="data">$current($max_delta=3600).healthVersionC</td>
    </tr>


  </table>
  </div>

</div>
