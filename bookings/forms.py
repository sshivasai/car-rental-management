
from django import forms
from .models import Booking
from cars.models import ServiceLocations

class BookingForm(forms.ModelForm):
    pickup_location = forms.ModelChoiceField(queryset=ServiceLocations.objects.all(), label='Pickup Location', disabled=True)
    dropoff_location = forms.ModelChoiceField(queryset=ServiceLocations.objects.all(), label='Drop-off Location')
    pickup_date = forms.DateField(label='Pickup Date', widget=forms.DateInput(attrs={'type': 'date'}))
    pickup_time = forms.TimeField(label='Pickup Time', widget=forms.TimeInput(attrs={'type': 'time'}))
    dropoff_date = forms.DateField(label='Drop-off Date', widget=forms.DateInput(attrs={'type': 'date'}))
    dropoff_time = forms.TimeField(label='Drop-off Time', widget=forms.TimeInput(attrs={'type': 'time'}))
    coupon_code = forms.CharField(max_length=50, required=False, label='Coupon Code')

    class Meta:
        model = Booking
        fields = ['pickup_location', 'dropoff_location', 'pickup_date', 'pickup_time', 'dropoff_date', 'dropoff_time']

    def clean(self):
        cleaned_data = super().clean()
        pickup_date = cleaned_data.get('pickup_date')
        dropoff_date = cleaned_data.get('dropoff_date')

        if pickup_date and dropoff_date:
            if pickup_date > dropoff_date:
                raise forms.ValidationError("Drop-off date cannot be before pickup date.")
        

        return cleaned_data
