#errorCatcher Echo
#set $history_items = $to_list($HistoryReport.get('history_items', ['min_temp', 'avg_temp', 'max_temp', 'rain', 'rain_days', 'max_wind', 'NOAA']))
#set $header_values = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
<!-- Graph panel -->
<div class="table-container">
    <table class="table-striped">
	<tbody>
	    <tr>
		<td colspan="13" class="records-header">$gettext("Annual_overview")</td>
	    </tr>
	    <tr>
		<th class="records-header-alltime hist-size-small">$gettext("Year")</th>
		##<td width= 9% class="records-header-year-small">$gettext("Hot_days_max_ge_40C")</td>
		##<td width= 9% class="records-header-year-small">$gettext("Hot_days_max_ge_35C")</td>
		<td width= 9% class="records-header-year-small">$gettext("Hot_days_max_ge_30C")</td>
		<td width= 9% class="records-header-year-small">$gettext("Summer_days_max_ge_25C")</td>
		<td width= 9% class="records-header-year-small">$gettext("Warm_days_max_ge_18C")</td>
		<td width= 9% class="records-header-year-small">$gettext("Veg_days_avg_ge_5C")</td>
		<td width= 9% class="records-header-year-small">$gettext("Cold_days_max_lt_10C")</td>
		<td width= 7% class="records-header-year-small">$gettext("Frost_days_min_lt_0C")</td>
		<td width= 7% class="records-header-year-small">$gettext("Ice_days_max_lt_0C")</td>
		<td width= 7% class="records-header-year-small">$gettext("Rainy_days_ge_001mm")</td>
		<td width= 7% class="records-header-year-small">$gettext("Rainy_days_ge_010mm")</td>
		<td width= 7% class="records-header-year-small">$gettext("Rainy_days_ge_100mm")</td>
		<td width= 7% class="records-header-year-small">$gettext("Heating_days_avg_lt_12C")</td>
		##<td width= 7% class="records-header-year-small">$gettext("Heating_degree_sum_20_12")</td>
	    </tr>

        #for $year in $alltime.years

	    <tr>
		<th class="center hist-size-small">$year.dateTime.format("%Y")</th>
		##<td class="center hist-size-value">$year.outTemp.max_ge((40, "degree_C", "group_temperature")).format("%.0f")</td>
		##<td class="center hist-size-value">$year.outTemp.max_ge((35, "degree_C", "group_temperature")).format("%.0f")</td>
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
    <br>

####    
    <div class="row">
            #for $history_item in $history_items
            #set $table = $history_tables[$history_item]
            <tr style="line-height: 1.0;">&nbsp;</tr>
            <caption class="historyHeader"><span style="font-size: 1.2em; font-weight: 500;">$gettext($table.header_text)</span></caption>
            <table class="table historyTable text-center">
                #if 'noaa' not in $table.settings or not $table.settings.noaa
                <thead>
                    <tr>
                        <th class="head">$table.unit</th>
                        #for $headervalue in $header_values
                        <th class="month">$gettext($headervalue)</th>
                        #end for
                        #if $table.settings.summary_column
                        <th class="year">$gettext($table.summary_heading)</th>
                        #end if
                    </tr>
                </thead>
                <tbody>
                #for $line in $table.year
                    <tr>
                        <th class="head">$line.head.value</th>
                        #for $linevalue in $line.values
                        #set $cell_format = $format_cell($linevalue.value, $table.settings)
                        <td class="month" style="background-color:$cell_format.background_color; color:$cell_format.font_color;">$cell_format.formatted_value</td>
                        #end for
                        #if "summary" in $line.keys()
                        #set $cell_format = $format_cell($line.summary.value, $table.settings, True)
                        <td class="year" style="background-color:$cell_format.background_color; color:$cell_format.font_color;">$cell_format.formatted_value</td>
                        #end if

                    </tr>
                #end for
                </tbody>
                #if "aggregations" in $table
                <tfoot>
                    <tr><th colspan="14" class="head">$gettext("Overall")</th><tr>
                    #for $aggregation_type in ['min', 'avg', 'max']
                    #if $aggregation_type in $table.aggregations.values[0].keys()
                    <tr>
                    <th class="head">$gettext($aggregation_type)</th>
                    #for $line in $table.aggregations.values
                        #set $value = $line.get($aggregation_type)
                        #set $cell_format = $format_cell($value, $table.settings)
                        <td class="month" style="background-color:$cell_format.background_color; color:$cell_format.font_color;">$cell_format.formatted_value</td>
                    #end for
                    #if "summary" in $table.aggregations.keys() and $aggregation_type in $table.aggregations.get("summary").keys()
                    #set $cell_format = $format_cell($table.aggregations.get("summary").get($aggregation_type), $table.settings, True)
                    <td class="year" style="background-color:$cell_format.background_color; color:$cell_format.font_color;">$cell_format.formatted_value</td>
                    #end if
                    </tr>
                    #end if
                    #end for
                </tfoot>
                #end if

                #else if 'noaa' in $table.settings and $table.settings.noaa
                <tbody>
                #for $line in $table.year
                    <tr>
                        <th class="noaa"><a href="../$line.head.url" class="btn btn-sm btn-primary primaryLive btnNOAA">$line.head.value</a></th>
                        #for $linevalue in $line.values
                        #set $data = '-'
                        #if $linevalue.value
                        #set $data = '<a href="../' + $linevalue.url + '" class="btn btn-sm btn-light primaryLight btnNOAA">' + $linevalue.value + '</a>'
                        #end if
                        <td class="noaa">$data</td>
                        #end for
                    </tr>
                #end for
                </tbody>
                #end if
            </table>
            #end for
    </div>
</div>

