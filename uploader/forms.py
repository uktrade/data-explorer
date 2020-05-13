from django import forms
from .models import Pipeline


class PipelineForm(forms.ModelForm):

    class Meta:
        model = Pipeline
        fields = '__all__'
        widgets = {
            'organisation': forms.TextInput(attrs={'class': 'govuk-input'}),
            'dataset': forms.TextInput(attrs={'class': 'govuk-input'}),
        }
