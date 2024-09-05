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


def authenticate_club_membership(user_id, username):
    return (
        supabase.rpc(
            "authenticate_club_membership",
            {"user_id": user_id, "username": username},
        )
        .execute()
        .data
    )


def get_groups_titles():
    return supabase.table("groups").select("*").execute().data
