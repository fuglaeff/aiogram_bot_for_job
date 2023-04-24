from datetime import date

from pydantic import BaseModel, Field


class RateInfo(BaseModel):
    rate: float


class RateQuery(BaseModel):
    amount: float
    from_: str = Field(alias='from')
    to: str


class ExchangeModel(BaseModel):
    """
    Pydantic модель для работы с json ответами от API
    """
    date: date
    info: RateInfo
    query: RateQuery
    result: float
    success: bool

    def make_text_message(self) -> str:
        # формируем сообщение
        return (f'{self.date}\n' +
                f'{self.query.amount} {self.query.from_} -> {self.result} {self.query.to}\n\n' +
                f'1 {self.query.from_} -> {self.info.rate} {self.query.to}\n' +
                f'1 {self.query.to} -> {round(1 / self.info.rate, 6)} {self.query.from_}'
                )
