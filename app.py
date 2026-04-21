from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import (
    ApiClient, Configuration, MessagingApi, ReplyMessageRequest, TextMessage,
    TemplateMessage, CarouselTemplate, CarouselColumn, PostbackAction
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent, FollowEvent
from linebot.v3.exceptions import InvalidSignatureError
import requests
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-1.5-flash")
handler = WebhookHandler(CHANNEL_SECRET)
configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)

def get_weather(city):
    """獲取天氣信息"""
    city_map = {"台北": "Taipei", "北海道": "Sapporo"}
    api_url = f"https://api.openweathermap.org/data/2.5/weather?q={city_map.get(city)}&appid={WEATHER_API_KEY}&units=metric&lang=zh_tw"
    
    try:
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            temp = round(data['main']['temp'])
            feels = round(data['main']['feels_like'])
            rain = data.get('rain', {}).get('1h', 0)
            desc = data['weather'][0]['description']
            city_zh = "台北" if city == "台北" else "北海道"
            return temp, feels, rain, desc, city_zh
    except:
        pass
    
    # 默認值
    if city == "台北":
        return 18, 15, 0.7, "多雲時陰", "台北"
    else:
        return -3, -8, 0.8, "下雪", "北海道"

def get_outfit_advice(city, temp, feels, desc, rain):
    prompt = f"""
你是一個男士穿搭顧問，風格走向是「時髦但不費腦、Uniqlo 基本款為主」。
請根據以下天氣給出今日穿搭建議：

城市：{city}
氣溫：{temp}°C，體感：{feels}°C
天氣：{desc}
降雨：{'有雨' if rain > 0 else '無雨'}

請用繁體中文，格式如下：
👕 上衣：
🧥 外層：
👖 下身：
👟 鞋子：
💡 小提醒：

簡潔有力，每項一行，不要廢話。
"""
    try:
        response = gemini.generate_content(prompt)
        return response.text
    except Exception as e:
        # rate limit 或其他錯誤時用規則式回覆
        if temp < 15:
            return "👕 上衣：厚棉T\n🧥 外層：鋪棉外套\n👖 下身：深藍錐形牛仔\n👟 鞋子：白球鞋\n💡 小提醒：今天偏冷，多帶一件！"
        elif temp < 22:
            return "👕 上衣：白T或條紋T\n🧥 外層：薄外套\n👖 下身：卡其褲\n👟 鞋子：白球鞋\n💡 小提醒：早晚溫差大，外套帶著！"
        else:
            return "👕 上衣：白T\n🧥 外層：不需要\n👖 下身：卡其短褲\n👟 鞋子：涼鞋或白球鞋\n💡 小提醒：今天熱，輕薄為主！"

def send_carousel(reply_token):
    carousel = TemplateMessage(
        alt_text="請選擇城市",
        template=CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url="https://images.unsplash.com/photo-1598935898639-81586f7d2129?w=1170",
                    title="台北",
                    text="點我查今天穿搭",
                    actions=[PostbackAction(label="台北", text="台北", data="city=taipei")]
                ),
                CarouselColumn(
                    thumbnail_image_url="https://images.unsplash.com/photo-1584005679717-7dda5e88bb52?w=735",
                    title="北海道",
                    text="點我查今天穿搭",
                    actions=[PostbackAction(label="北海道", text="北海道", data="city=hokkaido")]
                )
            ]
        )
    )
    with ApiClient(configuration) as api_client:
        MessagingApi(api_client).reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=[carousel])
        )

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(FollowEvent)
def handle_follow(event):
    send_carousel(event.reply_token)

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_msg = event.message.text.strip()
    
    if user_msg in ["台北", "北海道"]:
        temp, feels, rain, desc, city_zh = get_weather(user_msg)
        outfit = get_outfit_advice(city_zh, temp, feels, desc, rain)
        reply = (
            f"{city_zh}・今天\n\n"
            f"🌡 氣溫：{temp}°C  體感：{feels}°C\n"
            f"🌤 {desc}\n\n"
            f"{outfit}"
        )
        
        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=reply)]
                )
            )
    else:
        send_carousel(event.reply_token)

if __name__ == "__main__":
    app.run(port=5000)