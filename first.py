import flet as ft
from flet import *
import mysql.connector
import sys
from datetime import datetime
import subprocess

def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="tolik2"
    )

def format_date(date_str):
    return datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")

def main(page: ft.Page):
    global current_background
    user_code = sys.argv[1]
    fio = sys.argv[2]

    
    page.window_resizable = False
    page.window_width = 1300  # Ширина окна
    page.window_height = 700  # Высота окна
    page.window_center() 

    print(f"Переданное ФИО: {fio}")

    backgrounds = ["background1.png", "background2.jpg", "background3.jpg"]

    current_background = backgrounds[0]

    page.title = f"Личный кабинет - {fio}"

    def on_checkbox_change(e):
        if checkbox.value:
            page.snack_bar = ft.SnackBar(ft.Text("Внимание! При выборе дат, будьте внимательны! Не выбирайте несколько дат одного назначения!"), open=True)
            page.update()
        button_container.visible = checkbox.value
        page.update()

    page.title = f"Личный кабинет - {fio}"

    def change_background(e):
        global current_background
        current_index = backgrounds.index(current_background)
        current_background = backgrounds[(current_index + 1) % len(backgrounds)]
        print(f"Меняем фон на: {current_background}")  # Выводим новый фон

        page.bgimage = f"assets/{current_background}"  # Убедитесь, что путь к файлу правильный
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
            page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка загрузки данных: {ex}"), open=True)
            page.update()
            return None

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

    def calculate_salary(fio, month):
        try:
            conn = connect_to_db()
            cursor = conn.cursor(dictionary=True)

            # Проверка формата месяца
            if isinstance(month, int):
                # Если передан только номер месяца, добавим 2025 год
                year = 2025
                start_date = datetime(year, month, 1)
            else:
                # Если передан формат 'YYYY-MM', проверим год и обновим при необходимости
                input_year, input_month = map(int, month.split('-'))
                if input_year != 2025:
                    input_year = 2025
                start_date = datetime(input_year, input_month, 1)

            # Определение конца месяца
            if start_date.month == 12:
                end_date = datetime(start_date.year + 1, 1, 1)
            else:
                end_date = datetime(start_date.year, start_date.month + 1, 1)

            # Запрос для подсчета смен
            query = """
                SELECT COUNT(*) as shift_count 
                FROM shifts 
                WHERE fio = %s AND date >= %s AND date < %s
            """
            cursor.execute(query, (fio, start_date, end_date))

            result = cursor.fetchone()

            shift_count = result['shift_count'] if result else 0

            cursor.close()
            conn.close()

            # Рассчитываем зарплату
            salary = shift_count * 150

            if shift_count == 0:
                print(f"Для {fio} смен в {start_date.strftime('%B %Y')} не найдено.")

            return salary
        except Exception as ex:
            print(f"Ошибка при расчете зарплаты: {ex}")
            return 0

    
    user_data = load_user_data()

    user_data = load_user_data()
    if user_data and user_data.get("hire_date"):
        experience_text = calculate_experience(user_data["hire_date"])
    if user_data:
        user_info_controls = [
            ft.Text(f"ФИО: {user_data['fio']}", size=16),
            ft.Text(f"Возраст: {user_data['age']}", size=16),
            ft.Text(f"Дата устройства: {user_data['hire_date']}", size=16),
            ft.Text(f"Отдел: {user_data['department']}", size=16),
            ft.Text(f"Стаж: {experience_text}", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE)
        ]
    else:
        user_info_controls = [ft.Text("Не удалось загрузить данные пользователя", size=16, color=ft.colors.RED)]

    text_elements = [
        ft.Text("Справки и смены", size=16),
        *user_info_controls,  # Включаем элементы с данными пользователя
        ft.Text(f"Добро пожаловать, {fio}!", size=24, weight=ft.FontWeight.BOLD, text_align="center")
    ]

    selected_dates = {"Охрана труда": None, "Мед справки": None}  # Словарь для хранения выбранных дат
    shift_dates = []  # Список дат для смен
    shift_date_containers = ft.Row(wrap=True, spacing=10, scroll=ft.ScrollMode.AUTO)  # Контейнер для смен
    date_containers = ft.Row(wrap=True, spacing=10, scroll=ft.ScrollMode.AUTO)  # Контейнер для других дат
    
    def confirm_date(e):
        selected_date = date_picker.value.strftime("%d/%m/%Y")

        if len(shift_dates) >= 31:
            page.snack_bar = ft.SnackBar(ft.Text("Ошибка: Нельзя выбрать больше 31 даты!"), open=True)
        else:
            shift_dates.append(selected_date)  
            add_shift_date_container(selected_date, category="Смена")  # Передаем категорию "Смена"

        confirm_dialog.open = False
        page.update()

    def add_shift_date_container(date, category):
        """Добавляет дату и категорию в контейнер для смен с возможностью удаления"""
        def on_hover(e):
            e.control.bgcolor = ft.colors.RED_200 if e.data == "true" else ft.colors.LIGHT_BLUE_200
            e.control.update()

        def on_click(e):
            shift_dates.remove(date)  # Удаляем дату из списка
            shift_date_containers.controls.remove(e.control)  # Удаляем контейнер
            page.update()

        date_box = ft.Container(
            content=ft.Text(f"{category}: {date}", size=14),
            width=150,
            height=50,
            bgcolor=ft.colors.LIGHT_BLUE_200,
            alignment=ft.alignment.center,
            border_radius=5,
            on_hover=on_hover,
            on_click=on_click
        )
        shift_date_containers.controls.append(date_box)
        page.update()

    def add_date_container(date, category):
        """Добавляет дату в контейнер для мед. справок и охраны труда с возможностью удаления"""
        def on_hover(e):
            e.control.bgcolor = ft.colors.RED_200 if e.data == "true" else ft.colors.LIGHT_BLUE_200
            e.control.update()

        def on_click(e):
            selected_dates[category] = None  # Удаляем дату из словаря
            date_containers.controls.remove(e.control)  # Удаляем контейнер
            page.update()

        date_box = ft.Container(
            content=ft.Text(f"{category}: {date}", size=14),
            width=150,
            height=50,
            bgcolor=ft.colors.LIGHT_BLUE_200,
            alignment=ft.alignment.center,
            border_radius=5,
            on_hover=on_hover,
            on_click=on_click
        )
        date_containers.controls.append(date_box)
        page.update()

    def load_shifts(fio):
        try:
            conn = connect_to_db()
            cursor = conn.cursor(dictionary=True)

            # Получаем текущую дату
            today = datetime.today().strftime("%Y-%m-%d")

            # Измененный SQL-запрос с условием WHERE для фильтрации дат
            query = "SELECT fio, date FROM shifts WHERE fio = %s AND date > %s"
            cursor.execute(query, (fio, today))  # Параметры: fio и сегодняшняя дата
            shifts = cursor.fetchall()
            cursor.close()
            conn.close()
            return shifts
        except Exception as ex:
            print(f"Ошибка загрузки смен: {ex}")
            return []

    def display_shifts_table(shifts):
        headers = ["ФИО", "Дата смены"]
        rows = []

        if not shifts:
            print("Нет данных о сменах!")
        
        for shift in shifts:
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(shift['fio'], size=14)), 
                ft.DataCell(ft.Text(shift['date'], size=14))
            ]))

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.DataTable(
                        columns=[ft.DataColumn(ft.Text(header, size=16)) for header in headers],
                        rows=rows,
                        bgcolor=ft.colors.LIGHT_BLUE_50,
                        border_radius=10,
                    )
                ],
                scroll=True,  # Включаем прокрутку
                height=180,   # Ограничиваем высоту для прокрутки
            ),
            width=460,
        )

    shifts = load_shifts(fio)
    shifts_table = display_shifts_table(shifts)


    def on_date_select(e):
        selected_date = date_picker.value.strftime("%d/%m/%Y")

        if date_picker.category == "Смена":
            if len(shift_dates) >= 31:
                page.snack_bar = ft.SnackBar(ft.Text("Ошибка: Нельзя выбрать больше 31 даты!"), open=True)
            else:
                shift_dates.append(selected_date)
                add_shift_date_container(selected_date, "Смена")  
        else:
            selected_dates[date_picker.category] = selected_date
            add_date_container(selected_date, date_picker.category)

        confirm_dialog.open = False
        page.update()


    def show_calendar(e):
        date_picker.pick_date()

    def show_font_dialog(e):
        font_dialog.open = True
        page.update()

    def change_font(e):
        selected_font_value = selected_font.value or "Times New Roman"
        print(f"Изменение шрифта на {selected_font_value}")  

        def change_font_recursively(control):
            if isinstance(control, ft.Text):
                control.font_family = selected_font_value
                control.update()  # Обновляем текст сразу
            if hasattr(control, "controls"):  # Если есть вложенные элементы
                for child in control.controls:
                    change_font_recursively(child)
            control.update()  # Обновляем контейнер

        for control in page.controls:
            change_font_recursively(control)

        page.update()  

    date_picker = ft.DatePicker(
        on_change=on_date_select,
        first_date=datetime(1900, 1, 1),
        last_date=datetime(2100, 12, 31)
    )
    page.overlay.append(date_picker)

    selected_font = ft.Dropdown(
        options=[ft.dropdown.Option("Times New Roman"), ft.dropdown.Option("Calibri"), ft.dropdown.Option("Arial"), ft.dropdown.Option("Courier New")],
        value="Times New Roman",
        on_change=change_font
    )

    font_dialog = ft.AlertDialog(
        title=ft.Text("Выберите шрифт"),
        content=selected_font,
        actions=[ft.TextButton("OK", on_click=lambda e: setattr(font_dialog, "open", False) or page.update())]
    )

    confirm_text = ft.Text("")
    confirm_dialog = ft.AlertDialog(
        title=ft.Text("Подтверждение даты"),
        content=confirm_text,
        actions=[ft.TextButton("Да", on_click=confirm_date), ft.TextButton("Отмена", on_click=lambda e: setattr(confirm_dialog, "open", False) or page.update())]
    )

    page.dialog = font_dialog
    page.overlay.append(confirm_dialog)

    user_data = load_user_data()
    # Список месяцев для выбора
    months_dropdown = ft.Dropdown(
        label="Выберите месяц",
        options=[
            ft.dropdown.Option("2025-01", "Январь 2025"),
            ft.dropdown.Option("2025-02", "Февраль 2025"),
            ft.dropdown.Option("2025-03", "Март 2025"),
            ft.dropdown.Option("2025-04", "Апрель 2025"),
            ft.dropdown.Option("2025-05", "Май 2025"),
            ft.dropdown.Option("2025-06", "Июнь 2025"),
            ft.dropdown.Option("2025-07", "Июль 2025"),
            ft.dropdown.Option("2025-08", "Август 2025"),
            ft.dropdown.Option("2025-09", "Сентябрь 2025"),
            ft.dropdown.Option("2025-10", "Октябрь 2025"),
            ft.dropdown.Option("2025-11", "Ноябрь 2025"),
            ft.dropdown.Option("2025-12", "Декабрь 2025"),
        ],
        value="2025-01"  # Значение по умолчанию
    )

    # Текст для отображения зарплаты
    salary_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)

    # Кнопка для расчета зарплаты
    def on_calculate_salary(e):
        selected_month = months_dropdown.value
        salary = calculate_salary(fio, selected_month)
        salary_text.value = f"Примерная зарплата за {selected_month}: {salary} руб."
        page.update()

    calculate_salary_button = ft.ElevatedButton(
        text="Рассчитать зарплату",
        on_click=on_calculate_salary
    )

    checkbox = ft.Checkbox(label="Включить выбор дат", value=False, on_change=on_checkbox_change)

    
    def select_medical_date(e):
        date_picker.category = "Мед справки"
        date_picker.pick_date()

    def select_safety_date(e):
        date_picker.category = "Охрана труда"
        date_picker.pick_date()

    def show_calendar(e):
        date_picker.category = "Смена"
        date_picker.pick_date()


    button_container = ft.Column(
        controls=[ 
            ft.ElevatedButton("Мед справки", on_click=select_medical_date),
            ft.ElevatedButton("Охрана труда", on_click=select_safety_date)
        ],
        spacing=10,
        visible=False  # Изначально скрыт
    )

    def save_data(e):
        if not user_data:
            page.snack_bar = ft.SnackBar(ft.Text("Ошибка: не загружены данные пользователя!"), open=True)
            page.update()
            return

        hire_date = user_data["hire_date"]
        safety_date = selected_dates["Охрана труда"]
        medical_date = selected_dates["Мед справки"]

        if not safety_date or not medical_date:
            page.snack_bar = ft.SnackBar(ft.Text("Ошибка: не выбраны даты!"), open=True)
            page.update()
            return

        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            query = """
                INSERT INTO med (fio, hire_date, safety_check, medical_certificate) 
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, (fio, hire_date, format_date(safety_date), format_date(medical_date)))
            conn.commit()
            cursor.close()
            conn.close()

            # Очистка списка дат и контейнеров
            selected_dates["Охрана труда"] = None
            selected_dates["Мед справки"] = None
            shift_dates.clear()
            shift_date_containers.controls.clear()
            date_containers.controls.clear()

            page.snack_bar = ft.SnackBar(ft.Text("Данные успешно сохранены!"), open=True)
            page.update()

        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка сохранения: {ex}"), open=True)
            page.update()

    background_button = ft.ElevatedButton("Сменить фон", on_click=change_background)

    page.bgimage = current_background

    text_elements = [ft.Text("Справки и Смены", size=16)]
    save_button = ft.ElevatedButton(
        text="Сохранить", 
        on_click=save_data,
        width=100  
    )
    

    def create_check_icon():
        if check_fio_and_answers():
            return ft.Icon(ft.Icons.CHECK, color=ft.colors.GREEN)
        else:
            return ft.Icon(ft.Icons.CANCEL, color=ft.colors.RED)


    def check_fio_and_answers():
        try:
            conn = connect_to_db()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT name, correct_answers FROM results WHERE name = %s"
            cursor.execute(query, (fio,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                print(f"Полученные данные: {user}")  # Добавьте это для отладки
                if user['correct_answers'] > 9:
                    return True  # Возвращаем True, если правильных ответов больше 9
            return False
        except Exception as ex:
            print(f"Ошибка при проверке: {ex}")
            return False

    def open_training_page(e):
        try:
            print("Открыт курс 1 (traning.py)")
            subprocess.run(["python", "G:\\дипломик\\tolik_diplom\\traning.py"])
        except subprocess.CalledProcessError as ex:
            print(f"Ошибка при запуске traning.py: {ex}")
        except FileNotFoundError as ex:
            print(f"Файл не найден: {ex}")
        except Exception as ex:
            print(f"Неизвестная ошибка: {ex}")

    def open_newp_page(e):
        try:
            print("Открыт курс 1 (traning.py)")
            subprocess.run(["python", "G:\\дипломик\\tolik_diplom\\task.py"])
        except subprocess.CalledProcessError as ex:
            print(f"Ошибка при запуске traning.py: {ex}")
        except FileNotFoundError as ex:
            print(f"Файл не найден: {ex}")
        except Exception as ex:
            print(f"Неизвестная ошибка: {ex}")

 
    training_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Обучение", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Выберите курс для обучения", size=16),
                ft.Row(
                    controls=[
                        ft.ElevatedButton("Курс 1", on_click=open_training_page),
                        create_check_icon()
                    ],
                    alignment=ft.alignment.center_left
                ),
                ft.ElevatedButton("Курс 2", on_click=lambda e: print("Курс 2 выбран")),
            ],
            alignment=ft.alignment.top_left,
        ),
        width=250,
        height=200,
        bgcolor=ft.colors.GREY_200,
        alignment=ft.alignment.top_left,
        border_radius=10,
        padding=10
    )

    new_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Список задач", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Здесь вы увидите свои задачи.", size=14)
            ],
            alignment="center",
            spacing=10
        ),
        width=250,
        height=100,
        bgcolor=ft.colors.GREY_200,
        alignment=ft.alignment.top_center,
        on_click=open_newp_page,
        border_radius=10,
        padding=10
    )

    left_container = ft.Column(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Выбор дат", size=18, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        checkbox,
                        button_container,
                        date_containers,
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    save_button,
                                    ft.IconButton(icon=ft.icons.CALENDAR_TODAY, on_click=show_calendar, tooltip="Выбрать дату"),
                                    ft.IconButton(icon=ft.icons.SETTINGS, on_click=show_font_dialog, tooltip="Выбрать шрифт"),
                                ],
                                alignment="start",
                                spacing=10,
                            ),
                            alignment=ft.alignment.bottom_center,
                            padding=25
                        ),
                    ],
                    spacing=10,
                    alignment="start",
                ),
                width=250,
                height=350,  # Уменьшаем высоту, чтобы контейнер "Обучение" поместился ниже
                bgcolor=ft.colors.GREY_200,
                alignment=ft.alignment.top_center,
                border_radius=10,
                padding=10
            ),
            training_container  # Контейнер "Обучение" теперь ниже
        ],
        spacing=10,
    )

    top_center_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Смены пользователя", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),  # Разделительная линия
                shifts_table
            ],
            alignment="center",
            spacing=10
        ),
        width=500,
        height=250,
        bgcolor=ft.colors.GREY_200,
        alignment=ft.alignment.top_center,
        border_radius=10,
        padding=10
    )


    bottom_center_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Выбранные смены", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),  # Разделительная линия
                shift_date_containers
            ],
            scroll=ft.ScrollMode.AUTO
        ),
        width=500,
        height=250,
        bgcolor=ft.colors.GREY_200,
        alignment=ft.alignment.top_center,
        border_radius=10,
        padding=10
    )

    if user_data:
        user_info_controls = [
            ft.Text(f"ФИО: {user_data['fio']}", size=16),
            ft.Text(f"Возраст: {user_data['age']}", size=16),
            ft.Text(f"Дата устройства: {user_data['hire_date']}", size=16),
            ft.Text(f"Отдел: {user_data['department']}", size=16),
            ft.Text(f"Стаж: {experience_text}", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
        ]
    else:
        user_info_controls = [ft.Text("Не удалось загрузить данные пользователя", size=16, color=ft.colors.RED)]

    user_photo_container = ft.Container(
        content=ft.Image(
            src="G:\\дипломик\\tolik_diplom\\image.jpg",  # Путь к фото
            width=120,  
            height=120,  
            fit=ft.ImageFit.CONTAIN  
        ),
        width=120,  # Размер контейнера
        height=120,  # Размер контейнера
        bgcolor=ft.colors.GREY_400,  # Фоновый цвет, если изображение не загрузится
        border_radius=60,  # Закругленные углы
        alignment=ft.alignment.center  # Выравнивание изображения в центре контейнера
    )

    # Обновленный правый контейнер с фото сверху
    right_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("Информация о пользователе", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),  # Разделительная линия
                user_photo_container,

                ft.Container(
                    content=ft.ListView(
                        controls=user_info_controls,
                        spacing=10,
                        
                    ),
                    expand=True  # Занимает всё оставшееся пространство
                ),
                ft.Text("Расчет зарплаты:", size=16, weight=ft.FontWeight.BOLD),
                # Элементы, закрепленные внизу
                months_dropdown,
                calculate_salary_button,
                salary_text
            ],
            spacing=10,
            alignment="spaceBetween", 
            scroll=ft.ScrollMode.AUTO # Размещает элементы вверху и внизу
        ),
        width=250,
        height=500,
        bgcolor=ft.colors.GREY_200,
        alignment=ft.alignment.top_center,
        border_radius=10,
        padding=10,
    )

    def send_data(e):
        if not shift_dates:  # Проверяем только список смен
            snack_bar = ft.SnackBar(ft.Text("Ошибка: нет выбранных дат!"), open=True)
            page.snack_bar = snack_bar
            snack_bar.open = True
            page.update()
        else:
            try:
                conn = connect_to_db()
                cursor = conn.cursor()
                for date in shift_dates:
                    formatted_date = format_date(date)
                    query = "INSERT INTO user_dates (fio, date_selected) VALUES (%s, %s)"
                    cursor.execute(query, (fio, formatted_date))
                conn.commit()
                cursor.close()
                conn.close()

                # Очистка списка дат и контейнеров
                shift_dates.clear()
                shift_date_containers.controls.clear()
                date_containers.controls.clear()

                snack_bar = ft.SnackBar(ft.Text("Даты успешно отправлены!"), open=True)
                page.snack_bar = snack_bar
                snack_bar.open = True
                page.update()
            except Exception as ex:
                snack_bar = ft.SnackBar(ft.Text(f"Ошибка при сохранении данных: {ex}"), open=True)
                page.snack_bar = snack_bar
                snack_bar.open = True
                page.update()


    send_button = ft.ElevatedButton(text="Отправить", on_click=send_data)

    layout = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    # Группируем right_container и new_container в одну колонку
                    ft.Column(
                        controls=[
                            right_container,
                            new_container  # Новый контейнер будет ниже right_container
                        ],
                        spacing=10  # Добавляет пространство между контейнерами
                    ),
                    ft.Column(
                        controls=[
                            top_center_container,
                            bottom_center_container,
                            send_button
                        ],
                        spacing=20,
                        alignment="center"
                    ),
                    left_container
                ],
                alignment="center",
                spacing=20
            ),
        ]
    )


    page.add(ft.Text(f"Добро пожаловать, {fio}!", size=24, weight=ft.FontWeight.BOLD, text_align="center"))
    page.add(layout)

if __name__ == "__main__":
    ft.app(target=main, view="flet_app")
