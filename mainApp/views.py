from django.shortcuts import render
import requests
from django.http import Http404, HttpResponse
from django.utils.datastructures import MultiValueDictKeyError
from .models import Spot,Song

from . import weatherAPI

def index(request):
    spots = Spot.objects.order_by('spotName')
    names = list()
    coordinates = list()
    for spot in spots:
        names.append(spot.spotName)
        coordinates.append(spot.coordinates)
    data = zip(names,coordinates)
    context = {'data':data}
    return render(request, 'mainApp/index.html',context)


def weather(request):
    if request.method == 'GET':       
        try:
            coordinates = request.GET['coordinates']
        except MultiValueDictKeyError:
            raise Http404
        
        if weatherAPI.isValidCoordinates(coordinates):
            try:
                ans = weatherAPI.getAPIresponse(coordinates)
                timestamps = weatherAPI.getTimestamps(ans)
                temperatures = weatherAPI.getTemperatures(ans)
                windSpeeds = weatherAPI.getWindSpeed(ans)
                beauforts = weatherAPI.knotsToBeaufort(windSpeeds)
                windDirections = weatherAPI.getWindDirection(ans)
                windDirectionsVerbosed = weatherAPI.verboseWindDirection(windDirections)
                plotURI = weatherAPI.getPlot(timestamps,temperatures,windSpeeds)
            except KeyError:
                 responseString = "Niewłaściwe współrzędne!<br>Wpisz współrzędne w postaci: <i>d.ddd...ddd,d.ddd...ddd</i> (stopnie miaromierne)."
                 return HttpResponse(responseString)
            
            spots = Spot.objects.order_by('spotName')
            spotsNames = list()
            spotsCoordinates = list()
            
            for spot in spots:
                spotsNames.append(spot.spotName)
                spotsCoordinates.append(spot.coordinates)

            if coordinates in spotsCoordinates:
                for i in range(len(spotsNames)):
                    if spotsCoordinates[i] == coordinates:
                        spotName = spotsNames[i]
                        context = {'spotName':spotName,'data':zip(timestamps,temperatures,windSpeeds,beauforts,windDirections,windDirectionsVerbosed),'plot':plotURI}
            else:
                spotName = coordinates
                context = {'spotName':spotName,'data':zip(timestamps,temperatures,windSpeeds,beauforts,windDirections,windDirectionsVerbosed),'plot':plotURI}
            
            return render(request, 'mainApp/weather.html', context)
        else:
            responseString = "Niewłaściwe współrzędne!<br>Wpisz współrzędne w postaci: <i>d.ddd...ddd,d.ddd...ddd</i> (stopnie miaromierne)."
            return HttpResponse(responseString)

def songs(request):
    songs = Song.objects.order_by('songName')
    titles = list()
    texts = list()
    
    for song in songs:
        titles.append(song.songName)
        texts.append(song.songText)
    data = zip(titles,texts)
    context = {'titles':titles,'data':data}
    return render(request, 'mainApp/songs.html', context)

def map(request):
    return render(request, 'mainApp/map.html')