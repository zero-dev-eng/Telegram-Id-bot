import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, KeyboardButtonRequestChat, KeyboardButtonRequestUsers, ChatAdministratorRights
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode, ChatType
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

def get_main_keyboard():
    """Create the main keyboard with chat/user selection buttons"""
    # Create administrator rights object for "My" buttons
    admin_rights = ChatAdministratorRights(
        can_manage_chat=True,
        can_post_messages=True,
        can_edit_messages=True,
        can_delete_messages=True,
        can_manage_video_chats=True,
        can_restrict_members=True,
        can_promote_members=True,
        can_change_info=True,
        can_invite_users=True,
        can_pin_messages=True
    )
    
    keyboard = [
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
            KeyboardButton("👥 My Group", request_chat=KeyboardButtonRequestChat(request_id=7, chat_is_channel=False, user_administrator_rights=admin_rights)),
            KeyboardButton("📢 My Channel", request_chat=KeyboardButtonRequestChat(request_id=8, chat_is_channel=True, user_administrator_rights=admin_rights)),
            KeyboardButton("💬 My Forum", request_chat=KeyboardButtonRequestChat(request_id=9, chat_is_channel=False, chat_is_forum=True, user_administrator_rights=admin_rights))
        ]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message when /start is issued"""
    
    user = update.effective_user
    user_id = user.id
    
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
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_keyboard(),
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    
    help_text = f"""
<b>🔍 How to use this bot:</b>

<b>1️⃣ Get User ID:</b>
• Click "👤 User" button and select any user
• Click "⭐ Premium" button to select premium users
• Click "🤖 Bot" button to select bots

<b>2️⃣ Get Chat ID:</b>
• Click "👥 Group" button and select any group
• Click "📢 Channel" button and select any channel
• Click "💬 Forum" button and select any forum

<b>3️⃣ Get Your Chats:</b>
• Click "👥 My Group" for groups where you're admin
• Click "📢 My Channel" for channels where you're admin
• Click "💬 My Forum" for forums where you're admin

<b>4️⃣ Commands:</b>
/start - Start bot & show main menu
/help - Show this help
/id - Get your ID

<b>💡 Tips:</b>
✅ Use the keyboard buttons to select chats
✅ You can also forward messages to get IDs
✅ Share contacts to get user IDs

<b>Developer:</b> {DEVELOPER}
<b>Update Channel:</b> {UPDATE_CHANNEL}
<b>Support Group:</b> {SUPPORT_GROUP}
"""
    
    try:
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_main_keyboard(),
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Error in help command: {e}")

async def get_id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get ID of user or replied message"""
    
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

<i>💡 Tip: Use the keyboard buttons to select users and chats!</i>

