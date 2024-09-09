import os
import database.database as botdb
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters


def require_auth(handler):
    async def wrapper(update, context):
        if botdb.authenticate_member_by_id(
            update.message.from_user.id
        ) or botdb.authenticate_member_by_username_and_set_id(
            update.message.from_user.username, update.message.from_user.id
        ):
            return await handler(update, context)
        return await update.message.reply_text("sir pls sign up 4 cas :(")

    return wrapper


async def message_handler(update, context):
    await update.message.reply_text("stuff")


@require_auth
async def list_groups(update, context):
    groups = botdb.get_groups()
    await update.message.reply_text(f"Available groups:\n{groups}")


@require_auth
async def auth_test_handler(update, context):
    await update.message.reply_text("you are authenticated")


async def start_handler(update, context):
    await update.message.reply_text("hiya loser welcome to the club")


if __name__ == "__main__":
    bot_token: str = os.environ.get("TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("testAuth", auth_test_handler))
    app.add_handler(CommandHandler("groups", list_groups))

    app.add_handler(MessageHandler(filters.ALL, message_handler))

    app.run_polling()
