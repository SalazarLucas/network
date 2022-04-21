import json
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator, EmptyPage
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import Post, User


def index(request):
    try:
        page_number = int(request.GET.get('page'))
    except (TypeError, ValueError):
        page_number = 1

    post_objects = Post.objects.all()
    ordered_post_objects = post_objects.order_by("-timestamp").all()
    paginator = Paginator(ordered_post_objects, 10)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        return render(request, "network/error.html", status=404)

    return render(request, "network/index.html", {
        "page_obj": page_obj
    })


def profile(request, profile_name):
    try:
        profile = User.objects.get(username=profile_name)
    except User.DoesNotExist:
        return render(request, "network/error.html", status=404)

    try:
        page_number = int(request.GET.get('page'))
    except (TypeError, ValueError):
        page_number = 1

    post_objects = profile.posts.all()
    ordered_post_objects = post_objects.order_by("-timestamp").all()
    paginator = Paginator(ordered_post_objects, 10)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        return render(request, "network/error.html", status=404)

    return render(request, "network/profile.html", {
        "profile": profile,
        "page_obj": page_obj
    })


def following(request):
    if request.user.is_authenticated:
        try:
            page_number = int(request.GET.get('page'))
        except (TypeError, ValueError):
            page_number = 1

        post_objects = Post.objects.all()
        ordered_post_objects = post_objects.order_by("-timestamp").all()
        following_posts = [post for post in ordered_post_objects if post.writer in request.user.following.all()]
        paginator = Paginator(following_posts, 10)

        try:
            page_obj = paginator.page(page_number)
        except EmptyPage:
            return render(request, "network/error.html", status=404)

        return render(request, "network/following.html", {
            "page_obj": page_obj
        })
    
    return HttpResponseRedirect(reverse('index'))


def new_post(request):
    if request.method == "POST" and request.user.is_authenticated:
        content = request.POST["content"]
        post = Post(content=content, writer=request.user)
        if post.is_valid():
            post.save()
    
    return HttpResponseRedirect(reverse('index'))


def follow_unfollow(request, profile_name):
    if request.method == "POST" and request.user.is_authenticated:
        profile = User.objects.get(username=profile_name)
        user = User.objects.get(pk=request.user.id)

        if profile not in user.following.all():
            user.following.add(profile)
        else:
            user.following.remove(profile)
        
        user.save()
    
    return HttpResponseRedirect(reverse('profile', args=[profile_name,]))


def edit_post(request):
    if request.method != "PUT":
        return JsonResponse({"message": "PUT request required"}, status=403)
    
    if not request.user.is_authenticated:
        return JsonResponse({"message": "User not authenticated"}, status=403)
    
    data = json.loads(request.body)
    post = Post.objects.get(pk=data.get("post_id"))
    new_content = data.get("content")

    if request.user == post.writer:
        post.content = new_content
        post.save()

        return JsonResponse({"content": new_content}, status=200)
    
    else:
        return JsonResponse({"message": "You cannot edit a post you don't own."}, status=403)


def like_unlike(request):
    if request.method != "PUT":
        return JsonResponse({"message": "PUT request required"}, status=403)
    
    if not request.user.is_authenticated:
        return JsonResponse({"message": "User not authenticated"}, status=403)
    
    data = json.loads(request.body)
    post = Post.objects.get(pk=data.get("post_id"))
    user = User.objects.get(pk=request.user.id)

    if post in user.likes.all():
        user.likes.remove(post)
        user.save()
        return JsonResponse({"message": f": success, you unliked a post from {post.writer}"})
    else:
        user.likes.add(post)
        user.save()
        return JsonResponse({"message": f": success, you liked a post from {post.writer}"})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
