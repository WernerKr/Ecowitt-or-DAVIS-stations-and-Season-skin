<div class="row records-table">
  <table id="t1" class="table-striped">
  #set $Time = "%H:%M"
  #set $d = $current.dateTime.format("%H:%M")
    <tbody>
      <tr>
        <td class="records-header" colspan="7">Mittlere Stundenwerte von heute</td>
      </tr>

      <tr>
        <td class="records-header-alltime hist-size-small" width="10%">Uhrzeit</td>
        <td class="records-header-alltime" width="15%">Au&szlig;entemperatur</td>
        <td class="records-header-alltime" width="15%">Luftfeuchte</td>
        <td class="records-header-alltime" width="15%">rel. Luftdruck</td>
        <td class="records-header-alltime" width="15%">Niederschlag</td>
        <td class="records-header-alltime" width="15%">Wind</td>
        <td class="records-header-alltime" width="15%">Solarstrahlung</td>
      </tr>

  #for $hour in $day.hours
    #if ($hour.dateTime.format($Time) < $d)
      <tr>
        <td class="records-header-alltime hist-size-small">$hour.dateTime.format($Time)</td> 
        <td class="links">$hour.outTemp.avg</td>
        <td class="links">$hour.outHumidity.avg</td>
        <td class="links">$hour.barometer.avg</td>
        <td class="links">$hour.rain.sum.format("%.1f")</td>
        <td class="links">$hour.windSpeed.avg / $hour.windDir.avg.ordinal_compass</td>
        <td class="links">$hour.radiation.avg</td>
      </tr>
    #end if
  #end for

      <tr>
        <td class="records-header" colspan="7">H&ouml;chst-/Tiefst- und Mittelwerte von heute</td>
      </tr>
      <tr>
        <td class="records-header hist-size-small">Minimum</td>
        <td class="links"><div>$day.outTemp.min</div><font size="2"><div>um $day.outTemp.minTime.format("%H:%M")</div></font></td>
        <td class="links"><div>$day.outHumidity.min</div><font size="2"><div>um $day.outHumidity.minTime.format("%H:%M")</div></font></td>
        <td class="links"><div>$day.barometer.min</div><font size="2"><div>um $day.barometer.minTime.format("%H:%M")</div></font></td>
        <td class="links"></td>
        <td class="links"><div>$day.windGust.min</div><font size="2"><div>um $day.windGust.minTime.format("%H:%M")</div></font></td>
        <td class="links"></td
      </tr>
      <tr>
        <td class="records-header hist-size-small">Mittelwert</td>
        <td class="links">$day.outTemp.avg</td>
        <td class="links">$day.outHumidity.avg</td>
        <td class="links">$day.barometer.avg</td>
        <td class="links"><div><font size="2">gesamt heute</font></div><div>$day.rain.sum.format("%.1f")</div></td>
        <td class="links"><font size="2"><div>B&ouml;en aus</div></font><div>$day.wind.gustdir.ordinal_compass</div></td>
        <td class="links">$day.radiation.avg</td>
      </tr>
      <tr>
        <td class="records-header hist-size-small">Maximum</td>
        <td class="links"><div>$day.outTemp.max</div><font size="2"><div>um $day.outTemp.maxTime.format("%H:%M")</div></font></td>
        <td class="links"><div>$day.outHumidity.max</div><font size="2"><div>um $day.outHumidity.maxTime.format("%H:%M")</div></font></td>
        <td class="links"><div>$day.barometer.max</div><font size="2"><div>um $day.barometer.maxTime.format("%H:%M")</div></font></td>
        <td class="links"><font size="1"><div>Niederschlagsint&auml;nsit&auml;t um $day.rainRate.maxTime.format("%H:%M")</div></font><div>$day.rainRate.max</div></td>
        <td class="links"><div>$day.windGust.max</div><font size="2"><div>um $day.windGust.maxTime.format("%H:%M")</div></font></td>
        <td class="links"><div>$day.radiation.max</div><font size="2"><div>um $day.radiation.maxTime.format("%H:%M")</div></font></td>
      </tr>
      
      <tr>
        <td class="records-header-year" colspan="7">H&ouml;chst-/Tiefst- und Mittelwerte von gestern</td>
      </tr>
      <tr>
        <td class="records-header-year hist-size-small">Minimum</td>
        <td class="links"><div>$yesterday.outTemp.min</div><font size="2"><div>um $yesterday.outTemp.minTime.format("%H:%M")</div></font></td>
        <td class="links"><div>$yesterday.outHumidity.min</div><font size="2"><div>um $yesterday.outHumidity.minTime.format("%H:%M")</div></font></td>
        <td class="links"><div>$yesterday.barometer.min</div><font size="2"><div>um $yesterday.barometer.minTime.format("%H:%M")</div></font></td>
        <td class="links"></td>
        <td class="links"><div>$yesterday.windGust.min</div><font size="2"><div>um $yesterday.windGust.minTime.format("%H:%M")</div></font></td>
        <td class="links"></td>
      </tr>
      <tr>
        <td class="records-header-year hist-size-small">Mittelwert</td>
        <td class="links">$yesterday.outTemp.avg</td>
        <td class="links">$yesterday.outHumidity.avg</td>
        <td class="links">$yesterday.barometer.avg</td>
        <td class="links"><div><font size="2">gesamt gestern</font></div><div>$yesterday.rain.sum.format("%.1f")</div></td>
        <td class="links"><font size="2"><div>B&ouml;en aus</div></font><div>$yesterday.wind.gustdir.ordinal_compass</div></td>
        <td class="links">$yesterday.radiation.avg</td>
      </tr>
      <tr>
        <td class="records-header-year hist-size-small">Maximum</td>
        <td class="links"><div>$yesterday.outTemp.max</div><font size="2"><div>um $yesterday.outTemp.maxTime.format("%H:%M")</div></font></td>
        <td class="links"><div>$yesterday.outHumidity.max</div><font size="2"><div>um $yesterday.outHumidity.maxTime.format("%H:%M")</div></font></td>
        <td class="links"><div>$yesterday.barometer.max</div><font size="2"><div>um $yesterday.barometer.maxTime.format("%H:%M")</div></font></td>
        <td class="links"><font size="1"><div>Niederschlagsint&auml;nsit&auml;t um $yesterday.rainRate.maxTime.format("%H:%M")</div></font><div>$yesterday.rainRate.max</div></td>
        <td class="links"><div>$yesterday.windGust.max</div><font size="2"><div>um $yesterday.windGust.maxTime.format("%H:%M")</div></font></td>
        <td class="links"><div>$yesterday.radiation.max</div><font size="2"><div>um $yesterday.radiation.maxTime.format("%H:%M")</div></font></td>
      </tr>
      
      <tr>
        <td class="records-header-alltime" colspan="7">H&ouml;chst-/Tiefst- und Mittelwerte $current.dateTime.format("%B %Y")</td>
      </tr>
      <tr>
        <td class="records-header-alltime hist-size-small">Minimum</td>
        <td class="links"><div>$month.outTemp.min</div><font size="2"><div>$month.outTemp.minTime.format("%d. %H:%M")</div></font></td>
        <td class="links"><div>$month.outHumidity.min</div><font size="2"><div>$month.outHumidity.minTime.format("%d. %H:%M")</div></font></td>
        <td class="links"><div>$month.barometer.min</div><font size="2"><div>$month.barometer.minTime.format("%d. %H:%M")</div></font></td>
        <td class="links"></td>
        <td class="links"><div>$month.windGust.min</div><font size="2"><div>$month.windGust.minTime.format("%d. %H:%M")</div></font></td>
        <td class="links"></td>
      </tr>
      <tr>
        <td class="records-header-alltime hist-size-small">Mittelwert</td>
        <td class="links">$month.outTemp.avg</td>
        <td class="links">$month.outHumidity.avg</td>
        <td class="links">$month.barometer.avg</td>
        <td class="links"><div><font size="2">Monatssumme</font></div><div>$month.rain.sum.format("%.1f")</div></td>
        <td class="links"><font size="2"><div>B&ouml;en aus</div></font><div>$month.wind.gustdir.ordinal_compass</div></td>
        <td class="links">$month.radiation.avg</td>
      </tr>
      <tr>
        <td class="records-header-alltime hist-size-small">Maximum</td>
        <td class="links"><div>$month.outTemp.max</div><font size="2"><div>$month.outTemp.maxTime.format("%d. %H:%M")</div></font></td>
        <td class="links"><div>$month.outHumidity.max</div><font size="2"><div>$month.outHumidity.maxTime.format("%d. %H:%M")</div></font></td>
        <td class="links"><div>$month.barometer.max</div><font size="2"><div>$month.barometer.maxTime.format("%d. %H:%M")</div></font></td>
        <td class="links"><font size="1"><div>Niederschlagsint&auml;nsit&auml;t $month.rainRate.maxTime.format("%d. %H:%M")</div></font><div>$month.rainRate.max</div></td>
        <td class="links"><div>$month.windGust.max</div><font size="2"><div>$month.windGust.maxTime.format("%d. %H:%M")</div></font></td>
        <td class="links"><div>$month.radiation.max</div><font size="2"><div>$month.radiation.maxTime.format("%d. %H:%M")</div></font></td>
      </tr>
