import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from telegram.constants import ParseMode
from telegram.error import BadRequest, TelegramError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEVELOPER = "@Zeroboy216"
UPDATE_CHANNEL = "https://t.me/zerodevbro"
SUPPORT_GROUP = "https://t.me/zerodevsupport1"
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", "@zerodevbro")

async def check_user_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is subscribed to the required channel"""
    try:
        channel_username = FORCE_SUB_CHANNEL.lstrip('@')
        member = await context.bot.get_chat_member(chat_id=f"@{channel_username}", user_id=user_id)
        
        if member.status in ["member", "administrator", "creator"]:
            return True
        else:
            return False
    except BadRequest as e:
        logger.warning(f"BadRequest while checking subscription: {e}")
        return True
    except TelegramError as e:
        logger.error(f"TelegramError while checking subscription: {e}")
        return True
    except Exception as e:
        logger.error(f"Unexpected error checking subscription: {e}")
        return True

async def force_subscribe_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check subscription and send force subscribe message if needed"""
    user = update.effective_user
    
    is_subscribed = await check_user_subscription(user.id, context)
    
    if not is_subscribed:
        keyboard = [
            [InlineKeyboardButton("📢 Join Update Channel", url=UPDATE_CHANNEL)],
            [InlineKeyboardButton("👥 Join Support Group", url=SUPPORT_GROUP)],
            [InlineKeyboardButton("✅ I Joined, Check Again", callback_data="check_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        access_denied_msg = f"""
<b>⛔ Access Denied</b>

You need to join our channel before using this bot.
Please click the button below to join and then check again. 🙏🏻

<b>Update Channel:</b> {UPDATE_CHANNEL}
<b>Support Group:</b> {SUPPORT_GROUP}

<b>Developer:</b> {DEVELOPER}
"""
        
        try:
            if update.message:
                await update.message.reply_text(
                    access_denied_msg,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
            elif update.callback_query:
                await update.callback_query.message.edit_text(
                    access_denied_msg,
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup,
                    disable_web_page_preview=True
                )
        except Exception as e:
            logger.error(f"Error sending force subscribe message: {e}")
        
        return False
    
    return True

async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle check subscription button click"""
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    is_subscribed = await check_user_subscription(user.id, context)
    
    if is_subscribed:
        await query.answer("✅ Verified! You can now use the bot.", show_alert=True)
        await start(update, context, from_callback=True)
    else:
        await query.answer("❌ You haven't joined yet! Please join first.", show_alert=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback=False):
    """Send welcome message when /start is issued"""
    
    if not from_callback:
        if not await force_subscribe_check(update, context):
            return
    
    user = update.effective_user
    user_id = user.id
    
    keyboard = [
        [
            InlineKeyboardButton("👤 User", callback_data="help_user"),
            InlineKeyboardButton("⭐ Premium", callback_data="help_premium"),
            InlineKeyboardButton("🤖 Bot", callback_data="help_bot")
        ],
        [
            InlineKeyboardButton("👥 Group", callback_data="help_group"),
            InlineKeyboardButton("📢 Channel", callback_data="help_channel"),
            InlineKeyboardButton("💬 Forum", callback_data="help_forum")
        ],
        [
            InlineKeyboardButton("👥 My Group", callback_data="help_mygroup"),
            InlineKeyboardButton("📢 My Channel", callback_data="help_mychannel"),
            InlineKeyboardButton("💬 My Forum", callback_data="help_myforum")
        ],
        [
            InlineKeyboardButton("📢 Update Channel", url=UPDATE_CHANNEL),
            InlineKeyboardButton("👥 Support Group", url=SUPPORT_GROUP)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_message = f"""
<b>Hi Welcome To @{context.bot.username} 👋</b>

Using this bot, you can get the numerical ID of users.

<b>Developer:</b> {DEVELOPER}

📚 <b>Help:</b> /help

🔔 <b>Update Channel:</b> <a href="{UPDATE_CHANNEL}">Click Here</a>
👥 <b>Support Group:</b> <a href="{SUPPORT_GROUP}">Click Here</a>

<b>Your ID:</b> <code>{user_id}</code>

<i>You can check any <b>User | Chat | IDBot</b> just forward or share any chat with me!</i>
"""
    
    try:
        if from_callback:
            await update.callback_query.message.edit_text(
                welcome_message,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        else:
            await update.message.reply_text(
                welcome_message,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"Error in start command: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    
    if not await force_subscribe_check(update, context):
        return
    
    help_text = f"""
<b>🔍 How to use this bot:</b>

<b>1️⃣ Get User ID:</b>
• Forward any message from user
• Share contact
• Reply to user's message with /id

<b>2️⃣ Get Chat ID:</b>
• Forward any message from group/channel
• Share group/channel with bot
• Add bot to group and send /id

<b>3️⃣ Get Your Info:</b>
• Just send /start or /id
• Bot will show your ID

<b>4️⃣ Commands:</b>
/start - Start bot & get your ID
/help - Show this help
/id - Get your ID or replied user ID
/info - Get detailed info

<b>📝 Examples:</b>
✅ Forward message → Get sender's ID
✅ Share contact → Get contact's ID
✅ Share chat → Get chat ID
✅ Reply + /id → Get replied user's ID

<b>💡 Tip:</b> You can forward/share anything with me!

<b>Developer:</b> {DEVELOPER}
<b>Update Channel:</b> {UPDATE_CHANNEL}
<b>Support Group:</b> {SUPPORT_GROUP}
"""
    
    keyboard = [
        [
            InlineKeyboardButton("📢 Update Channel", url=UPDATE_CHANNEL),
            InlineKeyboardButton("👥 Support Group", url=SUPPORT_GROUP)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in help command: {e}")

async def get_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get ID of user or replied message"""
    
    if not await force_subscribe_check(update, context):
        return
    
    message = update.message
    user = update.effective_user
    
    if message.reply_to_message:
        target_user = message.reply_to_message.from_user
        response = f"""
<b>👤 User Information:</b>

<b>User ID:</b> <code>{target_user.id}</code>
<b>First Name:</b> {target_user.first_name}
<b>Last Name:</b> {target_user.last_name or 'None'}
<b>Username:</b> @{target_user.username if target_user.username else 'None'}
<b>Is Bot:</b> {'Yes ✅' if target_user.is_bot else 'No ❌'}
<b>Is Premium:</b> {'Yes ⭐' if target_user.is_premium else 'No'}

<i>Reply sent by:</i> {user.first_name} (<code>{user.id}</code>)
"""
    else:
        response = f"""
<b>👤 Your Information:</b>

<b>Your ID:</b> <code>{user.id}</code>
<b>First Name:</b> {user.first_name}
<b>Last Name:</b> {user.last_name or 'None'}
<b>Username:</b> @{user.username if user.username else 'None'}
<b>Is Bot:</b> {'Yes ✅' if user.is_bot else 'No ❌'}
<b>Is Premium:</b> {'Yes ⭐' if user.is_premium else 'No'}
<b>Language:</b> {user.language_code or 'Unknown'}

<i>💡 Tip: Reply to someone's message with /id to get their ID!</i>

<b>Developer:</b> {DEVELOPER}
"""
    
    try:
        await message.reply_text(response, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error in get_id command: {e}")

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle forwarded messages to extract IDs"""
    
    if not await force_subscribe_check(update, context):
        return
    
    message = update.message
    user = update.effective_user
    
    try:
        if message.forward_from:
            forward_user = message.forward_from
            response = f"""
<b>✉️ Forwarded Message Info:</b>

<b>Sender ID:</b> <code>{forward_user.id}</code>
<b>First Name:</b> {forward_user.first_name}
<b>Last Name:</b> {forward_user.last_name or 'None'}
<b>Username:</b> @{forward_user.username if forward_user.username else 'None'}
<b>Is Bot:</b> {'Yes ✅' if forward_user.is_bot else 'No ❌'}
<b>Is Premium:</b> {'Yes ⭐' if forward_user.is_premium else 'No'}

<i>Forwarded by: {user.first_name}</i>

<b>Developer:</b> {DEVELOPER}
"""
            await message.reply_text(response, parse_mode=ParseMode.HTML)
            
        elif message.forward_from_chat:
            chat = message.forward_from_chat
            chat_type = chat.type
            
            if chat_type == "channel":
                emoji = "📢"
                type_name = "Channel"
            elif chat_type == "supergroup":
                emoji = "👥"
                type_name = "Supergroup"
            elif chat_type == "group":
                emoji = "👥"
                type_name = "Group"
            else:
                emoji = "💬"
                type_name = "Chat"
            
            response = f"""
<b>{emoji} {type_name} Information:</b>

<b>Chat ID:</b> <code>{chat.id}</code>
<b>Title:</b> {chat.title}
<b>Username:</b> @{chat.username if chat.username else 'None'}
<b>Type:</b> {type_name}

<i>Forwarded by: {user.first_name}</i>

<b>Developer:</b> {DEVELOPER}
"""
            await message.reply_text(response, parse_mode=ParseMode.HTML)
        
        elif message.forward_sender_name:
            response = f"""
<b>🔒 Privacy Protected User</b>

<b>Name:</b> {message.forward_sender_name}
<b>User ID:</b> <i>Hidden (User has privacy settings enabled)</i>

<i>This user has enabled privacy settings, so their ID cannot be retrieved.</i>

<i>Forwarded by: {user.first_name}</i>

<b>Developer:</b> {DEVELOPER}
"""
            await message.reply_text(response, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error handling forwarded message: {e}")

async def handle_shared_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shared contacts"""
    
    if not await force_subscribe_check(update, context):
        return
    
    message = update.message
    contact = message.contact
    user = update.effective_user
    
    response = f"""
<b>📇 Contact Information:</b>

<b>User ID:</b> <code>{contact.user_id if contact.user_id else 'Not available'}</code>
<b>First Name:</b> {contact.first_name}
<b>Last Name:</b> {contact.last_name or 'None'}
<b>Phone:</b> {contact.phone_number}

<i>Shared by: {user.first_name} (<code>{user.id}</code>)</i>

<b>Developer:</b> {DEVELOPER}
"""
    
    try:
        await message.reply_text(response, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error handling shared contact: {e}")

async def handle_chat_shared(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when user shares a chat with bot"""
    
    if not await force_subscribe_check(update, context):
        return
    
    message = update.message
    user = update.effective_user
    
    try:
        if hasattr(message, 'chat_shared') and message.chat_shared:
            chat_shared = message.chat_shared
            chat_id = chat_shared.chat_id
            
            response = f"""
<b>💬 Shared Chat Information:</b>

<b>Chat ID:</b> <code>{chat_id}</code>

<i>Shared by: {user.first_name} (<code>{user.id}</code>)</i>

<i>💡 Add this bot to the chat to get more details!</i>

<b>Developer:</b> {DEVELOPER}
"""
            await message.reply_text(response, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error handling shared chat: {e}")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages"""
    
    if not await force_subscribe_check(update, context):
        return
    
    message = update.message
    user = update.effective_user
    
    try:
        if message.chat.type == "private":
            response = f"""
<b>👋 Hi {user.first_name}!</b>

<b>Your ID:</b> <code>{user.id}</code>

<i>💡 Forward any message or share a chat with me to get IDs!</i>

Use /help for more information.

<b>Developer:</b> {DEVELOPER}
"""
            
            keyboard = [
                [
                    InlineKeyboardButton("📢 Update Channel", url=UPDATE_CHANNEL),
                    InlineKeyboardButton("👥 Support Group", url=SUPPORT_GROUP)
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await message.reply_text(response, parse_mode=ParseMode.HTML, reply_markup=reply_markup)
        else:
            chat = message.chat
            response = f"""
<b>📊 Chat Information:</b>

<b>Chat ID:</b> <code>{chat.id}</code>
<b>Chat Title:</b> {chat.title}
<b>Chat Type:</b> {chat.type}
<b>Your ID:</b> <code>{user.id}</code>

<b>Developer:</b> {DEVELOPER}
"""
            await message.reply_text(response, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error(f"Error handling text message: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f'Update {update} caused error {context.error}', exc_info=context.error)

def main():
    """Start the bot"""
    if not BOT_TOKEN:
        logger.error("❌ Error: BOT_TOKEN not found in environment variables!")
        return
    
    logger.info("🤖 Starting UserInfo Bot...")
    logger.info(f"👨‍💻 Developer: {DEVELOPER}")
    logger.info(f"📢 Update Channel: {UPDATE_CHANNEL}")
    logger.info(f"👥 Support Group: {SUPPORT_GROUP}")
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("id", get_id_command))
        application.add_handler(CommandHandler("info", get_id_command))
        
        application.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_subscription$"))
        application.add_handler(MessageHandler(filters.CONTACT, handle_shared_contact))
        application.add_handler(MessageHandler(filters.FORWARDED, handle_forwarded_message))
        application.add_handler(MessageHandler(filters.StatusUpdate.CHAT_SHARED, handle_chat_shared))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        
        application.add_error_handler(error_handler)
        
        logger.info("✅ Bot started successfully!")
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}", exc_info=True)

if __name__ == "__main__":
    main()
