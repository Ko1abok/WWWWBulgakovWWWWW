import logging
logger = logging.getLogger(__name__)
import random
from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply import dice_menu, games_menu, main_menu

router = Router()

@router.message(F.text == "🎲 Угадай число на кубике")
async def start_dice(message: Message):
    logger.info(f"Start dice game by user {message.from_user.id}")
    await message.answer(
        "Выберите число от 1 до 6:",
        reply_markup=dice_menu
    )

@router.message(F.text.in_(["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]))
async def play_dice(message: Message):
    logger.info(f"Получено сообщение: '{message.text}' от пользователя {message.from_user.id}")

    emoji_to_num = {
        "1️⃣": 1, "2️⃣": 2, "3️⃣": 3,
        "4️⃣": 4, "5️⃣": 5, "6️⃣": 6
    }

    user_guess = emoji_to_num[message.text]
    real_roll = random.randint(1, 6)

    logger.info(f"User guess: {user_guess}, Real roll: {real_roll}")

    if user_guess == real_roll:
        result = "<b>🎯 Поздравляю! Вы угадали!</b>"
    else:
        result = f"<b>❌ Не угадали.</b> Выпало: <code>{real_roll}</code>"

    dice_emoji = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"][real_roll - 1]

    # ИСПРАВЛЕНО: используем \n вместо <br>
    await message.answer(
        f"<b>Вы выбрали:</b> {message.text}\n"
        f"<b>Кубик показал:</b> {dice_emoji}\n\n"
        f"{result}",
        reply_markup=dice_menu,
        parse_mode="HTML"
    )

@router.message(F.text == "⬅️ Назад к играм")
async def back_to_games(message: Message):
    await message.answer("Выберите игру:", reply_markup=games_menu)

@router.message(F.text == "⬅️ Назад")
async def back_to_main(message: Message):
    await message.answer("Главное меню:", reply_markup=main_menu)