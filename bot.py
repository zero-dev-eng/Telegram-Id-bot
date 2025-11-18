import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, ChatAdministratorRights
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode, ChatType
from telegram.error import TelegramError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("❌ Error: BOT_TOKEN not found in environment variables!")
    exit()
    
DEVELOPER = "@Zeroboy216"
UPDATE_CHANNEL = "https://t.me/zerodevbro"
SUPPORT_GROUP = "https://t.me/zerodevsupport1"

# --- FORCE SUB CONFIGURATION ---
# The bot MUST be an administrator in this channel for the check to work.
MAIN_CHANNEL_ID = "@zerodevbro"
FORCE_SUB_IMAGE_URL = "https://envs.sh/xCy.jpg"
CHANNEL_LINK = UPDATE_CHANNEL
# -------------------------------

# --- Performance Optimization: Create Keyboard as a Global Constant ---

# Define the admin rights needed for "My" buttons once
DEFAULT_ADMIN_RIGHTS = ChatAdministratorRights(
    is_anonymous=False, can_manage_chat=True, can_delete_messages=True, can_manage_video_chats=True, 
    can_restrict_members=True, can_promote_members=True, can_change_info=True, can_invite_users=True, 
    can_post_messages=True, can_edit_messages=True, can_pin_messages=True, can_post_stories=True, 
    can_edit_stories=True, can_delete_stories=True, can_manage_topics=True
)

# Define the keyboard layout once
KEYBOARD_LAYOUT = [
    [
        KeyboardButton("👤 User", request_users=KeyboardButtonRequestUsers(request_id=1, user_is_bot=False)),
        KeyboardButton("⭐ Premium", request_users=KeyboardButtonRequestUsers(request_id=2, user_is_bot=False, user_is_premium=True)),
        KeyboardButton("🤖 Bot", request_users=KeyboardButtonRequestUsers(request_id=3, user_is_bot=True))
    ],
    [
        KeyboardButton("👥 Group", request_chat=KeyboardButtonRequestChat(request_id=4, chat_is_channel=False)),
        KeyboardButton("📢 Channel", request_chat=KeyboardButtonRequestChat(request_id=5, chat_is_channel=True)),
        KeyboardButton("💬 Forum", request_chat=KeyboardButtonRequestChat(request_id=6, chat_is_channel=False, chat_is_forum=True))
    ],
    [
        KeyboardButton("👥 My Group", request_chat=KeyboardButtonRequestChat(request_id=7, chat_is_channel=False, user_administrator_rights=DEFAULT_ADMIN_RIGHTS)),
        KeyboardButton("📢 My Channel", request_chat=KeyboardButtonRequestChat(request_id=8, chat_is_channel=True, user_administrator_rights=DEFAULT_ADMIN_RIGHTS)),
        KeyboardButton("💬 My Forum", request_chat=KeyboardButtonRequestChat(request_id=9, chat_is_channel=False, chat_is_forum=True, user_administrator_rights=DEFAULT_ADMIN_RIGHTS))
    ]
]

# Create the final ReplyKeyboardMarkup object as a constant
MAIN_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD_LAYOUT, resize_keyboard=True)

# ------------------- FORCE SUB HELPER FUNCTIONS ----------------------

