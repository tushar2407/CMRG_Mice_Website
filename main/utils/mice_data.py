from django.conf import settings

import csv
import os
import json


def get_csv_file_path(group):
    return os.path.join(settings.MEDIA_ROOT, f'group_{group}.csv')


def get_json_file_path(group):
    return os.path.join(settings.MEDIA_ROOT, f'mice_data/group_{group}.json')


def read_csv(file_path):
    with open(
        os.path.join(settings.MEDIA_ROOT, file_path), 
        newline=''
    ) as csvfile:
        reader = csv.reader(csvfile)
        return list(reader)


def write_csv(file_path, data):
    with open(
        os.path.join(settings.MEDIA_ROOT, file_path), 
        'w', 
        newline=''
    ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)


def read_json(file_path):
    with open(
        os.path.join(settings.MEDIA_ROOT, file_path), 
        'r'
    ) as jsonfile:
        return json.load(jsonfile)
    

def write_json(file_path, data):
    with open(
        os.path.join(settings.MEDIA_ROOT, file_path), 
        'w'
    ) as jsonfile:
        json.dump(data, jsonfile)


def create_new_group(group, mouse_names):
    data = {
        "meta": {
            "subjects": mouse_names
        }
    }
    write_json(get_json_file_path(group), data)