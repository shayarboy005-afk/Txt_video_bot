from pyrogram import Client, filters
import os
import re
from urllib.parse import urlparse

# ✅ Environment se API keys lena
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "video_extract_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

def extract_links(text):
    url_pattern = r'https?://[^\s]+'
    links = re.findall(url_pattern, text)
    video_domains = [
        'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
        'tiktok.com', 'instagram.com', 'facebook.com', 'twitter.com'
    ]
    video_links = []
    for link in links:
        parsed_url = urlparse(link)
        domain = parsed_url.netloc.lower()
        if any(video_domain in domain for video_domain in video_domains):
            video_links.append(link)
    return video_links


@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply("✅ Bot चल रहा है! अपने वीडियो लिंक भेजें।")


if __name__ == "__main__":
    print("✅ Bot शुरू हो गया है...")
    app.run()
