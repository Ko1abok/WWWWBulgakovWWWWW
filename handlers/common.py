from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply import main_menu, games_menu
from handlers.auth import USER_DATA

router = Router()

@router.message(F.text == "👤 Мой профиль")
async def my_profile(message: Message):
    profile = USER_DATA.get(message.from_user.id)
    if not profile:
        await message.answer("❌ Профиль не найден. Пройдите регистрацию заново (/start).")
        return

    lines = []
    lines.append(f"👤 <b>{profile['name']} {profile['surname']}</b>")
    if profile.get("age"):
        lines.append(f"🎂 Возраст: {profile['age']}")
    if profile.get("gender"):
        lines.append(f"⚧️ Пол: {profile['gender']}")
    if profile.get("region"):
        lines.append(f"📍 Регион: {profile['region']}")
    if profile.get("interests"):
        lines.append(f"❤️ Интересы: {profile['interests']}")

    text = "\n".join(lines)

    if profile.get("photo"):
        await message.answer_photo(photo=profile["photo"], caption=text, parse_mode="HTML")
    else:
        await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🎮 Игры")
async def show_games(message: Message):
    await message.answer("Выберите игру:", reply_markup=games_menu)

@router.message(F.text == "ℹ️ О боте")
async def about_bot(message: Message):
    await message.answer(
        "🤖 Это бот с двумя играми и читалкой:\n\n"
        "✂️ <b>Камень, ножницы, бумага</b>\n"
        "— Выбери один из трёх вариантов.\n"
        "— Бот тоже делает выбор.\n"
        "— Камень побеждает ножницы, ножницы — бумагу, бумага — камень.\n\n"
        "🎲 <b>Угадай число на кубике</b>\n"
        "— Выбери число от 1 до 6.\n"
        "— Бот «бросает» кубик.\n"
        "— Если угадал — победа! 🎯\n\n"
        "Читай, играй и веселись! 😊",
        reply_markup=main_menu,
        parse_mode="HTML"
    )

@router.message(F.text == "📖 Читалка Ведьмака")
async def witcher_reader(message: Message):
    await message.answer("Раздел 'Читалка Ведьмака' в разработке 🏗️", reply_markup=main_menu)

@router.message()
async def handle_unknown(message: Message):
    gif_url = "https://i.pinimg.com/originals/0d/ac/06/0dac06a5332d13e2a4e2dc30ba0c6411.gif?nii=t"
    await message.answer_animation(
        animation=gif_url,
        caption="Извините, я не понимаю это сообщение.\nПожалуйста, используйте кнопки меню.",
        reply_markup=main_menu
    )