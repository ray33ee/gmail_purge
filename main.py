from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    s = build('gmail', 'v1', credentials=creds)

    return s


def full_search(service, after, before, criteria="", ignore=set()):

    exclude = " "

    for sender in ignore:
        exclude += "NOT from:{" + sender + "} "

    results = service.users().messages().list(userId='me',
                                              q=criteria + exclude + " after:" + after.strftime("%Y/%m/%d") + " before:" + before.strftime("%Y/%m/%d")).execute()

    while results.get('resultSizeEstimate', []) != 0:
        message_ids = results.get('messages', [])

        for message_id in message_ids:
            id = message_id['id']

            message = service.users().messages().get(userId='me', id=id, format='metadata', metadataHeaders=["From", "List-Unsubscribe"]).execute()

            message_part = message.get('payload')

            header = message_part.get('headers')

            for attribute in header:
                if attribute['name'] == 'From':
                    frm = attribute['value'].split(' <')[0]
                    print("    " + frm)
                    ignore.add(frm)

            print("        " + str(id))

        next_page = results.get('nextPageToken', [])
        if next_page == []:
            break
        results = service.users().messages().list(userId='me',
                                                  pageToken=next_page).execute()


service = get_service()

ignore = set()

criteria = "unsubscribe OR account OR password OR username"

start_time = datetime.datetime.now() #fromisoformat("2011-03-28")

now = start_time

# List of time delta and count pairs
# pairs = [{"batch size": 1, "total": 36}, {"batch size": 10, "total": 33}]
# pairs = [{"batch size": 31, "total": 12}]
# pairs = [{"batch size": 366, "total": 5}]

pairs = [
    {"batch size": 1, "batch count": 36},
    {"batch size": 10, "batch count": 33},
    {"batch size": 1, "batch count": 36},
    {"batch size": 10, "batch count": 33},
    {"batch size": 31, "batch count": 12},
    {"batch size": 31, "batch count": 12},
    {"batch size": 31, "batch count": 12},
    {"batch size": 31, "batch count": 12},
    {"batch size": 31, "batch count": 12},
    {"batch size": 31, "batch count": 12},
    {"batch size": 31, "batch count": 12},
    {"batch size": 31, "batch count": 12}]

for pair in pairs:
    print(str(pair['batch size']) + " day(s) increment")
    for i in range(pair['batch count']):
        print(str(i) + "/" + str(pair['batch count']))

        full_search(service, now, now + datetime.timedelta(days=pair['batch size']), criteria, ignore)

        print("    " + str(ignore))
        print("    " + str(now))

        now = now - datetime.timedelta(days=pair['batch size'])

