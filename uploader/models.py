from django.db import models
from django.utils.text import slugify
from storages.backends.s3boto3 import S3Boto3Storage


def csv_file_name(instance, filename):
    return f"{instance.pipeline.organisation}/{instance.pipeline.dataset}/{filename}"


class FileStorage(S3Boto3Storage):
    location = 'generic'


class Pipeline(models.Model):
    organisation = models.CharField(max_length=256, null=False, blank=False)
    dataset = models.CharField(max_length=256, null=False, blank=False)
    slug = models.SlugField(
        editable=False, max_length=256
    )

    @property
    def data_workspace_table_name(self):
        return f'{self.organisation}_{self.dataset}'

    def __str__(self):
        return f'{self.organisation} {self.dataset}'

    class Meta:
        unique_together = ('organisation', 'dataset')

    def save(
        self, *args, **kwargs
    ):
        if not self.pk:
            value = " ".join([self.organisation, self.dataset])
            self.slug = slugify(value)
        return super().save(*args, **kwargs)


class DataFile(models.Model):
    pipeline = models.ForeignKey('Pipeline', null=False, blank=False, on_delete=models.CASCADE)
    csv_file = models.FileField(storage=FileStorage(), upload_to=csv_file_name)
