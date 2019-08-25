from django.db import transaction
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.views import APIView

from imports.api.operations import create_dataset
from imports.api.serializers import CreateDataSetSerializer


class CreateDataSetView(APIView):
    def create_dataset(self, data):
        serializer = CreateDataSetSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return create_dataset(citizens=serializer.validated_data['citizens'])

    def post(self, request):
        dataset_id = self.create_dataset(data=request.data)
        data = {
            'data': {
                'import_id': dataset_id,
            }
        }
        return Response(data=data, status=status.HTTP_201_CREATED)



class DataSetCitizenView(APIView):
    def patch(self, request, *args, **kwargs):
        data = {
            'args': args,
            'kwargs': kwargs,
            'description': 'Update citizen data.'
        }
        return Response(data=data)


class ListDataSetCitizensView(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'args': args,
            'kwargs': kwargs,
            'description': "View all citizens in dataset."
        }
        return Response(data=data)


class DataSetBirthdaysView(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'args': args,
            'kwargs': kwargs,
            'description': "Number of citizen relatives with birthdays in each month."
        }
        return Response(data=data)


class DataSetAgePercentiles(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'args': args,
            'kwargs': kwargs,
            'description': "Age percentiles per town."
        }
        return Response(data=data)
