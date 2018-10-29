#!/usr/bin/env python3

SERVICE_CLIENT_NAME = "(insert yours)"
SERVICE_CLIENT_SECRET = "(insert yours)"
BASE_URL = 'https://api.labs.corefiling.com/'
XBRL_FILING = '/path/to/SampleSIIFiling.xml' #insert path to your filing here

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

    # Look up validation profile by name
    def get_profile_id():
        req = requests.get(BASE_URL + 'document-service/v1/categories/validation', headers=auth_header)
        req.raise_for_status()
        profiles_by_name = {}
        for profile in json.loads(req.text)['profiles']:
            profiles_by_name[profile["name"]] = profile["id"]
        target_profile = profiles_by_name['Solvency II 2.2.0 hotfix / Bank of England Filing Rules']
        return target_profile

    # Upload filing to target validation profile - multipart POST request
    def post_filing():
         files = {'file': open(XBRL_FILING, 'rb')}
         upload_req = requests.post(BASE_URL + 'document-service/v1/filings?validationProfile=' + get_profile_id(), files=files, headers=auth_header)
         upload_req.raise_for_status()
         return json.loads(upload_req.text)['versions'][0]['id']

    # Poll until processing has completed - this depends on filing size but usually takes at least 30 seconds
    filing_version_id = post_filing()
    print ('Document is processing, please wait..')
    done = False
    while not done:
        filing_req = requests.get(BASE_URL + 'document-service/v1/filing-versions/' + filing_version_id, headers=auth_header)
        filing_req.raise_for_status()
        filing = json.loads(filing_req.text)
        done = "DONE" == filing["status"]
        time.sleep(5)

    # Once processing has completed, results can be accessed from other APIs, e.g. validation messages:
    val_results_req = requests.get(BASE_URL + 'validation-service/v1/filing-versions/%s/issues/' % filing_version_id, headers=auth_header)
    val_results_req.raise_for_status()
    for message in (json.loads(val_results_req.text)):
        print (message['validationMessage']['errorCode'] + '\t' + message['validationMessage']['messageDetail'])

    # Get the output document ID for an Excel rendering and then download the Excel file
    outputs_req = requests.get(BASE_URL + 'document-service/v1/filing-versions/' + filing_version_id, headers=auth_header)
    outputs_req.raise_for_status()
    documents_by_category = {}
    for document in json.loads(outputs_req.text)['documents']:
        documents_by_category[document["category"]] = document["id"]
    excel_req = requests.get(BASE_URL + 'document-service/v1/documents/%s/content' %documents_by_category['excel-rendering'], headers=auth_header)
    excel_req.raise_for_status()
    with open('TNDP-API-ExcelOutput.xlsx', 'wb' ) as excel_file:
        excel_file.write(excel_req.content)

if __name__=='__main__':
    main()
