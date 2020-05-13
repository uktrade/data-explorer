from django.urls import path

from .views import (
    PipelineCreateView,
    PipelineCreatedView,
    PipelineDataUploadView,
    PipelineDataUploadedView,
    PipelineSelectView,
)

app_name = 'uploader'

urlpatterns = [
    path('', PipelineSelectView.as_view(), name='pipeline-select'),
    path('create', PipelineCreateView.as_view(), name='pipeline-create'),
    path('created/<str:slug>/', PipelineCreatedView.as_view(), name='pipeline-created'),
    path('upload/<str:slug>/', PipelineDataUploadView.as_view(), name='pipeline-data-upload'),
    path('uploaded/<str:slug>/', PipelineDataUploadedView.as_view(), name='pipeline-data-uploaded'),
]
