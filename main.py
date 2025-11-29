import dearpygui.dearpygui as dpg
from gui.window import Window
from physics.objects import Ball, Line

if __name__ == "__main__":
    objects_list = []
    for x in range(20):
        for y in range(10):
            ball = Ball(cord=(x+2, 10 + y), r=0.5, mass=1.0)
            objects_list.append(ball)
    table = Line(p1=(-10, 40), p2=(200, 50), thickness=2)
    objects_list.append(table)

    app = Window(width=1400, height=800, objects=objects_list)
    app.run()
