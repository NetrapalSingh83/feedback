from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = "8710710101:AAEGsI0foALFLy91oOrobqAWoH98ZU7QWIQ"
ADMIN_CHAT_ID = "8523310365" # Paste your numerical ID here (e.g., "123456789")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the user types /start."""
    welcome_message = (
        "Hello! 👋\n"
        "Please send your feedback image here, and I will forward it to the admin."
    )
    await update.message.reply_text(welcome_message)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forwards the received photo directly to your personal Telegram ID."""
    photo_file_id = update.message.photo[-1].file_id
    
    sender_name = update.message.from_user.first_name
    sender_id = update.message.from_user.id
    
    # Send the photo to your personal account
    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo_file_id,
        caption=f"📸 New feedback received!\nFrom: {sender_name} (ID: {sender_id})"
    )
    
    # Send a confirmation back to the user
    await update.message.reply_text("Thank you for your feedback! Your image has been received.")
    print(f"Forwarded an image from {sender_name} to admin.")

async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows the admin to send a message back to the user."""
    
    # SECURITY: Check if the person sending the command is you (the admin)
    if str(update.message.from_user.id) != str(ADMIN_CHAT_ID):
        return # Silently ignore commands from anyone else
    
    # Check if you typed the command correctly
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Usage: /reply <user_id> <your message>\n"
            "Example: /reply 123456789 Thank you for pointing this out!"
        )
        return
    
    # Extract the user ID and your message from the command
    target_user_id = context.args[0]
    admin_message = " ".join(context.args[1:])
    
    # Send the message to the user
    try:
        await context.bot.send_message(
            chat_id=target_user_id, 
            text=f"👨‍💻 Message from Admin:\n\n{admin_message}"
        )
        await update.message.reply_text(f"✅ Message successfully sent to user {target_user_id}!")
        print(f"Reply sent to {target_user_id}.")
    except Exception as e:
        # If the user blocked the bot, it will throw an error here
        await update.message.reply_text(f"❌ Failed to send message. Error: {e}")

def main():
    """Starts the bot."""
    application = Application.builder().token(TOKEN).build()

    # Handlers for users
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Handler for the admin reply command
    application.add_handler(CommandHandler("reply", reply_to_user))

    print("Bot is running... Waiting for feedback images. Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == '__main__':
    main()
