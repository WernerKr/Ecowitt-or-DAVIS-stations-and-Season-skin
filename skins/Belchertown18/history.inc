#errorCatcher Echo
<!-- Graph panel -->
<div class="main">
    <table class="table-striped">
	<tbody>
	    <tr>
		<td colspan="13" class="records-header">Jahres&uuml;bersicht klimatologische Kenntage</td>
	    </tr>
	    <tr>
		<th class="records-header-alltime hist-size-small">Jahr</th>
		<td width= 9% class="records-header-year-small">Hei&szlig;e Tage<br>T<sub>max</sub>&ge;&nbsp;30&nbsp;&deg;C</td>
		<td width= 9% class="records-header-year-small">Sommertage<br>T<sub>max</sub>&ge;&nbsp;25&nbsp;&deg;C</td>
		<td width= 9% class="records-header-year-small">Warme Tage<br>T<sub>max</sub>&ge;&nbsp;18&nbsp;&deg;C</td>
		<td width= 9% class="records-header-year-small">Veg.-Tage<br>T<sub>&Oslash;</sub>&ge;&nbsp;5&nbsp;&deg;C</td>
		<td width= 9% class="records-header-year-small">Kalte Tage<br>T<sub>max</sub>&lt;&nbsp;10&nbsp;&deg;C</td>
		<td width= 7% class="records-header-year-small">Frosttage<br>T<sub>min</sub>&lt;&nbsp;0&nbsp;&deg;C</td>
		<td width= 7% class="records-header-year-small">Eistage<br>T<sub>max</sub>&lt;&nbsp;0&nbsp;&deg;C</td>
		<td width= 7% class="records-header-year-small">Regentage<br>&ge;&nbsp;0,1&nbsp;mm</td>
		<td width= 7% class="records-header-year-small">Regentage<br>&ge;&nbsp;1,0&nbsp;mm</td>
		<td width= 7% class="records-header-year-small">Regentage<br>&ge;&nbsp;10&nbsp;mm</td>
		<td width= 7% class="records-header-year-small">Heiztage<br>T<sub>&Oslash;</sub>&le;&nbsp;12&nbsp;&deg;C</td>
		##<td width= 7% class="records-header-year-small">Heizgrad-<br>&Sigma; 20/12</td>
	    </tr>

        #for $year in $alltime.years

	    <tr>
		<th class="center hist-size-small">$year.dateTime.format("%Y")</th>
		<td class="center hist-size-value">$year.outTemp.max_ge((30, "degree_C", "group_temperature")).format("%.0f")</td>
		<td class="center hist-size-value">$year.outTemp.max_ge((25, "degree_C", "group_temperature")).format("%.0f")</td>
		<td class="center hist-size-value">$year.outTemp.max_ge((18, "degree_C", "group_temperature")).format("%.0f")</td>
		<td class="center hist-size-value">$year.outTemp.avg_ge((5, "degree_C", "group_temperature")).format("%.0f")</td>
		<td class="center hist-size-value">$year.outTemp.max_le((10, "degree_C", "group_temperature")).format("%.0f")</td>
		<td class="center hist-size-value">$year.outTemp.min_le((0, "degree_C", "group_temperature")).format("%.0f")</td>
		<td class="center hist-size-value">$year.outTemp.max_le((0, "degree_C", "group_temperature")).format("%.0f")</td>
		<td class="center hist-size-value">$year.rain.sum_ge((0.1, "mm", "group_rain")).format("%.0f")</td>
		<td class="center hist-size-value">$year.rain.sum_ge((1, "mm", "group_rain")).format("%.0f")</td>
		<td class="center hist-size-value">$year.rain.sum_ge((10, "mm", "group_rain")).format("%.0f")</td>
		<td class="center hist-size-value">$year.outTemp.avg_le((12, "degree_C", "group_temperature")).format("%.0f")</td>
		##<td class="center hist-size-value">$year.hgs2012.sum.formatted</td>
	    </tr>
	#end for
	</tbody>
    </table>
####    
    #for $table in $history_tables
    <table class="table-striped">
	<br>
	    #if $table.noaa is False
	<tbody>
	    <tr>
		<td colspan="14" class="records-header">$gettext($table.header_text)</td>
	    </tr>
	    <tr>
		<th width= 7% class="records-header-alltime hist-size-small">$table.header.head</th>
		    #for $headervalue in $table.header.values
		<th width= 7% class="records-header-year hist-size-value">$gettext($headervalue)</th>
		    #end for
		    #if "summary" in $table.header.keys()
		<th class="records-header-alltime hist-size">$gettext($table.header.summary)</th>
		    #end if
	    </tr>
		#for $line in $table.lines
	    <tr>
		<th class="center hist-size-small">$line.head.value</th>
		    #for $linevalue in $line.values
		    #set $value = '-'
		    #set $style = ''
		    #if $linevalue.value
		    #set $value = $linevalue.value
		    #set $style = ' style="background-color:' + $linevalue.bgcolor + '; color:' + $linevalue.fontcolor + ';"'
		    #end if
		<td class="center hist-size-value" $style>$value</td>
		    #end for
		    #set $style = ''
		    #if "summary" in $line.keys()
		    #set $style = ' style="background-color:' + $line.summary.bgcolor + '; color:' + $line.summary.fontcolor + ';"'
		<td class="center hist-size" $style>$line.summary.value</td>
		    #end if
	    </tr>
		#end for
	</tbody>
	    #else
	<tbody>
	    <tr>
		<td colspan="13" class="records-header">$gettext($table.header_text)</td>
	    </tr>
	    <tr>
		#for $line in $table.lines
		<th class="noaa"><a href="../$line.head.url" class="btn btn-sm btn-primary primaryLive btnNOAA">$line.head.value</a></th>
		    #for $linevalue in $line.values
		    #set $data = '-'
		    #if $linevalue.value
		    #set $data = '<a href="../' + $linevalue.url + '" class="btn btn-sm btn-light primaryLight btnNOAA">' + $linevalue.value + '</a>'
		    #end if
		<td width= 8% class="noaa">$data</td>
		    #end for
	    </tr>
		#end for
	</tbody>
	    #end if
    </table>
	#end for
	<hr>
####
##    <div class="noaa_reports">
##        <H3>$obs.label.reports_title</H3>
##        <div class="row">
##            <div class="col-sm-12 wx-year-row">
##                $noaa_header_html
##            </div>
##        </div>
##        <a href="#" class="noaa_direct_link">$obs.label.reports_click_here_link</a> $obs.label.reports_view_more
##        <br><br>
##        <div class="noaa_report_container">
##            <pre id="noaa_contents"></pre>
##        </div> <!-- END noaa_report_container -->
##    </div> <!-- END noaa_reports -->
##    <hr>
####
</div>
