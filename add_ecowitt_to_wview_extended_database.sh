#!/bin/bash
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=co2_Temp --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=co2_Hum --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=co2_Batt --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=pm25_1 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=pm25_2 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=pm25_3 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=pm25_4 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=pm25_Batt1 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=pm25_Batt2 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=pm25_Batt3 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=pm25_Batt4 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWet3 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWet4 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWet5 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWet6 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWet7 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWet8 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWetBatt1 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWetBatt2 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWetBatt3 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWetBatt4 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWetBatt5 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWetBatt6 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWetBatt7 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leafWetBatt8 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leak_1 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leak_2 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leak_3 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leak_4 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leak_Batt1 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leak_Batt2 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leak_Batt3 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=leak_Batt4 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=lightning_Batt --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoist5 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoist6 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoist7 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoist8 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoist9 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoist10 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoist11 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoist12 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoist13 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoist14 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoist15 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoist16 --type=REAL

sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt1 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt2 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt3 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt4 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt5 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt6 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt7 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt8 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt9 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt10 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt11 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt12 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt13 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt14 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt15 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilMoistBatt16 --type=REAL

sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilTemp5 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilTemp6 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilTemp7 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilTemp8 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilTempBatt1 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilTempBatt2 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilTempBatt3 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilTempBatt4 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilTempBatt5 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilTempBatt6 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilTempBatt7 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=soilTempBatt8 --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=sunshine_hours --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=sunshine_time --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=sunshineDur --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=rainDur --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=hailDur --type=REAL

sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=pm4_0 --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=ws90_batt --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=ws90_sig --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=ws90cap_volt --type=REAL
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=ws85_batt --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=ws85cap_volt --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=ws85_sig --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=ldsbatt1 --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=depth_ch1 --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=thi_ch1 --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=air_ch1 --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=wh54_ch1_sig --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=ldsbatt2 --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=depth_ch2 --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=thi_ch2 --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=air_ch2 --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=wh54_ch2_sig --type=REAL -y
sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --add-column=vpd --type=REAL -y

sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --rename-column=co --to-name=co2in -y
#sudo echo "y" | wee_database --config=/etc/weewx/weewx.conf --rename-column=pb --to-name=heap -y

