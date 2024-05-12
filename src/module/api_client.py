import requests
from abc import ABC, abstractmethod
from typing import List

class VacancyAPI(ABC):
    """Абстрактный класс для работы с API сервиса вакансий."""
    @abstractmethod
    def get_vacancies(self, query: str) -> List[dict]:
        pass

class HeadHunterAPI(VacancyAPI):
    """Класс для работы с API hh.ru."""
    def __init__(self):
        self.base_url = "https://api.hh.ru/vacancies"
        self.headers = {'User-Agent': 'HH-User-Agent'}
        self.params = {
            "text": "",
            "page": 0,
            "per_page": 100,
        }
        self.vacancies = []

    def get_vacancies(self, query: str) -> List[dict]:
        self.params["text"] = query
        vacancies = []
        for page in range(20):
            self.params["page"] = page
            response = requests.get(self.base_url, headers=self.headers, params=self.params)
            response.raise_for_status()
            data = response.json()
            vacancies.extend(data["items"])
            if not data["pages"]:
                break
        return vacancies