import flet as ft
import mysql.connector
import subprocess


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
        # Контейнер для кнопки "More Info"
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
                        on_click=self.on_more_info_click,  # Клик на кнопку
                        style=ft.ButtonStyle(color=ft.colors.WHITE),
                    )
                ],
            ),
        )

        # Основной контейнер карточки
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
                            "Нажмите, если у вас возникли вопросы или проблемы с авторизацией",
                            color=ft.colors.BLACK,
                            size=14,
                            weight="w500",
                        ),
                    ),
                ],
            ),
        )

        # Карточка с анимацией
        self.__card = ft.Card(
            elevation=0,
            content=ft.Container(
                content=ft.Column(spacing=0, horizontal_alignment="center", controls=[self._container]),
            ),
        )

        # Компоновка карточки и кнопки
        self._card = ft.Column(
            horizontal_alignment="center",
            spacing=0,
            controls=[self.__card, self._icon_container_],
        )

        self._main = self._card
        return self._main 

    def AnimatedCardHover(self, e):
        if e.data == "true":
            # Показать кнопку "More Info"
            self._icon_container_.visible = True
            self._icon_container_.opacity = 1
            self._icon_container_.offset = ft.transform.Offset(0, -0.75)
            self._icon_container_.update()
        else:
            self.hide_more_info_button()

    def hide_more_info_button(self):
        self._icon_container_.opacity = 0
        self._icon_container_.offset = ft.transform.Offset(0, 0.25)
        self._icon_container_.update()

    def on_more_info_click(self, e):
        # Запуск формы info.py
        subprocess.run(["python", "G:\\дипломик\\tolik_diplom\\info.py"])


def main(page: ft.Page):
    page.title = "Авторизация пользователя"
    page.window_resizable = False
    page.window_width = 1300  # Ширина окна
    page.window_height = 700  # Высота окна
    page.window_center() 

    def authorize_user(e):
        
        # Получение данных из текстовых полей 
        fio = fio_field.value
        code = code_field.value

        # Проверка данных в базе
        try:
            conn = connect_to_db()
            cursor = conn.cursor(dictionary=True)  # dictionary=True, чтобы результат был словарем
            query = "SELECT fio FROM users WHERE fio = %s AND code = %s"
            cursor.execute(query, (fio, code))
            user = cursor.fetchone()

            if user:
                fio = user["fio"]

                # Логируем успешный вход
                cursor.execute("INSERT INTO login_logs (fio, success) VALUES (%s, %s)", (fio, True))
                conn.commit()

                if code.startswith("12"):
                    # Если начинается с "12", открываем форму two
                    subprocess.run(["python", "G:\\дипломик\\tolik_diplom\\two.py", code, fio])
                else:
                    # Иначе передаем код в first.py
                    subprocess.run(["python", "G:\\дипломик\\tolik_diplom\\first.py", code, fio])

                page.window_close()  # Закрываем текущее окно
            else:
                # Логируем ошибочный вход
                cursor.execute("INSERT INTO login_logs (fio, success, error_message) VALUES (%s, %s, %s)", 
                            (fio, False, "Неверное ФИО или код."))
                conn.commit()

                # Вывод ошибки при неверных данных
                snack_bar = ft.SnackBar(
                    content=ft.Row(
                        controls=[
                            ft.Icon(name=ft.icons.CLOSE, color="red", size=24),
                            ft.Text("Неверное ФИО или код.")
                        ]
                    )
                )
                page.overlay.append(snack_bar)
                snack_bar.open = True
                page.update()

            cursor.close()
            conn.close()

        except Exception as ex:
            # Логируем ошибку подключения или выполнения
            cursor.execute("INSERT INTO login_logs (fio, success, error_message) VALUES (%s, %s, %s)", 
                        (fio, False, str(ex)))
            conn.commit()

            snack_bar = ft.SnackBar(ft.Text(f"Ошибка: {ex}"))
            page.overlay.append(snack_bar)
            snack_bar.open = True
            page.update()


            
    def close_app(e):
        page.window_close()

    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.add(ft.Text("Авторизация:", size=24, weight=ft.FontWeight.BOLD))

    # Поля для ввода данных
    fio_field = ft.TextField(label="ФИО", width=300)
    code_field = ft.TextField(label="Код", keyboard_type=ft.KeyboardType.NUMBER, width=300)

    # Кнопки для авторизации и выхода
    login_button = ft.ElevatedButton("Войти", on_click=authorize_user)
    close_button = ft.ElevatedButton("Закрыть", on_click=close_app)

    # Создание и добавление карточки AnimatedCard
    info_card = AnimatedCard()

    # Расположение карточки слева от формы
    page.add(
        ft.Row(
            controls=[
                ft.Container(content=info_card, padding=10),  # Карточка слева
                ft.Column(
                    spacing=20,
                    controls=[
                        
                        fio_field,
                        code_field,
                        login_button,
                        close_button,
                    ],
                ),  # Форма справа
            ],
            alignment="center",
        )
    )

if __name__ == "__main__":
    ft.app(target=main, view="flet_app")
