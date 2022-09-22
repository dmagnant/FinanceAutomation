import os
import os.path
import sys

from django.shortcuts import render

# Create your views here.
def accounts(request):
    scripts = os.listdir(r'G:\My Drive\Projects\Coding\Python\FinanceAutomation\scripts\scripts\Accounts')
    try:
        scripts.remove("__pycache__")
    except ValueError:
        exception = "pycache file not listed"
    for script in scripts:
        if script.endswith(".py"):
            i = scripts.index(script)
            script = script.replace('.py','')
            scripts[i] = script
        else:
            scripts.remove(script)
    scripts.sort()
    return render(request,"accounts/accounts.html", {'scripts':scripts})
