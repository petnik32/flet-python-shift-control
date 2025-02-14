import flet as ft
import mysql.connector
import sys
from datetime import datetime, timedelta


# Подключение к базе данных
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="tolik2"
    )

def load_login_logs():
    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, fio, login_time, success, error_message FROM login_logs"  # Запрос для извлечения данных
        cursor.execute(query)
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        return logs
    except Exception as ex:
        print(f"Ошибка загрузки логов входа: {ex}")
        return None


def save_shift(page, date, name):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = "INSERT INTO shifts (date, fio) VALUES (%s, %s)"
        cursor.execute(query, (date, name))
        conn.commit()
        cursor.close()
        conn.close()
        
        page.snack_bar = ft.SnackBar(ft.Text("Смена сохранена!"), bgcolor=ft.colors.GREEN)
        page.snack_bar.open = True
        page.update()
    except Exception as ex:
        page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка сохранения: {ex}"), bgcolor=ft.colors.RED)
        page.snack_bar.open = True
        page.update()

def load_shifts():
    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, fio, date FROM shifts ORDER BY date DESC"  # Сортировка по убыванию даты
        cursor.execute(query)
        shifts = cursor.fetchall()
        cursor.close()
        conn.close()
        return shifts
    except Exception as ex:
        print(f"Ошибка загрузки смен: {ex}")
        return []



def load_users_for_date(selected_date):
    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT fio FROM user_dates WHERE date_selected = %s"
        cursor.execute(query, (selected_date,))
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users
    except Exception as ex:
        print(f"Ошибка загрузки пользователей для даты {selected_date}: {ex}")
        return []

def load_results():
    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, name, correct_answers FROM results"  
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as ex:
        print(f"Ошибка загрузки смен: {ex}")
        return []

def load_tasks():
    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, fio, task_description, task_date, task_status FROM tasks"  
        cursor.execute(query)
        tasks = cursor.fetchall()
        cursor.close()
        conn.close()
        return tasks
    except Exception as ex:
        print(f"Ошибка загрузки смен: {ex}")
        return []
    
# Функция для расчета стажа
def calculate_experience(hire_date):
    if not hire_date:
        return "Нет данных"
    hire_date = datetime.strptime(str(hire_date), "%Y-%m-%d")
    today = datetime.today()
    years = today.year - hire_date.year
    months = today.month - hire_date.month
    days = today.day - hire_date.day

    if days < 0:
        months -= 1
        days += 30
    if months < 0:
        years -= 1
        months += 12

    return f"{years} лет, {months} мес., {days} дн."

def close_dialog(page):
    page.dialog.open = False
    page.update()
   

# Функция для генерации столбцов таблицы
def generate_table_columns(column_names):
    return [ft.DataColumn(ft.Text(name)) for name in column_names]

