from django import forms
from .models import Pipeline, DataFile


class PipelineForm(forms.ModelForm):

    class Meta:
        model = Pipeline
        fields = '__all__'
        widgets = {
            'organisation': forms.TextInput(attrs={'class': 'govuk-input'}),
            'dataset': forms.TextInput(attrs={'class': 'govuk-input'}),
        }


class DataFileForm(forms.ModelForm):

    class Meta:
        model = DataFile
        fields = ['csv_file']
        widgets = {
            'csv_file': forms.FileInput(attrs={'class': 'govuk-file-upload'}),
        }

    def __init__(self, *args, **kwargs):
        self.pipeline = kwargs.pop('pipeline')
        super().__init__(*args, **kwargs)

    def save(
        self, *args, **kwargs
    ):
        self.instance.pipeline = self.pipeline
        return super().save(*args, **kwargs)
