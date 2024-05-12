class Vacancy:
    """Класс для работы с вакансиями."""
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