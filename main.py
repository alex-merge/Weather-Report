#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bot sending weather forecast sum ups each day and on request using telegram

@author: Alexis M.
@version: 2.0
"""

import meteofrance_api
from simple_telegram import telegram
import time
import os
import datetime

# Environment variables
CHATID = int(os.getenv('CHATID'))
BOTID = str(os.getenv('BOTID'))
CITY = str(os.getenv('CITY'))
REPORT_HOUR = int(os.getenv('RHOUR'))

# Initializing telegram bot communication handler
tg_bot = telegram.telegram(token = BOTID)
tg_bot.sendMessage("Weather Report v2.0 started", CHATID)

# Initializing meteofrance object
client = meteofrance_api.MeteoFranceClient()
city = client.search_places(CITY)[0]

phenomenons_names = {
    1 : "Wind",
    2 : "Rain/Flood",
    8 : "Storm",
    }

weather_icons = {
    "Très nuageux": "☁",
    "Rares averses": "🌧",
    "Ensoleillé": "☀",
    "Risque d'orages": "🌩",
    "Eclaircies": "⛅",
    }

# Function to create the bot message
def create_report():
    # The aim is to get the min/max temperature for the morning and afternoon
    # Also, show the weather for each hour in the day (8-20)
    
    forecast_instance = client.get_forecast_for_place(city)
    hourly_forecasts = [f for f in forecast_instance.forecast
                        if 8 <= forecast_instance.timestamp_to_locale_time(f['dt']).hour <= 20
                        and forecast_instance.timestamp_to_locale_time(f['dt']).day == datetime.date.today().day]
    times = [forecast_instance.timestamp_to_locale_time(f['dt']) for f in hourly_forecasts]
    
    # Weather temperature combo part
    sumup = "Weather:\n"
    
    for f in hourly_forecasts:
        _hour = forecast_instance.timestamp_to_locale_time(f['dt']).hour
        try :
            _tmp = f" {_hour : 03d}h - {weather_icons[f['weather']['desc']]} {f['weather']['desc']}\t\t{f['T']['windchill']}°C\n"
        except :
            _tmp = f" {_hour : 03d}h - {f['weather']['desc']}\t\t{f['T']['windchill']}°C\n"
        sumup += _tmp
    
    sumup += "\n"
    
    # Today's weather alerts
    sumup += "Today's alerts:\n"
    alerts = client.get_warning_current_phenomenoms(city.admin2).phenomenons_max_colors
    
    for elem in alerts:
        if elem["phenomenon_id"] in list(phenomenons_names.keys()) and (elem["phenomenon_max_color_id"] > 1):
            _tmp = f" {phenomenons_names[elem['phenomenon_id']]}\n"
            sumup += _tmp
        
    return sumup

tg_bot.getUpdates()
last_update_id = tg_bot.last_update["result"][-1]["update_id"]

# main loop
while True:
    current_date = datetime.datetime.now()
    current_hour = current_date.hour + round(current_date.minute/60, 1)
    
    # Daily report
    if abs(current_hour-REPORT_HOUR) <= 0.085 :
        print("Sending daily report !")
        msg = create_report()
        
        tg_bot.sendMessage(msg, CHATID)
        
        time.sleep(300)
    
    # Getting updates
    tg_bot.getUpdates()
    updates_from_chatid = [msg for msg in tg_bot.last_update["result"] 
                           if msg["message"]["chat"]["id"] == CHATID
                           and msg["update_id"] > last_update_id]
    
    if len(updates_from_chatid) >= 1 :
        print("New msg !")
        print(f"Old updateID : {last_update_id}", end="\t")
        last_update_id = updates_from_chatid[-1]["update_id"]
        print(f"New updateID : {last_update_id}")
        last_msg = updates_from_chatid[-1]["message"]["text"]
        
        if last_msg == "/report":
            print("Sending report as requested")
            msg = create_report()
            
            tg_bot.sendMessage(msg, CHATID)
        
    time.sleep(30)
    