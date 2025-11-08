from pyrogram import Client, filters
import os
import re
import aiohttp
import aiofiles
from urllib.parse import urlparse
from typing import List, Tuple
import asyncio

# ⚙️ Environment se values lena (Render ke environment variables se)
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🔧 Bot initialization
app = Client(
    "video_extract_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=100,
    sleep_threshold=60
)

# 🎬 Video domains for filtering
VIDEO_DOMAINS = {
    'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com',
    'tiktok.com', 'instagram.com', 'facebook.com', 'twitter.com', 'x.com',
    'twitch.tv', 'streamable.com', 'reddit.com', 'likee.video', 'kwai.com'
}

def extract_links(text: str) -> List[str]:
    """Extract and filter video links from text"""
    url_pattern = r'https?://[^\s]+'
    links = re.findall(url_pattern, text)
    video_links = []
    for link in links:
        try:
            parsed_url = urlparse(link)
            domain = parsed_url.netloc.lower()
            if any(video_domain in domain for video_domain in VIDEO_DOMAINS):
                video_links.append(link)
        except Exception:
            continue
    return video_links


async def process_text_file(file_path: str) -> Tuple[List[str], int]:
    """Process text file and extract links"""
    video_links = []
    total_lines = 0
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            async for line in file:
                total_lines += 1
                links = extract_links(line.strip())
                video_links.extend(links)
    except UnicodeDecodeError:
        async with aiofiles.open(file_path, 'r', encoding='latin-1') as file:
            async for line in file:
                total_lines += 1
                links = extract_links(line.strip())
                video_links.extend(links)

    # remove duplicates
    unique_links = []
    for link in video_links:
        if link not in unique_links:
            unique_links.append(link)
    return unique_links, total_lines


async def validate_video_links(links: List[str]) -> List[str]:
    """Validate video links asynchronously"""
    valid_links = []
    async def check_link(link):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.head(link, allow_redirects=True) as response:
                    if response.status == 200:
                        return link
        except:
            return None

    batch_size = 10
    for i in range(0, len(links), batch_size):
        batch = links[i:i + batch_size]
        tasks = [check_link(link) for link in batch]
        results = await asyncio.gather(*tasks)
        valid_links.extend([r for r in results if r])
        await asyncio.sleep(0.1)
    return valid_links


@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Start command"""
    await message.reply(
        "✅ **Bot चल रहा है!**\n\n"
        "मुझे कोई `.txt` file भेजो जिसमें video links हों,\n"
        "मैं सारे valid video links निकाल दूँगा।\n\n"
        "**Supported:** YouTube, Instagram, TikTok, Twitter, Facebook, etc."
    )


@app.on_message(filters.document)
async def handle_file(client, message):
    """Handle uploaded .txt file"""
    doc = message.document
    if not doc.file_name.endswith(".txt"):
        await message.reply("❌ केवल `.txt` file भेजें!")
        return

    downloading = await message.reply("📥 आपकी file डाउनलोड की जा रही है...")

    file_path = await message.download()
    links, total_lines = await process_text_file(file_path)
    valid_links = await validate_video_links(links)

    if not valid_links:
        await downloading.edit("❌ कोई valid video link नहीं मिला!")
    else:
        text_result = "\n".join(valid_links)
        async with aiofiles.open("extracted_links.txt", "w", encoding="utf-8") as f:
            await f.write(text_result)
        await downloading.edit(f"✅ {len(valid_links)} video links निकाले गए हैं ({total_lines} lines में से)")
        await message.reply_document("extracted_links.txt")

    os.remove(file_path)
    if os.path.exists("extracted_links.txt"):
        os.remove("extracted_links.txt")


if __name__ == "__main__":
    print("🚀 Bot Render पर शुरू हो गया...")
    app.run()
