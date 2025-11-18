import os
import logging
# 🚨 FIX: Added KeyboardButtonRequestUsers and KeyboardButtonRequestChat to the import list
from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, 
    InlineKeyboardButton, InlineKeyboardMarkup, ChatAdministratorRights,
    KeyboardButtonRequestChat, KeyboardButtonRequestUsers 
)
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
MAIN_CHANNEL_ID = "@zerodevbro"
FORCE_SUB_IMAGE_URL = "https://envs.sh/xCy.jpg"
CHANNEL_LINK = UPDATE_CHANNEL
# -------------------------------

# --- Performance Optimization: Create Keyboard as a Global Constant ---

DEFAULT_ADMIN_RIGHTS = ChatAdministratorRights(
    is_anonymous=False, can_manage_chat=True, can_delete_messages=True, can_manage_video_chats=True, 
    can_restrict_members=True, can_promote_members=True, can_change_info=True, can_invite_users=True, 
    can_post_messages=True, can_edit_messages=True, can_pin_messages=True, can_post_stories=True, 
    can_edit_stories=True, can_delete_stories=True, can_manage_topics=True
)

# Define the keyboard layout once (No change needed here, the fix was in the import)
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

MAIN_KEYBOARD = ReplyKeyboardMarkup(KEYBOARD_LAYOUT, resize_keyboard=True)

# ------------------- FORCE SUB HELPER FUNCTIONS ----------------------

