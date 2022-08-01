# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse , HttpResponseRedirect
from django.template.context_processors import csrf
from . import forms
from . import models
# Create your views here.
import requests
import serial

def home(request):
    data = {}
    form = forms.CodeForm()
    context   = { 'form':form }
    if request.method == 'POST':
        form = forms.CodeForm(request.POST)
        if form.is_valid():
            print (
                'Code Number',form.cleaned_data['code'],
                )
            CODE = form.cleaned_data['code']
            #ROOT_URL = f'http://127.0.0.1:8080/check/{CODE}'
            #r = requests.get(ROOT_URL)
            #print(r.status_code)
            #import subprocess
            #subprocess.call(['sh', './on.sh']) 
            #subprocess.call(['sh', './off.sh']) 
            if CODE == "101010":
                print (" Box 1")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x01,0x33,0x49])) # open Box 1
                print (ser.read())
            if CODE == "202020":
                print (" Box 2")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x02,0x33,0x4A])) # open Box 2
                print (ser.read())
            if CODE == "303030":
                print (" Box 3")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x03,0x33,0x4B])) # open Box 3
                print (ser.read())
            else:
                form.add_error('code', "Wrong Code")
                return render(request, 'home_base.html', { 'form':form })
        else:
            form = forms.CodeForm(request.POST)
            return render(request, 'home_base.html', { 'form':form })
    return render(request, 'home_base.html', context )

def index404(request):
	template = '404.html'
	return render(request,template)