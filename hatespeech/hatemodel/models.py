from calendar import day_abbr
from django.db import models


# Create your models here.
class Prediction(models.Model):
   
    date = models.DateField(auto_now_add=True)
    #day_of_week = models.CharField(max_length=11, blank=True)
    text = models.CharField(max_length=500, null = False, blank = False)
    prediction = models.CharField(max_length=25)

class Review(models.Model):
    class_choices = {
        1:"Hate speech detected",
        0:"No hate speech detected"
    }
    text = models.CharField(max_length = 500, blank = False, null = False)
    remarks = models.TextField(max_length=200, blank = True)
    classification = models.CharField(null = False, blank = False, max_length=25, choices = class_choices)