from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

import json
import boto3

from .forms import UserRegisterForm
from .models import Post, Seller
from .forms import UserRegisterForm

headers = {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
            }
# Create your views here.
@csrf_exempt
def index(request: HttpRequest):
    if request.method == "GET":
        posts_list = serializers.serialize("json", Post.objects.all())
        return HttpResponse(posts_list, headers)
    elif request.method == "POST" and request.user.is_authenticated:
        body = json.loads(request.body)
        try:
            seller = Seller.objects.get(name=body["seller"])
        except Seller.DoesNotExist:
            return HttpResponse("Seller not found", headers, status=404)
 
        p = Post(title=body["title"],
                    description=body["description"],
                    seller=seller,
                    image_url=body["image_url"],
                    pub_date=timezone.now())
        p.save()
        p_json = serializers.serialize("json", [p])
        return HttpResponse(p_json, headers)

    # response = json.dumps(posts_list)
    # return HttpResponse(f"Welcome to olx API \n{posts_list}")

@csrf_exempt
def sellers(request: HttpRequest):
    if request.method == "GET":
        seller_list = serializers.serialize("json", Seller.objects.all())
        return HttpResponse(seller_list, headers)
    elif request.method == "POST":
        body = json.loads(request.body)
        s = Seller(name=body["name"],
                    email=body["email"])
        s.save()
        s_json = serializers.serialize("json", [s])
        return HttpResponse(s_json, headers)


def seller_details(request: HttpRequest, id: int):
    if request.method == "GET":
        try:
            seller = Seller.objects.get(id=id)
            seller_json = serializers.serialize("json", [seller])
            return HttpResponse(seller_json, headers)
        except Seller.DoesNotExist:
            return HttpResponse("Seller not found", headers, status=404)


def details(request, id: int):
    post = Post.objects.filter(pk=id)
    response = serializers.serialize("json", post)
    if not post:
        return HttpResponse("No post found with this id.", headers, status=404)
    return HttpResponse(response, headers)


def init(request):
    for p in Post.objects.all():
        p.delete()
    for s in Seller.objects.all():
        s.delete()

    
    s = Seller(name="Stefan Vieru", email="stefan.vieru@student.tuiasi.ro")
    p = Post(title="Vand bicicleta", description="vand bicicleta cumparata in 2015",
              seller=s, image_url='s3_placeholder', pub_date=timezone.now())
    s.save()
    p.save()

    return HttpResponse("success", headers)

def aws_s3(request: HttpRequest, photo_id: str):
    s3 = boto3.client('s3')
    bucket = 'cc-olx-bucket'
    if request.method == "GET":
        s3.get_object
        return HttpResponse(s3.get_bucket_acl(Bucket=bucket), headers)
    elif request.method == "POST":
        pass
    return HttpResponse("S3 not working right now.", headers, status=404)

@csrf_exempt
def register(request: HttpRequest):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            return HttpResponse("Your account has been created!", headers, status=201)
        else:
            print(form.errors)
        
    return HttpResponse(str(form.errors))


