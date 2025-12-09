from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👤 Мой профиль")],
        [KeyboardButton(text="🎮 Игры")],
        [KeyboardButton(text="📖 Книги")],
        [KeyboardButton(text="ℹ️ О боте")]

    ],
    resize_keyboard=True
)

games_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✂️ Камень, ножницы, бумага")],
        [KeyboardButton(text="🎲 Угадай число на кубике")],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

rps_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🪨 Камень"), KeyboardButton(text="✂️ Ножницы"), KeyboardButton(text="📄 Бумага")],
        [KeyboardButton(text="⬅️ Назад к играм")]
    ],
    resize_keyboard=True
)

dice_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1️⃣"), KeyboardButton(text="2️⃣"), KeyboardButton(text="3️⃣")],
        [KeyboardButton(text="4️⃣"), KeyboardButton(text="5️⃣"), KeyboardButton(text="6️⃣")],
        [KeyboardButton(text="⬅️ Назад к играм")]
    ],
    resize_keyboard=True
)