import os
import sys
import json

import requests
from flask import Flask, request

from bs4 import BeautifulSoup
import requests
import random
import re

app = Flask(__name__)


popular_choice = ['motivational', 'life', 'positive', 'friendship', 'success', 'happiness', 'love']

def get_quotes(type, number_of_quotes=1):
    url = "http://www.brainyquote.com/quotes/topics/topic_" + type + ".html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    quotes = []
    for quote in soup.find_all('a', {'title': 'view quote'}):
        quotes.append(quote.contents[0])

    if quotes == [] :
        return 'Oops, could not find any quote. Try some other general topic. :)'
    random.shuffle(quotes)
    result = quotes[:number_of_quotes]
    return result


def get_random_quote():
    result = get_quotes(popular_choice[random.randint(0, len(popular_choice) - 1)])
    return result


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must
    # return the 'hub.challenge' value in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == 'test_token':
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


@app.route('/', methods=['POST'])
def webook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    
    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    
                    nameRegex = re.compile(r'quote (.*)')
                    mo = nameRegex.search(message_text.lower())

                    if message_text.lower() == 'hi' or message_text.lower() == 'hey' or message_text.lower() == 'hello' or message_text.lower() == 'yo':
                        send_message(sender_id, "Hello there")
                    elif message_text.lower() == 'quote': 
                        send_message(sender_id, str(get_random_quote()[0]))
                    elif mo != None :
                        send_message(sender_id, str(get_quotes(mo.group(1))[0]))


                    else :
                        send_message(sender_id, "type <quote> to get a random quote and <quote> <topic> to get a quote related to the topic :)")

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200



def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": 'EAAHOZCGZBWZCIYBAJKolxlhBnkO7KzUtjZA1iveVtJZAsFjIIgZAMPo0WSag7ALFoxwXqLjmjxVPaUrTs7aNHW9z7h7BmDZAZCZAOy5EZBQ6IYvISn6OXds9EWr45WBSOFsCwzOUNOZCVCMEUn57ZAhPDXJFKlGp2i3AktYUvCy8vt6BZCAZDZD'
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
