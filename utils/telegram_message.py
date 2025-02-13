import requests


def send_telegram_notification(success=True,chat_id = '2140322165'):
    bot_token = "7783224280:AAGnp2TdOPXXvH1n9rtS_E3ZpoaagKE7DN8"
    if success:
        message = ("✅Oi, mon ami! Your query has been sliced, diced, and served up fresh! You can check out the response in "
               "the chatbot app—go on, don’t keep it waiting! Allez, allez!")
    else:
        message = ("❌Zut alors! Looks like this tin-can chatbot couldn’t make heads or tails of your question! Maybe "
                   "try rewording it, mon ami? Even the mightiest warriors need a second strike sometimes!")
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, json=payload)
    return response.json()