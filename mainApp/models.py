from django.db import models

class Spot(models.Model):
    spotName = models.CharField(max_length = 200)
    coordinates = models.CharField(max_length = 50)

    def __str__(self):
        spotCoordinates = " (" + self.coordinates + ")"
        spotVerbose = self.spotName + spotCoordinates
        return spotVerbose

class Song(models.Model):
    songName = models.CharField(max_length = 200)
    songText = models.TextField()

    def __str__(self):
        return self.songName[:20] + "..."
