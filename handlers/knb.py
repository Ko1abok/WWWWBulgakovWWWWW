import random
from aiogram import Router, F
from aiogram.types import Message
from keyboards.reply import rps_menu, games_menu, main_menu

router = Router()

CHOICES = {
    "🪨 Камень": "🪨",
    "✂️ Ножницы": "✂️",
    "📄 Бумага": "📄"
}

WINNING_COMBINATIONS = {
    "🪨": "✂️",  # Камень бьет ножницы
    "✂️": "📄",  # Ножницы бьют бумагу
    "📄": "🪨"   # Бумага бьет камень
}

@router.message(F.text == "✂️ Камень, ножницы, бумага")
async def start_rps(message: Message):
    await message.answer(
        "Выберите свой ход:",
        reply_markup=rps_menu
    )

@router.message(F.text.in_(CHOICES.keys()))
async def play_rps(message: Message):
    user_choice_emoji = CHOICES[message.text]
    bot_choice_emoji = random.choice(list(CHOICES.values()))

    # Определяем результат
    if user_choice_emoji == bot_choice_emoji:
        result = "*Ничья!* 🤝"
    elif WINNING_COMBINATIONS[user_choice_emoji] == bot_choice_emoji:
        result = "*Вы победили!* 🎉"
    else:
        result = "_Вы проиграли._ ☹️"

    # Формируем сообщение с Markdown разметкой
    await message.answer(
        f"*Ваш выбор:* {user_choice_emoji}\n"
        f"*Выбор бота:* {bot_choice_emoji}\n\n"
        f"{result}",
        reply_markup=rps_menu,
        parse_mode="Markdown"  # Явно указываем Markdown
    )

@router.message(F.text == "⬅️ Назад к играм")
async def back_to_games_rps(message: Message):
    await message.answer("Выберите игру:", reply_markup=games_menu)

@router.message(F.text == "⬅️ Назад")
async def back_to_main_rps(message: Message):
    await message.answer("Главное меню:", reply_markup=main_menu)