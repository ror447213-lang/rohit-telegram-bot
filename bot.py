import telebot
import requests
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "8737098587:AAG4Co6DgYwrqEmZxogiTET2QMKyixO_wtU"
OWNER_ID = 7634132457

bot = telebot.TeleBot(TOKEN)

approved_users = set()

# ---------- MENU ----------

def menu(user_id):

    m = ReplyKeyboardMarkup(resize_keyboard=True)

    m.add(KeyboardButton("📧 Bind Info"))

    if user_id == OWNER_ID or user_id in approved_users:
        m.add(
            KeyboardButton("🔁 Change Bind"),
            KeyboardButton("❌ Unbind Email")
        )
        m.add(KeyboardButton("🚫 Cancel Bind"))

    if user_id == OWNER_ID:
        m.add(KeyboardButton("👑 Admin Panel"))

    return m


# ---------- START ----------

@bot.message_handler(commands=['start'])
def start(msg):

    bot.send_message(
        msg.chat.id,
        "🤖 RO4IT EMAIL MANAGER",
        reply_markup=menu(msg.from_user.id)
    )


# ---------- ACCESS CHECK ----------

def has_access(uid):

    if uid == OWNER_ID:
        return True

    if uid in approved_users:
        return True

    return False


# ---------- BIND INFO ----------

@bot.message_handler(func=lambda m: m.text == "📧 Bind Info")
def bindinfo(msg):

    bot.send_message(msg.chat.id,"Send Access Token")

    bot.register_next_step_handler(msg,process_bindinfo)


def process_bindinfo(msg):

    token = msg.text.strip()

    url = f"https://bind-cancel-c.vercel.app/info?access_token={token}"

    try:

        r = requests.get(url)
        data = r.json()

        current = data["data"]["current_email"] or "Not Linked"
        pending = data["data"]["pending_email"]
        confirm = data["data"]["countdown_human"]

        text = f"""
📧 Email Status

Current Email
{current}

Pending Email
{pending}

Confirm In
{confirm}
"""

        bot.send_message(msg.chat.id,text)

    except:

        bot.send_message(msg.chat.id,"❌ Invalid Token")


# ---------- CHANGE BIND ----------

@bot.message_handler(func=lambda m: m.text == "🔁 Change Bind")
def change_bind(msg):

    if not has_access(msg.from_user.id):

        bot.send_message(msg.chat.id,"❌ Admin permission required")
        return

    bot.send_message(msg.chat.id,"Access Token")

    bot.register_next_step_handler(msg,change_old_email)


def change_old_email(msg):

    token = msg.text

    bot.send_message(msg.chat.id,"Old Email")

    bot.register_next_step_handler(msg,send_old_otp,token)


def send_old_otp(msg,token):

    old_email = msg.text

    url = f"https://bind-cancel-c.vercel.app/send_otp?access_token={token}&email={old_email}"

    requests.get(url)

    bot.send_message(msg.chat.id,"Old Email OTP")

    bot.register_next_step_handler(msg,new_email_step,token,old_email)


def new_email_step(msg,token,old_email):

    old_otp = msg.text

    bot.send_message(msg.chat.id,"New Email")

    bot.register_next_step_handler(msg,send_new_otp,token,old_email,old_otp)


def send_new_otp(msg,token,old_email,old_otp):

    new_email = msg.text

    url = f"https://bind-cancel-c.vercel.app/send_otp?access_token={token}&email={new_email}"

    requests.get(url)

    bot.send_message(msg.chat.id,"New Email OTP")

    bot.register_next_step_handler(msg,final_change,token,old_email,old_otp,new_email)


def final_change(msg,token,old_email,old_otp,new_email):

    new_otp = msg.text

    url = f"https://bind-cancel-c.vercel.app/change?access_token={token}&old_email={old_email}&old_otp={old_otp}&new_email={new_email}&new_otp={new_otp}"

    r = requests.get(url)

    bot.send_message(msg.chat.id,r.text)


# ---------- UNBIND ----------

@bot.message_handler(func=lambda m: m.text == "❌ Unbind Email")
def unbind(msg):

    if not has_access(msg.from_user.id):

        bot.send_message(msg.chat.id,"❌ Admin permission required")
        return

    bot.send_message(msg.chat.id,"Access Token")

    bot.register_next_step_handler(msg,unbind_email)


def unbind_email(msg):

    token = msg.text

    bot.send_message(msg.chat.id,"Email")

    bot.register_next_step_handler(msg,unbind_otp,token)


def unbind_otp(msg,token):

    email = msg.text

    url = f"https://bind-cancel-c.vercel.app/send_otp?access_token={token}&email={email}"

    requests.get(url)

    bot.send_message(msg.chat.id,"OTP")

    bot.register_next_step_handler(msg,unbind_final,token,email)


def unbind_final(msg,token,email):

    otp = msg.text

    url = f"https://bind-src-by.vercel.app/unbind?access_token={token}&email={email}&otp={otp}"

    r = requests.get(url)

    bot.send_message(msg.chat.id,r.text)


# ---------- CANCEL BIND ----------

@bot.message_handler(func=lambda m: m.text == "🚫 Cancel Bind")
def cancel_bind(msg):

    if not has_access(msg.from_user.id):

        bot.send_message(msg.chat.id,"❌ Admin permission required")
        return

    bot.send_message(msg.chat.id,"Access Token")

    bot.register_next_step_handler(msg,cancel_step)


def cancel_step(msg):

    token = msg.text

    url = f"https://bind-cancel-c.vercel.app/cancel?access_token={token}"

    r = requests.get(url)

    bot.send_message(msg.chat.id,r.text)


# ---------- ADMIN PANEL ----------

@bot.message_handler(func=lambda m: m.text == "👑 Admin Panel")
def admin_panel(msg):

    if msg.from_user.id != OWNER_ID:
        return

    m = ReplyKeyboardMarkup(resize_keyboard=True)

    m.add(KeyboardButton("➕ Add User"))
    m.add(KeyboardButton("➖ Remove User"))

    bot.send_message(msg.chat.id,"Admin Panel",reply_markup=m)


# ---------- ADD USER ----------

@bot.message_handler(func=lambda m: m.text == "➕ Add User")
def add_user(msg):

    if msg.from_user.id != OWNER_ID:
        return

    bot.send_message(msg.chat.id,"Send User ID")

    bot.register_next_step_handler(msg,save_user)


def save_user(msg):

    uid = int(msg.text)

    approved_users.add(uid)

    bot.send_message(msg.chat.id,"✅ User Added")


# ---------- REMOVE USER ----------

@bot.message_handler(func=lambda m: m.text == "➖ Remove User")
def remove_user(msg):

    if msg.from_user.id != OWNER_ID:
        return

    bot.send_message(msg.chat.id,"Send User ID")

    bot.register_next_step_handler(msg,delete_user)


def delete_user(msg):

    uid = int(msg.text)

    approved_users.discard(uid)

    bot.send_message(msg.chat.id,"❌ User Removed")


print("BOT RUNNING")

bot.infinity_polling()
