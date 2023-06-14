# sunduration based on https://github.com/Jterrettaz/sunduration/blob/master/sunduration.py

"""

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

if sunduration.py is former used: 
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --rename-column=sunshine_time --to-name=sunshineDur
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=sunshine_time --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=rainDur --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=hailDur --type=REAL

if sunrainduration.py new used:
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=sunshine_time --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=sunshineDur --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=rainDur --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=hailDur --type=REAL

weewx.conf:
[RadiationDays]			# this are the default settings
    min_sunshine = 120
    sunshine_coeff = 0.95
    sunshine_min = 18
    sunshine_loop = 1
    rainDur_loop = 0
    hailDur_loop = 0
    sunshine_log = 0
    rainDur_log = 0
    hailDur_log = 0

[Engine]
    [[Services]]
        process_services = weewx.engine.StdConvert, weewx.engine.StdCalibrate, weewx.engine.StdQC, weewx.wxservices.StdWXCalculate, user.sunrainduration.SunshineDuration

schema:
#schema_with_sunshine = schemas.wview_extendedmy.schema + [('sunshine_time', 'REAL')]
#schema_with_sunshine = schemas.wview_extendedmy.schema + [('sunshineDur', 'REAL')]
#schema_with_sunshine = schemas.wview_extendedmy.schema + [('rainDur', 'REAL')]
#schema_with_sunshine = schemas.wview_extendedmy.schema + [('hailDur', 'REAL')]

"""

import syslog
from math import sin,cos,pi,asin
from datetime import datetime
import time
import weewx
import weewx.units
from weewx.wxengine import StdService
#import schemas.wview_extendedmy

weewx.units.obs_group_dict['sunshine_time'] = 'group_radiation'
weewx.units.obs_group_dict['sunshineDur'] = 'group_deltatime'
weewx.units.obs_group_dict['rainDur'] = 'group_deltatime'
weewx.units.obs_group_dict['hailDur'] = 'group_deltatime'

try:
    # Test for new-style weewx logging by trying to import weeutil.logger
    import weeutil.logger
    import logging

    log = logging.getLogger(__name__)


    def logdbg(msg):
        log.debug(msg)


    def loginf(msg):
        log.info(msg)


    def logerr(msg):
        log.error(msg)

except ImportError:
    # Old-style weewx logging
    import syslog


    def logmsg(level, msg):
        syslog.syslog(level, 'meteotemplate: %s' % msg)


    def logdbg(msg):
        logmsg(syslog.LOG_DEBUG, msg)


    def loginf(msg):
        logmsg(syslog.LOG_INFO, msg)


    def logerr(msg):
        logmsg(syslog.LOG_ERR, msg)


