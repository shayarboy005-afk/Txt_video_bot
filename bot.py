from pyrogram import Client, filters
import os
import re

# ✅ Environment variables se credentials lo
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ✅ Telegram Bot client initialize
app = Client("video_extract_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ Function: Extract only required domains or file types
def extract_links(text):
    # Sirf in domains aur extensions wale links nikaalega
    pattern = r'(https?://[^\s]+?(?:livelearn\.in|appx\.co\.in|\.m3u8|\.mp4)[^\s]*)'
    return re.findall(pattern, text)

# ✅ Command: /start
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(
        "✅ Bot चल रहा है!\n\n"
        "मुझे कोई `.txt` file भेजो जिसमें `livelearn.in`, `appx.co.in`, `.m3u8`, या `.mp4` links हों,\n"
        "मैं सारे valid video links निकाल दूँगा।\n\n"
        "⚙ Supported: livelearn.in | appx.co.in | .m3u8 | .mp4"
    )

# ✅ File handler
@app.on_message(filters.document)
async def handle_file(client, message):
    if message.document.file_name.endswith('.txt'):
        file_path = await message.download()
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        links = extract_links(content)

        if links:
            reply_text = "✅ Valid video links मिले:\n\n" + "\n".join(links)
        else:
            reply_text = "❌ कोई valid video link नहीं मिला!"
        await message.reply_text(reply_text)

    else:
        await message.reply_text("⚠️ कृपया सिर्फ `.txt` file भेजें!")

# ✅ Run the bot
print("🤖 Bot is running...")
app.run()
