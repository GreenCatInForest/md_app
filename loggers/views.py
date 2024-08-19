from core.models import Logger_Data, Logger, Logger_Health
from .serializers import LoggerDataSerializer, LoggerHealthSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from django.db.models import Q, Max

class LoggerDataCreateView(APIView):

    def post(self, request):
        print("Received POST request")
        data = request.data
        logger_serial = data['logger']
        data_list = data['data']

        # Fetch or create the logger
        logger, created = Logger.objects.get_or_create(serial_number=logger_serial)
        if created:
            print(f"Logger created: {logger_serial}")
        else:
            print(f"Logger fetched: {logger_serial}")

        # Fetch the maximum timestamp for the logger
        max_timestamp = Logger_Data.objects.filter(logger=logger).aggregate(Max('timestamp'))['timestamp__max']
        if max_timestamp is None:
            max_timestamp = 0

        print(f"Max timestamp in database: {max_timestamp}")

        # Filter the incoming data
        filtered_data_list = [item for item in data_list if int(item['timestamp']) > max_timestamp]
        
        if not filtered_data_list:
            return Response({"message": "No new data to insert"}, status=status.HTTP_200_OK)

        logger_data_instances = []
        logger_health_instances = []

        for item in filtered_data_list:
            timestamp = item['timestamp']
            print(f"Processing data for timestamp: {timestamp}")

            # Prepare data for Logger_Data
            logger_data_instance = Logger_Data(
                logger=logger,
                timestamp=timestamp,
                air_temperature=item['air_temperature'],
                humidity=item['humidity'],
                surface_temperature=item['surface_temperature'],
                pressure=item['pressure'],
                magnetometer_x=item.get('magnetometer_x'),
                magnetometer_y=item.get('magnetometer_y'),
                magnetometer_z=item.get('magnetometer_z')
            )
            logger_data_instances.append(logger_data_instance)

            # Prepare data for Logger_Health
            battery_voltage = item.get('battery_voltage')
            if battery_voltage:
                logger_health_instance = Logger_Health(
                    logger=logger,
                    timestamp=timestamp,
                    battery_voltage=battery_voltage
                )
                logger_health_instances.append(logger_health_instance)

        # Bulk create logger data
        Logger_Data.objects.bulk_create(logger_data_instances, ignore_conflicts=True, batch_size=1000)
        Logger_Health.objects.bulk_create(logger_health_instances, ignore_conflicts=True, batch_size=1000)

        return Response({"message": "Logger data created successfully"}, status=status.HTTP_201_CREATED)

    def delete(self, request):
        logger_data = Logger_Data.objects.all()
        logger = Logger.objects.all()
        logger_data.delete()
        logger.delete()
        return Response({"message": "All logger data deleted successfully"}, status=status.HTTP_200_OK)


class LoggerDataListView(ListAPIView):
    queryset = Logger_Data.objects.all()
    serializer_class = LoggerDataSerializer


class LoggerDataDetailView(RetrieveAPIView):
    queryset = Logger_Data.objects.all()
    serializer_class = LoggerDataSerializer


class LoggerDataDeleteView(DestroyAPIView):
    queryset = Logger_Data.objects.all()
    serializer_class = LoggerDataSerializer


class LoggerHealthListView(ListAPIView):
    queryset = Logger_Health.objects.all()
    serializer_class = LoggerHealthSerializer


class LoggerHealthDetailView(RetrieveAPIView):
    queryset = Logger_Health.objects.all()
    serializer_class = LoggerHealthSerializer

class LoggerHealthDeleteView(APIView):

    def delete(self, request):
        logger_health_data = Logger_Health.objects.all()
        logger_health_data.delete()
        return Response({"message": "All logger health data deleted successfully"}, status=status.HTTP_200_OK)


class LoggerDataSearchView(APIView):
    def get(self, request):
        query_params = request.query_params
        logger_serial = query_params.get('logger_serial')
        timestamp = query_params.get('timestamp')

        if not logger_serial or not timestamp:
            return Response({"error": "logger_serial and timestamp are required query parameters"}, status=status.HTTP_400_BAD_REQUEST)

        logger = Logger.objects.filter(serial_number=logger_serial).first()
        if not logger:
            return Response({"error": "Logger not found"}, status=status.HTTP_404_NOT_FOUND)

        logger_data = Logger_Data.objects.filter(logger=logger, timestamp=timestamp).first()
        if not logger_data:
            return Response({"error": "Logger Data not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = LoggerDataSerializer(logger_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    