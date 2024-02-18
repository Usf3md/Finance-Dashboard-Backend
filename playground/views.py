from django.shortcuts import render
from django.http import HttpResponse
from cashflow.models import Runner


def say_hello(request):
    runners = Runner.objects.all()
    return render(request, "hello.html", {"name": "Youssef"})
