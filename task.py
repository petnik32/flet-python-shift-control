import flet as ft
import mysql.connector

# Функция для получения задач по fio
def fetch_tasks_from_db(fio):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="tolik2"
    )
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fio VARCHAR(255),
            task_description TEXT,
            task_date DATE,
            task_status VARCHAR(50)
        )
    """)
    
    # Запрос для поиска задач с совпадающим fio
    cursor.execute("SELECT id, fio, task_description, task_date, task_status FROM tasks WHERE fio = %s", (fio,))
    tasks = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return tasks

# Проверка ФИО и кода в базе данных users
def check_user_in_db(fio, code):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="tolik2"
    )
    cursor = conn.cursor(dictionary=True)

    
    cursor.execute("SELECT * FROM users WHERE fio = %s AND code = %s", (fio, code))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return user

# Открытие новой страницы с задачами, если пользователь найден
def open_task_page(page: ft.Page, fio):
    # Очистка старых задач, если они уже были отображены
    if hasattr(page, "task_list"):
        page.controls.remove(page.task_list)
    
    tasks = fetch_tasks_from_db(fio)
    
    if not tasks:
        page.add(ft.Text("Задачи не найдены для этого пользователя"))
        page.update()
        return

    task_list = ft.Column(
        controls=[
            ft.Column([
                ft.Text(
                    f"ФИО: {task['fio']}\n"
                    f"Описание: {task['task_description']}\n"
                    f"Дата: {task['task_date']}\n"
                    f"Статус: {task['task_status']}\n",
                    size=14,
                    weight=ft.FontWeight.NORMAL
                ),
                ft.Divider()  # Разделитель для каждой задачи
            ])
            for task in tasks
        ],
        spacing=10,
        scroll="adaptive"
    )
    
    page.controls.append(task_list)
    page.task_list = task_list  # Сохраняем ссылку на task_list для удаления при следующем обновлении
    page.update()

# Главная страница с полями для ввода ФИО и Кода
def main(page: ft.Page):
    page.title = "Введите ФИО и Код"
    page.window_width = 400
    page.window_height = 300
    page.scroll = "adaptive"
    
    fio_field = ft.TextField(label="Введите ФИО", autofocus=True)  # Поле для ввода ФИО
    code_field = ft.TextField(label="Введите Код")  # Поле для ввода кода
    result_text = ft.Text("")  # Место для вывода результата
    
    # Функция проверки данных и открытия второй формы с задачами
    def check_user_and_open_tasks(e):
        fio = fio_field.value.strip()
        code = code_field.value.strip()
        
        if not fio or not code:
            result_text.value = "Пожалуйста, заполните все поля!"
            page.update()
            return
        
        user = check_user_in_db(fio, code)
        
        if user:
            # Если пользователь найден, открываем страницу с задачами
            result_text.value = f"Пользователь {fio} найден. Загружаем задачи..."
            page.update()
            open_task_page(page, fio)
        else:
            result_text.value = "Пользователь не найден. Проверьте данные."
            page.update()

    submit_button = ft.ElevatedButton("Показать задачи", on_click=check_user_and_open_tasks)  # Кнопка для поиска задач
    
    page.add(fio_field, code_field, submit_button, result_text)

ft.app(target=main)
