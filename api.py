import json
import os

from flask import Flask
from flask import make_response
from flask import render_template
from flask import request

from libs.slackbot import SlackBot

api = Flask(__name__)

@api.route("/listen", methods=["GET","POST"])
def listen():
	slack_event = json.loads(request.data.decode("utf-8"))

	if "challenge" in slack_event:
		return make_response(slack_event.get("challenge"), 200, {"content_type": "application/json"})

	bot = SlackBot()
	if bot.verification == slack_event.get("token"):
		event = slack_event.get("event")
		if event and event.get("type") == "message":
			team_id = slack_event.get("team_id")
			bot.connect(team_id)
			bot.event_handler(event)
		return "Ok", 200
	else:
		return make_response("Invalid Slack verification code", 403)

@api.route("/")
def index():
	bot = SlackBot()
	client_id = bot.oauth.get("client_id")
	scope = bot.oauth.get("scope")
	return render_template("index.html", client_id=client_id, scope=scope)


@api.route("/thanks")
def thanks():
	bot = SlackBot()
	code = request.args.get("code")
	if code:
		bot.auth(code)
		return render_template("thanks.html")
	else:
		return render_template("error.html")


if __name__ == "__main__":
	port = int(os.getenv("PORT")) or 5000
	api.run(debug=True, host="0.0.0.0", port=port, ssl_context="adhoc")