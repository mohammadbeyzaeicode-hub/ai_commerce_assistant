# # test_get_user_id.py
# import requests
# import time

# from core import settings


# BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
# URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"

# offset = None

# while True:
#     params = {"timeout": 30}
#     if offset:
#         params["offset"] = offset

#     resp = requests.get(URL, params=params).json()

#     for update in resp.get("result", []):
#         offset = update["update_id"] + 1

#         message = update.get("message")
#         if not message:
#             continue

#         user = message["from"]
#         user_id = user["id"]
#         username = user.get("username")

#         print("✅ New Message")
#         print("User ID:", user_id)
#         print("Username:", username)
#         print("Text:", message.get("text"))

#     time.sleep(1)
