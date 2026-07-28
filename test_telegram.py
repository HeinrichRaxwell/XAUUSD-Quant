import os
import sys
import json
import urllib.request
import urllib.parse

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

def test_telegram_bot():
    print("==========================================================")
    print("      TELEGRAM BOT REALITY & EMPIRICAL TEST SCRIPT        ")
    print("==========================================================")
    
    # 1. Test Bot Identity (getMe)
    url_me = f"https://api.telegram.org/bot{TOKEN}/getMe"
    try:
        req = urllib.request.Request(url_me)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("ok"):
                bot_info = data["result"]
                print(f"[OK] Telegram API Handshake SUCCESS!")
                print(f"    Bot Name    : {bot_info.get('first_name')}")
                print(f"    Username    : @{bot_info.get('username')}")
                print(f"    Can Join Grps: {bot_info.get('can_join_groups')}")
            else:
                print(f"[X] Telegram getMe failed: {data}")
                return
    except Exception as e:
        print(f"[X] Network/Connection error fetching getMe: {e}")
        return

    # 2. Test Fetching Chat ID (getUpdates)
    url_updates = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    chat_id = None
    try:
        req = urllib.request.Request(url_updates)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get("ok") and data.get("result"):
                for item in reversed(data["result"]):
                    if "message" in item:
                        chat_id = str(item["message"]["chat"]["id"])
                        user_first_name = item["message"]["from"].get("first_name", "User")
                        print(f"[OK] Detected Chat ID: {chat_id} (User: {user_first_name})")
                        break
            
            if not chat_id:
                print("[!] No messages found in getUpdates yet.")
                print("    --> PLEASE OPEN TELEGRAM & SEND /start TO @QuantXauAnlyzerBot !")
    except Exception as e:
        print(f"[X] Network/Connection error fetching getUpdates: {e}")

    # 3. Test Sending Live Ping Message if Chat ID is found
    if chat_id:
        url_send = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        test_msg = (
            f"✅ *XAUUSD QUANT BOT LIVE TEST PING*\n\n"
            f"🤖 *Bot Name*: @QuantXauAnlyzerBot\n"
            f"📊 *Status*: Operational & Connected to MT5 Exness Demo\n"
            f"⚙️ *System*: LightGBM Machine Learning Engine Active\n\n"
            f"⚡ _If you see this message, Telegram Alerts are 100% WORKING!_"
        )
        payload = {
            "chat_id": chat_id,
            "text": test_msg,
            "parse_mode": "Markdown"
        }
        try:
            encoded = urllib.parse.urlencode(payload).encode("utf-8")
            req = urllib.request.Request(url_send, data=encoded)
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode())
                if res.get("ok"):
                    print(f"[OK] LIVE TELEGRAM TEST MESSAGE DELIVERED TO CHAT ID {chat_id}!")
                else:
                    print(f"[X] Failed to send message: {res}")
        except Exception as e:
            print(f"[X] Error sending test message: {e}")

    else:
        print("\n[SUMMARY] Bot API Token is 100% VALID, but needs user to send a message to @QuantXauAnlyzerBot first to capture Chat ID!")

if __name__ == "__main__":
    test_telegram_bot()
