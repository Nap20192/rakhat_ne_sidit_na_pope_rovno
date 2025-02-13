import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

API_TOKEN = '7783224280:AAGnp2TdOPXXvH1n9rtS_E3ZpoaagKE7DN8'

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(message: Message):
    user = message.from_user
    chat_id = message.chat.id
    username = user.username if user.username else "No username"

    await message.answer(
        f"👋 Hello, {user.first_name}!\n"
        f"🆔 Your chat ID: `{chat_id}`\n"
        f"🔹 Your username: `{username}`",
        parse_mode="Markdown"
    )

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    print("Bot started")

if __name__ == "__main__":
    asyncio.run(main())
