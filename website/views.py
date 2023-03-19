from django.shortcuts import render

from scripts.scripts.Classes.WebDriver import Driver

def welcome(request):
    return render(request, "website/welcome.html")
    