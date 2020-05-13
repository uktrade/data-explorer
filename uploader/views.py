from .forms import PipelineForm
from .models import Pipeline

from django.shortcuts import reverse
from django.views.generic import CreateView, DetailView, TemplateView


class PipelineCreateView(CreateView):
    template_name = 'dsu/pipeline_create.html'
    form_class = PipelineForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['heading'] = 'Create pipeline'
        return context_data

    def get_success_url(self):
        return reverse('uploader:pipeline-created', kwargs={'slug': self.object.slug})


class PipelineCreatedView(DetailView):
    template_name = 'dsu/pipeline_created.html'
    model = Pipeline
    slug_url_kwarg = 'slug'


class PipelineUploadDataView(TemplateView):
    template_name = 'dsu/pipeline_upload_data.html'
    form_class = PipelineForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['heading'] = 'Upload data'
        return context_data
