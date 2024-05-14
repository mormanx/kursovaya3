

from api_client import HeadHunterAPI
from storage import JSONVacancyStorage, get_salary
from vacancy import Vacancy

def user_interaction(api: HeadHunterAPI, storage: JSONVacancyStorage):
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
            vacancy_objects = [Vacancy(vacancy['name'], vacancy['alternate_url'], get_salary(vacancy['salary']), vacancy.get('description', '')) for vacancy in vacancies]
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

if __name__ == "__main__":
    api = HeadHunterAPI()
    storage = JSONVacancyStorage("vacancies.json")
    user_interaction(api, storage)