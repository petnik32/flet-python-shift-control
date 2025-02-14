import flet as ft
import mysql.connector
import subprocess
from datetime import datetime


# Подключение к базе данных
def connect_to_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="tolik2"
    )


class AnimatedCard(ft.UserControl):
    def __init__(self):
        super().__init__()

    def build(self):
        self._icon_container_ = ft.Container(
            width=120,
            height=35,
            bgcolor=ft.colors.BLUE_800,
            border_radius=25,
            animate_opacity=200,
            offset=ft.transform.Offset(0, 0.25),
            animate_offset=ft.animation.Animation(duration=900, curve="ease"),
            visible=False,
            content=ft.Row(
                alignment="center",
                vertical_alignment="center",
                controls=[
                    ft.TextButton(
                        "More Info",
                        on_click=self.on_more_info_click,
                        style=ft.ButtonStyle(color=ft.colors.WHITE),
                    )
                ],
            ),
        )

        self._container = ft.Container(
            width=280,
            height=380,
            bgcolor=ft.colors.WHITE,
            border_radius=12,
            on_hover=self.AnimatedCardHover,  # Событие наведения
            on_click=self.on_more_info_click, 
            animate=ft.animation.Animation(600, "ease"),
            border=ft.border.all(2, ft.colors.WHITE24),
            content=ft.Column(
                alignment="center",
                horizontal_alignment="start",
                spacing=0,
                controls=[
                    ft.Container(
                        padding=20,
                        alignment=ft.alignment.bottom_center,
                        content=ft.Text("Карта информации", color=ft.colors.BLACK, size=28, weight="w800"),
                    ),
                    ft.Container(
                        padding=20,
                        alignment=ft.alignment.top_center,
                        content=ft.Text(
                            "Нажмите, если у вас возникли вопросы или проблемы с регистрацией",
                            color=ft.colors.BLACK,
                            size=14,
                            weight="w500",
                        ),
                    ),
                ],
            ),
        )

        self.__card = ft.Card(
            elevation=0,
            content=ft.Container(
                content=ft.Column(spacing=0, horizontal_alignment="center", controls=[self._container]),
            ),
        )

        self._card = ft.Column(
            horizontal_alignment="center",
            spacing=0,
            controls=[self.__card, self._icon_container_],
        )

        self._main = self._card
        return self._main

    def AnimatedCardHover(self, e):
        if e.data == "true":
            self._icon_container_.visible = True
            self._icon_container_.opacity = 1
            self._icon_container_.offset = ft.transform.Offset(0, -0.75)
            self._icon_container_.update()

            self.page.timer(2000, self.hide_more_info_button)

            self._container.border = ft.border.all(4, ft.colors.BLUE_800)
            self._container.update()
        else:
            self.hide_more_info_button()

    def hide_more_info_button(self):
        self._icon_container_.opacity = 0
        self._icon_container_.offset = ft.transform.Offset(0, 0.25)
        self._icon_container_.update()

    def on_more_info_click(self, e):
        subprocess.run(["python", "G:\\дипломик\\tolik_diplom\\info.py"])


def main(page: ft.Page):
    page.title = "Добавить пользователя"
    page.window_resizable = False
    page.window_width = 1300  # Ширина окна
    page.window_height = 700  # Высота окна
    page.window_center() 
    def save_data(e):
        fio = fio_field.value
        age = age_field.value
        hire_date = hire_date_field.value
        department = department_field.value
        code = code_field.value

        try:
            conn = connect_to_db()
            cursor = conn.cursor()
            query = "INSERT INTO users (fio, age, hire_date, department, code) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (fio, age, hire_date, department, code))
            conn.commit()
            cursor.close()
            conn.close()
            page.snack_bar = ft.SnackBar(ft.Text("Данные сохранены!"), open=True)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Ошибка: {ex}"), open=True)

        fio_field.value = ""
        age_field.value = ""
        hire_date_field.value = ""
        department_field.value = ""
        code_field.value = ""
        page.update()

    def close_data(e):
        page.window_close()

    def show_calendar(e):
        date_picker.pick_date()

    def on_date_select(e):
        hire_date_field.value = date_picker.value.strftime("%Y-%m-%d")
        page.update()

    # Создаем DatePicker
    date_picker = ft.DatePicker(
        on_change=on_date_select,
        first_date=datetime(1900, 1, 1),
        last_date=datetime(2100, 12, 31)
    )
    page.overlay.append(date_picker)

    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.add(ft.Text("Регистрация:", size=24, weight=ft.FontWeight.BOLD))


    fio_field = ft.TextField(label="ФИО", width=300)
    age_field = ft.TextField(label="Возраст", keyboard_type=ft.KeyboardType.NUMBER, width=300)
    hire_date_field = ft.TextField(label="Дата устройства", width=300, read_only=True)
    department_field = ft.TextField(label="Отдел", width=300)
    code_field = ft.TextField(label="Код", keyboard_type=ft.KeyboardType.NUMBER, width=300)

    hire_date_button = ft.IconButton(
        icon=ft.icons.CALENDAR_TODAY,
        on_click=show_calendar,
        tooltip="Выбрать дату"
    )

    save_button = ft.ElevatedButton("Зарегистрироваться", on_click=save_data)
    close_button = ft.ElevatedButton("Вернуться", on_click=close_data)

    app = AnimatedCard()

    page.add(
        ft.Row(
            alignment="center",
            controls=[
                ft.Container(content=app, padding=10),
                ft.Column(
                    controls=[
                        fio_field,
                        age_field,
                        ft.Row(controls=[hire_date_field, hire_date_button]),
                        department_field,
                        code_field,
                        save_button,
                        close_button,
                    ]
                ),
            ],
        )
    )

    page.update()


if __name__ == "__main__":
    ft.app(target=main, view="flet_app")
