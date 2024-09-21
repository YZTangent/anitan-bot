import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# Ideally for users authenticating with the bot for the first time,
# but realistically we have no way of knowing.
# This function checks if the user's username exists in the users table
# with no corresponding telegram id. If true, sets the telegram ID
# and returns trues.
#
# This function should only be called after authenticate_member_by_id
# returns false.
def authenticate_member_by_username_and_set_id(username, user_id):
    return (
        supabase.rpc(
            "authenticate_member_by_username_and_set_id",
            {"user_id": user_id, "username": username},
        )
        .execute()
        .data
    )


# The source of truth of authentication.
#
# The use's telegram ID is checked against the telegram ID column in the database.
# If the user's telegram ID exists in the users table, we can be sure they are
# an authenticated user.
def authenticate_member_by_id(user_id):
    return (
        supabase.rpc(
            "authenticate_member_by_id",
            {"user_id": user_id},
        )
        .execute()
        .data
    )


def verify_admin(user_id):
    return supabase.rpc("verify_admin", {"user_id": user_id}).execute().data


def update_managed_groups(group_id, group_title, join_link):
    return (
        supabase.table("groups")
        .upsert({"id": group_id, "title": group_title, "join_link": join_link})
        .execute()
        .data
    )


def get_groups():
    return supabase.table("groups").select("title, join_link").execute().data


def verify_email(email):
    return supabase.rpc("verify_email", {"email": email}).execute().data


def update_user_telegram(email, user_id, username):
    return (
        supabase.table("users")
        .update({"telegram_username": username, "telegram_id": user_id})
        .eq("nus_email", email)
        .execute()
    )


# def get_groups_id_by_title(title):
#     return supabase.table("groups").select("id").eq("title", title).execute().data
