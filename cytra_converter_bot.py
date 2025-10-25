import os
import tempfile
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from pydub import AudioSegment
import img2pdf
from PIL import Image
import speech_recognition as sr
import ffmpeg

# -----------------------------
# 🤖 BOT INFO
# -----------------------------
BOT_CREATOR = "Cytra 😎"
BOT_NAME = "Cytra Converter Bot"
TOKEN = os.getenv("TG_BOT_TOKEN")  # Set your bot token in Render environment variables

# -----------------------------
# ⚙️ START COMMAND
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hey there! 👋 I'm *{BOT_NAME}* — made by {BOT_CREATOR}.\n\n"
        "Send me an image, video, or voice message and I'll convert it for you 🔄",
        parse_mode="Markdown"
    )

# -----------------------------
# 🖼️ IMAGE HANDLER (to PDF)
# -----------------------------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
        await file.download_to_drive(temp.name)
        img = Image.open(temp.name).convert("RGB")
        pdf_path = temp.name.replace(".jpg", ".pdf")
        img.save(pdf_path, "PDF", resolution=100.0)

    await update.message.reply_document(document=open(pdf_path, "rb"), filename="converted.pdf")
    os.remove(temp.name)
    os.remove(pdf_path)

# -----------------------------
# 🎥 VIDEO HANDLER (to MP3)
# -----------------------------
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.video.get_file()
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp:
        await file.download_to_drive(temp.name)
        mp3_path = temp.name.replace(".mp4", ".mp3")

        # Extract audio using ffmpeg
        ffmpeg.input(temp.name).output(mp3_path, format='mp3', acodec='libmp3lame').run(quiet=True, overwrite_output=True)

    await update.message.reply_audio(audio=open(mp3_path, "rb"), filename="converted.mp3")
    os.remove(temp.name)
    os.remove(mp3_path)

# -----------------------------
# 🗣️ VOICE HANDLER (to TEXT)
# -----------------------------
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.voice.get_file()
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp:
        await file.download_to_drive(temp.name)
        wav_path = temp.name.replace(".ogg", ".wav")

        AudioSegment.from_file(temp.name).export(wav_path, format="wav")
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
                await update.message.reply_text(f"🗣️ Transcribed text:\n\n{text}")
            except sr.UnknownValueError:
                await update.message.reply_text("Sorry 😔 I couldn’t understand that voice message.")

    os.remove(temp.name)
    os.remove(wav_path)

# -----------------------------
# ✅ STATUS COMMAND (for Render)
# -----------------------------
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ {BOT_NAME} by {BOT_CREATOR} is online and running!")

# -----------------------------
# 🧠 MAIN APP
# -----------------------------
def main():
    if not TOKEN:
        print("❌ Please set your TG_BOT_TOKEN environment variable!")
        return

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print(f"🚀 {BOT_NAME} by {BOT_CREATOR} is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
