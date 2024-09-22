#encoding UTF-8
#set $xt = ''
#if $current.stationtype.has_data
 #if '_' in $current.stationtype.raw
  #set $xt = $current.stationtype.raw
 #elif $current.model.has_data
  #set $xt = $current.model.raw 
 #end if
#end if

<div class="entry-content about-outer" itemprop="text">
    <br>
<h3>Impressum</h3>

<h4>Angaben gemäß § 5 TMG</h4>
<p>Werner Krenn<br>
Lackenhäuser 149<br>
94089 Neureichenau</p>

<h4>Kontakt</h4>
<p>Telefon: +49 8583 91343<br>
E-Mail: werner.krenn@t-online.de</p>

<h4>Haftung für Inhalte</h4> 
<p>Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. 
Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen 
zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.</p> 
<p>Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. 
Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. 
Bei Bekanntwerden von entsprechenden Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.</p> 
<h4>Haftung für Links</h4> 
<p>Unser Angebot enthält Links zu externen Websites Dritter, auf deren Inhalte wir keinen Einfluss haben. 
Deshalb können wir für diese fremden Inhalte auch keine Gewähr übernehmen. 
Für die Inhalte der verlinkten Seiten ist stets der jeweilige Anbieter oder Betreiber der Seiten verantwortlich. 
Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf mögliche Rechtsverstöße überprüft. 
Rechtswidrige Inhalte waren zum Zeitpunkt der Verlinkung nicht erkennbar.</p> 
<p>Eine permanente inhaltliche Kontrolle der verlinkten Seiten ist jedoch ohne konkrete Anhaltspunkte einer Rechtsverletzung nicht zumutbar. 
Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen.</p> 
<h4>Urheberrecht</h4> 
<p>Die durch die Seitenbetreiber erstellten Inhalte und Werke auf diesen Seiten unterliegen dem deutschen Urheberrecht. 
Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Verwertung außerhalb der Grenzen des Urheberrechtes bedürfen 
der schriftlichen Zustimmung des jeweiligen Autors bzw. Erstellers. Downloads und Kopien dieser Seite sind nur für den privaten, 
nicht kommerziellen Gebrauch gestattet.</p> 
<p>Soweit die Inhalte auf dieser Seite nicht vom Betreiber erstellt wurden, werden die Urheberrechte Dritter beachtet. 
Insbesondere werden Inhalte Dritter als solche gekennzeichnet. Sollten Sie trotzdem auf eine Urheberrechtsverletzung aufmerksam werden, 
bitten wir um einen entsprechenden Hinweis. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Inhalte umgehend entfernen.</p>

<p>Quelle: <a href="https://www.e-recht24.de/">eRecht24</a></p>

<ul>
        <li>Station hardware: $station.hardware $xt</li>
        <li>Server uptime: $station.os_uptime.long_form</li>
        <li>WeeWX uptime: $station.uptime.long_form</li>
        <li>WeeWX version: $station.version</li>
        <li>Belchertown Skin Version: $belchertown_version</li>
</ul>
</div>