async def check_subscription(user_id, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Checks if the user is a member of the required channel."""
    try:
        member = await context.bot.get_chat_member(MAIN_CHANNEL_ID, user_id)
        # Check if the user is subscribed (member, administrator, or creator)
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except TelegramError as e:
        logger.error(f"Force Sub Error (Check Subscription): {e}")
        # If the bot can't check, assume subscribed to prevent lockouts
        return True 

async def send_force_sub_message(update: Update, context: ContextTypes.DEFAULT_TYPE, message_object):
    """Sends the force subscribe message with image and inline keyboard."""
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔔 Join Update Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("🔄 Try Again", callback_data='check_sub')]
    ])
    
    message_text = f"""
<b>🛑 Access Denied!</b>

You must join our Update Channel {MAIN_CHANNEL_ID} to use this bot.
Please click the button below and then click **Try Again**.

<b>Developer:</b> {DEVELOPER}
"""
    
    try:
        if message_object.photo:
            # If replying to a message with a photo, we can use reply_photo
            await message_object.reply_photo(
                photo=FORCE_SUB_IMAGE_URL,
                caption=message_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
                reply_to_message_id=message_object.message_id
            )
        else:
            # If not replying to a photo, send a regular message or upload the image
             await message_object.reply_text(
                message_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML,
                reply_to_message_id=message_object.message_id
            )
        
        # Optional: Remove the main reply keyboard to clean up the interface
        await context.bot.send_message(
            chat_id=message_object.chat_id,
            text="Tap a command or button when ready:",
            reply_markup=ReplyKeyboardRemove(),
            resize_keyboard=True
        )
        
    except Exception as e:
        logger.error(f"Error sending force sub message: {e}")
        await message_object.reply_text(
            f"Please join {MAIN_CHANNEL_ID} and try again."
        )

# ------------------- HANDLERS WITH SUB CHECK -------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued"""
    user = update.effective_user
    
    if not await check_subscription(user.id, context):
        await send_force_sub_message(update, context, update.message)
        return
        
    user_id = user.id
    welcome_message = f"""
<b>Hi Welcome To @{context.bot.username} 👋</b>
... [Welcome message content truncated for brevity] ...
<b>Your ID:</b> <code>{user_id}</code>

<i>You can check any <b>User | Chat | IDBot</b> just forward or share any chat with me!</i>
"""
    
    try:
        await update.message.reply_html(
            welcome_message,
            reply_markup=MAIN_KEYBOARD,
            disable_web_page_preview=True,
            reply_to_message_id=update.message.message_id
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    user = update.effective_user
    if not await check_subscription(user.id, context):
        await send_force_sub_message(update, context, update.message)
        return
        
    help_text = f"""
<b>🔍 How to use this bot:</b>
... [Help message content truncated for brevity] ...
<b>Developer:</b> {DEVELOPER}
"""
    
    try:
        await update.message.reply_html(
            help_text,
            reply_markup=MAIN_KEYBOARD,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in help command: {e}")

async def get_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get ID of user or replied message"""
    message = update.message
    user = update.effective_user
    
    if not await check_subscription(user.id, context):
        await send_force_sub_message(update, context, update.message)
        return
    
    # ... [Rest of get_id_command logic] ...
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        response = f"""
<b>👤 User Information:</b>
<b>User ID:</b> <code>{target_user.id}</code>
...
"""
    else:
        response = f"""
<b>👤 Your Information:</b>
<b>Your ID:</b> <code>{user.id}</code>
...
"""
    
    try:
        await message.reply_html(response, reply_markup=MAIN_KEYBOARD)
    except Exception as e:
        logger.error(f"Error in get_id command: {e}")

# ... (Other handlers like handle_user_shared, handle_chat_shared, etc., should also have the subscription check added if they are command-driven) ...

# ---------------------- CALLBACK HANDLER -----------------------------

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from the 'Try Again' button."""
    query = update.callback_query
    user = query.from_user
    
    # Always answer the query to dismiss the loading animation
    await query.answer()
    
    if query.data == 'check_sub':
        if await check_subscription(user.id, context):
            # User is now subscribed, delete the message and show main menu
            try:
                await query.edit_message_caption(
                    caption="✅ **Subscription Confirmed!** You now have full access.",
                    parse_mode=ParseMode.HTML
                )
                
                # Send the main keyboard after success
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="Welcome back! Select an option below.",
                    reply_markup=MAIN_KEYBOARD
                )
                
            except Exception:
                # Fallback if message editing fails
                 await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="✅ Subscription Confirmed! Select an option below.",
                    reply_markup=MAIN_KEYBOARD
                )
        else:
            # User is still not subscribed, alert them
            await query.edit_message_caption(
                caption="❌ **Subscription Failed.** Please ensure you have joined the channel and try again.",
                parse_mode=ParseMode.HTML,
                reply_markup=query.message.reply_markup
            )

# ------------------------- MAIN FUNCTION -----------------------------

def main():
    """Start the bot"""
    logger.info("🤖 Starting UserInfo Bot...")
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("id", get_id_command))
        application.add_handler(CommandHandler("info", get_id_command))
        
        # Callback query handler for Force Sub check
        application.add_handler(CallbackQueryHandler(handle_callback_query))
        
        # ... (Other handlers like MessageHandler, etc.) ...
        
        # Error handler
        application.add_error_handler(error_handler)
        
        logger.info("✅ Bot started successfully! Polling for updates...")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}", exc_info=True)

if __name__ == "__main__":
    # Ensure all other functions (handle_user_shared, handle_chat_shared, etc.) 
    # from the previous working script are present, or add the subscription check 
    # to them as well if they handle commands.
    main()
