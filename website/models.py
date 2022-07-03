from django.db import models
from django.urls import reverse

# Create your models here.


class Article(models.Model):
    slug = models.SlugField()  # new

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug": self.slug})
