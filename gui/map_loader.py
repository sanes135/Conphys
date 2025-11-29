import dearpygui.dearpygui as dpg
import math
from physics.objects import Ball, Line

class MapLoader:
    def __init__(self, render_system, physics_simulator, window_instance):
        self.render_system = render_system
        self.physics_simulator = physics_simulator
        self.window = window_instance
        self.objects = []
        self.object_configs = {}
        self.object_properties_tags = {}
        self.object_panel_window_tag = "object_panel_window"

    def add_object(self, obj, config=None):
        if config is None:
            config = self._get_default_config(obj)
        self.objects.append(obj)
        self.object_configs[id(obj)] = config.copy() # Сохраняем копию
        self.render_system.add_object(obj)

    def _get_default_config(self, obj):
        if isinstance(obj, Ball):
            return {
                'type': 'ball',
                'cord': (obj.x * self.physics_simulator.mpp, obj.y * self.physics_simulator.mpp),
                'r': obj.radius * self.physics_simulator.mpp,
                'mass': obj.mass,
                'x': obj.x, 'y': obj.y, 'vx': obj.vx, 'vy': obj.vy,
                'rotation': obj.rotation, 'angular_velocity': obj.angular_velocity
            }
        elif isinstance(obj, Line):
            return {
                'type': 'line',
                'p1': (obj.x1 * self.physics_simulator.mpp, obj.y1 * self.physics_simulator.mpp),
                'p2': (obj.x2 * self.physics_simulator.mpp, obj.y2 * self.physics_simulator.mpp),
                'thickness': obj.thickness
            }
        return {}

    def create_ui_for_objects(self):
        if dpg.does_item_exist(self.object_panel_window_tag):
            dpg.delete_item(self.object_panel_window_tag)

        with dpg.child_window(tag=self.object_panel_window_tag, width=self.window.object_panel_width, height=self.window.height, parent="main_window_group"):
            dpg.add_text("Объекты", color=(255, 255, 0))
            self.object_properties_tags.clear()
            for i, obj in enumerate(self.objects):
                obj_id = id(obj)
                header_label = f"{obj.__class__.__name__} {i+1} (ID: {obj_id})"
                header_tag = f"obj_header_{obj_id}"
                with dpg.collapsing_header(label=header_label, tag=header_tag, default_open=False):
                    if isinstance(obj, Ball):
                        props_tag = f"ball_props_{obj_id}"
                        self.object_properties_tags[obj_id] = props_tag
                        with dpg.group(tag=props_tag):
                            dpg.add_slider_float(label="Масса", default_value=obj.mass,
                                                 min_value=0.1, max_value=10.0, format="%.2f",
                                                 tag=f"mass_{obj_id}", callback=self._update_object_property_callback)
                            dpg.add_slider_float(label="Радиус", default_value=obj.radius * self.physics_simulator.mpp,
                                                 min_value=1.0, max_value=50.0, format="%.1f",
                                                 tag=f"radius_{obj_id}", callback=self._update_object_property_callback)
                            dpg.add_slider_float(label="Вращение", default_value=obj.rotation_degrees,
                                                 min_value=0, max_value=360, format="%.1f",
                                                 tag=f"rotation_{obj_id}", callback=self._update_object_property_callback)

                            dpg.add_text("", tag=f"info_pos_{obj_id}")
                            dpg.add_text("", tag=f"info_vel_{obj_id}")
                            dpg.add_text("", tag=f"info_energy_{obj_id}")
                            dpg.add_text("", tag=f"info_forces_{obj_id}")
                    elif isinstance(obj, Line):
                        props_tag = f"line_props_{obj_id}"
                        self.object_properties_tags[obj_id] = props_tag
                        with dpg.group(tag=props_tag):
                            dpg.add_slider_float(label="Толщина", default_value=obj.thickness,
                                                 min_value=1, max_value=20, format="%.0f",
                                                 tag=f"thickness_{obj_id}", callback=self._update_object_property_callback)

    def _update_object_property_callback(self, sender, app_data):
        # sender имеет формат "type_property_object_id" например "mass_12345"
        parts = sender.split('_')
        if len(parts) < 3:
            return
        prop_type = parts[0]
        obj_id_str = '_'.join(parts[1:]) # Обрабатываем ID с подчеркиваниями
        obj_id = int(obj_id_str)
        obj = next((o for o in self.objects if id(o) == obj_id), None)
        if not obj:
            return
        value = dpg.get_value(sender)
        if isinstance(obj, Ball):
            if prop_type == "mass":
                obj.mass = value
            elif prop_type == "radius":
                old_radius = obj.radius
                new_radius = value / self.physics_simulator.mpp
                obj.radius = new_radius
                obj.mass *= (new_radius / old_radius) ** 2
            elif prop_type == "rotation":
                obj.rotation = math.radians(value)
                obj.rotation_degrees = value
        elif isinstance(obj, Line):
            if prop_type == "thickness":
                obj.thickness = value

    def reset_all_objects(self):
        for obj in self.objects:
            obj_id = id(obj)
            config = self.object_configs.get(obj_id)
            if config:
                if isinstance(obj, Ball):
                    obj.x = config['x']
                    obj.y = config['y']
                    obj.vx = config['vx']
                    obj.vy = config['vy']
                    obj.rotation = config['rotation']
                    obj.angular_velocity = config['angular_velocity']
                    obj.rotation_degrees = math.degrees(obj.rotation)
                # Линию не сбрасываем, т.к. она статичная
        self.physics_simulator.reset_time()

    def update_object_info_ui(self):
        for obj in self.objects:
            obj_id = id(obj)
            # Обновляем информацию для шаров
            if isinstance(obj, Ball) and hasattr(obj, 'physics_calc'):
                ke = obj.physics_calc.kinetic_energy
                pe = obj.physics_calc.potential_energy
                total_energy = obj.physics_calc.total_energy
                momentum = obj.physics_calc.momentum
                velocity = obj.physics_calc.velocity_magnitude
                acceleration = obj.physics_calc.acceleration
                gravity_force = obj.physics_calc.gravity_force
                friction_force = obj.physics_calc.friction_force
                elastic_force = obj.physics_calc.elastic_force

                pos_text = f"Позиция (м): ({obj.x * self.physics_simulator.mpp:.2f}, {obj.y * self.physics_simulator.mpp:.2f})"
                vel_text = f"Скорость (м/с): ({obj.vx * self.physics_simulator.mpp:.2f}, {obj.vy * self.physics_simulator.mpp:.2f}), Вел: {velocity:.2f}"
                energy_text = f"Энергии (J): K={ke:.2f}, P={pe:.2f}, T={total_energy:.2f}"
                forces_text = f"Силы (N): G={gravity_force:.2f}, F={friction_force:.2f}, E={elastic_force:.2f}, A={acceleration:.2f} (м/с²)"

                dpg.set_value(f"info_pos_{obj_id}", pos_text)
                dpg.set_value(f"info_vel_{obj_id}", vel_text)
                dpg.set_value(f"info_energy_{obj_id}", energy_text)
                dpg.set_value(f"info_forces_{obj_id}", forces_text)
