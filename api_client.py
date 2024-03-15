import os
import re
import http.client as httplib
import httplib2
import random
import time

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
  httplib.IncompleteRead, httplib.ImproperConnectionState,
  httplib.CannotSendRequest, httplib.CannotSendHeader,
  httplib.ResponseNotReady, httplib.BadStatusLine)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

# File should be refactored into using a class and have authentication be done on initialization

SPEADSHEET_NAME = "Episode 8 Act 2"

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
    response = append_sheet_data(credentials, spreadsheetId, SPEADSHEET_NAME, [])
    p = re.compile('^.*![A-Z]+\\d+:([A-Z]+)(\\d+)$')
    match = p.match(response['tableRange'])
    lastcolumn = match.group(1)
    lastrow = match.group(2)
    response = get_sheet_data(credentials, spreadsheetId, f"A${lastrow}:${lastcolumn}${lastrow}")
    return response[0]

def initialize_upload(credentials, options):
  body=dict(
    snippet=dict(
      title=options["title"],
      description=options["description"],
    ),
    status=dict(
      privacyStatus=options["privacyStatus"]
    )
  )

  # Call the API's videos.insert method to create and upload the video.
  with build('youtube', 'v3', credentials=credentials) as youtube:
    insert_request = youtube.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options["file"], chunksize=-1, resumable=True)
    )

    return resumable_upload(insert_request)

# This method implements an exponential backoff strategy to resume a
# failed upload.
def resumable_upload(request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print('Uploading file...')
            status, response = request.next_chunk()
            if response is not None:
                if 'id' in response:
                    print('Video id "%s" was successfully uploaded.' % response['id'])
                    return response
            else:
                exit('The upload failed with an unexpected response: %s' % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.resp.status,
                                                                    e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e

    if error is not None:
        print(error)
        retry += 1
        if retry > MAX_RETRIES:
            exit('No longer attempting to retry.')

        max_sleep = 2 ** retry
        sleep_seconds = random.random() * max_sleep
        print('Sleeping %f seconds and then retrying...' % sleep_seconds)
        time.sleep(sleep_seconds)

def authenticate_client_user():
    SCOPES = ["https://www.googleapis.com/auth/youtube.readonly", "https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/spreadsheets"]
    CLIENT_SECRETS_FILE = "client_secret_494135269922-03i1gfsobfjj1ei86pu75sdmmcfa3ojg.apps.googleusercontent.com.json"

    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    # Get credentials and create an API client
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server()

    return credentials