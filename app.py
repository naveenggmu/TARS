# Authors: Nanda H Krishna (https://github.com/nandahkrishna), Abhijith Ragav (https://github.com/abhijithragav)

import os
from datetime import *
import json
import requests
import threading
from flask import Flask, jsonify, render_template, request
from slacker import Slacker

app = Flask(__name__)
app.debug = True

vineethv_id = os.environ.get("VINEETHV_ID")
tars_admin = os.environ.get("TARS_ADMIN")
slack_key = os.environ.get("SLACK_KEY")
slack = Slacker(slack_key)

@app.route("/", methods=["GET"])
def index():
	return render_template("index.html")

@app.route("/event", methods=["POST"])
def event():
	payload = json.loads(request.get_data())
	thread = threading.Thread(target=event_handler, args=(payload,))
	thread.start()
	return "", 200

def event_handler(payload):
	slack.chat.post_message(tars_admin, payload["event"]["text"][1:])

@app.route("/interact", methods=["POST"])
def interact():
	payload = json.loads(request.form.get("payload"))
	thread = threading.Thread(target=interact_handler, args=(payload,))
	thread.start()
	return "", 200

def interact_handler(payload):
	response_url = payload["response_url"]
	action_id = payload["actions"][0]["action_id"]
	slack.chat.post_message(tars_admin, action_id)
	headers = {"Content-type": "application/json"}
	if action_id == "enter_office_hours":
		requests.post(response_url, headers=headers, json=json.load(open("messages/office_hours_slot.json")))
	elif action_id == "cancel_office_hours":
		requests.post(response_url, headers=headers, json=json.load(open("messages/cancel_office_hours.json")))
	elif action_id == "slot_done":
		requests.post(response_url, headers=headers, json=json.load(open("messages/confirm_office_hours.json")))
	elif action_id == "done_office_hours":
		requests.post(response_url, headers=headers, json=json.load(open("messages/done_office_hours.json")))

if __name__ == "__main__":
	app.run()
