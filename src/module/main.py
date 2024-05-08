import json
import requests
from abc import ABC, abstractmethod
from typing import List


# Абстрактный класс для работы с API сервиса вакансий
class VacancyAPI(ABC):
    @abstractmethod
    def get_vacancies(self, query: str) -> List[dict]:
        pass


# Класс для работы с API hh.ru
class HeadHunterAPI(VacancyAPI):
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


# Класс для работы с вакансиями
class Vacancy:
    def __init__(self, title: str, url: str, salary: str, description: str):
        self.title = title
        self.url = url
        self.salary = self.validate_salary(salary)
        self.description = description

    def validate_salary(self, salary: str) -> str:
        if not salary:
            return "Зарплата не указана"
        else:
            return salary.replace("\u202f", "")

    def __repr__(self):
        return f"Vacancy('{self.title}', '{self.url}', '{self.salary}', '{self.description[:20]}...')"

    def __lt__(self, other):
        if self.salary == "Зарплата не указана":
            return True
        elif other.salary == "Зарплата не указана":
            return False
        else:
            try:
                self_salary = int(self.salary.replace(" ", ""))
            except ValueError:
                self_salary = 0
            try:
                other_salary = int(other.salary.replace(" ", ""))
            except ValueError:
                other_salary = 0
            return self_salary < other_salary


# Абстрактный класс для работы с хранилищем вакансий
class VacancyStorage(ABC):
    @abstractmethod
    def add_vacancies(self, vacancies: List[Vacancy]):
        pass

    @abstractmethod
    def get_vacancies(self, filters: dict) -> List[Vacancy]:
        pass

    @abstractmethod
    def remove_vacancies(self, filters: dict):
        pass


# Класс для работы с JSON-файлом
class JSONVacancyStorage(VacancyStorage):
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


# Функция для извлечения зарплаты из словаря вакансии
def get_salary(salary_dict):
    if salary_dict is None:
        return "Зарплата не указана"
    elif "value" in salary_dict:
        return salary_dict["value"]
    elif "from" in salary_dict and "to" in salary_dict:
        return f"от {salary_dict['from']} до {salary_dict['to']}"
    else:
        return "Зарплата не указана"


# Функция для взаимодействия с пользователем
def user_interaction(api: VacancyAPI, storage: VacancyStorage):
    while True:
        print("\nВыберите действие:")
        print("1. Ввести поисковый запрос")
        print("2. Получить топ N вакансий по зарплате")
        print("3. Получить вакансии с ключевым словом в описании")
        print("4. Удалить вакансии с ключевым словом")
        print("0. Выход")

        choice = input("Введите номер действия: ")

        if choice == "1":
            query = input("Введите поисковый запрос: ")
            vacancies = api.get_vacancies(query)
            vacancy_objects = [Vacancy(vacancy['name'], vacancy['alternate_url'], get_salary(vacancy['salary']),
                                       vacancy.get('description', '')) for vacancy in vacancies]
            storage.vacancies = []  # Очистка списка вакансий
            storage.add_vacancies(vacancy_objects)
            print(f"Добавлено {len(vacancy_objects)} вакансий.")

        elif choice == "2":
            top_n = int(input("Введите количество вакансий для вывода: "))
            filtered_vacancies = storage.get_vacancies({"top_n": top_n})
            for vacancy in filtered_vacancies:
                print(vacancy)

        elif choice == "3":

            keyword = input("Введите ключевое слово: ")
            filtered_vacancies = storage.get_vacancies({"keyword": keyword, "description_only": True})
            if filtered_vacancies:  # Проверяем, есть ли отфильтрованные вакансии
                print(f"Найдено {len(filtered_vacancies)} вакансий:")
                for vacancy in filtered_vacancies:
                    print(vacancy)

            else:
                print("По вашему запросу ничего не найдено.")
                print("Доступные вакансии:")
                for vacancy in storage.vacancies:
                    print(vacancy)

        elif choice == "4":
            keyword = input("Введите ключевое слово для удаления вакансий: ")
            storage.remove_vacancies({"keyword": keyword})
            print("Вакансии удалены.")

        elif choice == "0":
            break

        else:
            print("Неверный выбор. Попробуйте еще раз.")


# Пример использования
if __name__ == "__main__":
    api = HeadHunterAPI()
    storage = JSONVacancyStorage("vacancies.json")
    user_interaction(api, storage)


