#!/usr/bin/env python3

SERVICE_CLIENT_NAME = "(insert yours)"
SERVICE_CLIENT_SECRET = "(insert yours)"
BASE_URL = 'https://api.labs.corefiling.com/'

import re
import json
import requests
import time
from os.path import expanduser
from requests.auth import HTTPBasicAuth


def main():
    # Authenticate and obtain access token. More usually an OAuth2 client library would be used
    at_response = json.loads(requests.post('https://login.corefiling.com/auth/realms/platform/protocol/openid-connect/token',
                                        data={'grant_type':'client_credentials'},
                                        auth=HTTPBasicAuth(SERVICE_CLIENT_NAME, SERVICE_CLIENT_SECRET)).text)
    access_token = at_response['access_token']
    auth_header = {'Authorization': 'Bearer ' + access_token}

    filing_version_id = input("Enter filing version ID to obtain statistics for: ")

    # Obtain and print the filing statistics
    stats_req = requests.get(BASE_URL + 'filing-statistics-service/v1/filing-versions/%s/statistics/' % filing_version_id, headers=auth_header)
    stats_req.raise_for_status()
    print(json.dumps(stats_req.json(), indent=2))

if __name__=='__main__':
    main()
