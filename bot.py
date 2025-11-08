from pyrogram import Client, filters
import os
import re
import asyncio

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("video_extract_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

SUPPORTED_DOMAINS = ["livelearn.in", "appx.co.in"]
SUPPORTED_EXTENSIONS = [".m3u8", ".mp4"]

def extract_links(text):
    pattern = r'https?://[^\s]+'
    links = re.findall(pattern, text)
    valid_links = []
    for link in links:
        if any(domain in link for domain in SUPPORTED_DOMAINS) or any(link.endswith(ext) for ext in SUPPORTED_EXTENSIONS):
            valid_links.append(link)
    return valid_links

@app.on_message(filters.command(["start", "help"]))
async def start(_, message):
    await message.reply_text(
        "✅ Bot चल रहा है!\n\n"
        "मुझे कोई .txt file भेजो जिसमें livelearn.in, appx.co.in, .m3u8, या .mp4 links हों,\n"
        "मैं सारे valid video links निकाल दूँगा।\n\n"
        "⚙️ Supported: livelearn.in | appx.co.in | .m3u8 | .mp4"
    )

@app.on_message(filters.document)
async def get_doc(_, message):
    doc = message.document

    if not doc.file_name.endswith(".txt"):
        return await message.reply_text("⚠️ सिर्फ .txt files भेजो जिनमें video links हों।")

    file_path = await message.download()
    await asyncio.sleep(1)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    links = extract_links(content)
    os.remove(file_path)

    if not links:
        return await message.reply_text("❌ कोई valid video link नहीं मिला।")

    # Split into smaller parts
    chunk_size = 50  # ek message me 50 links tak
    for i in range(0, len(links), chunk_size):
        part = links[i:i + chunk_size]
        text = "🎯 **Valid Video Links (Part {}/{}):**\n\n{}".format(
            i // chunk_size + 1, (len(links) + chunk_size - 1) // chunk_size, "\n".join(part)
        )
        await message.reply_text(text)
        await asyncio.sleep(0.5)  # Telegram floodwait avoid

print("🤖 Bot started successfully!")
app.run()
