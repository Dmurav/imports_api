from django.db import transaction, models
from rest_framework.exceptions import APIException, NotFound
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.views import APIView

from imports.api.models import Citizen, DataSet
from imports.api.operations import create_dataset, update_citizen, get_birthday_stats2
from imports.api.serializers import (CreateDataSetSerializer, CitizenSerializer,
                                     UpdateCitizenSerializer, )


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


class UpdateCitizenView(APIView):
    def update_citizen(self, data_set_id, citizen_id, citizen_data):
        key_serializer = UpdateCitizenSerializer(data={
            'data_set_id': data_set_id,
            'citizen_id': citizen_id,
        })
        key_serializer.is_valid(raise_exception=True)

        data_set_id = key_serializer.validated_data['data_set_id']
        citizen_id = key_serializer.validated_data['citizen_id']

        serializer = CitizenSerializer(data=citizen_data, partial=True)
        serializer.is_valid(raise_exception=True)
        relatives = serializer.validated_data.get('relatives')
        if relatives and citizen_id in relatives:
            raise serializers.ValidationError('Citizen can not be relative to itself.')

        citizen_validated_data = serializer.validated_data
        try:
            updated_citizen = update_citizen(data_set_id=data_set_id,
                                             citizen_id=citizen_id,
                                             citizen_data=citizen_validated_data)
        except models.ObjectDoesNotExist as e:
            raise NotFound(detail=e)

        return CitizenSerializer(instance=updated_citizen).data

    def patch(self, request, data_set_id, citizen_id):
        updated_citizen_data = self.update_citizen(
                data_set_id, citizen_id, citizen_data=request.data)
        data = {
            'data': updated_citizen_data,
        }
        return Response(data=data, status=status.HTTP_200_OK)


class ListDataSetCitizensView(APIView):
    def get(self, request, data_set_id):
        try:
            data_set = DataSet.objects.get(id=data_set_id)
        except DataSet.DoesNotExist as e:
            raise NotFound(e)

        citizens = (Citizen.objects
                    .filter(data_set=data_set).order_by('citizen_id')
                    # .prefetch_related('to_citizen_relatives')
                    # .prefetch_related('from_citizen_relatives')
                    .prefetch_related('relatives').all())
        response_data = {
            'data': CitizenSerializer(citizens, many=True).data
        }

        return Response(data=response_data, status=status.HTTP_200_OK)


class DataSetBirthdaysView(APIView):
    def get(self, request, data_set_id):
        try:
            DataSet.objects.get(id=data_set_id)
        except DataSet.DoesNotExist as e:
            raise NotFound(detail=e)

        response_data = {
            'data': get_birthday_stats2(data_set_id=data_set_id)
        }
        return Response(data=response_data, status=status.HTTP_200_OK)


class DataSetAgePercentiles(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'args': args,
            'kwargs': kwargs,
            'description': "Age percentiles per town."
        }
        return Response(data=data)
