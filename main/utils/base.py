from django.conf import settings

BASE_DIR = settings.BASE_DIR


import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd


group_to_sheet = {
    "6": "REGroup6",
    "7": "Group 7",
    "9": "Group 9"
}

group_to_mice = {
    "6": ['F0085', 'F0086', 'F0087', 'F0088', 'F0090', 'F0093', 'F0095', 'F0098', 'F0100', 'F0101', 'F0102', 'F0104'],
    "7": ['F0106', 'F0107', 'F0108', 'F0109'],
    "9": ['F0149', 'F0150', 'F0151', 'F0152', 'F0153', 'F0154', 'F0155', 'F0156', 'F0157', 'F0158', 'F0159', 'F0160']
}

group_to_control_mice = {
    "6" : ['F0089', 'F0091', 'F0092', 'F0094', 'F0096', 'F0097', 'F0099', 'F0103'],
    "7" : ['F0105', 'F0110', 'F0111', 'F0112'],
    "9" : ['F0133', 'F0134', 'F0135', 'F0136', 'F0137', 'F0138', 'F0139', 'F0140', 'F0141', 'F0142', 'F0143', 'F0144', 'F0145', 'F0146', 'F0147', 'F0148'] 
}


# Use the JSON key you downloaded when creating your Google Cloud Platform project
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/spreadsheets']
credentials = ServiceAccountCredentials.from_json_keyfile_name(f'{BASE_DIR}/credentials.json', scope)

# Authenticate and access the Google Sheets document
gc = gspread.authorize(credentials)
spreadsheet_key = '1WwHzVLZYN5hdCIWN6scgkkwaaJgvpu_E1qWTQfd9WSk'  # Extracted from the Google Sheets link
book = gc.open_by_key(spreadsheet_key)
