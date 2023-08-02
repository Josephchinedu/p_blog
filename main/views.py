from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import render
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from main.models import Post, PostImage
from main.serializers import (
    CreatePostSerializer,
    LoginSerializer,
    PostSerializer,
    RegisterSerializer,
    UploadImageSerializer,
)


# Create your views here.
## --------------- AUTHENTICATION CLASSES
class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        username = serializer.validated_data.get("username")
        first_name = serializer.validated_data.get("first_name")
        last_name = serializer.validated_data.get("last_name")
        password = serializer.validated_data.get("password")

        User = get_user_model()

        # validate the data
        if User.objects.filter(email=email).exists():
            data = {"error": True, "message": "Email already exists"}

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            data = {
                "error": True,
                "message": "Username already exists",
            }
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        user_instance = User.objects.create(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password),
        )

        # handle account verification here

        # handle token generation here
        tokenr = TokenObtainPairSerializer().get_token(user_instance)
        tokena = AccessToken().for_user(user_instance)

        data = {
            "error": False,
            "code": "201",
        }

        data["tokens"] = {"refresh": str(tokenr), "access": str(tokena)}
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")

        User = get_user_model()

        try:
            user_instance = User.objects.get(username=username)
        except User.DoesNotExist:
            data = {"error": True, "message": "incorrect username or password"}

            return Response(data, status=status.HTTP_404_NOT_FOUND)

        if not check_password(password, user_instance.password):
            data = {"error": True, "message": "incorrect username or password"}

            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        tokenr = TokenObtainPairSerializer().get_token(user_instance)
        tokena = AccessToken().for_user(user_instance)

        data = {
            "error": False,
            "code": "200",
        }

        data["tokens"] = {"refresh": str(tokenr), "access": str(tokena)}
        return Response(data, status=status.HTTP_200_OK)


## --------------- END OF AUTHENTICATION CLASSES



class BlogPostApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    create_post_serializer = CreatePostSerializer
    post_serializer = PostSerializer

    def post(self, request):
        serializer = self.create_post_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        title = serializer.validated_data.get("title")
        content = serializer.validated_data.get("content")

        Post().create_post(title=title, content=content, created_by=request.user)

        # create post here
        return Response(
            {"error": False, "message": "Post created successfully"},
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        post_id = request.GET.get("id", 0)

        if str(post_id).isdigit():
            post_id = int(post_id)
        else:
            data = {"error": True, "message": "Invalid post id"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        if post_id == 0:
            posts = Post().fetch_posts()
            posts = self.post_serializer(posts, many=True)
            data = {
                "error": False,
                "message": "Posts retrieved successfully",
                "posts": posts.data,
            }
            return Response(data, status=status.HTTP_200_OK)

        post = Post().get_post(id=post_id)
        posts = self.post_serializer(post)
        data = {
            "error": False,
            "message": "Post retrieved successfully",
            "post": posts.data,
        }

        return Response(data, status=status.HTTP_200_OK)


class BlogPostImageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    upload_image_serializer_class = UploadImageSerializer

    def post(self, request):
        serializer = self.upload_image_serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        post_id = serializer.validated_data.get("post_id")
        images_data = request.FILES.getlist("image")

        get_post = Post().get_post(id=post_id)

        if get_post is None:
            return Response(
                {"error": True, "message": "Post does not exist"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not images_data:
            return Response(
                {"error": True, "message": "No image was uploaded"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        for image_data in images_data:
            PostImage().create_post_image(post=get_post, image=image_data)

        post_image_qs = PostImage().get_post_images(post_id=post_id)

        data = {
            "error": False,
            "message": "Images uploaded successfully",
        }

        return Response(data, status=status.HTTP_201_CREATED)
