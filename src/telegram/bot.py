import requests
import os

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"

    def send_message(self, text, parse_mode="Markdown", reply_markup=None):
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        response = requests.post(url, json=payload)
        return response.json()

    def send_photo(self, photo_path, caption=None, parse_mode="Markdown", reply_markup=None):
        url = f"{self.base_url}/sendPhoto"
        with open(photo_path, 'rb') as photo:
            files = {"photo": photo}
            payload = {
                "chat_id": self.chat_id,
                "caption": caption,
                "parse_mode": parse_mode
            }
            if reply_markup:
                payload["reply_markup"] = reply_markup
            response = requests.post(url, data=payload, files=files)
        return response.json()

    def get_inline_keyboard(self, trade_id):
        return {
            "inline_keyboard": [
                [
                    {"text": "📊 Full Scan", "callback_data": f"scan_{trade_id}"},
                    {"text": "❌ Close Trade", "callback_data": f"close_{trade_id}"}
                ],
                [
                    {"text": "📈 View Chart", "callback_data": f"chart_{trade_id}"}
                ]
            ]
        }

    def format_signal_message(self, signal_data):
        emoji = "🚀" if signal_data['direction'] == "BUY" else "🔻"
        header = "💎 *QUANTUM APEX | ULTRA SIGNAL* 💎"
        msg = (
            f"{header}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{emoji} *ASSET:* {signal_data['coin']}\n"
            f"📈 *DIRECTION:* {signal_data['direction']}\n\n"
            f"🎯 *ENTRY:* `{signal_data['entry_price']:.6f}`\n"
            f"🛑 *STOP LOSS:* `{signal_data['stop_loss']:.6f}`\n\n"
            f"💰 *TARGET 1:* `{signal_data['tp1']:.6f}`\n"
            f"💰 *TARGET 2:* `{signal_data['tp2']:.6f}`\n"
            f"💰 *TARGET 3:* `{signal_data['tp3']:.6f}`\n\n"
            f"📊 *CONFIDENCE:* `{signal_data['confidence']}%`\n"
            f"⚖️ *R/R RATIO:* `{signal_data['risk_reward']}`\n\n"
            f"🔍 *STRATEGY:* `SMC + Multi-TF Quant`\n"
            f"🆔 *TRADE ID:* `{signal_data.get('trade_id', 'N/A')}`\n\n"
            f"⚠️ _Proprietary logic. Risk management required._"
        )
        return msg

    def format_update_message(self, update):
        coin = update['coin']
        new_status = update['new_status']
        
        status_emojis = {
            'ACTIVE': "✅",
            'TP1 HIT': "💰",
            'TP2 HIT': "💰💰",
            'TP3 HIT': "💰💰💰",
            'COMPLETED': "🏆",
            'SL HIT': "❌",
            'EXPIRED': "⏱"
        }
        
        emoji = status_emojis.get(new_status, "ℹ️")
        return f"{emoji} *UPDATE: {coin}* - Status changed to *{new_status}*"
