import logging
import random
from typing import List
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp
from bs4 import BeautifulSoup

from keyboards.reply import main_menu

router = Router()
user_reading_states = {}

def escape(text: str) -> str:
    special_chars = r'_*[]()~`>#+-=|{}.!'
    for char in special_chars:
        text = text.replace(char, '\\' + char)
    return text

ARTICLES = [
    # Краткие содержания из Википедии
    {"title": "Война и мир (краткое содержание)", "url": "https://ru.wikipedia.org/wiki/Война_и_мир"},
    {"title": "Преступление и наказание (краткое содержание)", "url": "https://ru.wikipedia.org/wiki/Преступление_и_наказание"},
    {"title": "Мастер и Маргарита (краткое содержание)", "url": "https://ru.wikipedia.org/wiki/Мастер_и_Маргарита"},
    {"title": "Евгений Онегин (краткое содержание)", "url": "https://ru.wikipedia.org/wiki/Евгений_Онегин"},
    {"title": "Мцыри (краткое содержание)", "url": "https://ru.wikipedia.org/wiki/Мцыри"},
    {"title": "Горе от ума (краткое содержание)", "url": "https://ru.wikipedia.org/wiki/Горе_от_ума"},
    {"title": "Тихий Дон (краткое содержание)", "url": "https://ru.wikipedia.org/wiki/Тихий_Дон"},
    {"title": "Гарри Поттер и философский камень (краткое содержание)", "url": "https://ru.wikipedia.org/wiki/Гарри_Поттер_и_философский_камень"},
    {"title": "Властелин колец (краткое содержание)", "url": "https://ru.wikipedia.org/wiki/Властелин_колец"},
    {"title": "Три мушкетера (краткое содержание)", "url": "https://ru.wikipedia.org/wiki/Три_мушкетёра"},
    {"title": "Метро 2033 (краткое содержание)", "url": "https://ru.wikipedia.org/wiki/Метро_2033"},
]

def split_text_into_parts(text: str, max_chars: int = 1800) -> List[str]:
    parts = []
    while len(text) > max_chars:
        split_point = text.rfind("\n", 0, max_chars)
        if split_point == -1:
            split_point = text.rfind(" ", 0, max_chars)
        if split_point == -1:
            split_point = max_chars
        parts.append(text[:split_point].rstrip())
        text = text[split_point:].lstrip()
    if text:
        parts.append(text)
    return parts

async def fetch_article_text(url: str) -> str:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return "❌ Статья недоступна."
                html = await response.text()

        soup = BeautifulSoup(html, "lxml")

        # Специальная обработка для Wikipedia
        if "wikipedia.org" in url:
            # Ищем основной контент
            content = soup.find("div", {"id": "mw-content-text"})
            if content:
                # Удаляем ненужные элементы
                for el in content.select(".toc, .navbox, .mw-empty-elt, .thumb, .reference, .reflist, .infobox, .mw-editsection"):
                    el.decompose()

                # Извлекаем текст
                text = content.get_text(separator="\n", strip=True)
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                cleaned = "\n".join(lines)

                # Ограничиваем объем текста
                return cleaned[:10000] + "\n\n📚 Полная статья на Wikipedia: " + url if len(cleaned) > 10000 else cleaned

        # Обработка для других сайтов (старая логика)
        content = soup.find("div", class_="mw-parser-output")
        if not content:
            return "❌ Текст не найден."

        for el in content.select(".toc, .navbox, sup, .mw-empty-elt, .thumb, .gallery, .reference, .reflist, .infobox"):
            el.decompose()

        text = content.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned = "\n".join(lines)
        return cleaned[:12000] + "..." if len(cleaned) > 12000 else cleaned

    except Exception as e:
        logging.error(f"Ошибка при загрузке статьи {url}: {e}")
        return "❌ Не удалось загрузить статью."

def get_reader_keyboard(article_index: int, part_index: int, total_articles: int, has_bookmark: bool, total_parts: int) -> InlineKeyboardMarkup:
    nav_row = []
    if part_index > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Назад (часть)", callback_data=f"read_prev_part_{article_index}_{part_index}"))
    if part_index + 1 < total_parts:
        nav_row.append(InlineKeyboardButton(text="▶️ Вперёд (часть)", callback_data=f"read_next_part_{article_index}_{part_index}"))

    article_nav_row = []
    if article_index > 0:
        article_nav_row.append(InlineKeyboardButton(text="⏪ Пред. книга", callback_data=f"read_prev_article_{article_index}"))
    if article_index + 1 < total_articles:
        article_nav_row.append(InlineKeyboardButton(text="⏩ След. книга", callback_data=f"read_next_article_{article_index}"))

    buttons = []
    if nav_row:
        buttons.append(nav_row)
    if article_nav_row:
        buttons.append(article_nav_row)

    buttons.append([InlineKeyboardButton(
        text="↩️ К закладке" if has_bookmark else "🔖 Закладка",
        callback_data="read_bookmark" if has_bookmark else "read_set_bookmark"
    )])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def show_article(obj, user_id: int, article_index: int, part_index: int = 0):
    if article_index < 0 or article_index >= len(ARTICLES):
        msg = "📖 Книги закончились."
        if isinstance(obj, Message):
            await obj.answer(msg, reply_markup=main_menu)
        else:
            await obj.message.edit_text(msg, reply_markup=main_menu)
        user_reading_states.pop(user_id, None)
        return

    article = ARTICLES[article_index]
    full_text = await fetch_article_text(article["url"])

    if full_text.startswith("❌"):
        escaped_title = escape(article['title'])

        msg = f"📚 *{escaped_title}*\n\n{escape(full_text)}"
        kb = get_reader_keyboard(article_index, part_index, len(ARTICLES), False, 1)
        if isinstance(obj, Message):
            await obj.answer(msg, reply_markup=kb, parse_mode="MarkdownV2")
        else:
            await obj.message.edit_text(msg, reply_markup=kb, parse_mode="MarkdownV2")
            await obj.answer()
        return

    parts = split_text_into_parts(full_text, 1800)
    if part_index >= len(parts):
        part_index = len(parts) - 1

    current_part = parts[part_index]
    total_parts = len(parts)

    escaped_title = escape(article['title'])
    escaped_part = escape(current_part)

    msg = f"📚 *{escaped_title}* \\| Часть {part_index + 1}/{total_parts}\n\n{escaped_part}"

    has_bookmark = (
        user_reading_states.get(user_id, {}).get("bookmark_article") is not None and
        user_reading_states.get(user_id, {}).get("bookmark_part") is not None
    )
    kb = get_reader_keyboard(article_index, part_index, len(ARTICLES), has_bookmark, total_parts)

    if isinstance(obj, Message):
        await obj.answer(msg, reply_markup=kb, parse_mode="MarkdownV2")
    else:
        await obj.message.edit_text(msg, reply_markup=kb, parse_mode="MarkdownV2")
        await obj.answer()

