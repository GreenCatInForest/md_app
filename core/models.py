import os
import uuid
from django.contrib.auth.models import (
    AbstractBaseUser, 
    BaseUserManager, 
    PermissionsMixin,
    Group, 
    Permission,
)
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


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
    
    
class PasswordReset(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Password reset for {self.user.email}"
    
def company_logo_upload_path(instance, filename):
    company_name = instance.company if instance.company else 'temp'
    return os.path.join('img', 'companies_img', str(company_name), filename)


   
def property_photo_upload_path(instance, filename):
    # Get the company ID
        property_address = instance.address if instance.address else 'temp'
    # Generate the upload path
        return os.path.join('img', 'properties_img', str(property_address), filename)

def room_photo_upload_path(instance, filename):
    # Get the company ID
        report = instance.report if instance.report else 'temp'
    # Generate the upload path
        return os.path.join('img', 'rooms_img', str(report), filename)

def report_property_photo_upload_path(instance, filename):
    property_address = instance.property_address if instance.property_address else 'temp'
    # Generate the upload path
    return os.path.join('img', 'properties_img', str(property_address), filename)
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

class Logger_Rental (models.Model):
    LOGGER_STATUS_CHOICES = [
        ('RENTAL_REQUESTED', 'Rental Requested'),
        ('IN_TRANSIT_TO_CLIENT', 'In Transit to Client'),
        ('WITH_CLIENT', 'With Client'),
        ('IN_TRANSIT_FROM_CLIENT', 'In Transit from Client'),
        ('RETURNED', 'Returned'),
    ]

    LOGGER_TYPE_CHOICES = [
        ('External', 'External'),
        ('Surface', 'Surface'),
        ('Ambient', 'Ambient'),
    ]
    status = models.CharField(max_length=30, choices=LOGGER_STATUS_CHOICES)
    logger_type = models.CharField(max_length=10, choices=LOGGER_TYPE_CHOICES)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = 'logger_rentals')
    logger = models.ForeignKey(Logger, on_delete=models.SET_NULL, null=True, blank=True)
    rental_start_date = models.DateTimeField()
    rental_end_date = models.DateTimeField()
    shipping_tracking_number = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add = True)
    last_updated = models.DateTimeField(auto_now = True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def rental_duration(self):
        return (self.rental_end_date - self.rental_start_date).days

    @property
    def is_paid(self):
        return self.payments.filter(status='succeeded').exists()
    
    def __str__(self):
        return f"Logger Rental {self.id} - {self.user.email}"


class Report (models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('generated', 'Generated'),
        ('paid', 'Paid'),
        ('unpaid', 'Unpaid'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    report_timestamp = models.DateTimeField(auto_now=True)
    property_address = models.CharField(max_length=455)
    external_picture = models.ImageField(upload_to=report_property_photo_upload_path, null=True, blank=True)
    external_logger = models.CharField(max_length=7)
    company = models.CharField(max_length=255)
    company_logo = models.ImageField(upload_to=company_logo_upload_path, null=True, blank=True)
    surveyor = models.CharField(max_length=255)
    notes = models.TextField()
    occupied = models.BooleanField(default=False)
    occupied_during_all_monitoring = models.BooleanField(default=False)
    number_of_occupants = models.IntegerField(default=0)
    report_file = models.FileField(upload_to='reports_save/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True, default='unpaid')
      # Ensure the file path is correctly formatted using instance-specific information
    def save(self, *args, **kwargs):
        if not self.report_file:
            self.report_file = f'reports/{self.id}/{self.property_address}_{self.start_time.strftime("%Y%m%d%H%M%S")}.pdf'
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Report {self.property_address} - {self.start_time.strftime('%Y-%m-%d')}"

    def add_report (cls, start_time, end_time, property, property_photo, company, surveyor, notes, report_file, report_requirements):
        report = Report(start_time=start_time, end_time=end_time, property=property, property_photo=property_photo, company=company, surveyor=surveyor, notes=notes, report_file=report_file, report_requirements=report_requirements)
        report.save()
        return report 
    
    # Additional logic for validation or processing
    def clean(self):
        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError(_('End time must be after start time.'))
        
    # Additional logic for payments    
    def mark_unpaid(self):
        if self.status == 'generated':
            self.status = 'unpaid'
            self.save()  

    @property
    def is_paid(self):
        return self.payments.filter(status='succeeded').exists()
    
    @property
    def update_payment_status(self):
        if self.is_paid:
            self.status = 'paid'
        else:
            self.status = 'unpaid'
        self.save()
    
    def __str__(self):
        return f"Report {self.id} - {self.user.email}"

   

class Room(models.Model):
    report = models.ForeignKey(Report, related_name='rooms', on_delete=models.CASCADE)
    room_name = models.CharField(max_length=255)
    room_picture = models.ImageField(upload_to=room_photo_upload_path, null=True, blank=True)
    room_ambient_logger = models.CharField(max_length=7)
    room_surface_logger = models.CharField(max_length=7)
    room_monitor_area = models.CharField(max_length=255, blank=True, null=True)
    room_mould_visible = models.BooleanField(default=False)

    def __str__(self):
        return f"Room {self.room_name} in Report {self.report_id}"
    
class Downloads(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=400, null=True, blank=True)
    file = models.FileField(upload_to='downloads/')
    class Meta:
        db_table = 'md_downloads'
        verbose_name_plural = 'downloads'

    def __str__(self):
        return self.name
    
    def get_file_url(self):
        if self.file:
            return self.file.url  
        return None
    

class PriceSetting(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('report', 'Report'),
        ('rental', 'Rental'),
        ('credit', 'Credit'),
    ]

    CURRENCY_CHOICES = [
        ('GBP', 'British Pound'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('AUD', 'Australian Dollar'),
        ('JPY', 'Japanese Yen'),
        ('CREDITS', 'Credits'),
    ]

    BILLING_TYPE_CHOICES = [
        ('per_item', 'Per Item'),
        ('per_time', 'Per Time (N Days)'),
        ('credit_based', 'Credit-Based'),
    ]

    PURCHASE_TYPE_CHOICES = [
        ('purchased', 'Purchased'),
        ('promotional', 'Promotional'),
    ]

    service_type = models.CharField(max_length=20, choices=SERVICE_TYPE_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    currency = models.CharField(max_length=7, choices=CURRENCY_CHOICES, default='GBP')

    billing_type = models.CharField(max_length=20, choices=BILLING_TYPE_CHOICES, default='per_item')
    interval_days = models.PositiveIntegerField(null=True, blank=True, help_text="Applicable only for 'per_time' billing.")
    credit_type = models.CharField(max_length=20, choices=PURCHASE_TYPE_CHOICES, null=True, blank=True, help_text="Applicable only for 'credit-based' billing.")

    def __str__(self):
        description = f"{self.get_service_type_display()} - {self.price} {self.currency} ({self.get_billing_type_display()})"
        if self.billing_type == 'per_time':
            description += f" every {self.interval_days} days"
        if self.billing_type == 'credit_based':
            description += f" ({self.get_credit_type_display()})"
        return description
    

class Payment(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=7, choices=PriceSetting.CURRENCY_CHOICES, default='GBP')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    logger_rental = models.ForeignKey(Logger_Rental, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')

    def update_report_status(self):
        if self.report:
            if self.status == 'succeeded':
                self.report.status = 'paid'
            elif self.status in ['failed', 'refunded', 'cancelled']:
                self.report.status = 'unpaid'
            else:
                self.report.status = 'pending'
            self.report.save()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print(f"[DEBUG] Payment saved with uuid: {self.uuid}")
        self.update_report_status()


    def set_price(self, *args, **kwargs):
        # Automatically set the price based on the service type
        if self.report:
            price_info = self.get_price_for_service('report')
        elif self.logger_rental:
            price_info = self.get_price_for_service('rental')
        else:
            raise ValidationError("Payment must be linked to either a report or logger rental.")
        
        self.amount = price_info['price']
        self.currency = price_info['currency']
        super().save(*args, **kwargs)

    def get_price_for_service(self, service_type):
        try:
            price_setting = PriceSetting.objects.get(service_type=service_type)
            return {
                "price": price_setting.price,
                "currency": price_setting.currency,
        }
        except ObjectDoesNotExist:
            raise ValidationError(f"Price for service type '{service_type}' is not set in the database.")
        
    def get_payment_type(self):
        if self.report:
            return "Report"
        elif self.logger_rental:
            return "Logger Rent"
        return "Unknown"

    def get_report_number(self):
        return self.report.id if self.report else None
    
    def get_report_date(self):
        return self.report.report_timestamp if self.report else None
    
    def get_report_link(self):
        if self.report:
            return format_html(
                '<a href="/admin/core/report/{}/change/">View Report</a>',
                self.report.id
            )
        return "-"
    get_report_link.short_description = "Report Link"
    get_report_link.allow_tags = True
    
    get_payment_type.short_description = "Payment Type"
    get_report_number.short_description = "Report Number"
    get_report_date.short_description = "Report Date"

    def __str__(self):
        return f"Payment {self.id} - {self.status}"
    
    def clean(self):
        # Ensure only one of the foreign keys is set
        items = [self.report, self.logger_rental]
        if sum(item is not None for item in items) != 1:
            raise ValidationError('Exactly one of report, logger_rental, or credit_package must be set.')
        
    