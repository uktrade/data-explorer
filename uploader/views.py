from .forms import PipelineForm, DataFileForm
from .models import Pipeline

from django.shortcuts import reverse, get_object_or_404
from django.views.generic import CreateView, DetailView


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


class PipelineDataUploadView(CreateView):
    template_name = 'dsu/pipeline_data_upload.html'
    form_class = DataFileForm

    def get_pipeline(self):
        return get_object_or_404(Pipeline, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['heading'] = 'Upload data'
        context_data['pipeline'] = self.get_pipeline()
        return context_data

    def get_success_url(self):
        return reverse(
            'uploader:pipeline-data-uploaded',
            kwargs={'slug': self.object.pipeline.slug}
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['pipeline'] = self.get_pipeline()
        return kwargs


class PipelineDataUploadedView(DetailView):
    template_name = 'dsu/pipeline_data_uploaded.html'
    model = Pipeline
    slug_url_kwarg = 'slug'
