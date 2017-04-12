from django.shortcuts import render, HttpResponse
from django.template import loader
import requests
import json
import pyowm 
from OWMapp.forms import WeatherForm
import sqlite3

# Create your views here.
# reference: http://drksephy.github.io/2015/07/16/django/

#For future reference, a database should not be used for weather

def index(request):
    return HttpResponse("Welcome to the Weather site!")

def weather(request):
    #template = loader.get_template('templates_app\weather.html')
    
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()

    #cur.execute('DROP TABLE IF EXISTS Weather ')
    cur.execute('CREATE TABLE IF NOT EXISTS Weather (city TEXT, status TEXT, humidity INTEGER, temperature INTEGER, wind INTEGER)')

    conn.close()
    
    parsedData = []
    
    owm = pyowm.OWM('c646db9215792630a0891c27e40c6745')
    
    if request.method == 'POST':
        
        city = request.POST.get('search-term')
        
        cityData = {}  

        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()
        print('Weather:')
        
        cur.execute("SELECT * FROM Weather WHERE city = '%s'" %city)
        x = cur.fetchone()  
        
        if (x != None):
            print("Executed")            
            
            cityData['status'] = x[1]
            cityData['humidity'] = x[2]
            cityData['temperature'] = x[3]
            cityData['wind_speed'] = x[4]
            parsedData.append(cityData)
            
            cur.close()
            return render(request, 'weather.html', {'data': parsedData})

        cur.close()
                
        forecast = owm.weather_at_place(city)
        w = forecast.get_weather()
        status = w.get_status()
        humidity = w.get_humidity()  
        temperature = w.get_temperature()
        wind = w.get_wind()

        temp = int(round((((temperature['temp'] - 273.15) * 9 / 5) + 32), 0))
        wind_speed = wind['speed']
        
        cityData['status'] = status
        cityData['humidity'] = humidity
        cityData['temperature'] = temp
        cityData['wind_speed'] = wind_speed
        
        parsedData.append(cityData)
        print(parsedData)
        
        conn = sqlite3.connect('db.sqlite3')
        cur = conn.cursor()

        cur.execute('INSERT INTO Weather (city, status, humidity, temperature, wind) VALUES ( ?, ?, ?, ?, ? )', 
                (city, cityData['status'], cityData['humidity'], cityData['temperature'], cityData['wind_speed']))
        conn.commit()
        
    #cur.execute('DELETE FROM Weather WHERE plays < 100')
    #conn.commit()

        cur.close()
        
    return render(request, 'weather.html', {'data': parsedData})
    