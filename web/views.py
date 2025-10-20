# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import random
import string
from pathlib import Path

import qrcode
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from . import forms, locker, models

DASHBOARD_MASTER_CODE = "89E154gs12828-34r0361R8t765-416d61g56D509"


def key_generator(size: int = 12, chars: str = string.digits) -> str:
    """Generate a pseudo-random access code."""

    return "".join(random.choice(chars) for _ in range(size))


def home(request):
    """Display the home page where customers can enter their locker code."""

    form = forms.CodeForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        access_code = form.cleaned_data["code"]

        if access_code == DASHBOARD_MASTER_CODE:
            return HttpResponseRedirect("/dashboard/")

        try:
            target = models.Cell.objects.get(code=access_code)
        except models.Cell.DoesNotExist:
            form.add_error("code", "Wrong Code")
        else:
            locker_identifier = locker.locker_for_cell(target.cell)
            if locker_identifier is None:
                form.add_error("code", "Unknown locker identifier")
            elif locker.trigger_locker(locker_identifier):
                locker.remove_qr_code_file(settings.STATIC_ROOT, access_code)
                target.delete()
                form = forms.CodeForm()  # Reset the form after a successful unlock.
            else:
                form.add_error(None, "Unable to open the locker. Please try again.")

    return render(request, "home_base.html", {"form": form})


def dashboard(request):
    """Administrative dashboard used to open lockers manually."""

    form = forms.OpenForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        locker_identifier = form.cleaned_data["cell"]

        if locker.trigger_locker(locker_identifier):
            form = forms.OpenForm()
        else:
            form.add_error(None, "Unable to open the locker. Please try again.")

    return render(request, "dashboard.html", {"form": form})


def key(request, slug):
    """Generate a new QR code for the provided cell identifier."""

    if not slug or locker.locker_for_cell(slug) is None:
        return HttpResponseRedirect("/dashboard/")

    cell_key = key_generator()

    try:
        models.Cell.objects.get(code=cell_key)
    except models.Cell.DoesNotExist:
        img = qrcode.make(cell_key)

        static_root = Path(settings.STATIC_ROOT)
        static_root.mkdir(parents=True, exist_ok=True)
        img_path = static_root / f"{cell_key}.png"
        img.save(img_path)

        new_key = models.Cell(cell=slug, code=cell_key)
        new_key.save()
        os.chmod(img_path, 0o777)
        context = {"cell_key": cell_key, "cell": slug, "img": f"{cell_key}.png"}
        return render(request, "key.html", context)

    return HttpResponseRedirect("/dashboard/")


def index404(request):
    template = "404.html"
    return render(request, template)
