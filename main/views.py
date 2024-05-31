from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views import View
from django.conf import settings
BASE_DIR = settings.BASE_DIR
MEDIA_URL = settings.MEDIA_URL

from main.utils.generate_plots import trigger_generate_plots
from main.utils.mice_data import (
    read_csv, 
    write_csv, 
    get_csv_file_path,
    get_json_file_path, 
    read_json,
    write_json,
    create_new_group
)
from main.utils.general import extract_number

import pandas as pd
import os


class ReportView(View):
    def get(self, request, *args, **kwargs):
        groups = [
            extract_number(f) for f in os.listdir(os.path.join(BASE_DIR, 'media', 'mice_data')) 
        ]
        return render(request, 'generate_report.html', {'groups': groups})

    def post(self, request, *args, **kwargs):
        trigger_generate_plots(request.POST)
        return render(
            request, 
            'generate_report.html', 
            {
                'report': f'{MEDIA_URL}Female_lifters_{request.POST["group"]}.pdf'
            }
        )


class MiceData(View):
    def get(self, request, *args, **kwargs):
        group = request.GET.get('group', '6')
        file_path = get_json_file_path(group)
        data = read_json(file_path)
        meta = data.pop('meta', {})

        groups = [
            extract_number(f) for f in os.listdir(os.path.join(BASE_DIR, 'media', 'mice_data')) 
        ]
        
        subjects = meta.get('subjects', [])

        context = {
            'subjects': subjects,
            'dates_data': data,
            'group': group,
            'groups': groups
        }
        return render(request, 'mice_data.html', context)

    def post(self, request, *args, **kwargs):
        group = request.POST.get('group', '6')
        file_path = get_json_file_path(group)
        dates_data = read_json(file_path)
        
        file_path = get_json_file_path(group)
        
        date = request.POST.get('date')
        if date in dates_data :
            ...
            # TODO: through error
        elif not date:
            return redirect(f'/mice_data?group={group}')
        else:
            dates_data[date] = {}
        
        for key, value in request.POST.items():
            if key == 'group' or key == 'csrfmiddlewaretoken' or key == 'date':
                continue
            subject, field = key.split()

            if subject not in dates_data[date]:
                dates_data[date][subject] = {}
            
            dates_data[date][subject][field] = value
        
        write_json(file_path, dates_data)   

        return redirect(f'/mice_data?group={group}')


def create_group_view(request):
    if request.method == 'POST':
        group = request.POST['group']
        start_date = request.POST['start_date']
        mouse_names = []
        for key in request.POST:
            if 'mouse_names' in key:
                mouse_names.append(request.POST[key])
        create_new_group(group, start_date, mouse_names)

        return redirect(f'/mice_data?group={group}')

    return render(request, 'add_new_group.html')