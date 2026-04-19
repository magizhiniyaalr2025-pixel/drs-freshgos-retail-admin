from app.core.security import verify_password, create_token

class AuthService:
    def __init__(self, repo):
        self.repo = repo

    async def login(self, email, password):
        user = await self.repo.get_by_email(email)

        if not user or not verify_password(password, user["password"]):
            raise Exception("Invalid credentials")

        return create_token({
            "sub": user["email"],
            "role": user.get("role", "user")
        })
