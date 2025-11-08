from pyrogram import Client, filters
import os
import re
import asyncio
from urllib.parse import urlparse
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
app = Client(
    "video_extract_bot",
    api_id=A21180805,
    api_hash=7a7471487558a0bce88d5574d96ff7dd, 
    bot_token=7a7471487558a0bce88d5574d96ff7dd
)

def extract_links(text):
    url_pattern = r'https?://[^\s]+'
    links = re.findall(url_pattern, text)
    video_domains = [
        'youtube.com', 'youtu.be', 'vimeo.com',
        'dailymotion.com', 'tiktok.com', 'instagram.com',
        'facebook.com', 'twitter.com', 'twitch.tv',
        'vimeo.com', 'dailymotion.com', 'likee.video',
        'kwai.com', 'snapchat.com', 'pinterest.com',
        'linkedin.com', 'reddit.com', 'tumblr.com',
        'flickr.com', 'imgur.com', 'gfycat.com',
        'streamable.com', 'vid.me', 'vevo.com',
        'metacafe.com', 'vine.co', 'funnyordie.com',
        'worldstarhiphop.com', 'liveleak.com', 'break.com'
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
    await message.reply(
        """🤖 Video Link Extractor Bot

📁 How to use:
1. Send a .txt file containing video links
2. Or send links directly in message

📝 Supported Platforms:
YouTube, Instagram, TikTok, Facebook, Twitter, Vimeo, Dailymotion, Twitch, Likee, Kwai, Snapchat, Pinterest, LinkedIn, Reddit, Tumblr, Flickr, Imgur, Gfycat, Streamable, Vid.me, Vevo, Metacafe, Vine, Funny or Die, WorldStarHipHop, LiveLeak, Break.com

⚡ Bot will extract all video links!"""
    )

@app.on_message(filters.document & filters.private)
async def handle_txt_file(client, message):
    if message.document and message.document.file_name.endswith('.txt'):
        try:
            await message.reply("📥 Downloading file...")
            file_path = await message.download()
            
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            video_links = extract_links(text)
            
            if not video_links:
                await message.reply("❌ No video links found in the file!")
                return
            
            await message.reply(f"🎯 Found {len(video_links)} video links in file!")
            
            # Send links in batches to avoid rate limiting
            batch_size = 5
            for i in range(0, len(video_links), batch_size):
                batch = video_links[i:i + batch_size]
                links_text = "\n".join([f"📹 {i+j+1}. {link}" for j, link in enumerate(batch)])
                await message.reply(links_text)
                await asyncio.sleep(2)
            
            # Clean up downloaded file
            os.remove(file_path)
            
        except Exception as e:
            await message.reply(f"❌ Error processing file: {str(e)}")

@app.on_message(filters.text & filters.private & ~filters.command("start"))
async def handle_text_links(client, message):
    text = message.text
    video_links = extract_links(text)
    
    if not video_links:
        await message.reply("❌ No video links found!")
        return
    
    await message.reply(f"🎯 Found {len(video_links)} video links!")
    
    # Send links in batches
    batch_size = 5
    for i in range(0, len(video_links), batch_size):
        batch = video_links[i:i + batch_size]
        links_text = "\n".join([f"📹 {i+j+1}. {link}" for j, link in enumerate(batch)])
        await message.reply(links_text)
        await asyncio.sleep(2)

@app.on_message(filters.command("help"))
async def help_command(client, message):
    await message.reply(
        """🆘 Help Guide

Commands:
/start - Start the bot
/help - Show this help message   

 Features:
• Extract video links from text messages
• Extract video links from .txt files
• Support for 30+ video platforms
• Batch processing for multiple links

Supported Formats:
• Direct links in messages
• .txt files containing multiple links

Note: The bot only extracts links, it doesn't download videos."""
    )

if name == "main":
    print("✅ Bot is running...")
    app.run()
