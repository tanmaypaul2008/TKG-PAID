import time
import json
import requests
from datetime import datetime

# Load bot token and channel ID from config file
with open("ig.json") as config_file:
    config = json.load(config_file)

BOT_TOKEN = config["bot_token"]
CHANNEL_ID = config["channel_id"]
API_URL = "https://api.bdg88zf.com/api/webapi/GetNoaverageEmerdList"
IMAGE_URL = "https://t.me/winsticker124/2166"  # Change as needed

# Statistics counters
total_bets = 0
total_wins = 0
total_losses = 0
win_streak = 0
loss_streak = 0
last_predicted_period = 0


# Function to make API requests
def make_api_request(url, data):
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    return response.json()


# Function to fetch the latest period number
def fetch_latest_period():
    data = {
        "pageSize": 10,
        "pageNo": 1,
        "typeId": 1,
        "language": 0,
        "random": "4a0522c6ecd8410496260e686be2a57c",
        "signature": "334B5E70A0C9B8918B0B15E517E2069C",
        "timestamp": int(time.time())
    }
    result = make_api_request(API_URL, data)
    return result["data"]["list"][0]["issueNumber"] if "data" in result and "list" in result["data"] else None


# Function to generate a random prediction
def generate_prediction(period):
    signals = ["BIG", "SMALL"]
    number = int(time.time()) % 10  # Generate a pseudo-random number (0-9)
    signal = "BIG" if number >= 5 else "SMALL"
    color = "🌚" if signal == "BIG" else "💎"
    return {"period": str(period), "signal": signal, "number": str(number), "color": color}


# Function to send a prediction message
def send_prediction_message(prediction):
    global total_bets

    total_bets += 1
    text = f"""
🔥 *TKG PAID PREDICTION* 🔥

📅 *Date:* {datetime.now().strftime("%d-%m-%Y")}
🕒 *Time:* {datetime.now().strftime("%I:%M %p")}

🎮 *Game Information* 🎮
🔹 *Period:* `{prediction["period"]}`
💹 *Bot Signal:* `{prediction["signal"]}`
🔢 *Predicted Number:* `{prediction["number"]}`
🎨 *Color:* `{prediction["color"]}`

🏆 *Result:* ⏳ PENDING
📊 *Bets:* {total_bets} | ✅ *Wins:* {total_wins} | ❌ *Losses:* {total_losses}

🔗 *Main Channel:* [Join Now](https://t.me/+dvXSCRb7daM0MjI1)
"""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {"chat_id": CHANNEL_ID, "photo": IMAGE_URL, "caption": text, "parse_mode": "Markdown"}
    response = make_api_request(url, data)
    return response.get("result", {}).get("message_id")


# Function to fetch actual results
def get_result(period):
    while True:
        data = {
            "pageSize": 10,
            "pageNo": 1,
            "typeId": 1,
            "language": 0,
            "random": "4a0522c6ecd8410496260e686be2a57c",
            "signature": "334B5E70A0C9B8918B0B15E517E2069C",
            "timestamp": int(time.time())
        }
        results = make_api_request(API_URL, data).get("data", {}).get("list", [])

        for result in results:
            if str(result["issueNumber"]) == str(period):
                return {"number": str(result["number"])}  # Convert to string to avoid concatenation errors

        time.sleep(3)  # Retry every 3 seconds


# Function to edit the message with the final result
def edit_message(message_id, prediction, result):
    global total_wins, total_losses, win_streak, loss_streak

    win = (prediction["signal"] == "BIG" and int(result["number"]) >= 5) or \
          (prediction["signal"] == "SMALL" and int(result["number"]) < 5)
    jackpot = (prediction["number"] == result["number"])

    if jackpot:
        win_text = "🎉 *JACKPOT WIN!* 🎉"
        sticker_id = "CAACAgUAAxkBAAEOAfxny8dF3KgdhIAtavVt7FeCHaUBewACgwIAAmt8UFW6k9PrOMHHZDYE"
    elif win:
        win_text = "✅ WIN"
        sticker_id = "CAACAgIAAxkBAAENsKFnnk4PchJ4r5Pld96cCtpPd6ki_gACRjwAAgOpCEvYbLyS2BY3EjYE"
    else:
        win_text = "❌ LOSS"
        sticker_id = "CAACAgUAAxkBAAEN-elnyAczF7NzbIjEm8R35RyZFakz9QACyQ4AApmj2FeuwtBKxDbzUDYE"

    if win or jackpot:
        total_wins += 1
        win_streak += 1
        loss_streak = 0
        streak_message = "🔥 *Back-to-back Wins!* Keep it up! 🔥" if win_streak >= 2 else ""
    else:
        total_losses += 1
        loss_streak += 1
        win_streak = 0
        streak_message = "😔 *Don't lose hope!* Better luck next time! 💪" if loss_streak >= 2 else ""

    text = f"""
🔥 *TKG PAID SERVICE* 🔥

🎮 *Period:* `{prediction["period"]}`
💹 *Bot Signal:* `{prediction["signal"]}`
🔢 *Predicted Number:* `{prediction["number"]}`
🎨 *Color:* `{prediction["color"]}`
🏆 *Result:* {win_text} ({result["number"]})

📊 *Bets:* {total_bets} | ✅ *Wins:* {total_wins} | ❌ *Losses:* {total_losses}
{streak_message}
"""

    # Edit the message
    edit_url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageCaption"
    make_api_request(edit_url, {
        "chat_id": CHANNEL_ID,
        "message_id": message_id,
        "caption": text,
        "parse_mode": "Markdown"
    })

    # Send sticker
    sticker_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendSticker"
    make_api_request(sticker_url, {"chat_id": CHANNEL_ID, "sticker": sticker_id})


# Run prediction loop
while True:
    latest_period = fetch_latest_period()
    if not latest_period or last_predicted_period == int(latest_period) + 1:
        time.sleep(3)
        continue

    last_predicted_period = int(latest_period) + 1
    prediction = generate_prediction(last_predicted_period)
    message_id = send_prediction_message(prediction)
    result = get_result(prediction["period"])
    edit_message(message_id, prediction, result)
