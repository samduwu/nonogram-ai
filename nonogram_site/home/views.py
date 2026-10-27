from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, "home/landing.html",  {})

def process(request):
    # TODO: Remove because this is a temporary response to test button upload.
    return HttpResponse("Process page.")