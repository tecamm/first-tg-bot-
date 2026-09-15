import asyncio
import ftplib
from os import getenv

from aiohttp.web_routedef import delete

import db
from db import pop_order
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram import *
from forms.user import Form
from defs.inlinek_replyk_keyboards import main_menu_buttons, admin_ban_user, knopki_keyboard

router = Router()

async def check_ban(message: Message):
    if db.check_on_ban(message.from_user.id):
        return False
    return True

@router.callback_query(F.data.startswith('ban_'))
async def ban_id(callback: CallbackQuery):
    await callback.answer()

    client_id = int(callback.data.split('_')[1])

    db.ban_user_id(client_id)

    await callback.bot.send_message(chat_id=getenv('ADMIN_ID'), text=f'Забанили! '
                                                                     f'\nID:{client_id}')

@router.message(Command('my_orders'))
@router.message(F.text.lower() == 'ваши заказы')
async def my_orders(message: Message):
    user_id = message.from_user.id
    orders = db.user_get_order_id(user_id)

    if not orders:
        await message.answer('У вас нет заказов... :(')
        return

    await message.answer(f'*Ваши активные заказы:*', parse_mode="Markdown")

    for order in orders:
        order_id, wish, tz  = order

        delete_order = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f'Удалить заказ', callback_data=f'del_{order_id}')]
        ])

        text = (
            f'<b>Заказ: #{order_id}</b>\n'
            f'<b>Требование: {wish}</b>\n'
            f'<b>ТЗ: {tz}</b>\n'
        )

        await message.answer(text, reply_markup=delete_order, parse_mode='HTML')


@router.callback_query(F.data.startswith('del_'))
async def process_delete_order(callback: CallbackQuery):
    order_id = int(callback.data.split('_')[1])
    user_id = callback.from_user.id

    success = db.pop_order(order_id, user_id)

    if success:
        await callback.message.edit_text(f"✅ <i>Заказ #{order_id} был успешно отменен.</i>", parse_mode='HTML')
    else:
        await callback.answer("Заказ не найден или уже удален!", show_alert=True)

    await callback.answer()

# @router.message(Command('delete'))
# async def cancel_form(message: Message, state: FSMContext):
#     await state.clear()
#     try:
#         await message.answer('Заявка удалена!')
#     except Exception as e:
#         await message.bot.send_message(chat_id=int(getenv('ADMIN_ID')), text=f'{message.from_user.id} или {message.from_user.full_name} удалил заявку!' )


@router.callback_query(F.data == 'purchase')
async def zakaz(callback: CallbackQuery, state: FSMContext):
    active_orders = db.get_active_orders_count(callback.from_user.id)

    if active_orders >= 3:
        await callback.answer(" У вас уже есть 3 активные заявки! Удалите старые или дождитесь их выполнения.",
                              show_alert=True)
        return

    await callback.answer()
    await callback.message.answer('Отлично! Тогда приступим к заполнению заявки.\n*Ваше имя*?', parse_mode='Markdown')
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
    if len(message.text) < 10:
        await message.answer("⚠️ ТЗ слишком короткое. Опишите задачу чуть подробнее (минимум 10 символов).")
        return

    if len(message.text) > 1000:
        await message.answer("⚠️ ТЗ слишком длинное. Постарайтесь уложиться в 1000 символов.")
        return

    await state.update_data(tz=message.text)

    data = await state.get_data()
    name = data['name']
    wish = data['wish']
    tz = data['tz']
    status = 'True'

    client_id = message.from_user.id
    client_username = message.from_user.username or "Нет юзернейма"

    await message.answer('_Заявка готова и отправлена мне! Она выглядит следующим образом:_\n\n'
                         f'*Ваше имя*: {name} или {message.from_user.first_name} \n'
                         f'*Вы хотите*: {wish}\n'
                         f'*Ваши требования/пожелания*: {tz}\n\n'
                         f'Скоро свяжусь с вами!', parse_mode='Markdown')

    db.add_order(client_id, client_username, name, wish, tz, status)

    admin_text = (
        f"🚨 <b>НОВЫЙ ЗАКАЗ</b> 🚨\n\n"
        f"<b>От кого:</b> {name} (@{client_username})\n"
        f"<b>ID:</b> <code>{client_id}</code>\n"
        f"<b>Что хочет:</b> {wish}\n"
        f"<b>ТЗ:</b> {tz}")

    try:
        await message.bot.send_message(chat_id=int(getenv('ADMIN_ID')), text=admin_text, parse_mode='HTML', reply_markup=admin_ban_user(client_id))
    except Exception as e:
        print(f"Ошибка при отправке уведомления админу: {e}")

    await state.clear()

@router.message(Command("start"))
@router.message(F.text.lower() == 'главное меню')
async def command_start_handler(message: Message):
    await message.answer("Привет! Это бот-помощник для автоматизации заявок. "
                         "Мы можем сразу создать заказ и потом я вам отпишу в ЛС.\n"
                         "Для полной информации рекомендуется использовать \n/help, чтобы открыть справочник."
                         "По срочным вопросам писать сразу сюда: @tecamm ", reply_markup= main_menu_buttons())



@router.message(Command('help'))
@router.message(F.text.lower() == 'помощь')
async def helper(message: Message):
    await  message.reply('Доступные команды: \n/start - Главное меню🏠'
                         '\n/help - Справка📃'
                         '\n/about - Про меня👾'
                         '\n/delete - Удалить заявку❌', reply_markup=knopki_keyboard())

@router.message(Command('about'))
@router.message(F.text.lower() == 'обо мне')
async def about(message: Message):
    await message.answer('👋Привет! 🗣 Я - *Tecam*. Мне *22*, я обычный студент с магистратуры, который хочет '
                         'предложить вам свои услуги. Этот бот специально создан для заказов:'
                         '\n\n_-Создание telegram-бота_'
                         '\n_-Помочь вам с вашим дз_'
                         '\n\nУзнать больше информации или задать вопросы можно в ЛС: @tecamm', parse_mode='Markdown')

@router.message()
async def users_message(message: Message):
    await message.reply(f'Бот не понимает вашего сообщения :(\n'
                        f'Надеюсь там что-то приличное...\n'
                        f'В любом случае, просто создайте заявку и напишите все там :)')
