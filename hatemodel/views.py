from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.exceptions import ParseError
import json

from datetime import date, timedelta
from django.db.models import Count

from .models import Prediction, Review
from .serialisers import PredictionSerializer, ReviewSerializer

from hatemodel.services.prediction import predict, model_accuracy

class PredictView(APIView):
    def post(self, request):
        try:
            predtext = request.data.get("text")
            if not predtext:
                return Response({"error": "No text provided."}, status=status.HTTP_400_BAD_REQUEST)
                
            prediction_label, confidence = predict(predtext)
            
            prediction_obj = Prediction.objects.create(text=predtext, prediction=prediction_label)
            
            return Response(
                {
                    "text": predtext,
                    "prediction": prediction_label,
                    "confidence": confidence,
                    "id": prediction_obj.id,
                    'accuracy': model_accuracy
                },
                status=status.HTTP_201_CREATED,
            )
        except json.JSONDecodeError:
            raise ParseError("Request must be valid JSON")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PredictionListAPIView(generics.ListAPIView):
    serializer_class = PredictionSerializer
    queryset = Prediction.objects.all()

class PredictionDeleteView(generics.DestroyAPIView):
    serializer_class = PredictionSerializer
    queryset = Prediction.objects.all()
    lookup_field = "pk"

class PredictionCountByPredictionView(APIView):
    HATE_SPEECH = "Hate speech detected"
    OFFENSIVE_SPEECH = "Offensive speech detected"
    NORMAL_SPEECH = "Normal speech"

    def get(self, request):
        today = date.today()
        past_week_start = today - timedelta(days=7)
        
        base_queryset = Prediction.objects.filter(date__gte=past_week_start)
        
        predictions_hate = base_queryset.filter(prediction=self.HATE_SPEECH).values('date').annotate(count=Count('id'))
        predictions_offensive = base_queryset.filter(prediction=self.OFFENSIVE_SPEECH).values('date').annotate(count=Count('id'))
        predictions_normal = base_queryset.filter(prediction=self.NORMAL_SPEECH).values('date').annotate(count=Count('id'))

        days = [(past_week_start + timedelta(days=i)).strftime("%A") for i in range(7)]
        day_counts_hate = {day: 0 for day in days}
        day_counts_offensive = {day: 0 for day in days}
        day_counts_normal = {day: 0 for day in days}

        for p in predictions_hate:
            day_counts_hate[p['date'].strftime("%A")] = p['count']
        for p in predictions_offensive:
            day_counts_offensive[p['date'].strftime("%A")] = p['count']
        for p in predictions_normal:
            day_counts_normal[p['date'].strftime("%A")] = p['count']

        response_data = {
            'labels': days,
            'datasets': [
                {'label': self.HATE_SPEECH, 'data': list(day_counts_hate.values())},
                {'label': self.OFFENSIVE_SPEECH, 'data': list(day_counts_offensive.values())},
                {'label': self.NORMAL_SPEECH, 'data': list(day_counts_normal.values())},
            ]
        }
        return Response(response_data)

class ReviewPostView(APIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()

    def get(self, request):
        last_prediction = Prediction.objects.last()
        if last_prediction:
            return Response({'text': last_prediction.text})
        return Response({'text': ''})

    def post(self, request):
        try:
            last_prediction = Prediction.objects.last()
            if not last_prediction:
                return Response({"error": "No prediction to review."}, status=status.HTTP_404_NOT_FOUND)
            
            reviewobj = Review.objects.create(
                text=last_prediction.text,
                remarks=request.data.get("remarks"),
                classification=request.data.get("classification")
            )
            return Response(
                {"text": last_prediction.text, "remarks": reviewobj.remarks, "classification": reviewobj.classification},
                status=status.HTTP_201_CREATED,
            )
        except json.JSONDecodeError:
            raise ParseError("Request must be valid JSON")
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReviewListView(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class PredictionStatsView(APIView):
    def get(self, request):
        total_predictions = Prediction.objects.count()
        
        today = date.today()
        last_week_start = today - timedelta(days=7)
        last_week_predictions = Prediction.objects.filter(date__gte=last_week_start).count()
        
        hate_speech_count = Prediction.objects.filter(prediction="Hate speech detected").count()
        offensive_speech_count = Prediction.objects.filter(prediction="Offensive speech detected").count()
        normal_speech_count = Prediction.objects.filter(prediction="Normal speech").count()
        
        def calculate_pct(count, total):
            return (count / total) * 100 if total > 0 else 0

        response_data = {
            'total_predictions': total_predictions,
            'last_week_predictions': last_week_predictions,
            'hate_speech_count': hate_speech_count,
            'offensive_speech_count': offensive_speech_count,
            'normal_speech_count': normal_speech_count,
            'hate_speech_percentage': calculate_pct(hate_speech_count, total_predictions),
            'offensive_speech_percentage': calculate_pct(offensive_speech_count, total_predictions),
            'normal_speech_percentage': calculate_pct(normal_speech_count, total_predictions),
            'accuracy': model_accuracy
        }
        return Response(response_data)