import asyncio
import json
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile

# ================= BLACKLIST ====================

def is_blocked(user_id: int) -> bool:
    return user_id in blocked_users
# ================= НАЛАШТУВАННЯ =================
load_dotenv()
bot = Bot(os.getenv("BOT_TOKEN"))
ADMIN_ID = 8626987492  # Замініть на ваш Telegram ID
CHANNEL_LINK = "https://t.me/+-0rRbkJCKGgzNzhi"  # Посилання на ваш канал
photo = FSInputFile("paradox.jpg")  # Посилання на фото або file_id

dp = Dispatcher(storage=MemoryStorage())

# ================== Block =================
async def check_block(message_or_callback):
    user_id = message_or_callback.from_user.id

    if is_blocked(user_id):
        if hasattr(message_or_callback, "message"):  # callback
            await message_or_callback.message.answer(
                "⛔ Вы заблокированы и не можете пользоваться ботом."
            )
        else:  # message
            await message_or_callback.answer(
                "⛔ Вы заблокированы и не можете пользоваться ботом."
            )
        return True

    return False
# ================ Bans ======================
BAN_FILE = "bans.json"
def load_bans():
    try:
        with open(BAN_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_bans():
    with open(BAN_FILE, "w") as f:
        json.dump(list(blocked_users), f)

blocked_users = load_bans()
# ================= СТАНИ =================
class AdminState(StatesGroup):
    ban_id = State()
    unban_id = State()

class Registration(StatesGroup):
    name = State()
    experience = State()
    skills = State()

# ================= КНОПКИ =================

def start_keyboard():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 ПОДПИСАТЬСЯ", url=CHANNEL_LINK)],
            [InlineKeyboardButton(text="✅ Я ПОДПИСАЛСЯ", callback_data="subscribed")]
        ]
    )
    return keyboard

# ================= BAN SYSTEM =================

@dp.message(Command("ban"))
async def ban_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(message.text.split()[1])
        blocked_users.add(user_id)
        save_bans()

        await message.answer(f"🚫 Пользователь {user_id} заблокирован")
    except:
        await message.answer("❗ Использование: /ban user_id")
# ================= СТАРТ =================

photo = FSInputFile("paradox.jpg")

@dp.message(CommandStart())
async def start_handler(message: Message):
    if await check_block(message):
        return
    text = (
        "👋 Поздравляем в нашей команде!\n\n"
        "Мы ищем мотивированых людей для долгосрочного сотрудничества.\n"
        "Остался последний шаг, подпишитесь на наш тгк и продолжите регистрацию."
    )

    await message.answer_photo(
    photo=photo,
    caption=text,
    reply_markup=start_keyboard()
)
# ================= Unban ========================
@dp.message(Command("unban"))
async def unban_user(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        user_id = int(message.text.split()[1])
        blocked_users.discard(user_id)
        save_bans()

        await message.answer(f"✅ Пользователь {user_id} разблокирован")
    except:
        await message.answer("❗ Использование: /unban user_id")
# ================= ПІСЛЯ ПІДПИСКИ =================

@dp.callback_query(F.data == "subscribed")
async def subscribed_handler(callback, state: FSMContext):
    if await check_block(callback):
        return

    await callback.message.answer(
        "📝 Регистрация\n\n"
        "Введите ваше имя:"
    )
    await state.set_state(Registration.name)
    await callback.answer()

# ================= ІМ'Я =================

@dp.message(Registration.name)
async def get_name(message: Message, state: FSMContext):
    if await check_block(message):
        return

    await state.update_data(name=message.text)

    await message.answer(
        "💼 Введите ваш опыт (например: 1 год, новичок, 3 года):"
    )

    await state.set_state(Registration.experience)

# ================= ДОСВІД =================

@dp.message(Registration.experience)
async def get_experience(message: Message, state: FSMContext):
    if await check_block(message):
        return

    await state.update_data(experience=message.text)

    await message.answer(
        "🛠 Сколько заливаете в неделю(если нет опыта, просто пишите 0):"
    )

    await state.set_state(Registration.skills)

# ================= НАВИЧКИ =================

@dp.message(Registration.skills)
async def get_skills(message: Message, state: FSMContext):
    if await check_block(message):
        return

    await state.update_data(skills=message.text)

    data = await state.get_data()

    user_text = (
        f"🎉 Благодарим за регистрацию!\n\n"
        f"Имя: {data['name']}\n"
        f"Опыт: {data['experience']}\n"
        f"Сколько заливаете: {data['skills']}\n"
        f"Наш менеджер скоро свяжется с вами, ожидайте!"
    )

    await message.answer(user_text)

    admin_text = (
        "🔔 Новая заявка!\n\n"
        f"👤 Имя: {data['name']}\n"
        f"💼 Опыт: {data['experience']}\n"
        f"🛠 Сколько заливает: {data['skills']}\n"
        f"📩 Username: @{message.from_user.username}\n"
        f"🆔 ID: {message.from_user.id}"
    )

    await bot.send_message(ADMIN_ID, admin_text)

    await state.clear()

# ================= АДМІН ПАНЕЛЬ =================

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    def admin_keyboard():
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🚫 Бан", callback_data="ban_menu")],
                [InlineKeyboardButton(text="✅ Анбан", callback_data="unban_menu")],
            ]
        )

    await message.answer(
        "🛠 Админ панель",
        reply_markup=admin_keyboard()
    )
@dp.callback_query(F.data == "ban_menu")
async def ban_menu(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return

    await callback.message.answer("Введи ID пользователя для ban:")
    await state.set_state(AdminState.ban_id)
    await callback.answer()

@dp.callback_query(F.data == "unban_menu")
async def unban_menu(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != ADMIN_ID:
        return

    await callback.message.answer("Введи ID пользователя для unban:")
    await state.set_state(AdminState.unban_id)
    await callback.answer()
# ================= ЗАПУСК =================

async def main():
    print("Bot started...")
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())