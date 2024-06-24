from typing import Any, Optional, List
from datetime import datetime, timedelta
import pytz

from .field import Field

from exception.core.models import field


class DateTimeField(Field):
    """
    DATETIME FIELD
    ==============
    Field pour les dates et heures
    """

    def __init__(
        self,
        format: Optional[List[str]] = ['%Y-%m-%d %H:%M:%S'],
        tz: Optional[str] = None,
        max_datetime: Optional[datetime] = None,
        min_datetime: Optional[datetime] = None,
        auto_updated: bool = False,
        auto_created: bool = False,
        nullable: bool = True,
        default: datetime | None = None,
        primary_key: bool = False,
        unique: bool = False,
        editable: bool = True,
    ):
        super().__init__(
            nullable=nullable,
            default=default,
            primary_key=primary_key,
            unique=unique,
            editable=editable,
        )
        self._format = format
        self._tz = tz
        self._min_datetime = min_datetime
        self._max_datetime = max_datetime
        self._auto_update = auto_updated
        self._auto_created = auto_created
        if self._auto_created:
            self._value = datetime.now().strftime(self._format[0])

    def __set__(self, instance, value):
        if isinstance(value, str):
            value = self.__parse_datetime(value)
        return super().__set__(instance, value)

    def _validated(self, value: Any) -> bool:
        if not self._validated(value):
            raise field.DateTimeFieldValidationError("Invalid datetime value")
        if self._min_datetime and value < self._min_datetime:
            raise field.DateTimeFieldValidationError(
                f"Date cannot be earlier than {self._min_date}")
        if self._max_datetime and value > self._max_datetime:
            raise field.DateTimeFieldValidationError(f"Date cannot be later than {self._max_date}")
        return super()._validated(value)

    def __parse_datetime(self, value: str) -> datetime:
        for fmt in self._format:
            try:
                dt = datetime.strptime(value, fmt)
                if self._tz:
                    tz = pytz.timezone(self._tz)
                    dt = tz.localize(dt)
                return dt
            except ValueError:
                continue
        raise field.FieldValidationError(f"Datetime format should be one of {self.formats}")

    def load(self, value: str) -> datetime:
        return self.__parse_datetime(value)

    def dump(self) -> str:
        return self._value.strftime(self._format[0])

    def __contains__(self, item: datetime) -> bool:
        return self._min_datetime <= item <= self._max_datetime

    def __lt__(self, other: datetime) -> bool:
        return self._value < other

    def __le__(self, other: datetime) -> bool:
        return self._value <= other

    def __gt__(self, other: datetime) -> bool:
        return self._value > other

    def __ge__(self, other: datetime) -> bool:
        return self._value >= other

    def __add__(self, other: timedelta) -> datetime:
        return self._value + other

    def __sub__(self, other: timedelta) -> datetime:
        return self._value - other

    def __iadd__(self, other: timedelta) -> 'DateTimeField':
        self._value = self.__add__(other)
        return self

    def __isub__(self, other: timedelta) -> 'DateTimeField':
        self._value = self.__sub__(other)
        return self
