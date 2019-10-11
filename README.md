# gdocs-export

A python script to export all your Google documents, sheets and presentations and download them in open document formats.  
Very useful when you are migrating from GoogleDrive to a different cloud platform.

> Because of a restriction in the Google API this works only for files smaller than 10 MB.

## Prerequisites

- [Python 3](https://www.python.org/)
- [pip](https://pypi.org/project/pip/)

## Getting Started

### Installation

- `git clone https://github.com/PhilInTheGaps/gdocs-export`
- `cd gdocs-export`  
- `pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib`  

### Create Google Project

- Visit the [Google developer console](https://console.developers.google.com)
- Create a new project and add the GoogleDrive API
- Create an oauth consent screen and add https://www.googleapis.com/auth/drive.readonly as a scope  
  (As the project is for personal use only, you don't have to verify it. Ignore the warning.)
- Create credentials and select `OAuth Client ID`
    - Application type is `other`
    - Give the credentials some name, it does not matter
    - Select your new credentials and click `Download JSON`
    - Save the file in the `gdocs-export` folder and rename it to `client_secrets.json`

### Run the script

- `python3 export.py`
- The script will now find all documents, sheets and presentations in your drive and download them.
