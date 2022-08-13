
from django.shortcuts import render
from django.http import HttpResponse
# import os, os.path
import runpy

import sys
sys.path.append("..")
from scripts.scripts.Functions import openWebDriver
from scripts.scripts.Crypto.test import submitTest

def welcome(request):
    if request.method == 'POST' and 'run_script' in request.POST:
        print('here:')
        print(request.body)
        submitTest()
    return render(request, "website/welcome.html")