import os
import logging
import database.dbcontext as botdb
from database.exco_roles import Exco
from utils.utils import test_valid_otp, test_valid_nus_email
from cache.cache import otp_cache, authenticated_users_cache, Otp
from datetime import datetime
from auth.auth_context import send_otp
from telegram import ChatMember
from telegram.ext import (
    ApplicationBuilder,
    ChatJoinRequestHandler,
    ChatMemberHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

# logging
logging.basicConfig(
    # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    level=logging.INFO,
    # Define the log message format
    format="%(asctime)s - %(levelname)s - %(message)s",
    # filename='bot.log',  # Specify the log file
    # filemode='a'  # Append mode (append new logs to the end of the file)
)

logging.getLogger("httpx").setLevel(logging.WARNING)


def require_auth(handler):
    async def wrapper(update, context):
        if botdb.authenticate_user_with_telegram(
            update.message.from_user.username, update.message.from_user.id
        ):
            return await handler(update, context)
        return await update.message.reply_text("Please login using /login.")

    return wrapper


async def message_handler(update, context):
    await update.message.reply_text("stuff")


@require_auth
async def list_groups(update, context):
    groups = botdb.get_groups()
    groups = "\n".join(
        [f"{group["title"]}\n{group["join_link"]}\n" for group in groups]
    )
    logging.info(
        f"""User {update.message.from_user.username}
        requested for group links. Returning groups:\n{groups}"""
    )
    await update.message.reply_text(f"Available groups:\n\n{groups}")


@require_auth
async def auth_test_handler(update, context):
    await update.message.reply_text("you are authenticated")


# This handler listens to updates to the bot status only, and if the update is
# one to promote the bot to an administator, it will add the group to the list
# of groups it manage if the user adding the bot as adiministator is an exco.
async def track_managed_group(update, context):
    _, new_status = update.my_chat_member.difference().get("status")
    adder = update.my_chat_member.from_user.id

    # check if the bot has just been made a group admin
    # by a member of the prescell
    #
    # We are also praying that the admin gives the bot the
    # invite user permission else the bot won't work either
    #
    # TODO: add code to verify that bot has invite user permissions
    if (
        new_status == ChatMember.ADMINISTRATOR
        and botdb.verify_admin_by_sufficient_authority(adder, Exco.PRESCELL)
    ):
        group_id = update.my_chat_member.chat.id
        group_title = update.my_chat_member.chat.title

        # Create a new join link for the group as the bot cannot
        # retrieve existing join links
        chat_invite_link_obj = await context.bot.create_chat_invite_link(
            group_id, creates_join_request=True
        )
        join_link = chat_invite_link_obj.invite_link

        botdb.update_managed_groups(group_id, group_title, join_link)
        await context.bot.send_message(
            adder,
            f"""Group {group_title} is now being managed automatically
            by the bot. Invite link for the group is {join_link}.""",
        )


async def validate_join_req_handler(update, context):
    request = update.chat_join_request
    if botdb.authenticate_user_with_telegram(request.user.username, request.user.id):
        context.bot.approve_chat_join_request(request.chat.id, request.user.id)
    else:
        await context.bot.send_message(
            request.user_chat_id, "Please login using /login."
        )


EMAIL, OTP = range(2)


async def begin_email_auth_handler(update, context):
    await update.message.reply_text(
        """Please send me your nus email that you used to sign up with NUSCAS :)
        \nSend me /cancel to cancel the login process."""
    )
    return EMAIL


async def get_email_handler(update, context):
    email = update.message.text

    if not test_valid_nus_email(email):
        await update.messge.reply_text("Please input a valid nus email!")
        return EMAIL

    if not botdb.verify_email(email):
        await update.message.reply_text(
            """You don't appear to be registered member of CAS :(
            \nPlease contact our Treasurer or Secretary if there is a mistake."""
        )

    otp = send_otp(email)

    # Side note but I don't really like how the dependencies are lookings here
    # but fuck it ill fix this shit later or smth
    otp_cache[update.message.from_user.id] = Otp(email, otp[0], otp[1])

    await update.message.reply_text(
        f"""OTP has been sent to {email}.
        \nPlease send me your OTP within 5 minutes."""
    )
    return OTP


async def otp_handler(update, context):
    no_existing_otp_msg = (
        "Something has went wrong, please request for an OTP again by sending /login."
    )
    incorrect_otp_msg = "Please enter the correct OTP!"
    expired_otp_message = (
        "Your OTP has expired. Please get a new one by sending /login."
    )

    correct_otp = otp_cache.get(update.message.from_user.id)
    otp = update.message.text

    # Something has went terribly wrong here, if they can be here in this part
    # of the conversation without a cached otp.
    if not correct_otp:
        await update.message.reply_text(no_existing_otp_msg)
        return ConversationHandler.END

    if not test_valid_otp(otp):
        await update.message.reply_text(incorrect_otp_msg)
        return OTP

    if correct_otp.expires_at < datetime.now():
        await update.message.reply_text(expired_otp_message)
        return ConversationHandler.END

    if otp != correct_otp.otp:
        await update.message.reply_text(incorrect_otp_msg)
        return OTP

    assert otp == correct_otp.otp
    user_id = update.message.from_user.id
    username = update.message.from_user.username

    botdb.update_user_telegram(correct_otp.email, user_id, username)
    authenticated_users_cache.add(user_id)

    await update.message.reply_text(
        "You're logged in now! Join us at our various interest groups! :) "
    )
    return ConversationHandler.END


async def cancel_login_handler(update, context):
    await update.message.reply_text("login cancelled")
    return ConversationHandler.END


async def start_handler(update, context):
    await update.message.reply_text("hiya loser welcome to the club")


if __name__ == "__main__":
    botdb.update_exco_roles()

    bot_token: str = os.environ.get("TELEGRAM_BOT_TOKEN")

    app = ApplicationBuilder().token(bot_token).build()

    # This handler listens to updates to the bot only.
    app.add_handler(ChatMemberHandler(track_managed_group, block=False))

    # This handler automatically approves valid chat join requests.
    app.add_handler(ChatJoinRequestHandler(
        validate_join_req_handler, block=False))

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("testAuth", auth_test_handler))
    app.add_handler(CommandHandler("groups", list_groups))

    # Login conversation handler.
    app.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("login", begin_email_auth_handler)],
            states={
                EMAIL: [MessageHandler(filters.TEXT, get_email_handler)],
                OTP: [MessageHandler(filters.TEXT, otp_handler)],
            },
            fallbacks=[CommandHandler("cancel", cancel_login_handler)],
            conversation_timeout=300,
        )
    )

    app.add_handler(MessageHandler(filters.TEXT, message_handler))

    app.run_polling()
