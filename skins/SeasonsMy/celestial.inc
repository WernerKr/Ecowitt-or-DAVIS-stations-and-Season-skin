## celestial module for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights
#errorCatcher Echo
#encoding UTF-8
#import weewx.almanac
## get a list of the names of the installed almanac extensions
#set $almanac_names = [$alm.__class__.__name__ for $alm in $weewx.almanac.almanacs]
## check if the Skyfield and Skymap almanac extension are available
#set global $skyfield_almanac_available = 'SkyfieldAlmanacType' in $almanac_names and $almanac.hasExtras
#set global $skymap_almanac_available = 'SkymapAlmanacType' in $almanac_names and $almanac.hasExtras

## If extended almanac information is available, do extra calculations.
#if $almanac.hasExtras
  ## Pick a "None string" on the basis of whether the sun is above or below the horizon
  #set $sun_altitude = $almanac.sun.altitude
  #if $sun_altitude.raw < 0
    #set $sun_None='<i>%s</i>' % $gettext("Always down")
  #else
    #set $sun_None='<i>%s</i>' % $gettext("Always up")
  #end if

  ## For the change in daylight, pick a string to indicate whether it is more or
  ## less than yesterday:
  #set $sun_visible_change = $almanac.sun.visible_change

  #if $sun_visible_change.raw < 0
    #set $change_str = $gettext("less than yesterday")
  #else
    #set $change_str = $gettext("more than yesterday")
  #end if
#end if


