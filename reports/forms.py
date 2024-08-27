from django import forms
from core.models import Report, Room
from django.forms import TextInput, FileInput, CheckboxInput, DateInput, IntegerField, modelformset_factory, formset_factory


class ReportForm(forms.ModelForm): 
    class Meta:
        model = Report
        fields = [
            'company', 'company_logo', 'surveyor', 'property_address', 'external_picture',
            'external_logger', 'occupied', 'occupied_during_all_monitoring', 
            'number_of_occupants', 'notes', 'start_time', 'end_time'
        ]
        widgets = {
            'company': TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Enter company name',
                'id':'company',
                'required': True,
            }),
            'company_logo': FileInput(attrs={
                'class': 'hidden',
                'id': 'company_logo',
                'required': True,
            }),
            'surveyor': TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Enter surveyor name',
                'id':'surveyor',
                'required': True,
            }),
            'property_address': TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Enter property address',
                'id':'property_address',
                'required': True,
            }),
            'external_picture': FileInput(attrs={
                'class': 'hidden',
                'id': 'external_picture',
                'required': True,
            }),
            'external_logger': TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Enter Logger Serial Number',
                'id':'external_logger',
                'required': True,
            }),
            'occupied': CheckboxInput(attrs={
                'class':"w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
                'id':'occupied',
                'type':'checkbox',
                'required': False,
            }),
            'occupied_during_all_monitoring': CheckboxInput(attrs={
                'class':"w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
                'id':'occupied_during_all_monitoring',
                'type':'checkbox',
                'required': False,
            }),
            'number_of_occupants': TextInput(attrs={
                'class': "block py-2.5 px-1 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none dark:text-white dark:border-gray-600 dark:focus:border-blue-500 focus:outline-none focus:ring-0 focus:border-blue-600 peer", 
                'style':"border-radius: 0;",
                'placeholder': '',
                'id':'number_of_occupants',
                'required': False,
            }),
            'notes': forms.Textarea(attrs={
                'class': 'block p-2.5 w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Notes',
                'rows':'2',
                'id':'notes',
                'required': False,
            }),
           
            'start_time': DateInput(attrs={'type': 'text', 
                                           'id':'start_time',
                                            'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500", 
                                            'placeholder': 'Select date start'}),
            'end_time': DateInput(attrs={'type': 'text', 'id':'end_time',
                                          'class': "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full ps-10 p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500",
                                         'placeholder': 'Select date end'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['room_name', 'room_ambient_logger', 'room_surface_logger',
                  'room_monitor_area', 'room_mould_visible', 'room_picture']
        widgets = {
            'room_name': TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Enter room name',
                'id':'room_name',
                'required': True,
            }),
            'room_picture': FileInput(attrs={
                'class': 'hidden',
                'id':'room_picture',
                'required': True,
            }),
            'room_ambient_logger': TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Ambient Logger',
                'id':'room_ambient_logger',
                'required': True,
            }),
            'room_surface_logger': TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Surface Logger',
                'id':'room_surface_logger'
            }),
            'room_monitor_area': TextInput(attrs={
                'class': 'bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-primary-500 dark:focus:border-primary-500',
                'placeholder': 'Monitor Area',
                'id':'room_monitor_area',
                'required': True,
            }),
            'room_mould_visible': CheckboxInput(attrs={
                'class':"w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600",
                'id':'room_mould_visible',
                'type':'checkbox',
                'required': False,
            }),
            
        }

RoomFormSet = modelformset_factory(
    Room,
    form=RoomForm,  
    extra=1,
    
)