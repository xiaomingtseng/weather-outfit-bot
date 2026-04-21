# Weather Outfit Bot

一個 Line Bot，根據天氣自動推薦穿搭建議。

## 功能特性

- 💬 支援「台北」和「北海道」天氣查詢
- 🎨 使用 Google Gemini AI 生成個性化穿搭建議
- 📱 輪播菜單選擇城市
- ⚡ 智能 fallback 機制，API 超配額時仍可提供推薦

## 技術棧

- **後端**: Flask
- **Line Bot SDK**: line-bot-sdk v3
- **天氣 API**: OpenWeatherMap
- **AI**: Google Generative AI (Gemini 1.5 Flash)
- **環境管理**: python-dotenv

## 安裝

1. 克隆本倉庫
   ```bash
   git clone https://github.com/xiaomingtseng/weather-outfit-bot.git
   cd weather-outfit-bot
   ```

2. 安裝依賴
   ```bash
   uv sync
   ```

3. 配置環境變數 (`.env`)
   ```
   CHANNEL_SECRET=your_line_channel_secret
   CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
   WEATHER_API_KEY=your_openweather_api_key
   GEMINI_API_KEY=your_gemini_api_key
   ```

4. 運行應用
   ```bash
   uv run python app.py
   ```

應用將在 `http://127.0.0.1:5000` 運行。

## 使用方式

1. 加入 Line Bot
2. 發送任何訊息以查看城市選擇輪播
3. 點擊「台北」或「北海道」獲取當日穿搭建議

## 環境變數

| 變數 | 說明 |
|------|------|
| `CHANNEL_SECRET` | Line Channel Secret |
| `CHANNEL_ACCESS_TOKEN` | Line Channel Access Token |
| `WEATHER_API_KEY` | OpenWeatherMap API Key |
| `GEMINI_API_KEY` | Google Generative AI API Key |

## 目錄結構

```
weather-outfit-bot/
├── app.py              # 主應用程式
├── pyproject.toml      # 依賴配置
├── .env               # 環境變數（不上傳到版本控制）
├── .gitignore         # Git 忽略文件
└── README.md          # 專案說明
```

## 授權

MIT License
