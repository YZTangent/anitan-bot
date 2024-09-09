import database as db


def require_auth(func):
    async def wrapper(update, context):
        msg = update.message
        if db.authenticate_club_membership_by_id(
            msg.from_user.id
        ) or db.authenticate_club_membership(msg.from_user.id, msg.from_user.username):
            return await func(update, context)
        else:
            return await msg.reply_text("sir pls sign up 4 cas :(")

    return wrapper


async def start_handler(update, context):
    await update.message.reply_text("hiya loser welcome to the club")
