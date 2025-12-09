from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply import main_menu, games_menu

router = Router()

@router.message(F.text == "🎮 Игры")
async def show_games(message: Message):
    await message.answer("Выберите игру:", reply_markup=games_menu)

@router.message(F.text == "ℹ️ О боте")
async def about_bot(message: Message):
    await message.answer(await message.answer(
        "🤖 Это бот с двумя играми и читалкой:\n\n"
        "✂️ <b>Камень, ножницы, бумага</b>\n"
        "— Выбери один из трёх вариантов.\n"
        "— Бот тоже делает выбор.\n"
        "— Камень побеждает ножницы, ножницы — бумагу, бумага — камень.\n\n"
        "🎲 <b>Угадай число на кубике</b>\n"
        "— Выбери число от 1 до 6.\n"
        "— Бот «бросает» кубик.\n"
        "— Если угадал — победа! 🎯\n\n"
        "Читай Играй и веселись! 😊",
        reply_markup=main_menu
    ))

@router.message(F.text == "⬅️ Назад")
async def back_to_main(message: Message):
    await message.answer("Главное меню:", reply_markup=main_menu)

@router.message(F.text == "⬅️ Назад к играм")
async def back_to_games(message: Message):
    await message.answer("Выберите игру:", reply_markup=games_menu)