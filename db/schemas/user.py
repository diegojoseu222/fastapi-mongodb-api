def user_schema(user) -> dict:
    return {
     "id": str(user["_id"]),
     "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "disabled": user["disabled"]
    }

# Mapea una lista de documentos de MongoDB
def users_schema(users) -> list:
    return [user_schema(user) for user in users]