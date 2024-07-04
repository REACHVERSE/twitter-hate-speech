from calendar import day_abbr
from django.db import models


# Create your models here.
class Prediction(models.Model):
   
    date = models.DateTimeField(auto_now_add=True)
    #day_of_week = models.CharField(max_length=11, blank=True)
    text = models.CharField(max_length=500, null = False, blank = False)
    prediction = models.CharField(max_length=25)

    """def save(self, *args, **kwargs):
        
        #Override the save method to calculate and store the day of the week.
        
        #self.day_of_week = self.date("%A")  # Full day name (Monday, Tuesday, etc.)
        if self.date:
            self.day_of_week = day_abbr(self.date.year, self.date.month, self.date.day)
            super().save(*args, **kwargs)"""