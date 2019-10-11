from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2 import credentials
import json
import os
import sys

CLIENT_SECRETS_FILE = 'client_secrets.json'
CREDENTIALS_FILE = 'credentials.json'
EXPORT_DIR = 'export'


def get_credentials():
    with open(CREDENTIALS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return credentials.Credentials(
            data['token'],
            data["refresh_token"],
            data["id_token"],
            data["token_uri"],
            data["client_id"],
            data["client_secret"],
            data["scopes"])

    return None


def save_credentials(credentials):
    data = {
        "token": "",
        "refresh_token": credentials.refresh_token,
        "id_token": credentials.id_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes
    }

    with open(CREDENTIALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_authenticated_service():
    print('Authenticating ...')

    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secrets.json',
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid', 'https://www.googleapis.com/auth/drive.readonly'])

    credentials = get_credentials()

    if (credentials is None):
        flow.run_local_server()
        credentials = flow.credentials
        save_credentials(credentials)
    elif (credentials.expired):
        credentials.refresh()
        save_credentials(credentials)

    print('Authentication successful.')

    return build('drive', 'v3', credentials=credentials)


def get_extension(item):
    if item['mimeType'] == 'application/vnd.google-apps.document':
        return ".odt"
    elif item['mimeType'] == 'application/vnd.google-apps.presentation':
        return ".odp"
    elif item['mimeType'] == 'application/vnd.google-apps.spreadsheet':
        return ".ods"

    return ""


def get_target_mime_type(item):
    if item['mimeType'] == 'application/vnd.google-apps.document':
        return "application/vnd.oasis.opendocument.text"
    elif item['mimeType'] == 'application/vnd.google-apps.presentation':
        return "application/vnd.oasis.opendocument.presentation"
    elif item['mimeType'] == 'application/vnd.google-apps.spreadsheet':
        return "application/vnd.oasis.opendocument.spreadsheet"

    return ""


def download_file(service, item, path):
    content = None
    extension = get_extension(item)
    mimeType = get_target_mime_type(item)
    folderPath = EXPORT_DIR + "/" + path
    filePath = folderPath + "/" + item['name'].replace("/", "_") + extension

    if not extension or not mimeType:
        print("Error: File {} of type {} can not be exported!".format(item['name'], item['mimeType']))
        return

    if os.path.exists(filePath):
        print("    File already exits!")
        return

    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

    try:
        # Download exported file
        content = service.files().export(fileId=item['id'], mimeType=mimeType).execute()

        # Save downloaded file
        file = open(filePath, "wb")
        file.write(content)
        file.close()
    except:
        e = sys.exc_info()[0]
        print("Error: Could not export file! ({})".format(e))


def export_docs(service, parentId, parentName):
    results = service.files().list(
        q="'{}' in parents and trashed = false and (mimeType='application/vnd.google-apps.document' or mimeType='application/vnd.google-apps.presentation' or mimeType='application/vnd.google-apps.spreadsheet')".format(parentId),
        pageSize=1000
    ).execute()
    items = results.get('files', [])

    for item in items:
        print("  " + item['name'] + " ({})".format(item['mimeType']))
        download_file(service, item, parentName)


def export_folders(service, parentId, parentName):
    print(parentName + ":")

    # Files
    export_docs(service, parentId, parentName)
    print("")

    # Folders
    results = service.files().list(
        q="'{}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false".format(parentId),
        pageSize=1000
    ).execute()
    items = results.get('files', [])

    for item in items:
        export_folders(service, item['id'].replace("/", "_"), parentName + "/" + item['name'])

    print("")


def start_export():
    service = get_authenticated_service()
    print('Starting docs export ...\n')
    export_folders(service, 'root', "MyDrive")


if __name__== "__main__":
    start_export()
    print("Finished.")