class SunshineDuration(StdService):
    def __init__(self, engine, config_dict):
        # Pass the initialization information on to my superclass:
        super(SunshineDuration, self).__init__(engine, config_dict)

        # Default threshold value is 0.8
        self.sunshine_coeff = 0.8

        # Default Log threshold
        self.sunshine_log = 0
        self.rainDur_log = 0
        self.hailDur_log = 0

        # Default min value
        self.sunshine_min = 0

        self.sunshine_loop = 1
        self.rainDur_loop = 0
        self.hailDur_loop = 0

        if 'RadiationDays' in config_dict:
            self.sunshine_coeff = float(config_dict['RadiationDays'].get('sunshine_coeff', self.sunshine_coeff))
            self.sunshine_log = int(config_dict['RadiationDays'].get('sunshine_log', self.sunshine_log))
            self.sunshine_min = float(config_dict['RadiationDays'].get('sunshine_min', self.sunshine_min))
            self.sunshine_loop = int(config_dict['RadiationDays'].get('sunshine_loop', self.sunshine_loop))
            self.rainDur_loop = int(config_dict['RadiationDays'].get('rainDur_loop', self.rainDur_loop))
            self.hailDur_loop = int(config_dict['RadiationDays'].get('hailDur_loop', self.hailDur_loop))
            self.rainDur_log = int(config_dict['RadiationDays'].get('rainDur_log', self.rainDur_log))
            self.hailDur_log = int(config_dict['RadiationDays'].get('hailDur_log', self.hailDur_log))

        # Start intercepting events:
        self.bind(weewx.NEW_LOOP_PACKET, self.newLoopPacket)
        self.bind(weewx.NEW_ARCHIVE_RECORD, self.newArchiveRecord)

        self.lastdateTime = 0
        self.LoopDuration = 0
        self.sunshineSeconds = 0
        self.lastSeuil = 0
        self.firstArchive = True

        self.lastdateTimeRain = 0
        self.LoopDurationRain = 0
        self.rainSeconds = 0
        self.lastRain = 0
        self.firstArchiveRain = True

        self.lastdateTimeHail = 0
        self.LoopDurationHail = 0
        self.hailSeconds = 0
        self.lastHail = 0
        self.firstArchiveHail = True

        self.Archive = False

    def newLoopPacket(self, event):
        """Gets called on a new loop packet event."""
        radiation = event.packet.get('radiation')
        if radiation is not None:
            if self.lastdateTime == 0:
                self.lastdateTime = event.packet.get('dateTime')
            self.LoopDuration = event.packet.get('dateTime') - self.lastdateTime
            self.lastdateTime = event.packet.get('dateTime')
            seuil = self.sunshineThreshold(event.packet.get('dateTime'))
            
            if radiation > seuil and radiation > self.sunshine_min and seuil > 0:
                self.sunshineSeconds += self.LoopDuration
            self.lastSeuil = seuil
            if radiation > 0 and self.sunshine_log == 1:
               loginf("LOOP time=%.0f sec, sum sunshineSeconds=%.0f, radiation=%.2f, threshold=%.4f, %.3f" % (
                self.LoopDuration, self.sunshineSeconds, radiation, seuil, self.sunshine_coeff))

        rain = event.packet.get('rain')
        if rain is not None:
            if self.lastdateTimeRain == 0:
                self.lastdateTimeRain = event.packet.get('dateTime')
            self.LoopDurationRain = event.packet.get('dateTime') - self.lastdateTimeRain
            self.lastdateTimeRain = event.packet.get('dateTime')
            
            if rain > 0:
                self.rainSeconds += self.LoopDurationRain
            #self.lastRain = rainDur
            if rain > 0 and self.rainDur_log == 1:
               loginf("LOOP time=%.0f sec, sum rainSeconds=%.0f, rain=%.3f" % (
                self.LoopDurationRain, self.rainSeconds, rain))

        hail = event.packet.get('hail')
        if hail is not None:
            if self.lastdateTimeHail == 0:
                self.lastdateTimeHail = event.packet.get('dateTime')
            self.LoopDurationHail = event.packet.get('dateTime') - self.lastdateTimeHail
            self.lastdateTimeHail = event.packet.get('dateTime')
            
            if hail > 0:
                self.hailSeconds += self.LoopDurationHail
            #self.lastHail = hailDur
            if hail > 0 and self.hailDur_log == 1:
               loginf("LOOP time=%.0f sec, sum hailSeconds=%.0f, hail=%.3f" % (
                self.LoopDurationHail, self.hailSeconds, hail))

    def newArchiveRecord(self, event):
        """Gets called on a new archive record event."""
        self.secondsInterval = event.record['interval'] * 60
        radiation = event.record.get('radiation')
        # maxtime = self.secondsInterval
        if self.lastdateTime == 0 or self.firstArchive:  # LOOP packets not yet captured : missing archive record extracted from datalogger at start OR first archive record after weewx start
            event.record['sunshineDur'] = 0.0
            event.record['sunshineThreshold'] = 0.0
            event.record['sunshine_time'] = 0.0
            if radiation is not None:
                seuil = self.sunshineThreshold(event.record.get('dateTime'))
                self.lastSeuil = seuil
                event.record['sunshine_time'] = seuil
                if radiation > seuil and radiation > self.sunshine_min and seuil > 0:
                    event.record['sunshineDur'] = self.secondsInterval
                if self.lastdateTime != 0:  # LOOP already started, this is the first regular archive after weewx start
                    self.firstArchive = False
                event.record['sunshineThreshold'] = self.lastSeuil
                if radiation > 0 and self.sunshine_log == 1:
                   loginf("Sunshine - archive record=%.0f sec, radiation=%.2f, threshold=%.4f" % (
                      event.record['sunshineDur'], event.record['radiation'], event.record['sunshineThreshold']))
 
        else:
            event.record['sunshineThreshold'] = self.lastSeuil
            event.record['sunshine_time'] = self.lastSeuil
            if self.sunshineSeconds > self.secondsInterval * 2:
              event.record['sunshineDur'] = self.secondsInterval
            else:
              if self.sunshine_loop != 1:
               event.record['sunshineDur'] = self.secondsInterval
              else: 
               event.record['sunshineDur'] = self.sunshineSeconds
            if radiation is not None:
             if radiation > 0 and self.sunshine_log == 1:
               loginf("Sunshine - loop packets=%.0f sec, radiation=%.2f, threshold=%.4f" % (
                event.record['sunshineDur'], event.record['radiation'], event.record['sunshineThreshold']))
        self.sunshineSeconds = 0

        rain = event.record.get('rain')
        # maxtime = self.secondsInterval
        if self.Archive == False:
          loginf("Archiv-Record-Interval=%.0f sec" % (self.secondsInterval))		# 5 minutes default
          self.Archive = True
        if self.lastdateTimeRain == 0 or self.firstArchiveRain:  # LOOP packets not yet captured : missing archive record extracted from datalogger at start OR first archive record after weewx start
            event.record['rainDur'] = 0.0
            if rain is not None:
                self.lastRain = rain 
                if rain > 0:
                    event.record['rainDur'] = self.secondsInterval
                if self.lastdateTimeRain != 0:  # LOOP already started, this is the first regular archive after weewx start
                    self.firstArchiveRain = False
                if rain > 0 and self.rainDur_log == 1:
                   loginf("RainDur - archive record=%.0f sec, rain=%.3f" % (
                      event.record['rainDur'], event.record['rain']))
 
        else:
            #event.record['rainDurThreshold'] = self.lastRain
            if self.rainSeconds > self.secondsInterval * 2:
              event.record['rainDur'] = self.secondsInterval
            else:
              if self.rainDur_loop == 1:
                 event.record['rainDur'] = self.rainSeconds
              else: 
                if self.rainSeconds > 0:
                   event.record['rainDur'] = self.secondsInterval
                else: 
                   event.record['rainDur'] = 0
            if rain is not None:
             if rain > 0 and self.rainDur_log == 1:
               loginf("RainDur - loop packets=%.0f sec, rain=%.3f" % (
                event.record['rainDur'], event.record['rain']))
        self.rainSeconds = 0

        hail = event.record.get('hail')
        # maxtime = self.secondsInterval
        if self.lastdateTimeHail == 0 or self.firstArchiveHail:  # LOOP packets not yet captured : missing archive record extracted from datalogger at start OR first archive record after weewx start
            event.record['hailDur'] = 0.0
            if hail is not None:
                self.lastHail = hail
                if hail > 0:
                    event.record['hailDur'] = self.secondsInterval
                if self.lastdateTimeHail != 0:  # LOOP already started, this is the first regular archive after weewx start
                    self.firstArchiveHail = False
                if hail > 0 and self.hailDur_log == 1:
                   loginf("HailDur - archive record=%.0f sec, hail=%.3f" % (
                      event.record['hailDur'], event.record['hail']))
 
        else:
            #event.record['hailDurThreshold'] = self.lastHail
            if self.hailSeconds > self.secondsInterval * 2:
              event.record['hailDur'] = self.secondsInterval
            else:
              if self.hailDur_loop == 1:
                 event.record['hailDur'] = self.hailSeconds
              else: 
                if self.hailSeconds > 0:
                   event.record['hailDur'] = self.secondsInterval
                else: 
                   event.record['hailDur'] = 0
            if hail is not None:
             if hail > 0 and self.hailDur_log == 1:
               loginf("HailDur - loop packets=%.0f sec, hail=%.3f" % (
                event.record['hailDur'], event.record['hail']))
        self.hailSeconds = 0

    def sunshineThreshold(self, mydatetime):
        #coeff = 0.9  # change to calibrate with your sensor
        utcdate = datetime.utcfromtimestamp(mydatetime)
        dayofyear = int(time.strftime("%j", time.gmtime(mydatetime)))
        theta = 360 * dayofyear / 365
        equatemps = 0.0172 + 0.4281 * cos((pi / 180) * theta) - 7.3515 * sin(
            (pi / 180) * theta) - 3.3495 * cos(2 * (pi / 180) * theta) - 9.3619 * sin(
            2 * (pi / 180) * theta)

        latitude = float(self.config_dict["Station"]["latitude"])
        longitude = float(self.config_dict["Station"]["longitude"])
        corrtemps = longitude * 4
        declinaison = asin(0.006918 - 0.399912 * cos((pi / 180) * theta) + 0.070257 * sin(
            (pi / 180) * theta) - 0.006758 * cos(2 * (pi / 180) * theta) + 0.000908 * sin(
            2 * (pi / 180) * theta)) * (180 / pi)
        minutesjour = utcdate.hour * 60 + utcdate.minute
        tempsolaire = (minutesjour + corrtemps + equatemps) / 60
        angle_horaire = (tempsolaire - 12) * 15
        hauteur_soleil = asin(sin((pi / 180) * latitude) * sin((pi / 180) * declinaison) + cos(
            (pi / 180) * latitude) * cos((pi / 180) * declinaison) * cos((pi / 180) * angle_horaire)) * (180 / pi)
        if hauteur_soleil > 0:
            seuil = (0.73 + 0.06 * cos((pi / 180) * 360 * dayofyear / 365)) * 1080 * pow(
                (sin(pi / 180 * hauteur_soleil)), 1.25) * self.sunshine_coeff
        else :
            seuil=0
        return seuil
