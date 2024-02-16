import os
import re
from pathlib import Path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload

# FIle should be refactored into using a class and have authentication be done on initialization

def get_sheet_data(credentials, spreadsheetId, range):
    with build('sheets', 'v4', credentials=credentials) as service:
        spreadsheets = service.spreadsheets()
        response = spreadsheets.values().get(spreadsheetId=spreadsheetId, range=range).execute()
        rows = response['values']

        return rows
    
def update_sheet_data(credentials, spreadsheetId, range, data):
    value_input_options="USER_ENTERED"

    with build('sheets', 'v4', credentials=credentials) as service:
        spreadsheets = service.spreadsheets()
        response = spreadsheets.values().update(
            spreadsheetId=spreadsheetId, 
            range=range, 
            valueInputOption=value_input_options, 
            body={ "values": data }
        ).execute()
        return response
    
def append_sheet_data(credentials, spreadsheetId, range, data):
    value_input_options="USER_ENTERED"

    with build('sheets', 'v4', credentials=credentials) as service:
        spreadsheets = service.spreadsheets()
        response = spreadsheets.values().append(
            spreadsheetId=spreadsheetId, 
            range=range, 
            valueInputOption=value_input_options, 
            body={ "values": data }
        ).execute()
        return response
    
def get_last_row_from_spreadsheet(credentials, spreadsheetId):
    response = append_sheet_data(credentials, spreadsheetId, "Episode 8 Act 1", [])
    p = re.compile('^.*![A-Z]+\\d+:([A-Z]+)(\\d+)$')
    match = p.match(response['tableRange'])
    lastcolumn = match.group(1)
    lastrow = match.group(2)
    response = get_sheet_data(credentials, spreadsheetId, f"A${lastrow}:${lastcolumn}${lastrow}")
    return response[0]

def upload_to_youtube(credentials, video_path, title, description, privacyStatus):
    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name, api_version, credentials=credentials)

    request = youtube.videos().insert(
        part="snippet, status",
        body={
            "snippet": {
                "title": title,
                "description": description
            },
            "status": {"privacyStatus": privacyStatus}
        },
        media_body=MediaFileUpload(video_path)
    )
    response = request.execute()
    return response

def authenticate_client_user():
    scopes = ["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/spreadsheets"]

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    client_secrets_file = "client_secret_494135269922-03i1gfsobfjj1ei86pu75sdmmcfa3ojg.apps.googleusercontent.com.json"

    # Get credentials and create an API client
    flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_local_server()

    return credentials
