import json
from abc import ABC, abstractmethod
from typing import List
from vacancy import Vacancy

class VacancyStorage(ABC):
    """Абстрактный класс для работы с хранилищем вакансий."""
    @abstractmethod
    def add_vacancies(self, vacancies: List[Vacancy]):
        pass

    @abstractmethod
    def get_vacancies(self, filters: dict) -> List[Vacancy]:
        pass

    @abstractmethod
    def remove_vacancies(self, filters: dict):
        pass

class JSONVacancyStorage(VacancyStorage):
    """Класс для работы с JSON-файлом."""
    def __init__(self, file_path):
        self.file_path = file_path
        self.vacancies = []
        self.load_vacancies()

    def load_vacancies(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                vacancy_dicts = json.load(file)
                self.vacancies = [Vacancy(**vacancy_dict) for vacancy_dict in vacancy_dicts]
        except (FileNotFoundError, json.JSONDecodeError):
            self.vacancies = []

    def save_vacancies(self):
        with open(self.file_path, "w", encoding="utf-8") as file:
            vacancy_dicts = [
                {
                    "title": vacancy.title,
                    "url": vacancy.url,
                    "salary": vacancy.salary,
                    "description": vacancy.description,
                }
                for vacancy in self.vacancies
            ]
            json.dump(vacancy_dicts, file, ensure_ascii=False, indent=2)

    def add_vacancies(self, vacancies: List[Vacancy]):
        self.vacancies.extend(vacancies)
        self.save_vacancies()

    def get_vacancies(self, filters: dict) -> List[Vacancy]:
        filtered_vacancies = self.vacancies.copy()
        if "keyword" in filters:
            keyword = filters["keyword"].lower()
            filtered_vacancies = [
                vacancy
                for vacancy in filtered_vacancies
                if keyword in vacancy.title.lower() or keyword in vacancy.description.lower()
            ]
        if "top_n" in filters:
            top_n = filters["top_n"]
            filtered_vacancies.sort(reverse=True)
            filtered_vacancies = filtered_vacancies[:top_n]
        if "description_only" in filters and filters["description_only"]:
            keyword = filters["keyword"].lower()
            filtered_vacancies = [
                vacancy
                for vacancy in filtered_vacancies
                if keyword in vacancy.description.lower()
            ]
            print("Отфильтрованные вакансии:")
            for vacancy in filtered_vacancies:
                print(vacancy)
        return filtered_vacancies

    def remove_vacancies(self, filters: dict):
        if "keyword" in filters:
            keyword = filters["keyword"].lower()
            self.vacancies = [
                vacancy
                for vacancy in self.vacancies
                if keyword not in vacancy.title.lower() and keyword not in vacancy.description.lower()
            ]
        self.save_vacancies()

def get_salary(salary_dict):
    if salary_dict is None:
        return "Зарплата не указана"
    elif "value" in salary_dict:
        return salary_dict["value"]
    elif "from" in salary_dict and "to" in salary_dict:
        return f"от {salary_dict['from']} до {salary_dict['to']}"
    else:
        return "Зарплата не указана"