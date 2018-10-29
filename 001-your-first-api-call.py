#!/usr/bin/env python3

SERVICE_CLIENT_NAME = "my-service-client"
SERVICE_CLIENT_SECRET = "insert-your-secret-here-it-is-a-string-of-hexadecimal"

import re
import json
import requests
from os.path import expanduser
from requests.auth import HTTPBasicAuth

def main():
    at_response = json.loads(requests.post('https://login.corefiling.com/auth/realms/platform/protocol/openid-connect/token',
                                        data={'grant_type':'client_credentials'},
                                        auth=HTTPBasicAuth(SERVICE_CLIENT_NAME, SERVICE_CLIENT_SECRET)).text)
    access_token = at_response['access_token']

    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token}

    def get_filings(page=1):
        req = requests.get('https://api.apps.corefiling.com/document-service/v1/filings/?pageSize=1000&amp;pageNumber=%s' % page, headers=headers)
        req.raise_for_status()
        return json.loads(req.text)

    print("Here is a list of filings in your account:")
    for f in get_filings:
        print("\t" + (f)["name"])

if __name__=='__main__':
    main()
