import requests
import dateutil
import re
from dateutil import parser
import keys
import numpy as np

import matplotlib.pyplot as plt
import io
import urllib,base64

def isValidCoordinates(coordinates):
    regex1 = "^[0-9]*.[0-9]*,[0-9]*.[0-9]*$"
    regex2 = "^[0-9]*.[0-9]*,%2C[0-9]*.[0-9]*$"

    isValid = re.match(regex1,coordinates) or re.match(regex2,coordinates)

    if isValid:
        return True
    else:
        return False


def getAPIresponse(coordinates):
    lat = coordinates.split(",")[0]
    lng = coordinates.split(",")[1]
    
    url = "https://stormglass.p.rapidapi.com/forecast"
    querystring = {"lat":lat,"lng":lng}  
    headers = {
            'x-rapidapi-host': "stormglass.p.rapidapi.com",
            'x-rapidapi-key': keys.apiKey
            }
    
    response = requests.request("GET", url, headers=headers, params=querystring)
    jsonResponse = response.json()
    
    return jsonResponse

def getTimestamps(jsonResponse):
    rawTimestamps = list()
    
    for record in jsonResponse["hours"]:
        timestamp = record["time"]
        rawTimestamps.append(timestamp)
        
    formattedDates = list()
    
    for timestamp in rawTimestamps:
        dateProcessed = parser.isoparse(timestamp)
        dateProcessed = dateProcessed.astimezone(dateutil.tz.gettz("+01:00"))
        dateProcessed = dateProcessed.strftime("%d/%m/%Y, %H:%M:%S")
        formattedDates.append(dateProcessed)
        
    return formattedDates


def getTemperatures(jsonResponse):
    temperatures = list()
    
    for record in jsonResponse["hours"]:
        temp = record["airTemperature"]
        temperatures.append(temp)
        
    temperaturesNOAA = list()
    
    for item in temperatures:
        for i in range(len(item)):
            if item[i]['source'] == 'noaa':
                temperaturesNOAA.append(item[i]['value'])
                
    return temperaturesNOAA


def getWindSpeed(jsonResponse):
    speeds = list()
    
    for record in jsonResponse["hours"]:
        spd = record['windSpeed']
        speeds.append(spd)
        
    speedsNOAA = list()
 
    for item in speeds:
        for i in range(len(item)):
            if item[i]['source'] == 'noaa':
                speedsNOAA.append(item[i]['value'])
                
    return speedsNOAA

def knotsToBeaufort(windSpeeds):
    beauforts = list()
    thresholds = [0,1,3.5,6.5,10.5,16.5,21.5,27.5,33.5,40.5,47.5,55.5,63.5]
    
    count = 0
    
    for speed in windSpeeds:
        while count < len(thresholds)-1:
            if speed >= thresholds[count] and speed < thresholds[count+1]:
                beauforts.append(count)
                count = 0
                break
            elif speed >= thresholds[len(thresholds)-1]:
                beauforts.append(12)
                break
            count += 1
    
    return beauforts

def getWindDirection(jsonResponse):
    directions = list()
    
    for record in jsonResponse["hours"]:
        direction = record['windDirection']
        directions.append(direction)
        
    directionsNOAA = list()

    for item in directions:
        for i in range(len(item)):
            if item[i]['source'] == 'noaa':
                directionsNOAA.append(item[i]['value'])
                
    return directionsNOAA

def verboseWindDirection(windDirections):
    directionsVerbosed = list()
    
    for direction in windDirections:
        if direction > 348.75 or direction >= 0 and direction < 11.25:
            directionsVerbosed.append("N")
        else:
            degrees = list()
            for i in range(1,30):
                if i % 2 != 0:
                    degrees.append(11.25*i)
            
            counter = 0
            for treshold in degrees:
                directionNames = ["NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
                if direction >= treshold and direction < treshold+22.5:
                    directionsVerbosed.append(directionNames[counter])
                    counter = 0
                counter += 1
        
            
    return directionsVerbosed

def getPlot(timestamps,temperatures,windSpeeds):
    plt.figure()

    fig, temperatureAxis = plt.subplots()
    
    ticks = list()
    for i in range(0,len(timestamps),20):
        ticks.append(timestamps[i])

    plt.xticks(np.arange(0,len(timestamps),len(timestamps)/len(ticks)),ticks,rotation=45)
    plt.grid()

    color = 'tab:red'
    temperatureAxis.set_xlabel('Czas')
    temperatureAxis.set_ylabel('Temperatura ($^\circ$C)', color=color)
    temperatureAxis.plot(timestamps,temperatures, color=color)
    temperatureAxis.tick_params(axis='y', labelcolor=color)
    
    windSpeedAxis = temperatureAxis.twinx()
     
    color = 'tab:blue'
    windSpeedAxis.set_ylabel('Prędkość wiatru [kn.]', color=color)
    windSpeedAxis.plot(windSpeeds, color=color)
    windSpeedAxis.tick_params(axis='y', labelcolor=color)
    
    fig.tight_layout()
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri =  urllib.parse.quote(string)
    return uri