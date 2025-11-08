from pyrogram import Client, filters
import os
import re
import asyncio
from urllib.parse import urlparse

API_ID = int(os.getenv(21180805) 
API_HASH = os.getenv(7a7471487558a0bce88d5574d96ff7dd) 
BOT_TOKEN = os.getenv(7a7471487558a0bce88d5574d96ff7dd) 

app = Client("video_extract_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def extract_links(text):
    """Extract video links from text using regex"""
    url_pattern = r'https?://[^\s]+'
    links = re.findall(url_pattern, text)
    
    # Filter video links (you can add more video domains)
    video_domains = ['youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com', 
                    'tiktok.com', 'instagram.com', 'facebook.com', 'twitter.com']
    
    video_links = []
    for link in links:
        parsed_url = urlparse(link)
        domain = parsed_url.netloc.lower()
        if any(video_domain in domain for video_domain in video_domains):
            video_links.append(link)
    
    return video_links

@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Handle /start command"""
    welcome_text = """
🤖 Video Link Extractor Bot

📁 कैसे इस्तेमाल करें:
1. एक .txt फाइल भेजें जिसमें वीडियो लिंक हों
2. या सीधे मैसेज में लिंक भेजें

📝 सपोर्टेड फॉर्मेट:
- YouTube, Instagram, TikTok
- Facebook, Twitter, Vimeo
- Dailymotion और अन्य वीडियो साइट्स

⚡ बॉट ऑटोमेटिकली सभी वीडियो लिंक extract कर देगा!
    """
    await message.reply(welcome_text)

@app.on_message(filters.text & filters.private & ~filters.command("start"))
async def handle_text_links(client, message):
    """Extract video links from text messages"""
    text = message.text
    video_links = extract_links(text)
    
    if not video_links:
        await message.reply("❌ कोई वीडियो लिंक नहीं मिला! कृपया वैलिड लिंक भेजें।")
        return
    
    await message.reply(f"🎯 {len(video_links)} वीडियो लिंक मिले!\n\nप्रोसेसिंग शुरू...")
    
    success_count = 0
    failed_links = []
    
    for i, link in enumerate(video_links, 1):
        try:
            await message.reply(
                f"📹 वीडियो {i}/{len(video_links)}\n{link}",
                disable_web_page_preview=False
            )
            success_count += 1
            await asyncio.sleep(1)  # Avoid flooding
        except Exception as e:
            failed_links.append(link)
            print(f"Error processing {link}: {e}")
    
    # Send summary
    summary = f"""
✅ प्रोसेसिंग पूरी हुई!

📊 रिजल्ट:
• ✅ सफल: {success_count}
• ❌ फेल: {len(failed_links)}
• 📧 कुल: {len(video_links)}
    """
    
    if failed_links:
        summary += f"\nफेल हुए लिंक्स:\n" + "\n".join(failed_links[:5])
        if len(failed_links) > 5:
            summary += f"\n... और {len(failed_links) - 5} और"
    
    await message.reply(summary)

@app.on_message(filters.document & filters.private)
async def handle_txt_file(client, message):
    """Handle TXT files with video links"""
    if not message.document.mime_type == "text/plain":
        await message.reply("❌ कृपया सिर्फ .txt फाइल भेजें!")
        return
    
    # Check file size (max 1MB)
    if message.document.file_size > 1024 * 1024:
        await message.reply("❌ फाइल साइज बहुत बड़ी है! मैक्सिमम 1MB की फाइल भेजें।")
        return
    
    processing_msg = await message.reply("📥 फाइल डाउनलोड हो रही है...")
    
    try:
        file_path = await message.download()
        
        await processing_msg.edit("🔍 फाइल से वीडियो लिंक निकाले जा रहे हैं...")
        
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
        
        # Clean up downloaded file
        os.remove(file_path)
        
        video_links = extract_links(file_content)
        
        if not video_links:
            await processing_msg.edit("❌ TXT फाइल में कोई वीडियो लिंक नहीं मिला!")
