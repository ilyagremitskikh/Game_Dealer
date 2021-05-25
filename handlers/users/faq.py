import logging

from aiogram import types
from aiogram.dispatcher.filters import Command

logger = logging.getLogger(__name__)

from loader import dp

@dp.message_handler(Command('faq'))
async def send_faq(message: types.Message):
    text = f"""<b>1. Как часто обновляется база скидок?</b>
    
База скидок обновляется каждый час, т.к. скидки обычно длятся 1-3 недели,
этого достаточно чтобы всегда иметь актуальную базу скидок


<b>2. В каких магазинах проверяются скидки?</b>

Бот ищет скидки в 12 магазинах: Blizzard, Epic Game Store, Fanatical, GOG, GamersGate, GreenManGaming,
Humble Store, Humble Widgets, Microsoft Store, Origin, Steam, Uplay


<b>3. Почему у некоторых игр в поиске нет изображения и рейтинга? Они работают?</b>

Рейтинг и изображения мы получаем от Steam, а как мы знаем некоторые игры являются эксклюзивами других магазинов и
в Steam не присутствуют. В любом случае, их можно добавлять в свой список и получать по ним актуальные скидки в
других магазинах.


<b>4. Не могу найти игру %Название игры%. Её нет в боте?</b>

В названиях некоторых игр используются специальные символы, например, Call of Duty®: Black Ops - Cold War.
Попробуйте скопировать в поиск название игры целиком или отправить ссылку на игру в Steam.


<b>5. Бот умеет оповещать о появлении новых скидок? Проверять вручную неудобно (</b>

Мы работаем над этим и скоро бот научится оповещать вас о новых скидках автоматически


<b>6. Как связаться с автором бота?</b>

Связаться с автором можно с помощью бота обратной связи: @GameDealer_SupportBot
 """
    await message.answer(text=text)