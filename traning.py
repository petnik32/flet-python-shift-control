import flet as ft
import mysql.connector

def save_to_db(name, correct_answers):
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1111",
        database="tolik2"
    )
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже такое имя в базе данных
    cursor.execute("SELECT * FROM results WHERE name = %s", (name,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        # Если имя уже существует, возвращаем ошибку
        return False
    
    # Если имя не найдено, сохраняем данные
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            correct_answers INT
        )
    """)
    cursor.execute("INSERT INTO results (name, correct_answers) VALUES (%s, %s)", (name, correct_answers))
    conn.commit()
    cursor.close()
    conn.close()
    
    return True

def main(page: ft.Page):
    page.title = "Опрос"
    page.window_width = 400
    page.window_height = 600
    page.scroll = "adaptive"
    
    questions = [
        ("Сколько будет 2+2?", ["3", "4", "5"], "4"),
        ("Какой цвет у неба?", ["Зеленый", "Синий", "Красный"], "Синий"),
        ("Сколько лап у кошки?", ["2", "3", "4"], "4"),
        ("Какой сегодня день недели?", ["Понедельник", "Среда", "Не знаю"], "Не знаю"),
        ("Сколько букв в слове 'кот'", ["2", "3", "4"], "3"),
        ("Какая планета ближе всего к Солнцу?", ["Земля", "Меркурий", "Марс"], "Меркурий"),
        ("Сколько пальцев на руке?", ["3", "4", "5"], "5"),
        ("Какой цвет получается при смешении синего и желтого?", ["Зеленый", "Красный", "Оранжевый"], "Зеленый"),
        ("Кто говорит 'мяу'?", ["Собака", "Кошка", "Попугай"], "Кошка"),
        ("Сколько месяцев в году?", ["10", "11", "12"], "12")
    ]
    
    user_answers = {}
    name_field = ft.TextField(label="Введите ФИО")
    
    def submit_answers(e):
        if not name_field.value.strip():
            result_text.value = "Ошибка: введите ФИО!"
            page.update()
            return
        
        correct_count = sum(1 for i, (q, opts, ans) in enumerate(questions) if user_answers.get(i) == ans)
        result_text.value = f"Вы ответили правильно на {correct_count} из {len(questions)} вопросов."
        
        if correct_count >= 9:
            # Пытаемся сохранить в базу
            if save_to_db(name_field.value.strip(), correct_count):
                result_text.value += " Данные сохранены и скоро будут проверены."
            else:
                result_text.value += " Ошибка: такое имя уже существует."
        
        name_field.disabled = True
        submit_button.disabled = True
        for radio_group in radio_groups:
            radio_group.disabled = True
        
        page.update()
    
    quiz_widgets = []
    radio_groups = []
    
    for index, (question, options, correct) in enumerate(questions):
        question_text = ft.Text(question)
        radio_group = ft.RadioGroup(
            content=ft.Column([ft.Radio(value=option, label=option) for option in options]),
            on_change=lambda e, i=index: user_answers.update({i: e.control.value})
        )
        radio_groups.append(radio_group)
        quiz_widgets.append(ft.Column([question_text, radio_group]))
    
    submit_button = ft.ElevatedButton("Отправить", on_click=submit_answers)
    result_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
    
    page.add(
        ft.Column(
            [name_field] + quiz_widgets + [submit_button, result_text],
            scroll="adaptive"
        )
    )
    
ft.app(target=main)
