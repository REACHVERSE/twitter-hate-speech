from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, mixins
from rest_framework.exceptions import ParseError
import json

from datetime import date, datetime, timedelta
from django.db.models import Count, Q

from .models import Prediction, Review
from .serialisers import PredictionSerializer, ReviewSerializer

from hatemodel.services.prediction import predict
import pickle

model_acc = pickle.load(open("hatemodel/services/accuracy.pkl", "rb"))

class PredictView(APIView,):
    #serializer_class = PredictionSerializer
    def post(self, request):
        try:
            #data = request.data
            predtext = request.data#.get("text")
            print(predtext)
            prediction = predict(predtext)
            print(prediction)
            prediction_obj = Prediction.objects.create(text=predtext, prediction=prediction)
            #predaccuracy = ("{:.2f}%".format(accuracy))
            predaccuracy = model_acc

            return Response(
                {"text": predtext, "prediction": prediction, "id": prediction_obj.id,  'accuracy' : predaccuracy}, 
                status=status.HTTP_201_CREATED,
            )
            #return Response({"prediction":prediction})
        except json.JSONDecodeError:
            raise ParseError("Request must be valid JSON")   
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


        
    

class PredictionListAPIView(generics.ListAPIView):
    #permission_classes = []#"""""" #permissions.IsAuthenticatedOrReadOnly
    #authentication_classes = []
    serializer_class = PredictionSerializer
    queryset = Prediction.objects.all()





class PredictionDeleteView(generics.DestroyAPIView):
    serializer_class = PredictionSerializer
    queryset = Prediction.objects.all()
    lookup_field = "pk"





class PredictionCountByPredictionView(APIView):
  HATE_SPEECH = "Hate speech detected"
  NO_HATE_SPEECH = "No hate speech detected"

  def get(self, request):
    today = date.today()
    past_week_start = today - timedelta(days=7)
    filters = Q(date__gte=past_week_start)

    #predictions_hate_speech = Prediction.objects.filter(filters, prediction=self.HATE_SPEECH).order_by('date').values('date').annotate(count=Count('id'))
    #predictions_no_hate_speech = Prediction.objects.filter(filters, prediction=self.NO_HATE_SPEECH).order_by('date').annotate(count=Count('id'))


    # Combine filters and day_of_week retrieval (assuming day_of_week is a model field)
    base_queryset = Prediction.objects.filter(filters)
    predictions_hate_speech = base_queryset.filter(prediction=self.HATE_SPEECH).values('date').annotate(count=Count('id'))
    predictions_no_hate_speech = base_queryset.filter(prediction=self.NO_HATE_SPEECH).values('date').annotate(count=Count('id'))

    
    # Handle missing days and keep day names
    day_counts_hate_speech = {}
    for prediction in predictions_hate_speech:
        #print(prediction)
        day_counts_hate_speech[datetime.strftime(prediction['date'], "%A")] = prediction['count']  # Assuming prediction is the serializer method result
    

    day_counts_no_hate_speech = {}
    for prediction in predictions_no_hate_speech:
        #print(prediction)
        day_counts_no_hate_speech[datetime.strftime(prediction['date'], "%A")] = prediction['count']

    # Ensure all days are present with count 0 (optional)
    all_days = {day: 0 for day in set(datetime.strftime(pred['date'], "%A") for pred in predictions_hate_speech.union(predictions_no_hate_speech))}
    day_counts_hate_speech = {**all_days, **day_counts_hate_speech}
    day_counts_no_hate_speech = {**all_days, **day_counts_no_hate_speech}
    print(day_counts_hate_speech)
    print(day_counts_no_hate_speech)


    dates = list(day_counts_hate_speech.keys())  # Use day names as labels

    response_data = {
        'labels': dates,
        'datasets': [
            {
            'label': self.HATE_SPEECH,
            'data': list(day_counts_hate_speech.values()),
            },
            {
            'label': self.NO_HATE_SPEECH,
            'data': list(day_counts_no_hate_speech.values()),
            },
        ]
    }

    return Response(response_data)





class ReviewPostView(APIView):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    def post(self, request):
        #print(json.loads(request))
        try:
            text = Prediction.objects.last().text
            reviewobj = Review.objects.create(text = text, remarks = request.data.get("remarks"), classification = request.data.get("classification"))

            return Response(
                {"text": text, "remarks":reviewobj.remarks, "classification": reviewobj.classification},
                status=status.HTTP_201_CREATED,
            )
            #return Response({"prediction":prediction})
        except json.JSONDecodeError:
            raise ParseError("Request must be valid JSON")   
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ReviewListView(generics.ListAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

class PredictionStatsView(APIView):
    def get(self, request):
        today = date.today()
        last_week_start = today - timedelta(days=7)

        # Total predictions
        total_predictions = Prediction.objects.count()

        # Predictions in the last week
        last_week_predictions = Prediction.objects.filter(date__gte=last_week_start, date__lte=today).count()

        # Hate speech and non-hate speech counts (assuming classification field)
        hate_speech_count = Prediction.objects.filter(prediction="Hate speech detected").count()
        non_hate_speech_count = Prediction.objects.filter(prediction="No hate speech detected").count()

        # Calculate percentages (handle division by zero)
        total_hate_speech_pct = (hate_speech_count / total_predictions) * 100 if total_predictions > 0 else 0
        total_non_hate_speech_pct = (non_hate_speech_count / total_predictions) * 100 if total_predictions > 0 else 0

        # Prepare response data
        response_data = {
            'total_predictions': total_predictions,
            'last_week_predictions': last_week_predictions,
            'hate_speech_percentage': total_hate_speech_pct,
            'non_hate_speech_percentage': total_non_hate_speech_pct,
            'accuracy' : model_acc
        }

        return Response(response_data)
