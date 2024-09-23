## about module for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights
#errorCatcher Echo
#encoding UTF-8

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
