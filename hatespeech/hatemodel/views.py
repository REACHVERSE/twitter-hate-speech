from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, mixins
from rest_framework.exceptions import ParseError
import json

from datetime import date, timedelta
from django.db.models import Count, Q

from .models import Prediction
from .serialisers import PredictionSerializer

from hatemodel.services.prediction import predict

class PredictView(APIView,):
    #serializer_class = PredictionSerializer
    def post(self, request):
        try:
            data = json.loads(request.body)
            prediction = predict(data)
            print(prediction)
            prediction_obj = Prediction.objects.create(text=data.get("body"), prediction=prediction)

            return Response(
                {"text": data.get("body"), "prediction": prediction, "id": prediction_obj.id},
                status=status.HTTP_201_CREATED,
            )
            #return Response({"prediction":prediction})
        except json.JSONDecodeError:
            raise ParseError("Request must be valid JSON")   
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    #def create(request, )

class PredictionListAPIView(generics.ListAPIView):
    #permission_classes = []#"""""" #permissions.IsAuthenticatedOrReadOnly
    #authentication_classes = []
    serializer_class = PredictionSerializer
    queryset = Prediction.objects.all()

class PredictionDeleteView(generics.DestroyAPIView):
    serializer_class = PredictionSerializer
    queryset = Prediction.objects.all()
    lookup_field = "pk"

class PredictionWeekHistory(APIView):  
    serializer_class = PredictionSerializer
    queryset = Prediction.objects.all()
    def get(self, request):
        # ... (filtering logic as discussed previously)
        today = date.today()
        past_week_start = today - timedelta(days=7)
        predictions = Prediction.objects.all()
        serializer = PredictionSerializer(predictions, many=True)  # Serialize the predictions
        filters = Q(date__gte=past_week_start) & Q(day_of_week=request.GET.get('day_of_week'))
        predictions = Prediction.objects.filter(filters).annotate(count=Count('id')).order_by('day_of_week')
        serializer = PredictionSerializer(predictions, many=True)  # Serialize the filtered predictions
        serialized_data = serializer.data
        print(serialized_data)

        context = {'labels': [], 'data': []}
        for item in serialized_data:
            context['labels'].append(item['day_of_week'])
            context['data'].append(item['count'])
        return Response(context)