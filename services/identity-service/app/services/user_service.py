
class UserService:
    def __init__(self, repo):
        self.repo = repo

    async def create_user(self, data):
        user_dict = data.dict()
        return await self.repo.create(user_dict)

    async def list_users(self):
        return await self.repo.list()

    async def get_user(self, user_id):
        return await self.repo.get(user_id)

    async def update_user(self, user_id, data):
        return await self.repo.edit(user_id, data.dict())

    async def delete_user(self, user_id):
        return await self.repo.delete(user_id)