# Основная функция
def main(page: ft.Page):
    user_code = sys.argv[1]
    fio = sys.argv[2]

    page.window_resizable = False
    page.window_width = 1300  # Ширина окна
    page.window_height = 750  # Высота окна
    page.window_center() 
    
    page.title = f"Личный кабинет - {fio}"


    def open_shift_calendar(page):
        today = datetime.today()
        dates = [today + timedelta(days=i) for i in range(30)]  # Список дат на 30 дней вперед
        
        def select_date(e):
            selected_date = e.control.data
            fio_input = ft.TextField(label="Введите ФИО", width=300)

            # Загрузка всех пользователей, привязанных к выбранной дате
            users_on_date = load_users_for_date(selected_date)  # Функция для загрузки пользователей, связанных с выбранной датой
            if not users_on_date:
                users_on_date = [{"fio": "Нет данных"}]  # Если пользователей нет, отображаем "Нет данных"

            # Создаем текст с ФИО всех пользователей
            user_info = ft.Column(controls=[ft.Text(f"ФИО: {user['fio']}", size=16) for user in users_on_date])

            save_button = ft.ElevatedButton(
                text="Сохранить смену",
                on_click=lambda _: save_shift(page, selected_date, fio_input.value)
            )

            # Диалог с данными о пользователях
            page.dialog = ft.AlertDialog(
                title=ft.Text("Проставление смен"),
                content=ft.Column([fio_input, user_info, save_button]),
                actions=[ft.TextButton("Закрыть", on_click=lambda _: close_dialog(page))]
            )
            page.dialog.open = True
            page.update()

    

        # Формируем календарь с тремя кнопками в одном ряду
        calendar_controls = []
        for i in range(0, len(dates), 3):
            row_controls = []
            for date in dates[i:i + 3]:
                row_controls.append(
                    ft.ElevatedButton(
                        text=date.strftime("%d.%m.%Y"),
                        on_click=select_date,
                        data=date.strftime("%Y-%m-%d")
                    )
                )
            calendar_controls.append(ft.Row(controls=row_controls, alignment="center", spacing=10))

        # Диалог с календарем
        page.dialog = ft.AlertDialog(
            title=ft.Text("Календарь смен"),
            content=ft.Column(calendar_controls, scroll="auto"),
            actions=[ft.TextButton("Закрыть", on_click=lambda _: close_dialog(page))]
        )

        page.dialog.open = True
        page.update()

    def select_task_date(e): 
        fio_input = ft.TextField(label="Введите ФИО", width=300)
        task_description_input = ft.TextField(label="Описание задачи", width=300)
        task_status_input = ft.Dropdown(
            label="Статус задачи", 
            options=[ft.dropdown.Option("Не начата"), ft.dropdown.Option("В процессе"), ft.dropdown.Option("Завершена")]
        )

        # Загрузка всех задач (без фильтрации по дате)
        tasks_on_date = load_tasks_for_date()  # Функция для загрузки всех задач
        if not tasks_on_date:
            tasks_on_date = [{"fio": "Нет данных", "task_description": "Нет задач"}]

        # Функция для обновления списка задач и включения прокрутки
        def update_task_info():
            task_info.controls = []
            
            for index, task in enumerate(tasks_on_date):
                # Добавляем текст с задачей
                task_info.controls.append(
                    ft.Text(f"ФИО: {task['fio']}, Описание: {task['task_description']}", size=16)
                )
                # Добавляем разделитель, кроме последней строки
                if index < len(tasks_on_date) - 1:
                    task_info.controls.append(ft.Divider(thickness=1, color="grey"))
            
            task_info.scroll = "auto"  # Включаем прокрутку
            page.update()  # Обновляем страницу


        # Функция сохранения задачи с валидацией
        def save_task_with_validation(page, fio, task_desc, status):
            # Проверка на заполнение обязательных полей
            if not fio or not task_desc or not status:
                page.dialog.content = ft.Text("Ошибка: Все поля должны быть заполнены!")
                page.update()
                return
            
            # Добавляем новую задачу в список
            tasks_on_date.append({
                "fio": fio,
                "task_description": task_desc,
                "status": status
            })
            
            # Обновляем информацию о задачах и выводим скролл
            update_task_info()

            # Сохраняем задачу в базе данных или в другом месте
            save_task(page, fio, task_desc, status)

        # Кнопка для сохранения задачи с обработчиком ошибок
        save_button = ft.ElevatedButton(
            text="Сохранить задачу",
            on_click=lambda _: save_task_with_validation(page, fio_input.value, task_description_input.value, task_status_input.value)
        )

        # Диалог с данными о задачах
        task_info = ft.Column(
            controls=[
                item
                for i, task in enumerate(tasks_on_date)
                for item in (
                    [ft.Text(f"ФИО: {task['fio']}, Описание: {task['task_description']}", size=16)] +
                    ([ft.Divider(thickness=1, color="grey")] if i < len(tasks_on_date) - 1 else [])
                )
            ],
            scroll="auto"  # Включаем прокрутку по умолчанию
        )


        page.dialog = ft.AlertDialog(
            title=ft.Text("Проставление задач"),
            content=ft.Column([fio_input, task_description_input, task_status_input, task_info, save_button]),
            actions=[ft.TextButton("Закрыть", on_click=lambda _: close_dialog(page))]
        )
        page.dialog.open = True
        page.update()



    def load_user_data():
        try:
            conn = connect_to_db()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT fio, age, hire_date, department FROM users WHERE code = %s"
            cursor.execute(query, (user_code,))
            data = cursor.fetchone()
            cursor.close()
            conn.close()
            return data
        except Exception as ex:
            print(f"Ошибка загрузки данных: {ex}")
            return None

    # Загрузка дат пользователей
    def load_user_dates():
        try:
            conn = connect_to_db()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, fio, date_selected, created_at FROM user_dates"  # Добавляем 'id'
            cursor.execute(query)
            dates = cursor.fetchall()
            cursor.close()
            conn.close()
            return dates
        except Exception as ex:
            print(f"Ошибка загрузки дат: {ex}")
            return None
        
    def load_tasks_for_date():  # Убрали параметр date
        try:
            conn = connect_to_db()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, fio, task_description, task_date, task_status FROM tasks"
            cursor.execute(query)  # Теперь без условия по дате
            tasks = cursor.fetchall()
            cursor.close()
            conn.close()
            return tasks
        except Exception as ex:
            print(f"Ошибка загрузки задач: {ex}")
            return []


    # Загрузка всех пользователей
    def load_users():
        try:
            conn = connect_to_db()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, fio, age, department FROM users"  # Добавляем 'id'
            cursor.execute(query)
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            return users
        except Exception as ex:
            print(f"Ошибка загрузки данных пользователей: {ex}")
            return None


    user_data = load_user_data()

    experience_text = "Нет данных"
    if user_data and user_data.get("hire_date"):
        experience_text = calculate_experience(user_data["hire_date"])

    user_info_container = ft.Container(
        content=ft.Column(
            controls=[ 
                ft.Text(f"ФИО: {user_data['fio']}", size=16),
                ft.Text(f"Возраст: {user_data['age']}", size=16),
                ft.Text(f"Дата устройства: {user_data['hire_date']}", size=16),
                ft.Text(f"Отдел: {user_data['department']}", size=16),
                ft.Text(f"Стаж: {experience_text}", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
            ] if user_data else [
                ft.Text("Не удалось загрузить данные пользователя", size=16, color=ft.colors.RED),
            ],
            spacing=10,
        ),
        width=250,
        bgcolor=ft.colors.GREY_200,
        padding=10,
    )
    def load_med_data():
        try:
            conn = connect_to_db()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT id, fio, hire_date, safety_check, medical_certificate FROM med"
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            conn.close()
            return data
        except Exception as ex:
            print(f"Ошибка загрузки данных мед. проверок: {ex}")
            return None
    
    def delete_user_from_table(page, record_id, table_name):
        try:
            conn = connect_to_db()
            cursor = conn.cursor()

            # Формируем запрос на удаление записи по id
            query = f"DELETE FROM {table_name} WHERE id = %s"
            cursor.execute(query, (record_id,))
            conn.commit()

            cursor.close()
            conn.close()

            # Показываем сообщение об успехе
            page.snack_bar = ft.SnackBar(ft.Text("Запись удалена!"), bgcolor=ft.colors.GREEN)
            page.snack_bar.open = True
            page.update()

            # Обновление таблицы после удаления
            update_table(None)
        except Exception as ex:
            # Ошибка при удалении
            page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка удаления: {ex}"), bgcolor=ft.colors.RED)
            page.snack_bar.open = True
            page.update()

    def save_task(page, fio, task_description, task_status):
        try:
            # Получаем сегодняшнюю дату
            today_date = datetime.today().strftime('%Y-%m-%d')  # Пример формата "2025-02-07"
            
            # Подключение к базе данных
            conn = connect_to_db()
            cursor = conn.cursor()

            # SQL-запрос для вставки новой задачи в базу данных
            query = """
                INSERT INTO tasks (fio, task_description, task_date, task_status)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (fio, task_description, today_date, task_status))
            conn.commit()

            cursor.close()
            conn.close()
            
        except Exception as ex:
            print(f"Ошибка при сохранении задачи: {ex}")




    def confirm_delete(page, record_id, table_name):
        def delete_action(e):
            delete_user_from_table(page, record_id, table_name)  # Передаем record_id для удаления
            page.dialog.open = False  # Закрыть диалог
            page.update()

        def cancel_action(e):
            page.dialog.open = False  # Закрыть диалог
            page.update()

        page.dialog = ft.AlertDialog(
            title=ft.Text(f"Вы уверены, что хотите удалить запись из таблицы {table_name}?"),
            content=ft.Text("Это действие невозможно отменить."),
            actions=[
                ft.TextButton("Удалить", on_click=delete_action),
                ft.TextButton("Отмена", on_click=cancel_action)
            ]
        )
        page.dialog.open = True
        page.update()


# Обработчик нажатия на строку таблицы для вызова окна подтверждения удаления
    def on_user_row_click(e, user_id, user_fio, table_name):
        confirm_delete(e.page, user_id, table_name)

    def on_med_row_click(e, record_id):
        confirm_delete(e.page, record_id, "med")

    def on_shift_row_click(e, record_id):
        confirm_delete(e.page, record_id, "shift")

    def on_log_row_click(e, log_id):
        confirm_delete(e.page, log_id, "login_logs")
          # Передаем id для удаления
    def on_shift_row_results(e, record_id):
        confirm_delete(e.page, record_id, "results")

    def on_shift_row_tasks(e, record_id):
        confirm_delete(e.page, record_id, "tasks")



    # Переключатели для отображения данных
    toggle_user_dates = ft.Checkbox(label="Показать даты пользователей", value=True)
    toggle_users = ft.Checkbox(label="Показать пользователей", value=False)
    toggle_med_check = ft.Checkbox(label="Показать мед. проверки", value=False)
    toggle_shift_table = ft.Checkbox(label="Показать таблицу смен", value=False)
    toggle_login_logs = ft.Checkbox(label="Показать логи", value=False)
    toggle_results = ft.Checkbox(label="Показать обучение", value=False)
    toggle_tasks = ft.Checkbox(label="Показать cписок задач", value=False)

    # Определение столбцов для таблиц
    columns_db1 = ["ФИО", "Дата", "Создано"]
    columns_db2 = ["ФИО", "Возраст", "Отдел"]
    columns_med = ["ФИО", "Дата устройства", "Охрана труда", "Мед. справка"]
    columns_login_logs = ["ФИО", "Время входа", "Успех", "Сообщение об ошибке"]
    columns_results = ["ФИО", "Кол-во ответов"]
    columns_tasks = ["ФИО               ", "Задача", "Постановки задачи", "Статус"]

    table_columns = generate_table_columns(columns_db1)
    table_rows = []

    user_dates_table = ft.DataTable(
        columns=table_columns,
        rows=table_rows,
        width=900,
        bgcolor=ft.colors.GREY_300
    )
    
    def update_shift_table(e):
        shift_table.rows.clear()  # Очищаем перед обновлением
        shift_table.visible = toggle_shift_table.value  # Видимость таблицы

        if toggle_shift_table.value:
            shifts = load_shifts()
            if shifts:
                for shift in shifts:
                    shift_table.rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(shift["date"])),
                        ft.DataCell(ft.Text(shift["fio"])),
                    ]))
        
        shift_table.update()


    toggle_shift_table.on_change = update_shift_table


    scrollable_table = ft.Container(
        content=ft.Column(
            controls=[user_dates_table],
            scroll="auto"  # Добавляем прокрутку
        ),
        height=300  # Ограничиваем высоту таблицы
    )

    task_button = ft.ElevatedButton(
        text="Проставление задач",
        on_click=lambda e: select_task_date(page)  # Вызов функции только при нажатии на кнопку
    )
    
    def update_table(e):
        table_rows.clear()

        if toggle_user_dates.value:
            table_columns[:] = generate_table_columns(columns_db1)  # Обновляем заголовки
            data = load_user_dates()

            if data:
                for row in data:
                    table_rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.GestureDetector(
                            content=ft.Text(row['fio']),
                            on_tap=lambda e, user_id=row['id'], fio=row['fio']: on_user_row_click(e, user_id, fio, "user_dates")  # Передаем id
                        )),
                        ft.DataCell(ft.Text(row['date_selected'])),
                        ft.DataCell(ft.Text(row['created_at'])),
                    ]))

        elif toggle_users.value:
            table_columns[:] = generate_table_columns(columns_db2)  # Обновляем заголовки
            users = load_users()
            if users:
                for user in users:
                    table_rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.GestureDetector(
                            content=ft.Text(user['fio']),
                            on_tap=lambda e, user_id=user['id'], fio=user['fio']: on_user_row_click(e, user_id, fio, "users")  # Передаем id
                        )),
                        ft.DataCell(ft.Text(user['age'])),
                        ft.DataCell(ft.Text(user['department'])),
                    ]))

        elif toggle_med_check.value:
            table_columns[:] = generate_table_columns(columns_med)
            # Загружаем данные из мед. таблицы
            med_data = load_med_data()
            if med_data:
                for record in med_data:
                    table_rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.GestureDetector(
                            content=ft.Text(record['fio']),
                            on_tap=lambda e, record_id=record['id']: on_med_row_click(e, record_id)  # Передаем record_id
                        )),
                        ft.DataCell(ft.Text(record['hire_date'] if record['hire_date'] else "Нет данных")),
                        ft.DataCell(ft.Text(record['safety_check'] if record['safety_check'] else "Нет данных")),
                        ft.DataCell(ft.Text(record['medical_certificate'] if record['medical_certificate'] else "Нет данных"))
                    ]))

        elif toggle_shift_table.value:
            # Загружаем данные для смен
            shifts = load_shifts()
            if shifts:
                for shift in shifts:
                    shift_table.rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.Text(shift['date'])),
                        ft.DataCell(ft.GestureDetector(
                            content=ft.Text(shift['fio']),
                            on_tap=lambda e, shift_id=shift['id']: on_shift_row_click(e, shift_id)  # Передаем shift_id
                        )),
                    ]))

        elif toggle_login_logs.value:
            table_columns[:] = generate_table_columns(columns_login_logs)  # Обновляем заголовки для login_logs
            logs = load_login_logs()  # Загружаем данные из таблицы login_logs
            
            if logs:
                for log in logs:
                    table_rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.GestureDetector(
                            content=ft.Text(log['fio']),
                            on_tap=lambda e, log_id=log['id']: on_log_row_click(e, log_id)  # Передаем id лога
                        )),
                        ft.DataCell(ft.Text(log['login_time'])),
                        ft.DataCell(ft.Text("Успех" if log['success'] else "Неудача")),
                        ft.DataCell(ft.Text(log['error_message'] if log['error_message'] else "Нет данных")),
                    ]))
                    
        elif toggle_results.value:
            table_columns[:] = generate_table_columns(columns_results)  # Обновляем заголовки для результатов обучения
            results = load_results()  # Загружаем данные из таблицы результатов обучения
            
            if results:
                for result in results:
                    table_rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.GestureDetector(
                            content=ft.Text(str(result['name'])),
                            on_tap=lambda e, result_id=result['id']: on_shift_row_results(e, result_id)  # Передаем id результата
                        )),
                       
                        ft.DataCell(ft.Text(str(result['correct_answers']))),
                    ]))

        elif toggle_tasks.value:
            table_columns[:] = generate_table_columns(columns_tasks)  # Обновляем заголовки для задач
            tasks = load_tasks()  # Загружаем данные из таблицы задач

            if tasks:
                for task in tasks:
                    table_rows.append(ft.DataRow(cells=[
                        ft.DataCell(ft.GestureDetector(
                            content=ft.Text(
                                str(task['fio']),
                                size=12,
                                max_lines=3,  # Ограничиваем количество строк
                                overflow="clip"  # Обрезаем текст, если он превышает допустимое количество строк
                            ),
                            on_tap=lambda e, task_id=task['id']: on_shift_row_tasks(e, task_id)
                        )),

                        ft.DataCell(ft.Text(task['task_description'])),
                        ft.DataCell(ft.Text(task['task_date'])),
                        ft.DataCell(ft.Text(task['task_status'])),
                    ]))


        user_dates_table.update()


    def check_galoche_changes():
        if not toggle_user_dates.value and not toggle_users.value and not toggle_med_check.value and not toggle_login_logs.value and not toggle_results.value and not toggle_tasks.value:
            error_text = ft.SnackBar(ft.Text("Внимание! У вас не выбрана ни одна таблица"), open=True)
            page.add(error_text)
            page.update()
            toggle_user_dates.value = True
            toggle_users.value = False
            toggle_med_check.value = False
            update_table(None)
            page.add(ft.Text("", size=0))
            page.update()
            page.remove(error_text)

    toggle_user_dates.on_change = lambda e: (update_table(e), check_galoche_changes())
    toggle_users.on_change = lambda e: (update_table(e), check_galoche_changes())
    toggle_med_check.on_change = lambda e: (update_table(e), check_galoche_changes())
    toggle_login_logs.on_change = lambda e: (update_table(e), check_galoche_changes())
    toggle_results.on_change = lambda e: (update_table(e), check_galoche_changes())
    toggle_tasks.on_change = lambda e: (update_table(e), check_galoche_changes())

    shift_button = ft.ElevatedButton(
        text="Проставление смен",
        on_click=lambda _: open_shift_calendar(page)  
    )

    shift_table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("Дата")), ft.DataColumn(ft.Text("ФИО"))],
        rows=[], 
        visible=False, 
        bgcolor=ft.colors.GREY_200
    )

    # Добавляем контейнер с прокруткой
    shift_table_container = ft.Container(
        content=ft.Column(
            controls=[shift_table], 
            scroll="auto"  # Добавляем прокрутку
        ),
        height=200  # Ограничиваем высоту контейнера
    )


    main_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(controls=[user_info_container, scrollable_table], alignment="center", spacing=20),
                ft.Row(controls=[toggle_user_dates, toggle_users, toggle_med_check, toggle_shift_table, shift_button], alignment="center", spacing=10),
                ft.Row(controls=[toggle_login_logs, toggle_results, toggle_tasks,  task_button], alignment="center", spacing=20),
                shift_table_container  # Заменяем shift_table на shift_table_container
            ],
        ),
        expand=True,
        padding=20,
        bgcolor=ft.colors.WHITE,
        border_radius=10,
    )

    page.add(ft.Text(f"Добро пожаловать, {fio}!", size=24, weight=ft.FontWeight.BOLD, text_align="center"))
    page.add(main_container)
    update_table(None)

if __name__ == "__main__":
    ft.app(target=main, view="flet_app")
