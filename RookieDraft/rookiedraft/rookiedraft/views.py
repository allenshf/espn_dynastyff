from django.shortcuts import render
import requests
from subprocess import run,PIPE
import sys

def buttons(request):
    return render(request, 'home.html')

def external(request):
    inp = request.POST.get('param')
    out=run([sys.executable, 'C:\\Users\\dude0\\Desktop\\RookieDraft\\fa_request.py', inp], shell=False, stdout=PIPE)
    print(out)

    return render(request, 'home.html', {'data1':out.stdout})