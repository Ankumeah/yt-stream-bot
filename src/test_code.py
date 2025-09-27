#! /bin/env python

from googleapiclient.discovery import build
import requests
import subprocess

VIDEO_ID = "dkyPFzMwkwQ"
seen_message_ids = []

subprocess.run(["bash", "-c", "mkdir -p ./resources"])
subprocess.run(["bash", "-c", "echo '' > ./resources/responded_texts"])

with open("./api_key") as f:
  API_KEY = f.read().strip()

resp = requests.get(
  "https://www.googleapis.com/youtube/v3/videos",
  params = {
    "part": "liveStreamingDetails",
    "id": VIDEO_ID,
    "key": API_KEY
  }
).json()

live_chat_id = resp["items"][0]["liveStreamingDetails"]["activeLiveChatId"]
next_page_token = ""

r = requests.get(
  "https://www.googleapis.com/youtube/v3/liveChat/messages",
  params = {
    "liveChatId": live_chat_id,
    "part": "snippet, authorDetails",
    "key": API_KEY,
    "pageToken": next_page_token
  }
).json()

for message in r.get("items", []):
  id = message["id"]

  subprocess.run(["bash", "-c", f"echo '{id}' >> ./resources/responded_texts"]) 

with open("./resources/responded_texts") as f:
  raw_seen_message_ids = f.read().strip()

for i in raw_seen_message_ids:
  last_id = ""

  if i == "\n" and last_id != "":
    seen_message_ids.append(last_id)
  else:
    last_id += i

print(seen_message_ids)
