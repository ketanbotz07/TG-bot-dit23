from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import requests, os, time

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Send initial message
    msg = await update.message.reply_text("📥 Video received, processing started…")

    # Download video from Telegram
    tg_file = await update.message.video.get_file()
    in_path = f"temp_{update.message.message_id}.mp4"
    await tg_file.download_to_drive(in_path)

    # Upload to API
    with open(in_path, "rb") as f:
        r = requests.post(f"{API_URL}/upload", files={"file": f})
    task_id = r.json().get("task_id")

    # Polling for progress
    while True:
        p = requests.get(f"{API_URL}/progress/{task_id}").json().get("progress", 0)
        await msg.edit_text(f"⚙️ Processing… {p}%")
        if p >= 100:
            break
        time.sleep(3)

    # Download transformed video
    out_url = f"{API_URL}/download/{task_id}"
    out_path = f"final_{task_id}.mp4"
    with requests.get(out_url, stream=True) as rr:
        with open(out_path, "wb") as f:
            for c in rr.iter_content(8192):
                if c:
                    f.write(c)

    # Send back to user
    await update.message.reply_video(
        video=open(out_path, "rb"), caption="✅ Transformed video (No‑Reuse Safe)"
    )

    # Clean up
    os.remove(in_path)
    os.remove(out_path)


# Initialize bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.VIDEO, handle_video))

# Run the bot
app.run_polling()
