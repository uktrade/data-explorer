from .forms import PipelineForm, DataFileForm, PipelineSelectForm
from .models import Pipeline

from django.shortcuts import reverse, get_object_or_404
from django.views.generic import CreateView, DetailView, FormView
from django.http import HttpResponseRedirect


class PipelineSelectView(FormView):
    template_name = 'dsu/pipeline_select.html'
    form_class = PipelineSelectForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['heading'] = 'Select pipeline'
        return context_data

    def form_valid(self, form):
        url = reverse(
            'uploader:pipeline-data-upload', kwargs={'slug': form.cleaned_data['pipeline'].slug}
        )
        return HttpResponseRedirect(url)


class PipelineCreateView(CreateView):
    template_name = 'dsu/pipeline_create.html'
    form_class = PipelineForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['heading'] = 'Create dataset'
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
        pipeline = self.get_pipeline()
        context_data['pipeline'] = pipeline
        context_data['heading'] = f'Upload data to {pipeline} pipeline'
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
