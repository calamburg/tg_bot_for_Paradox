import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Command
from aiogram.types import FSInputFile

# ================= НАЛАШТУВАННЯ =================
load_dotenv()
bot = Bot(os.getenv("TOKEN"))
ADMIN_ID = 6124047244  # Замініть на ваш Telegram ID
CHANNEL_LINK = "https://t.me/+-0rRbkJCKGgzNzhi"  # Посилання на ваш канал
photo = FSInputFile("paradox.jpg")  # Посилання на фото або file_id

dp = Dispatcher(storage=MemoryStorage())

# ================= СТАНИ =================
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

# ================= СТАРТ =================

photo = FSInputFile("C:/Users/yagga/Downloads/paradox.jpg")

@dp.message(CommandStart())
async def start_handler(message: Message):
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

# ================= ПІСЛЯ ПІДПИСКИ =================

@dp.callback_query(F.data == "subscribed")
async def subscribed_handler(callback, state: FSMContext):
    await callback.message.answer(
        "📝 Регистрация\n\n"
        "Введите ваше имя:"
    )
    await state.set_state(Registration.name)
    await callback.answer()

# ================= ІМ'Я =================

@dp.message(Registration.name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer(
        "💼 Введите ваш опыт (например: 1 год, новичок, 3 года):"
    )

    await state.set_state(Registration.experience)

# ================= ДОСВІД =================

@dp.message(Registration.experience)
async def get_experience(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)

    await message.answer(
        "🛠 Сколько заливаете в неделю(если нет опыта, просто пишите 0):"
    )

    await state.set_state(Registration.skills)

# ================= НАВИЧКИ =================

@dp.message(Registration.skills)
async def get_skills(message: Message, state: FSMContext):
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

    await message.answer(
        "🛠 Админ панель\n\n"
        "Вы будете получать уведомление о новых траферах автоматично."
    )

# ================= ЗАПУСК =================

async def main():
    print("Bot started...")
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())