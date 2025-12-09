import re
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.reply import main_menu

router = Router()

class AuthStates(StatesGroup):
    waiting_for_phone = State()
    waiting_for_name = State()
    waiting_for_surname = State()
    waiting_for_gender = State()
    waiting_for_age = State()
    waiting_for_region = State()
    waiting_for_interests = State()
    waiting_for_photo = State()
    waiting_for_location = State()

USER_DATA = {}  # user_id → dict
ADMIN_PHONES = {"+79821211540"}

REGIONS = ["Москва", "Санкт-Петербург", "Екатеринбург", "Ижевск", "Казань", "Воткинск", "Другой"]
INTERESTS = ["Спорт", "Музыка", "Кино", "Путешествия", "Игры", "Книги", "Робототехника"]

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Давай начнём!",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Запустить")]],
            resize_keyboard=True
        )
    )

@router.message(F.text == "Запустить")
async def request_phone(message: Message, state: FSMContext):
    await message.answer(
        "Просим предоставить номер телефона",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Предоставить номер", request_contact=True)]],
            resize_keyboard=True
        )
    )
    await state.set_state(AuthStates.waiting_for_phone)

# --- Получение номера ---
@router.message(AuthStates.waiting_for_phone, F.contact)
async def handle_phone(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    if phone.startswith("8"):
        phone = "+7" + phone[1:]
    elif not phone.startswith("+"):
        phone = "+" + phone

    user_id = message.from_user.id
    await state.update_data(phone=phone, user_id=user_id)

    if phone in ADMIN_PHONES:
        await message.answer("✅ Вы вошли как администратор.", reply_markup=main_menu)
        await state.clear()
        return

    if user_id in USER_DATA:
        await message.answer("✅ Добро пожаловать!", reply_markup=main_menu)
        await state.clear()
        return

    await message.answer("Введите ваше Имя:")
    await state.set_state(AuthStates.waiting_for_name)

# --- РЕГИСТРАЦИЯ ---
def is_valid_name(text: str) -> bool:
    return bool(re.fullmatch(r"[а-яА-ЯёЁa-zA-Z]+", text))

@router.message(AuthStates.waiting_for_name)
async def handle_name(message: Message, state: FSMContext):
    if not is_valid_name(message.text):
        await message.answer("❌ Не похоже на имя. Попробуйте еще раз")
        return
    await state.update_data(name=message.text.strip())
    await message.answer("Введите вашу Фамилию:")
    await state.set_state(AuthStates.waiting_for_surname)

@router.message(AuthStates.waiting_for_surname)
async def handle_surname(message: Message, state: FSMContext):
    if not is_valid_name(message.text):
        await message.answer("❌ Не похоже на фамилию. Попробуйте еще раз")
        return
    await state.update_data(surname=message.text.strip())
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Мужской"), KeyboardButton(text="Женский")],
            [KeyboardButton(text="Пропустить")]
        ],
        resize_keyboard=True
    )
    await message.answer("Укажите пол:", reply_markup=kb)
    await state.set_state(AuthStates.waiting_for_gender)

@router.message(AuthStates.waiting_for_gender)
async def handle_gender(message: Message, state: FSMContext):
    if message.text in ("Мужской", "Женский"):
        await state.update_data(gender=message.text)
    elif message.text == "Пропустить":
        await state.update_data(gender=None)
    else:
        await message.answer("Пожалуйста, используйте кнопки.")
        return
    await message.answer("Укажите ваш возраст (например, 25):")
    await state.set_state(AuthStates.waiting_for_age)

@router.message(AuthStates.waiting_for_age)
async def handle_age(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (0 <= int(message.text) <= 100):
        await message.answer("❌ Не похоже на возраст. Укажите число от 0 до 100.")
        return
    await state.update_data(age=int(message.text))
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=r)] for r in REGIONS],
        resize_keyboard=True
    )
    await message.answer("Выберите ваш регион:", reply_markup=kb)
    await state.set_state(AuthStates.waiting_for_region)

@router.message(AuthStates.waiting_for_region)
async def handle_region(message: Message, state: FSMContext):
    if message.text not in REGIONS:
        await message.answer("Пожалуйста, выберите регион из списка.")
        return
    await state.update_data(region=message.text)
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=i)] for i in INTERESTS] + [[KeyboardButton(text="Пропустить")]],
        resize_keyboard=True
    )
    await message.answer("Выберите ваш интерес:", reply_markup=kb)
    await state.set_state(AuthStates.waiting_for_interests)

@router.message(AuthStates.waiting_for_interests)
async def handle_interests(message: Message, state: FSMContext):
    if message.text in INTERESTS:
        await state.update_data(interests=message.text)
    elif message.text == "Пропустить":
        await state.update_data(interests=None)
    else:
        await message.answer("Пожалуйста, выберите из списка.")
        return
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Пропустить")]],
        resize_keyboard=True
    )
    await message.answer("Загрузите фото или нажмите «Пропустить»:", reply_markup=kb)
    await state.set_state(AuthStates.waiting_for_photo)

@router.message(AuthStates.waiting_for_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await ask_location(message, state)

@router.message(AuthStates.waiting_for_photo, F.text == "Пропустить")
async def skip_photo(message: Message, state: FSMContext):
    await state.update_data(photo=None)
    await ask_location(message, state)

@router.message(AuthStates.waiting_for_photo)
async def invalid_photo(message: Message):
    await message.answer("Пожалуйста, отправьте фото или нажмите «Пропустить».")

async def ask_location(message: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить геопозицию", request_location=True)],
            [KeyboardButton(text="Пропустить")]
        ],
        resize_keyboard=True
    )
    await message.answer("Отправьте геопозицию или пропустите:", reply_markup=kb)
    await state.set_state(AuthStates.waiting_for_location)

@router.message(AuthStates.waiting_for_location, F.location | (F.text == "Пропустить"))
async def handle_location_or_skip(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    USER_DATA[user_id] = {
        "name": data["name"],
        "surname": data["surname"],
        "gender": data.get("gender"),
        "age": data.get("age"),
        "region": data.get("region"),
        "interests": data.get("interests"),
        "photo": data.get("photo"),
        "phone": data["phone"],
        "location": f"{message.location.latitude},{message.location.longitude}" if message.location else None
    }
    await message.answer("✅ Регистрация завершена!", reply_markup=main_menu)
    await state.clear()

@router.message(AuthStates.waiting_for_location)
async def invalid_location(message: Message):
    await message.answer("Пожалуйста, отправьте геопозицию или нажмите «Пропустить».")

USER_DATA = USER_DATA
