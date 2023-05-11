#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import meteofrance_api
import time
import os
import datetime

# Environment variables
CHATID = os.getenv('CHATID')
BOTID = os.getenv('BOTID')
FRDPT = str(os.getenv('FRDPT'))

# 1 : Vent
# 2 : pluie/inondation
# 3 : 
# 4 : crues
# 5 :
# 6 :
# 7 :
# 8 : orage

Forecast = meteofrance_api.MeteoFranceClient()
phenomenons_names = {
    1 : "Wind",
    2 : "Rain/Flood",
    8 : "Storm",
    }

# Timezone 
timezone = 2

subprocess.run(["echo", "Started Weather-Report Version 1.1"])

while True:
    alerts = Forecast.get_warning_current_phenomenoms(FRDPT).phenomenons_max_colors
    alert_sent = 0
    for elem in alerts:
        print(f"Alert found: {elem['phenomenon_id']}")
        subprocess.run(["echo", f"Alert found: {elem['phenomenon_id']}"])
        if (elem["phenomenon_id"] in [1, 2, 8]) and (elem["phenomenon_max_color_id"] > 1):
            subprocess.run(["./telegram_bot", 
                         f"New alert : {phenomenons_names[elem['phenomenon_id']]}",
                         CHATID,
                         BOTID])    
        alert_sent += 1
	
    if alert_sent == 0:
        subprocess.run(["./telegram_bot",
                        f"No weather alerts at the moment",
			CHATID,
			BOTID])
    
    t_hour, t_min = datetime.datetime.now().strftime("%H"), datetime.datetime.now().strftime("%M")
    n_min, n_hour = 60-int(t_min), 23-int(t_hour)-timezone+8
    n_sec = n_min*60+n_hour*60*60

    time.sleep(n_sec)