<div id="celestial_widget" class="widget">
  <div class="widget_title">
    $gettext("Celestial")
  </div>
  <div class="widget_contents">
  #if $almanac.hasExtras
    <div id="celestial_details">
      <div class="celestial_body">
        <table class="celestial">
          <tr>
            <th class="label">
              <svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="80" height="80" viewBox="-50 -50 100 100"><g stroke-width="3"><g stroke="#f6bc68"><circle cx="0" cy="0" r="18" fill="#f6bc68" /><path d="M 24.0,0.0 L 38.0,0.0 M 16.97056274847714,16.97056274847714 L 26.87005768508881,26.8700576850888 M 0.0,24.0 L 0.0,38.0 M -16.97056274847714,16.97056274847714 L -26.8700576850888,26.87005768508881 M -24.0,0.0 L -38.0,0.0 M -16.97056274847714,-16.97056274847714 L -26.87005768508881,-26.8700576850888 M -0.0,-24.0 L -1e-14,-38.0 M 16.97056274847714,-16.97056274847714 L 26.8700576850888,-26.87005768508881 " /></g></g></svg>
            </th>
            <th class="data" style="text-align:left">$gettext("Sun")</th>
          </tr>
          <tr>
            <td class="label">$gettext("Start civil twilight")</td>
            <td class="data">$almanac(horizon=-6).sun(use_center=1).rise</td>
          </tr>
          <tr>
            <td class="label">$gettext("Rise")</td>
            <td class="data">$almanac.sun.rise.format(None_string=$sun_None)</td>
          </tr>
          <tr>
            <td class="label">$gettext("Transit")</td>
            <td class="data">$almanac.sun.transit</td>
          </tr>
          <tr>
            <td class="label">$gettext("Set")</td>
            <td class="data">$almanac.sun.set.format(None_string=$sun_None)</td>
          </tr>
          <tr>
            <td class="label">$gettext("End civil twilight")</td>
            <td class="data">$almanac(horizon=-6).sun(use_center=1).set</td>
          </tr>
          <tr>
            <td class="label">$gettext("Azimuth")</td>
            <td class="data">$almanac.sun.azimuth.format("%03.1f")</td>
          </tr>
          <tr>
            <td class="label">$pgettext("Astronomical", "Altitude")</td>
            <td class="data">$sun_altitude.format("%.1f")</td>
          </tr>
          <tr>
            <td class="label">$gettext("Right ascension")</td>
            <td class="data">$almanac.sun.topo_ra.format("%03.1f")</td>
          </tr>
          <tr>
            <td class="label">$gettext("Declination")</td>
            <td class="data">$almanac.sun.topo_dec.format("%.1f")</td>
          </tr>
          #if $almanac.next_equinox.raw < $almanac.next_solstice.raw
            ## The equinox is before the solstice. Display them in order.
            <tr>
              <td class="label">$gettext("Equinox")</td>
              <td class="data">$almanac.next_equinox</td>
            </tr>
            <tr>
              <td class="label">$gettext("Solstice")</td>
              <td class="data">$almanac.next_solstice</td>
            </tr>
          #else
            ## The solstice is before the equinox. Display them in order.
            <tr>
              <td class="label">$gettext("Solstice")</td>
              <td class="data">$almanac.next_solstice</td>
            </tr>
            <tr>
              <td class="label">$gettext("Equinox")</td>
              <td class="data">$almanac.next_equinox</td>
            </tr>
          #end if
          #if $skyfield_almanac_available and $varExists("$almanac.next_perihelion") and $varExists("$almanac.next_aphelion")
          #if $almanac.next_aphelion.raw<$almanac.next_perihelion.raw
          <tr>
            <td class="label">$gettext("Aphelion")</td>
            <td class="data">$almanac.next_aphelion</td>
          </tr>
          <tr>
            <td class="label">$gettext("Perihelion")</td>
            <td class="data">$almanac.next_perihelion</td>
          </tr>
          #else
          <tr>
            <td class="label">$gettext("Perihelion")</td>
            <td class="data">$almanac.next_perihelion</td>
          </tr>
          <tr>
            <td class="label">$gettext("Aphelion")</td>
            <td class="data">$almanac.next_aphelion</td>
          </tr>
          #end if
          #end if
          <tr>
            <td class="label">$gettext("Total daylight")</td>
            <td class="data">$almanac.sun.visible.long_form<br/>$sun_visible_change.long_form $change_str</td>
            ##<td class="data">$almanac.sun.visible.long_form<br/>$delta_str $change_str</td>
          </tr>

        </table>
      </div>
      <div class="celestial_body">
        <table class="celestial">
          <tr>
            <th class="label">
              #if $skymap_almanac_available
              $almanac.moon_symbol(width=80)
              #else
              <svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="80" height="80" viewBox="-50 -50 100 100"><g stroke-width="3"><path stroke="#da4935" fill="#da4935" d="M 0,-24 a 26,26 0 0 1 -22,39 a 24,24 0 1 0 22,-39 z" /></g></svg>
              #end if
            </th>
            <th class="data" style="text-align:left">$gettext("Moon")</th>
          </tr>
          <tr><td class="label">&nbsp;</td><td class="data">&nbsp;</td></tr>
          <tr>
            <td class="label">$gettext("Rise")</td>
            <td class="data">$almanac.moon.rise</td>
          </tr>
          <tr>
            <td class="label">$gettext("Transit")</td>
            <td class="data">$almanac.moon.transit</td>
          </tr>
          <tr>
            <td class="label">$gettext("Set")</td>
            <td class="data">$almanac.moon.set</td>
          </tr>
          <tr><td class="label">&nbsp;</td><td class="data">&nbsp;</td></tr>
          <tr>
            <td class="label">$gettext("Azimuth")</td>
            <td class="data">$almanac.moon.azimuth.format("%.1f")</td>
          </tr>
          <tr>
            <td class="label">$pgettext("Astronomical", "Altitude")</td>
            <td class="data">$almanac.moon.altitude.format("%.1f")</td>
          </tr>
          <tr>
            <td class="label">$gettext("Right ascension")</td>
            <td class="data">$almanac.moon.topo_ra.format("%.1f")</td>
          </tr>
          <tr>
            <td class="label">$gettext("Declination")</td>
            <td class="data">$almanac.moon.topo_dec.format("%.1f")</td>
          </tr>
          #if $almanac.next_full_moon.raw < $almanac.next_new_moon.raw
            <tr>
              <td class="label">$gettext("Full moon")</td>
              <td class="data">$almanac.next_full_moon</td>
            </tr>
            <tr>
              <td class="label">$gettext("New moon")</td>
              <td class="data">$almanac.next_new_moon</td>
            </tr>
          #else
            <tr>
              <td class="label">$gettext("New moon")</td>
              <td class="data">$almanac.next_new_moon</td>
            </tr>
            <tr>
              <td class="label">$gettext("Full moon")</td>
              <td class="data">$almanac.next_full_moon</td>
            </tr>
          #end if
          #if $skyfield_almanac_available and $varExists("$almanac.next_perigee_moon") and $varExists("$almanac.next_apogee_moon")
          #if $almanac.next_perigee_moon.raw<$almanac.next_apogee_moon.raw
          <tr>
            <td class="label">$gettext("Perigee")</td>
            <td class="data">$almanac.next_perigee_moon</td>
          </tr>
          <tr>
            <td class="label">$gettext("Apogee")</td>
            <td class="data">$almanac.next_apogee_moon</td>
          </tr>
          #else
          <tr>
            <td class="label">$gettext("Apogee")</td>
            <td class="data">$almanac.next_apogee_moon</td>
          </tr>
          <tr>
            <td class="label">$gettext("Perigee")</td>
            <td class="data">$almanac.next_perigee_moon</td>
          </tr>
          #end if
          #end if
          <tr>
            <td class="label">$gettext("Phase")</td>
            <td class="data">$almanac.moon_phase<br/>
              $almanac.moon_fullness% $gettext("full")</td>
          </tr>
        </table>
      </div>
      #if $skymap_almanac_available
      <div class="celestial_body">
        <div style="margin-left:10px;margin-right:10px">
          $almanac.skymap(width=650,fromoutside=True,show_path_of_sun=True,show_path_of_moon=True,horizon=[12.5,12.9,13.3,13.3,12.1,11.0,11.0,10.6,12.5,12.9,11.0,9.4,8.3,7.2,6.4,4.5,3.7,2.2,1.0,1.0,0,0,0,0,0,0.3,0,0.3,0,0.3,0,0,0,0,0,0,0,1.0,1.8,3.7,4.5,7.2,8.7,9.8,9.8,10.2,11.0,11.7])          ##$almanac.skymap(width=650,show_path_of_sun=True,show_path_of_moon=True,horizon=[12.6,13.0,13.4,13.4,12.2,11.1,11.1,10.7,12.6,13.0,11.1,9.5,8.4,7.3,6.5,4.6,3.8,2.3,1.1,1.1,0,0,0,0,0,0.4,0,0.4,0,0.4,0,0,0,0,0,0,0,1.1,1.9,3.8,4.6,7.3,8.8,9.9,9.9,10.3,11.1,11.8])
          ##$almanac.skymap(width=650,fromoutside=True,show_path_of_sun=True,show_path_of_moon=True,horizon=[12.6,13.0,13.4,13.4,12.2,11.1,11.1,10.7,12.6,13.0,11.1,9.5,8.4,7.3,6.5,4.6,3.8,2.3,1.1,1.1,0,0,0,0,0,0.4,0,0.4,0,0.4,0,0,0,0,0,0,0,1.1,1.9,3.8,4.6,7.3,8.8,9.9,9.9,10.3,11.1,11.8])
          ##$almanac.skymap(width=650,fromoutside=True,show_path_of_sun=True,show_path_of_moon=True) 
        </div>
      </div>
      #end if
    </div>
  #else
    <p>Install <a href="https://pypi.org/project/ephem/"><em>ephem</em></a> for detailed celestial timings.</p>
  #end if
  </div>
</div>