async def check_subscription(user_id, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Checks if the user is a member of the required channel."""
    try:
        member = await context.bot.get_chat_member(MAIN_CHANNEL_ID, user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except TelegramError as e:
        logger.error(f"Force Sub Error (Check Subscription): {e}")
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
        await message_object.reply_photo(
            photo=FORCE_SUB_IMAGE_URL,
            caption=message_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML,
            reply_to_message_id=message_object.message_id
        )
        
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

Using this bot, you can get the numerical ID of users.

<b>Developer:</b> {DEVELOPER}

📚 <b>Help:</b> /help

🔔 <b>Update Channel:</b> <a href="{UPDATE_CHANNEL}">Click Here</a>
👥 <b>Support Group:</b> <a href="{SUPPORT_GROUP}">Click Here</a>

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
        await message.reply_html(response, reply_markup=MAIN_KEYBOARD)
    except Exception as e:
        logger.error(f"Error in get_id command: {e}")

async def handle_user_shared(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when user shares users (from keyboard buttons)"""
    message = update.message
    user = update.effective_user
    
    if not await check_subscription(user.id, context):
        await send_force_sub_message(update, context, update.message)
        return
        
    if not message.users_shared or not message.users_shared.users:
        return
    
    shared_users = message.users_shared.users
    
    if len(shared_users) == 1:
        shared_user = shared_users[0]
        user_id = shared_user.user_id  
        
        try:
            chat = await context.bot.get_chat(user_id)
            
            response = f"""
<b>👤 User Information:</b>

<b>User ID:</b> <code>{chat.id}</code>
<b>First Name:</b> {chat.first_name}
<b>Last Name:</b> {chat.last_name or 'None'}
<b>Username:</b> @{chat.username if chat.username else 'None'}
<b>Type:</b> {chat.type}

<i>Shared by: {user.first_name} (<code>{user.id}</code>)</i>

<b>Developer:</b> {DEVELOPER}
"""
        except Exception as e:
            logger.warning(f"Could not get_chat for user {user_id}: {e}")
            response = f"""
<b>👤 User Information:</b>

<b>User ID:</b> <code>{user_id}</code>

<i>Shared by: {user.first_name} (<code>{user.id}</code>)</i>

<b>Developer:</b> {DEVELOPER}
"""
    else:
        user_list = "\n".join([f"• <code>{u.user_id}</code>" for u in shared_users])
        response = f"""
<b>👥 Multiple Users Shared:</b>

{user_list}

<i>Shared by: {user.first_name} (<code>{user.id}</code>)</i>

<b>Developer:</b> {DEVELOPER}
"""
    
    try:
        await message.reply_html(response, reply_markup=MAIN_KEYBOARD)
    except Exception as e:
        logger.error(f"Error handling user shared: {e}")

async def handle_chat_shared(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when user shares a chat (from keyboard buttons)"""
    message = update.message
    user = update.effective_user
    
    if not await check_subscription(user.id, context):
        await send_force_sub_message(update, context, update.message)
        return
    
    if not message.chat_shared:
        return
    
    chat_shared = message.chat_shared
    chat_id = chat_shared.chat_id 
    
    try:
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
        logger.warning(f"Could not get_chat for chat {chat_id}: {e}")
        response = f"""
<b>💬 Chat Information:</b>

<b>Chat ID:</b> <code>{chat_id}</code>

<i>Shared by: {user.first_name} (<code>{user.id}</code>)</i>

<b>Developer:</b> {DEVELOPER}
"""
    
    try:
        await message.reply_html(response, reply_markup=MAIN_KEYBOARD)
    except Exception as e:
        logger.error(f"Error handling chat shared: {e}")

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle forwarded messages"""
    
    message = update.message
    user = update.effective_user
    
    if not await check_subscription(user.id, context):
        await send_force_sub_message(update, context, update.message)
        return
    
    try:
        if message.forward_from:
            forward_user = message.forward_from
            response = f"""
<b>✉️ Forwarded Message Info (User):</b>

<b>Sender ID:</b> <code>{forward_user.id}</code>
<b>First Name:</b> {forward_user.first_name}
<b>Last Name:</b> {forward_user.last_name or 'None'}
<b>Username:</b> @{forward_user.username if forward_user.username else 'None'}
<b>Is Bot:</b> {'Yes ✅' if forward_user.is_bot else 'No ❌'}
<b>Is Premium:</b> {'Yes ⭐' if forward_user.is_premium else 'No'}

<i>Forwarded by: {user.first_name}</i>

<b>Developer:</b> {DEVELOPER}
"""
            await message.reply_html(response, reply_markup=MAIN_KEYBOARD)
            
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
<b>{emoji} {type_name} Information (Forwarded):</b>

<b>Chat ID:</b> <code>{chat.id}</code>
<b>Title:</b> {chat.title}
<b>Username:</b> @{chat.username if chat.username else 'None'}
<b>Type:</b> {type_name}

<i>Forwarded by: {user.first_name}</i>

<b>Developer:</b> {DEVELOPER}
"""
            await message.reply_html(response, reply_markup=MAIN_KEYBOARD)
        
        elif message.forward_sender_name:
            response = f"""
<b>🔒 Privacy Protected User</b>

<b>Name:</b> {message.forward_sender_name}
<b>User ID:</b> <i>Hidden (User has privacy settings enabled)</i>

<i>This user has enabled forward privacy settings, so their ID cannot be retrieved.</i>

<i>Forwarded by: {user.first_name}</i>

<b>Developer:</b> {DEVELOPER}
"""
            await message.reply_html(response, reply_markup=MAIN_KEYBOARD)
    except Exception as e:
        logger.error(f"Error handling forwarded message: {e}")

async def handle_shared_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle shared contacts"""
    
    message = update.message
    user = update.effective_user
    
    if not await check_subscription(user.id, context):
        await send_force_sub_message(update, context, update.message)
        return
    
    contact = message.contact
    
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
        await message.reply_html(response, reply_markup=MAIN_KEYBOARD)
    except Exception as e:
        logger.error(f"Error handling shared contact: {e}")

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle other text messages"""
    message = update.message
    user = update.effective_user
    
    if not await check_subscription(user.id, context):
        await send_force_sub_message(update, context, update.message)
        return
    
    if message.chat.type == "private":
        response = f"""
<b>👋 Hi {user.first_name}!</b>

<b>Your ID:</b> <code>{user.id}</code>

<i>💡 Use the keyboard buttons below to select users or chats!</i>

Use /start to see the welcome message.

<b>Developer:</b> {DEVELOPER}
"""
        
        try:
            await message.reply_html(response, reply_markup=MAIN_KEYBOARD)
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
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
        try:
            await message.reply_html(response)
        except Exception as e:
            logger.error(f"Error handling group message: {e}")

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from the 'Try Again' button."""
    query = update.callback_query
    user = query.from_user
    
    await query.answer()
    
    if query.data == 'check_sub':
        if await check_subscription(user.id, context):
            try:
                await query.edit_message_caption(
                    caption="✅ **Subscription Confirmed!** You now have full access. Select an option below.",
                    parse_mode=ParseMode.HTML
                )
                
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="Welcome back! Select an option below.",
                    reply_markup=MAIN_KEYBOARD
                )
                
            except Exception:
                 await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="✅ Subscription Confirmed! Select an option below.",
                    reply_markup=MAIN_KEYBOARD
                )
        else:
            await query.edit_message_caption(
                caption="❌ **Subscription Failed.** Please ensure you have joined the channel and try again.",
                parse_mode=ParseMode.HTML,
                reply_markup=query.message.reply_markup
            )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f'Update {update} caused error {context.error}', exc_info=context.error)

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
        
        # Handle user shared (from keyboard)
        application.add_handler(MessageHandler(filters.StatusUpdate.USERS_SHARED, handle_user_shared))
        
        # Handle chat shared (from keyboard)
        application.add_handler(MessageHandler(filters.StatusUpdate.CHAT_SHARED, handle_chat_shared))
        
        # Handle contacts
        application.add_handler(MessageHandler(filters.CONTACT, handle_shared_contact))
        
        # Handle forwarded messages
        application.add_handler(MessageHandler(filters.FORWARDED & ~filters.COMMAND, handle_forwarded_message))
        
        # Handle any other text messages
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
        
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
    main()
