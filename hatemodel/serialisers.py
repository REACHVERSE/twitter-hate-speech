from rest_framework import serializers
from .models import Prediction, Review
import datetime


class PredictionSerializer(serializers.ModelSerializer):
    #day_of_week = serializers.SerializerMethodField()
    class Meta:
        model = Prediction
        fields = [
            "date",
            "text",
            "prediction",
            "id",
        ]
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "text",
            "remarks",
            "classification"
        ]
        
class PredictSerializer(serializers.Serializer):
    text = serializers.CharField()