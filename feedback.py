import os
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = "8710710101:AAEGsI0foALFLy91oOrobqAWoH98ZU7QWIQ"
ADMIN_CHAT_ID = "8523310365" # Paste your numerical ID here
STATS_FILE = "feedback_stats.json"

# --- DATA MANAGEMENT ---
def load_stats():
    """Loads the feedback counts from the JSON file."""
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_stats(stats):
    """Saves the feedback counts to the JSON file."""
    with open(STATS_FILE, "w") as file:
        json.dump(stats, file, indent=4)

# --- BOT COMMANDS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the user types /start."""
    welcome_message = (
        "Hello! 👋\n"
        "Please send your feedback image here, and I will forward it to the admin."
    )
    await update.message.reply_text(welcome_message)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forwards the received photo and updates the user's feedback count."""
    photo_file_id = update.message.photo[-1].file_id
    sender_name = update.message.from_user.first_name
    sender_id = str(update.message.from_user.id)
    
    # --- Update Stats ---
    stats = load_stats()
    
    if sender_id not in stats:
        stats[sender_id] = {"name": sender_name, "count": 0}
        
    stats[sender_id]["count"] += 1
    stats[sender_id]["name"] = sender_name 
    
    save_stats(stats)
    current_count = stats[sender_id]["count"]
    
    # --- Forward to Admin ---
    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=photo_file_id,
        caption=f"📸 New feedback received!\nFrom: {sender_name} (ID: {sender_id})\n📊 Total sent by this user: {current_count}"
    )
    
    # --- Reply to User ---
    await update.message.reply_text("Thank you for your feedback! Your image has been received.\n You can send new feedback after this message.")
    print(f"Forwarded image #{current_count} from {sender_name}.")

async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Allows the admin to send a message back to the user."""
    if str(update.message.from_user.id) != str(ADMIN_CHAT_ID):
        return 
    
    if len(context.args) < 2:
        await update.message.reply_text("⚠️ Usage: /reply <user_id> <your message>")
        return
    
    target_user_id = context.args[0]
    admin_message = " ".join(context.args[1:])
    
    try:
        await context.bot.send_message(
            chat_id=target_user_id, 
            text=f"👨‍💻 Message from Admin:\n\n{admin_message}"
        )
        await update.message.reply_text(f"✅ Message sent to {target_user_id}!")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send message. Error: {e}")

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows the admin a leaderboard of who sent the most feedback."""
    if str(update.message.from_user.id) != str(ADMIN_CHAT_ID):
        return
        
    stats = load_stats()
    
    if not stats:
        await update.message.reply_text("📉 No feedback received yet or stats were reset.")
        return
        
    sorted_stats = sorted(stats.items(), key=lambda item: item[1]['count'], reverse=True)
    
    message = "📊 **Feedback Leaderboard**\n\n"
    for user_id, data in sorted_stats:
        message += f"👤 {data['name']} (ID: {user_id}): {data['count']} images\n"
        
    await update.message.reply_text(message)

async def reset_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clears all tracking data and resets the leaderboard to zero."""
    if str(update.message.from_user.id) != str(ADMIN_CHAT_ID):
        return
    
    # Overwrite the stats file with an empty dictionary
    save_stats({})
    
    await update.message.reply_text("🔄 The leaderboard has been completely reset. All user counts are back to zero.")
    print("Leaderboard reset by admin.")

def main():
    """Starts the bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CommandHandler("reply", reply_to_user))
    application.add_handler(CommandHandler("stats", show_stats))
    
    # New reset command handler
    application.add_handler(CommandHandler("reset", reset_stats)) 

    print("Bot is running... Waiting for feedback images. Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == '__main__':
    main()
