from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ParseError
import json

from hatemodel.services.prediction import predict

class PredictionView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
            prediction = predict(data)
            return Response("{Prediction}:prediction")
        except json.JSONDecodeError:
            raise ParseError("Request must be valid JSON")   
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)