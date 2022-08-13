# from .models import Script
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
import os, os.path

def marketResearch(request):
    return render(request,"scripts/marketresearch.html")

def usd(request):
    return render(request,"scripts/usd.html")

def crypto(request):
    if request.method == 'POST' and "Coinbase.py" in request.POST:
        print(str(request.body)[87:].replace("='",''))
    scripts = os.listdir(r'G:\My Drive\Projects\Coding\Python\FinanceAutomation\scripts\scripts\Crypto')
    try:
        scripts.remove("__pycache__")
    except ValueError:
        exception = "pycache file not listed"
    for script in scripts:
        if script.endswith(".py"):
            i = scripts.index(script)
            script = script.replace('.py','')
            scripts[i] = script
            # try:
            #     Script.objects.get(name=script, type="crypto")
            # except ObjectDoesNotExist:
            #     Script.objects.create(name=script, type="crypto")
        else:
            scripts.remove(script)
    return render(request,"scripts/crypto.html",{'scripts':scripts})