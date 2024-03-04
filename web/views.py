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
            #subprocess.call(['sh', './off.sh']) ttyUSB0
            if CODE == "01":
                return render(request, 'drop.html', { 'form':form })
            if CODE == "10101":
                print (" Box 1")
                ser = serial.Serial('/dev/ttyUSB0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x02,0x01,0x33,0xc5])) # open Box 1
                print (ser.read())
            if CODE == "10102":
                print (" Box 2")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x02,0x33,0x4A])) # open Box 2
                print (ser.read())
            if CODE == "10103":
                print (" Box 3")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x03,0x33,0x4B])) # open Box 3
                print (ser.read())
            if CODE == "10104":
                print (" Box 4")
                ser = serial.Serial('/dev/ttyUSB0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x04,0x33,0x4C])) # open Box 4
                print (ser.read())
            if CODE == "10105":
                print (" Box 5")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x05,0x33,0x4D])) # open Box 5
                print (ser.read())
            if CODE == "10106":
                print (" Box 6")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x06,0x33,0x4E])) # open Box 6
                print (ser.read())
            if CODE == "10107":
                print (" Box 7")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x07,0x33,0x4F])) # open Box 7
                print (ser.read())
            if CODE == "10108":
                print (" Box 8")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x08,0x33,0x40])) # open Box 8
                print (ser.read())
            if CODE == "10109":
                print (" Box 9")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x09,0x33,0x41])) # open Box 9
                print (ser.read())
            if CODE == "101010":
                print (" Box 10")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x0A,0x33,0x42])) # open Box 10
                print (ser.read())
            if CODE == "101011":
                print (" Box 11")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x0B,0x33,0x43])) # open Box 11
                print (ser.read())
            if CODE == "101012":
                print (" Box 12")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x0C,0x33,0x44])) # open Box 12
                print (ser.read())
                #------------------------------------------------------------------------------------------------------------
            if CODE == "101013":
                print (" Box 13")
                ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                ser.write(serial.to_bytes([0x7A,0x01,0x03,0x33,0x4B])) # open Box 13
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