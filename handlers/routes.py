import asyncio
import ftplib
from os import getenv

import db
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram import *
from forms.user import Form

router = Router()

def knopki_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[

            [KeyboardButton(text='Главное меню')], [KeyboardButton(text='Помощь')],
            [KeyboardButton(text='Обо мне')], [KeyboardButton(text='Отзывы')]

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

@router.message(Command('cancel'))
async def cancel_form(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Заявка отменена')


@router.callback_query(F.data == 'purchase')
async def zakaz(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await callback.message.answer('Отлично! Тогда приступим к заполнению заявки.')

    await callback.message.answer('*Ваше имя*?', parse_mode='Markdown')
    await state.set_state(Form.name)


@router.message(Form.name, F.text)
async def process_name(message: Message, state: FSMContext):

    await state.update_data(name=message.text)

    await message.answer('*Что вы хотите?*\n_(Заказать выполненное дз, tg-бота)_', parse_mode='Markdown')
    await state.set_state(Form.wish)

@router.message(Form.wish, F.text)
async def process_wish(message: Message, state: FSMContext):

    await state.update_data(wish=message.text)

    await message.answer('*Вкратце опишите ваши пожелания/требования к работе*', parse_mode='Markdown')
    await state.set_state(Form.tz)

@router.message(Form.tz, F.text)
async def process_tz(message: Message, state: FSMContext):

    await state.update_data(tz=message.text)

    data = await state.get_data()
    name = data['name']
    wish = data['wish']
    tz = data['tz']

    client_id = message.from_user.id
    client_username = message.from_user.username or "Нет юзернейма"

    await message.answer('_Заявка готова и отправлена мне! Она выглядит следующим образом:_\n\n'
                         f'*Ваше имя*: {name} или {message.from_user.first_name} \n'
                         f'*Вы хотите*: {wish}\n'
                         f'*Ваши требования/пожелания*: {tz}\n\n'
                         f'Скоро свяжусь с вами!', parse_mode='Markdown')

    db.add_order(client_id, client_username, name, wish, tz)

    admin_text = (
        f"🚨 <b>НОВЫЙ ЗАКАЗ</b> 🚨\n\n"
        f"<b>От кого:</b> {name} (@{client_username})\n"
        f"<b>ID:</b> <code>{client_id}</code>\n"
        f"<b>Что хочет:</b> {wish}\n"
        f"<b>ТЗ:</b> {tz}"
    )

    try:
        # Обязательно используем message.bot.send_message
        await message.bot.send_message(chat_id=getenv('ADMIN_ID'), text=admin_text, parse_mode='HTML')
    except Exception as e:
        # Если будет ошибка (например, неверный токен или ID), скрипт не упадет, а просто выведет текст в консоль
        print(f"Ошибка при отправке уведомления админу: {e}")

    await state.clear()


@router.message(F.text.lower() == 'хочу сделать заказ')
async def start(message: Message):
    await  message.answer('Отлично')

@router.message(Command("start"))
@router.message(F.text.lower() == 'главное меню')
async def command_start_handler(message: Message):
    await message.answer("Привет! Это бот-помощник для автоматизации заявок. "
                         "Мы можем сразу создать заказ и потом я вам отпишу в ЛС.\n"
                         "По срочным вопросам писать сразу сюда: @tecamm ", reply_markup= main_menu_buttons())


@router.message(Command('help'))
@router.message(F.text.lower() == 'помощь')
async def helper(message: Message):
    await  message.reply('Доступные команды: \n/start - Главное меню🏠'
                         '\n/help - Справка📃'
                         '\n/about - Про меня👾', reply_markup=knopki_keyboard())

@router.message(Command('about'))
@router.message(F.text.lower() == 'обо мне')
async def about(message: Message):
    await message.answer('👋Привет! 🗣 Я - *Tecam*. Мне *19* и я обычный парень, который хочет '
                         'предложить вам свои услуги. Этот бот специально создан для заказов:'
                         '\n\n_-Создание telegram-бота_'
                         '\n_-Помочь вам с вашим дз_'
                         '\n\nУзнать больше информации или задать вопросы можно в ЛС: @tecamm', parse_mode='Markdown')
