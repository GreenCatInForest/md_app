from django.contrib.auth.models import (
    AbstractBaseUser, 
    BaseUserManager, 
    PermissionsMixin,
    Group, 
    Permission,
)
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    last_changed = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  #  custom related name to avoid conflicts
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',  #  custom related name to avoid conflicts
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )
    
    objects = UserManager()

    USERNAME_FIELD = 'email'    
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return f"{self.name} {self.surname}"
    

    from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.conf import settings

class Logger (models.Model):
    serial_number = models.CharField(max_length=255, unique=True)
    registered_date = models.DateTimeField(auto_now=True)
    rent_status = models.BooleanField(default=False)
    LOGGER_SURFACE_CHOICES = [('Surface', 'Surface'), ('Ambient', 'Ambient'), ('External', 'External')]
    logger_surface=models.CharField(max_length=10, choices=LOGGER_SURFACE_CHOICES, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'loggers'

    def __str__(self):
        return self.serial_number
    
    def add_logger (cls, serial_number, rent_status):
        logger = Logger(serial_number=serial_number, rent_status=rent_status)
        logger.save()
        return logger
    
    def edit_logger (cls, logger, serial_number, rent_status):
        logger.serial_number = serial_number
        logger.rent_status = rent_status
        logger.save()
        return logger
    
    def remove_logger (cls, logger_id):
        try:
            logger_to_remove = cls.objects.get(pk=logger_id)
            logger_to_remove.delete()
            return True
        except cls.DoesNotExist:
            return False 
    

class Logger_Changes (models.Model):
      user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
      logger = models.ForeignKey(Logger, on_delete=models.CASCADE)
      logger_sent_date = models.DateTimeField(auto_now=True)
      logger_received_date = models.DateTimeField(auto_now=True)
      rent_date = models.DateTimeField(auto_now=True)
      rent_days = models.IntegerField()
      change_date = models.DateTimeField(auto_now=True)
      class Meta:
            verbose_name_plural = 'logger changes'
        
class Logger_Data (models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    logger = models.ForeignKey(Logger, on_delete=models.CASCADE)
    timestamp = models.BigIntegerField()
    air_temperature = models.FloatField() 
    surface_temperature = models.FloatField() or None
    humidity = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    pressure = models.FloatField(validators=[MinValueValidator(950.00), MaxValueValidator(1100.00)])
    magnetometer_x = models.SmallIntegerField(null=True, blank=True, validators=[MinValueValidator(-32768), MaxValueValidator(32767)])  # Magnetometer x component as a 16-bit signed integer
    magnetometer_y = models.SmallIntegerField(null=True, blank=True, validators=[MinValueValidator(-32768), MaxValueValidator(32767)])  # Magnetometer y component as a 16-bit signed integer
    magnetometer_z = models.SmallIntegerField(null=True, blank=True, validators=[MinValueValidator(-32768), MaxValueValidator(32767)])  # Magnetometer z component as a 16-bit signed integer
    
    class Meta:
        verbose_name_plural = 'logger data'

    def __str__(self):
        return self.logger.serial_number + ' ' + str(self.timestamp) 
    
    def get_serial_number (cls, logger, serial_number):
        return cls.objects.get(serial_number = serial_number, logger=logger)

class Logger_Health (models.Model):
    logger = models.ForeignKey(Logger, on_delete=models.CASCADE)
    timestamp = models.BigIntegerField()
    battery_voltage = models.FloatField(validators=[MinValueValidator(2.4), MaxValueValidator(4.5)], null=True, blank=True) 
    faulty_status = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'logger health'


