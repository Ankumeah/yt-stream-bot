#! /bin/env python

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

flow = InstalledAppFlow.from_client_secrets_file(
  "./client_secret.json", SCOPES
)
creds = flow.run_local_server(port=0)

with open("oauth.json", "w") as f:
  f.write(creds.to_json())