@router.message(F.text == "📖 Книги")
async def start_reader(message: Message):
    user_id = message.from_user.id
    user_reading_states[user_id] = {
        "article_index": 0,
        "part_index": 0,
        "bookmark_article": None,
        "bookmark_part": None
    }
    await show_article(message, user_id, 0, 0)

@router.callback_query(F.data.startswith("read_next_part_"))
async def read_next_part(callback: CallbackQuery):
    try:
        _, _, _, article_index, part_index = callback.data.split("_")
        article_index, part_index = int(article_index), int(part_index)
        user_id = callback.from_user.id
        state = user_reading_states.get(user_id)
        if not state:
            return

        full_text = await fetch_article_text(ARTICLES[article_index]["url"])
        parts = split_text_into_parts(full_text, 1800)

        if part_index + 1 < len(parts):
            state["part_index"] = part_index + 1
            await show_article(callback, user_id, article_index, state["part_index"])
        else:
            await callback.answer("Это последняя часть статьи.", show_alert=True)
    except Exception as e:
        logging.error(f"Error in read_next_part: {e}")
        await callback.answer("Произошла ошибка.", show_alert=True)

@router.callback_query(F.data.startswith("read_prev_part_"))
async def read_prev_part(callback: CallbackQuery):
    try:
        _, _, _, article_index, part_index = callback.data.split("_")
        article_index, part_index = int(article_index), int(part_index)
        user_id = callback.from_user.id
        state = user_reading_states.get(user_id)
        if not state:
            return

        if part_index > 0:
            state["part_index"] = part_index - 1
            await show_article(callback, user_id, article_index, state["part_index"])
        else:
            await callback.answer("Это первая часть статьи.", show_alert=True)
    except Exception as e:
        logging.error(f"Error in read_prev_part: {e}")
        await callback.answer("Произошла ошибка.", show_alert=True)

@router.callback_query(F.data.startswith("read_next_article_"))
async def read_next_article(callback: CallbackQuery):
    try:
        _, _, _, article_index = callback.data.split("_")
        article_index = int(article_index)
        user_id = callback.from_user.id
        state = user_reading_states.get(user_id)
        if not state:
            return

        if article_index + 1 < len(ARTICLES):
            state["article_index"] = article_index + 1
            state["part_index"] = 0
            await show_article(callback, user_id, state["article_index"], 0)
        else:
            await callback.answer("Это последняя книга.", show_alert=True)
    except Exception as e:
        logging.error(f"Error in read_next_article: {e}")
        await callback.answer("Произошла ошибка.", show_alert=True)

@router.callback_query(F.data.startswith("read_prev_article_"))
async def read_prev_article(callback: CallbackQuery):
    try:
        _, _, _, article_index = callback.data.split("_")
        article_index = int(article_index)
        user_id = callback.from_user.id
        state = user_reading_states.get(user_id)
        if not state:
            return

        if article_index > 0:
            state["article_index"] = article_index - 1
            state["part_index"] = 0
            await show_article(callback, user_id, state["article_index"], 0)
        else:
            await callback.answer("Это первая книга.", show_alert=True)
    except Exception as e:
        logging.error(f"Error in read_prev_article: {e}")
        await callback.answer("Произошла ошибка.", show_alert=True)

@router.callback_query(F.data == "read_set_bookmark")
async def set_bookmark(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = user_reading_states.get(user_id)
    if state is not None:
        state["bookmark_article"] = state["article_index"]
        state["bookmark_part"] = state["part_index"]
        await callback.answer("🔖 Закладка установлена!", show_alert=True)

@router.callback_query(F.data == "read_bookmark")
async def go_to_bookmark(callback: CallbackQuery):
    user_id = callback.from_user.id
    state = user_reading_states.get(user_id)
    if state and state["bookmark_article"] is not None and state["bookmark_part"] is not None:
        state["article_index"] = state["bookmark_article"]
        state["part_index"] = state["bookmark_part"]
        await show_article(callback, user_id, state["article_index"], state["part_index"])
    else:
        await callback.answer("Нет активной закладки.", show_alert=True)

@router.message(F.text == "⬅️ Назад")
async def back_to_main(message: Message):
    user_id = message.from_user.id
    user_reading_states.pop(user_id, None)  # Очищаем состояние чтения
    await message.answer("Главное меню:", reply_markup=main_menu)