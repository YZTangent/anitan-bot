import os
import logging
import database.database as botdb
# import argparse
from telegram import (
    ChatMember
)
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    ChatMemberHandler,
    CommandHandler,
    MessageHandler,
    filters
)

# logging
logging.basicConfig(
    # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    level=logging.INFO,
    # Define the log message format
    format='%(asctime)s - %(levelname)s - %(message)s',
    # filename='bot.log',  # Specify the log file
    # filemode='a'  # Append mode (append new logs to the end of the file)
)

logging.getLogger('httpx').setLevel(logging.WARNING)


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
    groups = "\n".join(
        [": ".join([group['title'], group['join_link']]) for group in groups])
    logging.info(f"User {
                 update.message.from_user.username} requested for group links. Returning groups:\n{groups}")
    await update.message.reply_text(f"Available groups:\n{groups}")


@require_auth
async def auth_test_handler(update, context):
    await update.message.reply_text("you are authenticated")


# This handler listens to updates to the bot status only, and if the update is
# one to promote the bot to an administator, it will add the group to the list
# of groups it manage if the user adding the bot as adiministator is an exco.
async def track_managed_group(update, context):
    old_status, new_status = update.my_chat_member.difference().get("status")
    adder = update.my_chat_member.from_user.id
    if old_status == ChatMember.MEMBER and new_status == ChatMember.ADMINISTRATOR and botdb.verify_admin(adder):
        # the bot has just been made an admin
        group_id = update.my_chat_member.chat.id
        group_title = update.my_chat_member.chat.title
        chat_invite_link_obj = await context.bot.create_chat_invite_link(
            group_id, creates_join_request=True)
        join_link = chat_invite_link_obj.invite_link
        botdb.update_managed_groups(group_id, group_title, join_link)
        await context.bot.send_message(
            adder, f"Group {group_title} is now being managed automatically by the bot!")


async def validate_join_req_handler(update, context):
    logging.info(f"Update: {update}, Context: {context}")
    pass


async def start_handler(update, context):
    await update.message.reply_text("hiya loser welcome to the club")


if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-t", help="Testing mode flag.")
    # args= parser.parse_args()

    bot_token: str = os.environ.get("TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(bot_token).build()

    # This handler listens to updates to the bot only.
    app.add_handler(ChatMemberHandler(track_managed_group, block=False))
    app.add_handler(ChatJoinRequestHandler(
        validate_join_req_handler, block=False))

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("testAuth", auth_test_handler))
    app.add_handler(CommandHandler("groups", list_groups))

    app.add_handler(MessageHandler(filters.ALL, message_handler))

    app.run_polling()