<!---   
      <tr>
        <td class="records-header-year" colspan="7">H&ouml;chst-/Tiefst- und Mittelwerte $current.dateTime.format("%Y")</td>
      </tr>
      <tr>
        <td class="records-header-year hist-size-small">Minimum</td>
        <td class="links"><div>$year.outTemp.min</div><font size="2"><div>$year.outTemp.minTime.format("%d. %b. %H:%M")</div></font></td>
        <td class="links"><div>$year.outHumidity.min</div><font size="2"><div>$year.outHumidity.minTime.format("%d. %b. %H:%M")</div></font></td>
        <td class="links"><div>$year.barometer.min</div><font size="2"><div>$year.barometer.minTime.format("%d. %b. %H:%M")</div></font></td>
        <td class="links"></td>
        <td class="links"><div>$year.windGust.min</div><font size="2"><div>$year.windGust.minTime.format("%d. %b. %H:%M")</div></font></td>
        <td class="links"></td>
      </tr>
      <tr>
        <td class="records-header-year hist-size-small">Mittelwert</td>
        <td class="links">$year.outTemp.avg</td>
        <td class="links">$year.outHumidity.avg</td>
        <td class="links">$year.barometer.avg</td>
        <td class="links"><div><font size="2">Jahressumme</font></div><div>$year.rain.sum.format("%.1f")</div></td>
        <td class="links"><font size="2"><div>B&ouml;en aus</div></font><div>$year.wind.gustdir.ordinal_compass</div></td>
        <td class="links">$year.radiation.avg</td>
      </tr>
      <tr>
        <td class="records-header-year hist-size-small">Maximum</td>
        <td class="links"><div>$year.outTemp.max</div><font size="2"><div>$year.outTemp.maxTime.format("%d. %b. %H:%M")</div></font></td>
        <td class="links"><div>$year.outHumidity.max</div><font size="2"><div>$year.outHumidity.maxTime.format("%d. %b. %H:%M")</div></font></td>
        <td class="links"><div>$year.barometer.max</div><font size="2"><div>$year.barometer.maxTime.format("%d. %b. %H:%M")</div></font></td>
        <td class="links"><font size="1"><div>Niederschlagsint&auml;nsit&auml;t<br>$year.rainRate.maxTime.format("%d. %b. %H:%M")</div></font><div>$year.rainRate.max</div></td>
        <td class="links"><div>$year.windGust.max</div><font size="2"><div>$year.windGust.maxTime.format("%d. %b. %H:%M")</div></font></td>
        <td class="links"><div>$year.radiation.max</div><font size="2"><div>$year.radiation.maxTime.format("%d. %b. %H:%M")</div></font></td>
      </tr>
   
      <tr>
        <td class="records-header-alltime" colspan="7">H&ouml;chst-/Tiefst- und Mittelwerte $obs.label.records_all_time</td>
      </tr>
      <tr>
        <td class="records-header-alltime hist-size-small">Minimum</td>
        <td class="links"><div>$alltime.outTemp.min</div><font size="2"><div>$alltime.outTemp.minTime.format("%d. %b. %Y %H:%M")</div></font></td>
        <td class="links"><div>$alltime.outHumidity.min</div><font size="2"><div>$alltime.outHumidity.minTime.format("%d. %b. %Y %H:%M")</div></font></td>
        <td class="links"><div>$alltime.barometer.min</div><font size="2"><div>$alltime.barometer.minTime.format("%d. %b. %Y %H:%M")</div></font></td>
        <td class="links"></td>
        <td class="links"><div>$alltime.windGust.min</div><font size="2"><div>$alltime.windGust.minTime.format("%d. %b. %Y %H:%M")</div></font></td>
        <td class="links"></td>
      </tr>
      <tr>
        <td class="records-header-alltime hist-size-small">Mittelwert</td>
        <td class="links">$alltime.outTemp.avg</td>
        <td class="links">$alltime.outHumidity.avg</td>
        <td class="links">$alltime.barometer.avg</td>
        <td class="links"><div><font size="2">Gesamtsumme</font></div><div>$alltime.rain.sum.format("%.1f")</div></td>
        <td class="links"><font size="2"><div>B&ouml;en aus</div></font><div>$alltime.wind.gustdir.ordinal_compass</div></td>
        <td class="links">$alltime.radiation.avg</td>
      </tr>
      <tr>
        <td class="records-header-alltime hist-size-small">Maximum</td>
        <td class="links"><div>$alltime.outTemp.max</div><font size="2"><div>$alltime.outTemp.maxTime.format("%d. %b. %Y %H:%M")</div></font></td>
        <td class="links"><div>$alltime.outHumidity.max</div><font size="2"><div>$alltime.outHumidity.maxTime.format("%d. %b. %Y %H:%M")</div></font></td>
        <td class="links"><div>$alltime.barometer.max</div><font size="2"><div>$alltime.barometer.maxTime.format("%d. %b. %Y %H:%M")</div></font></td>
        <td class="links"><font size="1"><div>Niederschlagsint&auml;nsit&auml;t<br>$alltime.rainRate.maxTime.format("%d. %b. %Y %H:%M")</div></font><div>$alltime.rainRate.max</div></td>
        <td class="links"><div>$alltime.windGust.max</div><font size="2"><div>$alltime.windGust.maxTime.format("%d. %b. %Y %H:%M")</div></font></td>
        <td class="links"><div>$alltime.radiation.max</div><font size="2"><div>$alltime.radiation.maxTime.format("%d. %b. %Y %H:%M")</div></font></td>
      </tr>
--->
    </tbody>
  </table>
</div>
