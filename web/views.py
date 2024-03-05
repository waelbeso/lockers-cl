# -*- coding: utf-8 -*-
import os
from django.shortcuts import render
from django.http import HttpResponse , HttpResponseRedirect
from django.template.context_processors import csrf
from . import forms
from . import models
import requests
import serial
import string
import random
import qrcode
import time
from django.core.exceptions import ObjectDoesNotExist

def key_generator(size=12, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

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
            if form.cleaned_data['code'] == "89E154gs12828-34r0361R8t765-416d61g56D509": #Dashboard Key
                return HttpResponseRedirect("/dashboard")
            try:
                models.Cell.objects.get(code=form.cleaned_data['code'])
            except ObjectDoesNotExist:
                form.add_error('code', "Wrong Code")
                return render(request, 'home_base.html', { 'form':form })
            else:
                target = models.Cell.objects.get(code=form.cleaned_data['code'])
                target_cell = target.cell
                if target_cell == "89E154gs12828":
                    print('target 1')
                    #ser = serial.Serial('/dev/ttyUSB0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                    #ser.write(serial.to_bytes([0x7A,0x02,0x01,0x33,0xc5])) # open Box 1
                    #print (ser.read())
                    png_file = "static/" + form.cleaned_data['code'] + '.png'
                    os.remove(png_file)
                    target.delete()
                if target_cell == "34r0361R8t765":
                    print('target 2')
                    #ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                    #ser.write(serial.to_bytes([0x7A,0x01,0x02,0x33,0x4A])) # open Box 2
                    #print (ser.read())
                    png_file = "static/" + form.cleaned_data['code'] + '.png'
                    os.remove(png_file)
                    target.delete()
                if target_cell == "416d61g56D509":
                    print('target 3')
                    #ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                    #ser.write(serial.to_bytes([0x7A,0x01,0x03,0x33,0x4B])) # open Box 3
                    #print (ser.read())
                    png_file = "static/" + form.cleaned_data['code'] + '.png'
                    os.remove(png_file)
                    target.delete()
        else:
            form = forms.CodeForm(request.POST)
            return render(request, 'home_base.html', { 'form':form })
    return render(request, 'home_base.html', context )
def dashboard(request):
    data = {}
    form = forms.OpenForm()
    context   = { 'form':form }
    if request.method == 'POST':
        form = forms.OpenForm(request.POST)
        if form.is_valid():
            print ('Cell Number',form.cleaned_data['cell'],)
            if form.cleaned_data['cell'] == "1":
                print (" Box 1")
                #ser = serial.Serial('/dev/ttyUSB0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                #ser.write(serial.to_bytes([0x7A,0x02,0x01,0x33,0xc5])) # open Box 1
                #print (ser.read())
            if form.cleaned_data['cell'] == "2":
                print (" Box 2")
                #ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                #ser.write(serial.to_bytes([0x7A,0x01,0x02,0x33,0x4A])) # open Box 2
                #print (ser.read())
            if form.cleaned_data['cell'] == "3":
                print (" Box 3")
                #ser = serial.Serial('/dev/ttyS0', 9600, bytesize=8, stopbits=1, parity='N',timeout=10)   # open serial port
                #ser.write(serial.to_bytes([0x7A,0x01,0x03,0x33,0x4B])) # open Box 3
                #print (ser.read())
        #else:
        #    form.add_error('cell', "Wrong Cell")
        #   return render(request, 'dashboard.html', { 'form':form })
        else:
            form = forms.OpenForm(request.POST)
            return render(request, 'dashboard.html', { 'form':form })
    return render(request, 'dashboard.html', context )

def key(request, slug):
    print(slug)
    #img = qrcode.make( '89E154gs12828-34r0361R8t765-416d61g56D509')
    #img_name = "static/" + '89E154gs12828-34r0361R8t765-416d61g56D509' + ".png"
    #img.save(img_name)
    if not slug :
        return HttpResponseRedirect("/dashboard")
    if slug == "89E154gs12828" or slug == "34r0361R8t765" or slug == "416d61g56D509":
        cell_key = key_generator()
        try:
            models.Cell.objects.get(code=cell_key)
        except ObjectDoesNotExist:
            img = qrcode.make( cell_key)
            img_name = "static/" + cell_key + ".png"
            type(img)  # qrcode.image.pil.PilImage
            img.save(img_name)
            img_png = cell_key + ".png"
            new_key = models.Cell( cell = slug, code = cell_key)
            new_key.save()
            context   = { 'cell_key': cell_key ,'cell': slug , 'img': img_png}
            return render(request, 'key.html', context )
        else:
            return HttpResponseRedirect("/dashboard")
    else:
        return HttpResponseRedirect("/dashboard")


def index404(request):
	template = '404.html'
	return render(request,template)

#89E154gs12828
#34r0361R8t765
#416d61g56D509
#89E154gs12828-34r0361R8t765-416d61g56D509