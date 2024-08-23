from abc import ABC, abstractmethod

class BaseService(ABC):
    """
    Абстрактный базовый класс для всех сервисов получения номеров и SMS.
    Все сервисы должны реализовать этот интерфейс.
    """

    @abstractmethod
    async def fetch_numbers(self, session):
        """
        Метод для получения списка номеров.
        """
        pass

    @abstractmethod
    async def fetch_sms(self, session, number):
        """
        Метод для получения последних SMS для заданного номера.
        """
        pass

    @abstractmethod
    def get_supported_countries(self):
        """
        Метод для получения списка поддерживаемых стран.
        """
        pass
