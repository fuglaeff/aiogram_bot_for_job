from clients.base import BaseClient


class DuckClient(BaseClient):
    """
    Класс, реализующий взаимодействие с API сервиса с картинками
    """

    base_url = 'https://random-d.uk'
    picture_path = '/api/random'

    async def get_duck(self) -> tuple[str, str]:
        resource = await self.get(self.picture_path, {})
        duck_url = resource['url']
        return duck_url[-3:], duck_url
