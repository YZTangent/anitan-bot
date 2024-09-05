import database.database as db
import asyncio

if __name__ == "__main__":
    user = db.authenticate_club_membership(111, "yztangent")
    print(user)
