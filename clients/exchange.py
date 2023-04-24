import os

from clients.base import BaseClient
from models import ExchangeModel


class ExchangeClient(BaseClient):
    """
    Класс, реализующий взаимодействие с API сервиса с конвертацией валют
    """

    base_url = 'https://api.apilayer.com'
    headers = {
        'apikey': os.getenv('EXCHANGE_API'),
    }
    convert_path = '/exchangerates_data/convert'

    async def convert(self, amount: float | int, from_: str, to: str) -> ExchangeModel:
        params = {
            'amount': amount,
            'from': from_,
            'to': to,
        }
        response = await self.get(self.convert_path, params=params)

        return ExchangeModel(**response)
