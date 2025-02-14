import flet as ft
from math import pi
import random
import asyncio
import subprocess





class CustomPieChart(ft.UserControl):
    def __init__(self, val: int, color: any, title: str, on_click=None):
        # numerical instances for pie chart
        self.val: int = val
        self.delta_val: int = 100 - self.val
        self.random_range = random.randint(5, 9)

        # UI instances of pie chart
        self.color: any = color
        self.bg_color = ft.colors.with_opacity(0.025, "white")
        self.base_radius: int = 15
        self.title: str = title
        self.on_click = on_click  # Функция обработки клика

        # pie chart instance
        self.chart: ft.Control = ft.PieChart(
            sections=self.base_section(),
            sections_space=0,
            center_space_radius=60,
            expand=True,
            rotate=ft.Rotate((3 * pi) / 2),
            on_chart_event=lambda e: self.hover_circle(e),
        )

        # pocket container
        self.pocket: ft.Control = ft.Container(
            bottom=1,
            right=1,
            left=1,
            scale=ft.Scale(0.85),
            border_radius=10,
            bgcolor=ft.colors.with_opacity(0.05, ft.colors.BLUE_GREY_300),
            offset=ft.transform.Offset(0, -0.085),
            animate_offset=ft.Animation(650, "easeInOutBack"),
            on_hover=lambda e: asyncio.run(self.gather_methods(e)),
            content=ft.Stack(
                controls=[
                    self.chart,
                    ft.Container(
                        right=1,
                        left=1,
                        padding=25,
                        content=ft.Text(
                            self.title,
                            size=21,
                            weight="w700",
                            text_align="center",
                        ),
                    ),
                ],
            ),
        )

        # blurred container
        self.blurred_container: ft.Control = ft.Container(
            expand=True,
            height=250,
            bgcolor=ft.colors.with_opacity(0.0085, "white"),
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            bottom=0,
            left=0,
            right=1,
            on_hover=lambda e: asyncio.run(self.gather_methods(e)),
        )

        super().__init__()

    def base_chart_section(self, pie_value, pie_color, pie_radius):
        return ft.PieChartSection(
            value=pie_value,
            color=pie_color,    
            radius=pie_radius,
        )

    def base_section(self):
        section_list: list = [
            # dynamic PieSection circle
            self.base_chart_section(self.val, self.color, self.base_radius),
            # background PieSection circle
            self.base_chart_section(self.delta_val, self.bg_color, self.base_radius),
        ]

        return section_list

    async def gather_methods(self, e):
        if e.data == "true":
            await asyncio.gather(self.show(), self._set())

        else:
            await asyncio.gather(self.hide(), self._reset())

    async def show(self):
        self.pocket.offset = ft.transform.Offset(0, -0.6)
        self.pocket.update()

    async def hide(self):
        self.pocket.offset = ft.transform.Offset(0, -0.085)
        self.pocket.update()

    async def _set(self):
        for i in range(self.random_range):
            self.chart.sections[0].value += 5
            self.chart.sections[1].value -= 5
            self.chart.update()
            await asyncio.sleep(0.1)  # Увеличьте время ожидания между шагами


    async def _reset(self):
        for i in range(self.random_range):
            self.chart.sections[0].value -= 5
            self.chart.sections[1].value += 5
            self.chart.update()
            await asyncio.sleep(0.1)  # Увеличьте время ожидания между шагами


    def hover_circle(self, e):
        if self.chart.sections[0].radius != self.base_radius + 5:
            self.chart.sections[0].radius = self.base_radius + 5

        else:
            self.chart.sections[0].radius = self.base_radius

        self.chart.update()

    def build(self):
        return ft.Container(
            width=300,
            height=480,
            border_radius=ft.BorderRadius(
                bottom_left=25, bottom_right=25, top_left=0, top_right=0
            ),
            on_click=self.on_click,  # Добавляем обработчик клика
            content=ft.Stack(
                expand=True,
                controls=[
                    self.pocket,
                    self.blurred_container,
                ],
            ),
        )

    

def main(page: ft.Page):

    page.window_resizable = False
    page.window_width = 1300  # Ширина окна
    page.window_height = 700  # Высота окна
    page.window_center() 
    
    def open_reg(_):
        subprocess.run(["python", "G:\\дипломик\\tolik_diplom\\reg.py"])

    def open_log(_):
        subprocess.run(["python", "G:\\дипломик\\tolik_diplom\\log.py"])


    # Настройки страницы
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.add(ft.Text("Выберите действие:", size=24, weight=ft.FontWeight.BOLD))
    # Создание объектов CustomPieChart с обработчиками
    pie_one = CustomPieChart(val=25, color="teal", title="Регистрация", on_click=open_reg)
    pie_two = CustomPieChart(val=45, color="red", title="Вход", on_click=open_log)

    # Добавление объектов на страницу
    page.add(
    ft.Row(
        alignment="center",
        controls=[
            ft.Container(on_click=open_reg, content=pie_one),
            ft.Container(on_click=open_log, content=pie_two),
        ],
    )
)
    


"""
ссаный питон баля
????????????????????????????????????????

if main():
    open_reg() or open_log() = True
    CustomPieChart.visible = False
    

    pass 
    

    &??????????????????????????
"""

if __name__ == "__main__":
    ft.app(target=main, view="flet_app")

