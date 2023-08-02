from django.core.exceptions import ValidationError
from PIL import Image as PILImage
from rest_framework import serializers

from main.models import Post, PostImage


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, min_length=4)
    email = serializers.EmailField(max_length=255, min_length=4)
    first_name = serializers.CharField(max_length=255, min_length=4)
    last_name = serializers.CharField(max_length=255, min_length=4)
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, min_length=4)
    password = serializers.CharField(max_length=128, min_length=8, write_only=True)


# BLOG POST SERIALIZERS
class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "title",
            "content",
        ]


class UploadImageSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
    image = serializers.ImageField()

    def validate_image(self, value):
        try:
            pil_image = PILImage.open(value)
            if pil_image.format not in ["JPEG", "PNG"]:
                raise ValidationError("Only JPEG and PNG images are allowed.")
            max_image_size = 5 * 1024 * 1024  # 5 MB
            if value.size > max_image_size:
                raise ValidationError("Image size should be less than 5MB.")
        except PILImage.UnidentifiedImageError:
            raise ValidationError("Invalid image format.")

        return value


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("image",)

    def get_image_url(self, obj):
        request = self.context.get("request")
        if (
            obj.image
        ):  # Check if the image exists to avoid 'NoneType' object has no attribute 'url' error
            return request.build_absolute_uri(obj.image.url)
        return None


class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "content",
            "created_by",
            "images",
            "created_at",
            "updated_at",
        ]
