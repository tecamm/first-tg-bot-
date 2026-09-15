import asyncio
from os import getenv
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram import *

def knopki_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[

            [KeyboardButton(text='Главное меню')], [KeyboardButton(text='Помощь')],
            [KeyboardButton(text='Обо мне')], [KeyboardButton(text='Отзывы')], [KeyboardButton(text='Ваши заказы')]

        ],
        resize_keyboard=True
    )
    return keyboard

def main_menu_buttons():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard = [
            [InlineKeyboardButton(text='Создать заказ',callback_data = 'purchase') ],
            [InlineKeyboardButton(text='Заценить мой стим :)', url='https://steamcommunity.com/id/tecam/')]
        ]
    )

    return keyboard

def admin_ban_user(client_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard = [
            [InlineKeyboardButton(text='Забанить юзера',callback_data = f'ban_{client_id}') ],
        ]
    )

    return keyboard