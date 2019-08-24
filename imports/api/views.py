from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView


class DataSetCitizenView(APIView):
    def patch(self, request, *args, **kwargs):
        data = {
            'args': args,
            'kwargs': kwargs,
            'description': 'Update citizen data.'
        }
        return Response(data=data)


class CreateDataSetView(APIView):
    def post(self, request, *args, **kwargs):
        data = {
            'args': args,
            'kwargs': kwargs,
            'description': 'Create new dataset',
        }
        return Response(data=data, status=HTTP_200_OK)


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