<b>Developer:</b> {DEVELOPER}
"""
    
    try:
        await message.reply_text(response, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Error in get_id command: {e}")

async def handle_user_shared(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when user shares users"""
    message = update.message
    user = update.effective_user
    
    if not message.users_shared:
        return
    
    users_shared = message.users_shared
    user_ids = users_shared.user_ids
    
    if len(user_ids) == 1:
        user_id = user_ids[0]
        try:
            # Try to get user info
            shared_user = await context.bot.get_chat(user_id)
            
            response = f"""
<b>👤 User Information:</b>

<b>User ID:</b> <code>{shared_user.id}</code>
<b>First Name:</b> {shared_user.first_name}
<b>Last Name:</b> {shared_user.last_name or 'None'}
<b>Username:</b> @{shared_user.username if shared_user.username else 'None'}
<b>Type:</b> {shared_user.type}

<i>Shared by: {user.first_name} (<code>{user.id}</code>)</i>

<b>Developer:</b> {DEVELOPER}
"""
        except Exception as e:
            # If can't get full info, just show ID
            response = f"""
<b>👤 User Information:</b>

<b>User ID:</b> <code>{user_id}</code>

<i>Shared by: {user.first_name} (<code>{user.id}</code>)</i>

<b>Developer:</b> {DEVELOPER}
"""
    else:
        # Multiple users shared
        user_list = "\n".join([f"• <code>{uid}</code>" for uid in user_ids])
        response = f"""
<b>👥 Multiple Users Shared:</b>

{user_list}

<i>Shared by: {user.first_name} (<code>{user.id}</code>)</i>

<b>Developer:</b> {DEVELOPER}
"""
    
    try:
        await message.reply_text(response, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Error handling user shared: {e}")

async def handle_chat_shared(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when user shares a chat"""
    message = update.message
    user = update.effective_user
    
    if not message.chat_shared:
        return
    
    chat_shared = message.chat_shared
    chat_id = chat_shared.chat_id
    
    try:
        # Try to get chat info
        shared_chat = await context.bot.get_chat(chat_id)
        
        chat_type = shared_chat.type
        if chat_type == ChatType.CHANNEL:
            emoji = "📢"
            type_name = "Channel"
        elif chat_type == ChatType.SUPERGROUP:
            emoji = "👥"
            type_name = "Supergroup"
        elif chat_type == ChatType.GROUP:
            emoji = "👥"
            type_name = "Group"
        else:
            emoji = "💬"
            type_name = "Chat"
        
        response = f"""
<b>{emoji} {type_name} Information:</b>

<b>Chat ID:</b> <code>{shared_chat.id}</code>
<b>Title:</b> {shared_chat.title}
<b>Username:</b> @{shared_chat.username if shared_chat.username else 'None'}
<b>Type:</b> {type_name}

<i>Shared by: {user.first_name} (<code>{user.id}</code>)</i>

<b>Developer:</b> {DEVELOPER}
"""
    except Exception as e:
        # If can't get full info, just show ID
        response = f"""
<b>💬 Chat Information:</b>

<b>Chat ID:</b> <code>{chat_id}</code>

<i>Shared by: {user.first_name} (<code>{user.id}</code>)</i>

<b>Developer:</b> {DEVELOPER}
"""
    
    try:
        await message.reply_text(response, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Error handling chat shared: {e}")

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle forwarded messages"""
    
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
            await message.reply_text(response, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())
            
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
            await message.reply_text(response, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())
        
        elif message.forward_sender_name:
            response = f"""
<b>🔒 Privacy Protected User</b>

<b>Name:</b> {message.forward_sender_name}
<b>User ID:</b> <i>Hidden (User has privacy settings enabled)</i>

<i>This user has enabled privacy settings, so their ID cannot be retrieved.</i>

<i>Forwarded by: {user.first_name}</i>

<b>Developer:</b> {DEVELOPER}
"""
            await message.reply_text(response, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Error handling forwarded message: {e}")

async def handle_shared_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shared contacts"""
    
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
        await message.reply_text(response, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())
    except Exception as e:
        logger.error(f"Error handling shared contact: {e}")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    message = update.message
    user = update.effective_user
    
    if message.chat.type == "private":
        response = f"""
<b>👋 Hi {user.first_name}!</b>

<b>Your ID:</b> <code>{user.id}</code>

<i>💡 Use the keyboard buttons below to select users or chats!</i>

Use /start to see the welcome message.

<b>Developer:</b> {DEVELOPER}
"""
        
        try:
            await message.reply_text(response, parse_mode=ParseMode.HTML, reply_markup=get_main_keyboard())
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
    else:
        # In group chat
        chat = message.chat
        response = f"""
<b>📊 Chat Information:</b>

<b>Chat ID:</b> <code>{chat.id}</code>
<b>Chat Title:</b> {chat.title}
<b>Chat Type:</b> {chat.type}
<b>Your ID:</b> <code>{user.id}</code>

<b>Developer:</b> {DEVELOPER}
"""
        try:
            await message.reply_text(response, parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Error handling group message: {e}")

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
        
        # Command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("id", get_id_command))
        application.add_handler(CommandHandler("info", get_id_command))
        
        # Handle user shared
        application.add_handler(MessageHandler(filters.StatusUpdate.USERS_SHARED, handle_user_shared))
        
        # Handle chat shared
        application.add_handler(MessageHandler(filters.StatusUpdate.CHAT_SHARED, handle_chat_shared))
        
        # Handle contacts
        application.add_handler(MessageHandler(filters.CONTACT, handle_shared_contact))
        
        # Handle forwarded messages
        application.add_handler(MessageHandler(filters.FORWARDED & ~filters.COMMAND, handle_forwarded_message))
        
        # Handle text messages
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        
        # Error handler
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
