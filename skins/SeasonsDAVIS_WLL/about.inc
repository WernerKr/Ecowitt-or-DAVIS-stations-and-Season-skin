## about module for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights
#errorCatcher Echo
#encoding UTF-8

#set $allways_lang = False
#set $use_lang = False
#try
 #if $SKIN_VERSION != '' or $allways_lang == True
  #set $use_lang = True
 #end if
#except
 #pass
#end try

#if not $use_lang
<div id='about_widget' class="widget">
  <div class="widget_title">
    About this weather station
    <a class="widget_control"
      onclick="toggle_widget('about')">&diams;</a>
  </div>
  <div class="widget_contents">
  <table>
    <tr>
      <td class="label">Hardware</td>
      <td class="data">$station.hardware</td>
    </tr>
   #try
    #if $current.runtime.has_data
    <tr> 
      <td class="label">Station uptime</td>
      <td class="data">$current.runtime</td>
    </tr>
    #end if
    #if $current.ws_interval.has_data
    <tr> 
      <td class="label">Station interval</td>
      <td class="data">$current.ws_interval.format("%.0f") sec</td>
    </tr>
    #end if
    <tr> 
    #if $current.ws90_ver.has_data 
      <td class="label">WS90 Vers</td>
      <td class="data">$current.ws90_ver.format("%.0f")</td>
    </tr>
    #end if
   #except
    #pass
   #end try
    <tr>
      <td class="label">Latitude</td>
      <td class="data">$station.latitude[0]&deg; $station.latitude[1]' $station.latitude[2]</td>
    </tr>
    <tr>
      <td class="label">Longitude</td>
      <td class="data">$station.longitude[0]&deg; $station.longitude[1]' $station.longitude[2]</td>
    </tr>
    <tr>
      <td class="label">Altitude</td>
      <td class="data">$station.altitude</td>
    </tr>
    <tr>
      <td class="label">Server uptime</td>
      <td class="data">$station.os_uptime</td>
    </tr>
    <tr>
      <td class="label">WeeWX uptime</td>
      <td class="data">$station.uptime</td>
    </tr>
    <tr>
      <td class="label">WeeWX version</td>
      <td class="data">$station.version</td>
    </tr>
  </table>
  </div>

</div>
#else
<div id='about_widget' class="widget">
  <div class="widget_title">
    $gettext("About this station")
    <a class="widget_control"
      onclick="toggle_widget('about')">&diams;</a>
  </div>
  <div class="widget_contents">
  <table>
    <tr>
      <td class="label">$gettext("Hardware")</td>
      <td class="data">$station.hardware</td>
    </tr>
   #try
    #if $current.runtime.has_data
    <tr> 
      <td class="label">$gettext("Station uptime")</td>
      <td class="data">$current.runtime.long_form</td>
    </tr>
    #end if
    <tr> 
    #if $current.ws90_ver.has_data 
      <td class="label">$gettext("WS90 Vers")</td>
      <td class="data">$current.ws90_ver.format("%.0f")</td>
    </tr>
    #end if
   #except
    #pass
   #end try
    <tr>
      <td class="label">$gettext("Latitude")</td>
      <td class="data">$station.latitude[0]&deg; $station.latitude[1]' $station.latitude[2]</td>
    </tr>
    <tr>
      <td class="label">$gettext("Longitude")</td>
      <td class="data">$station.longitude[0]&deg; $station.longitude[1]' $station.longitude[2]</td>
    </tr>
    <tr>
      <td class="label">$pgettext("Geographical", "Altitude")</td>
      <td class="data">$station.altitude</td>
    </tr>
    <tr>
      <td class="label">$gettext("Server uptime")</td>
      <td class="data">$station.os_uptime.long_form</td>
    </tr>
    <tr>
      <td class="label">$gettext("WeeWX uptime")</td>
      <td class="data">$station.uptime.long_form</td>
    </tr>
    <tr>
      <td class="label">$gettext("WeeWX version")</td>
      <td class="data">$station.version</td>
    </tr>
    <tr>
      <td class="label">$gettext("Skin")</td>
      <td class="data">$SKIN_NAME $SKIN_VERSION</td>
    </tr>
  </table>
  </div>

</div>
#end if