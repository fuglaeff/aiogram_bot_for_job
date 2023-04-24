import logging
from typing import Any

from aiohttp import ClientSession, ClientResponseError


class ClientException(Exception):
    """
    Кастомная ошибка для всех HTTP ошибок
    """
    def __str__(self):
        return 'Что-то случилось на удаленном сервере, попробуйте позже'


class BaseClient:
    """
    Базовый класс для взаимодействия с внешними сервисами,
    реализующий вариант GET запроса
    """

    base_url: str | None = None
    headers: dict[str, Any] | None = None
    base_params: dict[str, Any] = {}

    async def get(
        self,
        url: str,
        params: dict[str, Any]
    ) -> dict[str, Any] | list[dict[str, Any]]:
        if self.base_url == '':
            raise Exception('Базовый url должен быть не пустым')

        async with ClientSession(
                base_url=self.base_url, headers=self.headers, raise_for_status=True) as session:
            try:
                return await self._get_response(session, url, params)
            except ClientResponseError as ex:
                logging.error(ex)
                raise ClientException() from ex

    async def _get_response(
        self,
        session: ClientSession,
        url: str,
        params: dict[str, Any]
    ) -> dict[str, Any] | list[dict[str, Any]]:
        async with session.get(url=url, params={**params, **self.base_params}) as response:
            return await response.json()
