def has_role(user: dict, role: str) -> bool:
    return user.get("role") == role

def require_roles(user: dict, allowed_roles: list):
    if user.get("role") not in allowed_roles:
        raise Exception("Unauthorized")
