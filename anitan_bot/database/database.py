import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


def get_user_by_telegram_id(user_id):
    return supabase.table("users").select("*").eq("telegram_id", user_id).single().data


def get_user_by_telegram_handle(username):
    return (
        supabase.table("users")
        .select("*")
        .eq("telegram_username", username)
        .single()
        .execute()
        .data
    )


def authenticate_member_by_username_and_set_id(username, user_id):
    return (
        supabase.rpc(
            "authenticate_member_by_username_and_set_id",
            {"user_id": user_id, "username": username},
        )
        .execute()
        .data
    )


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
    return supabase.table("groups").upsert({"id": group_id, "title": group_title, "join_link": join_link}).execute().data


def get_groups():
    return supabase.table("groups").select("title, join_link").execute().data


# def get_groups_id_by_title(title):
#     return supabase.table("groups").select("id").eq("title", title).execute().data
