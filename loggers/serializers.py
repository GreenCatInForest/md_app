from rest_framework import serializers
from core.models import Logger_Data, Logger_Health

class LoggerHealthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logger_Health
        fields = ['timestamp', 'battery_voltage', 'faulty_status']


class LoggerDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = Logger_Data
        fields = ['timestamp', 'air_temperature', 'humidity', 'surface_temperature', 'pressure']
        extra_kwargs = {
                    'magnetometer_x': {'required': False},
                    'magnetometer_y': {'required': False},
                    'magnetometer_z': {'required': False},
                }
        
 
