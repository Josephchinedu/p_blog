import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


def generate_unique_filename(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join("post_images", filename)


# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "POST"
        verbose_name_plural = "POSTS"

    @classmethod
    def fetch_posts(cls):
        return cls.objects.all()

    @classmethod
    def get_post(cls, id):
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def create_post(cls, title, content, created_by):
        return cls.objects.create(title=title, content=content, created_by=created_by)

    @classmethod
    def update_post(cls, id, title, content):
        return cls.objects.filter(id=id).update(title=title, content=content)


class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to=generate_unique_filename)

    class Meta:
        verbose_name = "POST IMAGE"
        verbose_name_plural = "POST IMAGES"

    @classmethod
    def get_post_images(cls, post_id):
        return cls.objects.filter(post=post_id)

    @classmethod
    def get_post_image(cls, id):
        return cls.objects.get(id=id)

    @classmethod
    def create_post_image(cls, post, image):
        return cls.objects.create(post=post, image=image)
    
    
