import database.database as db
import telegram_bot.bot
from telegram.ext import ApplicationBuilder, CommandHandler


if __name__ == "__main__":
    app = ApplicationBuilder().token("YOUR TOKEN HERE").build()

    app.run_polling()
