from django.urls import path

from .views import (
    PipelineCreateView,
    PipelineCreatedView,
    PipelineDataUploadView,
    PipelineDataUploadedView,
)

app_name = 'uploader'

urlpatterns = [
    path('', PipelineCreateView.as_view(), name='pipeline-create'),
    path('created/<str:slug>/', PipelineCreatedView.as_view(), name='pipeline-created'),
    path('upload/<str:slug>/', PipelineDataUploadView.as_view(), name='pipeline-data-upload'),
    path('uploaded/<str:slug>/', PipelineDataUploadedView.as_view(), name='pipeline-data-uploaded'),
]
