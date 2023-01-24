#https://github.com/Jterrettaz/sunduration/blob/master/sunduration.py

import syslog
from math import sin,cos,pi,asin
from datetime import datetime
import time
import weewx
from weewx.wxengine import StdService
#import schemas.wview_extendedmy

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

        # Default min value
        self.sunshine_min = 0

        self.sunshine_loop = 1

        if 'RadiationDays' in config_dict:
            self.sunshine_coeff = float(config_dict['RadiationDays'].get('sunshine_coeff', self.sunshine_coeff))
            self.sunshine_log = int(config_dict['RadiationDays'].get('sunshine_log', self.sunshine_log))
            self.sunshine_min = float(config_dict['RadiationDays'].get('sunshine_min', self.sunshine_min))
            self.sunshine_loop = float(config_dict['RadiationDays'].get('sunshine_loop', self.sunshine_loop))


        # Start intercepting events:
        if self.sunshine_loop == 1:
           self.bind(weewx.NEW_LOOP_PACKET, self.newLoopPacket)
           self.bind(weewx.NEW_ARCHIVE_RECORD, self.newArchiveRecord)
        else:
           self.bind(weewx.NEW_ARCHIVE_RECORD, self.newArchiveRecord_old)

        self.lastdateTime = 0
        self.LoopDuration = 0
        self.sunshineSeconds = 0
        self.lastSeuil = 0
        self.firstArchive = True

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

    def newArchiveRecord(self, event):
        """Gets called on a new archive record event."""
        radiation = event.record.get('radiation')
        # maxtime = event.record['interval']
        if self.lastdateTime == 0 or self.firstArchive:  # LOOP packets not yet captured : missing archive record extracted from datalogger at start OR first archive record after weewx start
            #radiation = event.record.get('radiation')
            event.record['sunshine_time'] = 0.0
            event.record['sunshineThreshold'] = 0.0
            if radiation is not None:
                seuil = self.sunshineThreshold(event.record.get('dateTime'))
                self.lastSeuil = seuil
                if radiation > seuil and radiation > self.sunshine_min and seuil > 0:
                    event.record['sunshine_time'] = event.record['interval'] / 60
                if self.lastdateTime != 0:  # LOOP already started, this is the first regular archive after weewx start
                    self.firstArchive = False
                event.record['sunshineThreshold'] = self.lastSeuil
                if radiation > 0 and self.sunshine_log == 1:
                   loginf("Sunshine - archive record=%.4f min, radiation=%.2f, threshold=%.4f" % (
                      event.record['sunshine_time']*60, event.record['radiation'], event.record['sunshineThreshold']))
 
        else:
            event.record['sunshineThreshold'] = self.lastSeuil
            if self.sunshineSeconds / 60 > event.record['interval'] * 2:
              event.record['sunshine_time'] = event.record['interval'] / 60
            else:
              event.record['sunshine_time'] = self.sunshineSeconds / 3600
            if radiation is not None:
             if radiation > 0 and self.sunshine_log == 1:
               loginf("Sunshine - loop packets=%.4f min, radiation=%.2f, threshold=%.4f" % (
                event.record['sunshine_time']*60, event.record['radiation'], event.record['sunshineThreshold']))

        self.sunshineSeconds = 0

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
                (sin(pi / 180) * hauteur_soleil), 1.25) * self.sunshine_coeff
        else :
            seuil=0
        return seuil

    def newArchiveRecord_old(self, event):
        """Gets called on a new archive record event."""
        seuil = 0
        #coeff = 0.9
        radiation = event.record.get('radiation')
        event.record['sunshine_time'] = 0.0
        if radiation is not None:
            utcdate = datetime.utcfromtimestamp(event.record.get('dateTime'))
            dayofyear = int(time.strftime("%j",time.gmtime(event.record.get('dateTime'))))
            theta = 360 * dayofyear / 365
            equatemps = 0.0172 + 0.4281 * cos((pi / 180) * theta) - 7.3515 * sin(
                (pi / 180) * theta) - 3.3495 * cos(2 * (pi / 180) * theta) - 9.3619 * sin(
                2 * (pi / 180) * theta)

            latitude= float(self.config_dict["Station"]["latitude"])
            longitude = float(self.config_dict["Station"]["longitude"])
            corrtemps = longitude * 4
            declinaison = asin(0.006918 - 0.399912 * cos((pi / 180) * theta) + 0.070257 * sin(
                (pi / 180) * theta) - 0.006758 * cos(2 * (pi / 180) * theta) + 0.000908 * sin(
                2 * (pi / 180) * theta)) * (180 / pi)

            minutesjour = utcdate.hour*60 + utcdate.minute
            tempsolaire = (minutesjour + corrtemps + equatemps) / 60
            angle_horaire = (tempsolaire - 12) * 15
            hauteur_soleil = asin(sin((pi / 180) * latitude) * sin((pi / 180) * declinaison) + cos(
                (pi / 180) * latitude) * cos((pi / 180) * declinaison) * cos((pi / 180) * angle_horaire)) * (180 / pi)
            if hauteur_soleil > 3 and radiation > self.sunshine_min:
                seuil = (0.73 + 0.06 * cos((pi / 180) * 360 * dayofyear / 365)) *1080 * pow((sin(pi / 180) * hauteur_soleil), 1.25) * self.sunshine_coeff
                if radiation > seuil:
                    event.record['sunshine_time'] = event.record['interval'] / 60.0
            if hauteur_soleil > -3 and self.sunshine_log == 1:
                loginf("Calculated sunshine_time = %.4f, based on radiation = %.2f, and threshold = %.4f, %.3f" % (
                    event.record['sunshine_time'], radiation, seuil, self.sunshine_coeff))


#schema_with_sunshine_time = schemas.wview_extendedmy.schema + [('sunshine_time', 'REAL')]
