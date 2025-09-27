#! /bin/env python

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests
import time
import subprocess
import sys
import random
import os
import json
import threading
import http.server
import socketserver

VIDEO_ID = os.environ.get("VIDEO_ID")
if not VIDEO_ID:
  print("Pls set the VIDEO_ID env var")
  sys.exit(1)

API_KEY = os.environ.get("YOUTUBE_API_KEY")
OAUTH_JSON = os.environ.get("YOUTUBE_OAUTH_JSON")

if not API_KEY:
  print("Error: YOUTUBE_API_KEY not set in environment")
  sys.exit(1)

if not OAUTH_JSON:
  print("Error: YOUTUBE_OAUTH_JSON not set in environment")
  sys.exit(1)

def init_local_storage():
  subprocess.run(["bash", "-c", "mkdir -p ./resources"])
  subprocess.run(["bash", "-c", "echo '' > ./resources/scoreboard"])

def send_message(live_chat_id: str, text: str):
  creds_dict = json.loads(OAUTH_JSON)
  creds = Credentials.from_authorized_user_info(creds_dict)
  youtube = build("youtube", "v3", credentials = creds)

  youtube.liveChatMessages().insert(
    part = "snippet",
    body = {
      "snippet": {
        "liveChatId": live_chat_id,
        "type": "textMessageEvent",
        "textMessageDetails": {
          "messageText": text
        }
      }
    }
  ).execute()

def main():
  joined = False
  chat_dict = {}
  seen_messages = set()

  init_local_storage()

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

  while True:
    r = requests.get(
      "https://www.googleapis.com/youtube/v3/liveChat/messages",
      params = {
        "liveChatId": live_chat_id,
        "part": "snippet,authorDetails",
        "key": API_KEY,
        "pageToken": next_page_token
      }
    ).json()

    for item in r.get("items", []):
      msg_id = item["id"]

      if msg_id in seen_messages:
        continue

      seen_messages.add(msg_id)
      username = item["authorDetails"]["displayName"]
      message = item["snippet"]["displayMessage"]
      chat_dict[username] = message

      if joined and message[0] == "!":
        print("\033[32m=> COMMAND FOUND:\t", end = "")
        handel_command(live_chat_id, username, message)

      print(f"{username}:\t{message} \033[0m")
      
    next_page_token = r.get("nextPageToken", "")

    if not joined:
      send_message(live_chat_id, "I have joined the chat!")
      joined = True

    try:
      time.sleep(r.get("pollingIntervalMillis", 1000) / 1000)
    except KeyboardInterrupt as e:
      print("\n\033[32mProgram closed\033[0m")
      sys.exit(0)

def handel_command(live_chat_id: str, username: str, message: str):
  if message == "!goon":
    send_message(live_chat_id, f"{username} has gooned!")
  elif message == "!jork":
    send_message(live_chat_id, f"Jarvis jorked {username}'s a little'")
  elif message == "!gamble":
    if gamble():
      send_message(live_chat_id, f"{username} has won the gamble!")
    else:
      send_message(live_chat_id, f"{username} sux")
  elif message == "!test":
    send_message(live_chat_id, f"Test passed")

def gamble():
  rand = random.randint(0, 101)
  return rand % 2

def run_server():
  port = int(os.environ.get("PORT", 8080))
  Handler = http.server.SimpleHTTPRequestHandler
  with socketserver.TCPServer(("", port), Handler) as httpd:
    print(f"Dummy server running at port {port}")
    httpd.serve_forever()

if __name__ == "__main__":
  threading.Thread(target=main, daemon=True).start()
  run_server()

