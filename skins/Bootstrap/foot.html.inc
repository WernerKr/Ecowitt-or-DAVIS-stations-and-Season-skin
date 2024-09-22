#set $xt = ''
#set $txt = 'Station: '
#if $current.stationtype.has_data
 #if '_' in $current.stationtype.raw
  #set $xt = $current.stationtype.raw
 #elif $current.model.has_data
  #set $xt = $current.model.raw 
 #end if
#end if

    <hr>
    <footer>
        #if $gettext("Footer text") == "Footer text"
        <p class="footer"><a href='https://github.com/brewster76/fuzzy-archer'>fuzzy-archer</a> version $fuzzy_archer_version, powered by <a href='https://weewx.com'>WeeWX</a><B>  $xt</B></p>
        #else
        <p>$gettext("Footer text")<B>  $xt</B></p>
        #end if
    </footer>