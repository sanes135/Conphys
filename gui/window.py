import dearpygui.dearpygui as dpg
import math
import os
from physics import Ball, Line, PhysicsSimulator
from .map_loader import MapLoader

class Window:
    def __init__(self, width=1200, height=700, objects=None):
        self.width = width
        self.height = height
        self.fps = 60
        self.dt = 1 / self.fps
        self.MPP = 0.1  # 1 пиксель = 0.1 метра
        self.gravity = 9.8
        self.bounce = 0.8
        self.friction = 0.999
        self.time_scale = 1.0
        self.sidebar_width = 250
        self.object_panel_width = 300

        self.calculate_render_sizes()

        if objects is None:
            self.ball = Ball(cord=(10, 20), r=5)
            self.table = Line(p1=(0, 40), p2=(100, 50))
            self.objects = [self.ball, self.table]
        else:
            self.objects = objects
            self.table = next((obj for obj in self.objects if isinstance(obj, Line)), None)
            if not self.table:
                raise ValueError("Не найден объект Line для стола.")


        self.renderer = RenderSystem()
        self.physics = PhysicsSimulator(
            objects=self.objects,
            table_line=self.table,
            width=self.drawlist_width,
            gravity=self.gravity,
            bounce=self.bounce,
            friction=self.friction,
            mpp=self.MPP
        )
        # Создаем MapLoader
        self.map_loader = MapLoader(self.renderer, self.physics, self)

        for obj in self.objects:
            config = self.get_object_config(obj)
            self.map_loader.add_object(obj, config)

        dpg.create_context()
        dpg.create_viewport(title="Conphys", width=width, height=height)

        dpg.set_viewport_resize_callback(self.on_viewport_resize)
        self.setup_ui()

    def get_object_config(self, obj):
        if isinstance(obj, Ball):
            return {
                'type': 'ball',
                'cord': (obj.x * self.physics.mpp, obj.y * self.physics.mpp),
                'r': obj.radius * self.physics.mpp,
                'mass': obj.mass,
                'x': obj.x, 'y': obj.y, 'vx': obj.vx, 'vy': obj.vy,
                'rotation': obj.rotation, 'angular_velocity': obj.angular_velocity
            }
        elif isinstance(obj, Line):
            return {
                'type': 'line',
                'p1': (obj.x1 * self.physics.mpp, obj.y1 * self.physics.mpp),
                'p2': (obj.x2 * self.physics.mpp, obj.y2 * self.physics.mpp),
                'thickness': obj.thickness
            }
        return {}

    def calculate_render_sizes(self):
        """Пересчитывает размеры области рендеринга."""
        self.drawlist_width = self.width - self.sidebar_width - self.object_panel_width
        self.drawlist_height = self.height - 50

    def setup_ui(self):
        font_path = self.find_font_path()
        if font_path:
            with dpg.font_registry():
                with dpg.font(font_path, 16) as default_font:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
                    dpg.bind_font(default_font)
        else:
            with dpg.font_registry():
                with dpg.font("C:/Windows/Fonts/calibri.ttf", 16) as default_font:
                    dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
                    dpg.bind_font(default_font)
        with dpg.window(label="Физическая симуляция",
                        width=self.width, height=self.height,
                        no_move=True, no_resize=True, no_collapse=True):

            with dpg.group(horizontal=True, tag="main_window_group"):

                with dpg.child_window(width=self.sidebar_width, height=self.height):
                    dpg.add_text("Настройки симуляции", color=(255, 255, 0))
                    dpg.add_slider_float(label="Гравитация", default_value=self.physics.gravity,
                                         min_value=1, max_value=100, format="%.0f",
                                         tag="gravity", callback=self.update_parameters)
                    dpg.add_slider_float(label="Отскок", default_value=self.physics.bounce,
                                         min_value=0.0, max_value=1.0, format="%.2f",
                                         tag="bounce", callback=self.update_parameters)
                    dpg.add_slider_float(label="Трение", default_value=self.physics.friction,
                                         min_value=0.0, max_value=1.0, format="%.3f",
                                         tag="friction", callback=self.update_parameters)
                    dpg.add_slider_float(label="Замедление", default_value=self.physics.time_scale,
                                         min_value=0.1, max_value=1.0, format="%.2f",
                                         tag="time_scale", callback=self.update_parameters)
                    dpg.add_slider_float(label="MPP", default_value=self.physics.mpp,
                                         min_value=0.01, max_value=1.0, format="%.2f",
                                         tag="mpp", callback=self.update_parameters)
                    dpg.add_separator()
                    dpg.add_button(label="Сбросить", callback=self.reset_all_objects, width=-1)
                    dpg.add_button(label="Начать", callback=self.start_simulation, width=-1, tag="start_button")
                    dpg.add_button(label="Пауза", callback=self.pause_simulation, width=-1, tag="pause_button")
                    dpg.add_separator()
                with dpg.child_window(width=self.drawlist_width, height=self.height):
                    dpg.add_drawlist(width=self.drawlist_width, height=self.drawlist_height,
                                     tag="drawlist",
                                     pos=(self.sidebar_width, 0))
                    self.renderer.draw_initial("drawlist")

                self.map_loader.create_ui_for_objects()

    def on_viewport_resize(self, sender, data):
        """Обработчик изменения размера окна."""
        new_width = dpg.get_viewport_width()
        new_height = dpg.get_viewport_height()
        if new_width != self.width or new_height != self.height:
            self.width = new_width
            self.height = new_height
            self.calculate_render_sizes()

            dpg.configure_item("drawlist", width=self.drawlist_width, height=self.drawlist_height)

            self.physics.width = self.drawlist_width

            self.map_loader.physics_simulator.mpp = self.physics.mpp

    def find_font_path(self):
        possible_paths = [
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/tahoma.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def update_parameters(self, sender, app_data):
        gravity = dpg.get_value("gravity")
        bounce = dpg.get_value("bounce")
        friction = dpg.get_value("friction")
        time_scale = dpg.get_value("time_scale")
        mpp = dpg.get_value("mpp")
        self.physics.set_parameters(
            gravity=gravity,
            bounce=bounce,
            friction=friction,
            time_scale=time_scale,
            mpp=mpp
        )
        self.map_loader.physics_simulator.mpp = mpp

    def update_ui_status(self):
        self.map_loader.update_object_info_ui()

    def render_frame(self, sender, app_data, user_data):
        self.physics.update(self.dt)
        self.renderer.update_draw()
        self.update_ui_status()
        if self.simulation_running:
            dpg.set_frame_callback(dpg.get_frame_count() + 1, self.render_frame)

    def reset_all_objects(self, sender, app_data):
        self.map_loader.reset_all_objects()
        self.map_loader.create_ui_for_objects()
        self.renderer.update_draw()

    def start_simulation(self, sender, app_data):
        self.simulation_running = True
        dpg.configure_item("start_button", show=False)
        dpg.configure_item("pause_button", show=True)
        dpg.set_frame_callback(dpg.get_frame_count() + 1, self.render_frame)

    def pause_simulation(self, sender, app_data):
        self.simulation_running = False
        dpg.configure_item("start_button", show=True)
        dpg.configure_item("pause_button", show=False)

    def run(self):
        self.simulation_running = False
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

class RenderSystem:
    def __init__(self):
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

    def draw_initial(self, drawlist_tag):
        for obj in self.objects:
            obj.draw(drawlist_tag)

    def update_draw(self):
        for obj in self.objects:
            obj.update_draw()
