from django.urls import path

from .views import PipelineCreateView, PipelineCreatedView, PipelineUploadDataView

app_name = 'uploader'

urlpatterns = [
    path('', PipelineCreateView.as_view(), name='pipeline-create'),
    path('created/<str:slug>/', PipelineCreatedView.as_view(), name='pipeline-created'),
    path('upload/<str:slug>/', PipelineUploadDataView.as_view(), name='pipeline-upload-data'),
]
