import flet as ft

def main(page: ft.Page):
    page.title = "Помощь по авторизации и регистрации"
    page.window_resizable = False
    page.window_width = 800  # Ширина окна
    page.window_height = 600  # Высота окна
    page.window_center()

    # Заголовок страницы
    page.add(ft.Text("Как авторизироваться и зарегистрироваться", size=24, weight=ft.FontWeight.BOLD, text_align="center"))

    # Инструкции по авторизации
    login_instructions = ft.Column(
        spacing=10,
        controls=[
            ft.Text("Авторизация:", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("1. Введите ваше ФИО в поле 'ФИО'."),
            ft.Text("2. Введите ваш персональный код в поле 'Код'."),
            ft.Text("3. Нажмите кнопку 'Войти'."),
            ft.Text("4. Если данные верны, вы будете перенаправлены в систему."),
            ft.Text("5. Если данные неверны, появится сообщение об ошибке.")
        ]
    )

    # Инструкции по регистрации
    registration_instructions = ft.Column(
        spacing=10,
        controls=[
            ft.Text("Регистрация:", size=20, weight=ft.FontWeight.BOLD),
            ft.Text("1. Введите ваше ФИО в поле 'ФИО'."),
            ft.Text("2. Укажите ваш возраст в поле 'Возраст'."),
            ft.Text("3. Нажмите на иконку календаря и выберите дату устройства."),
            ft.Text("4. Введите название вашего отдела в поле 'Отдел'."),
            ft.Text("5. Введите персональный код в поле 'Код'."),
            ft.Text("6. Нажмите кнопку 'Зарегистрироваться'."),
            ft.Text("7. Если регистрация прошла успешно, появится сообщение об успешном сохранении данных.")
        ]
    )

    # Возвращение в главное меню
    def return_to_main(e):
        page.window_close()

    return_button = ft.ElevatedButton("Вернуться", on_click=return_to_main)

    # Объединение инструкций в одну колонку
    instructions_layout = ft.Column(
        spacing=30,
        controls=[
            login_instructions,
            registration_instructions,
            return_button
        ]
    )

    # Добавление инструкций на страницу
    page.add(ft.Container(content=instructions_layout, padding=20))


if __name__ == "__main__":
    ft.app(target=main, view='flet_app')
