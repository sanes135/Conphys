import dearpygui.dearpygui as dpg
import math
from typing import Tuple

MPP = 0.1  # 1 пиксель = 0.1 метра

class Ball:
    def __init__(self, cord: Tuple[float, float] = (10, 20),
                 r: float = 20, mass: float = 1.0,
                 color: Tuple[int, int, int] = (255, 50, 50),
                 fill_color: Tuple[int, int, int, int] = (255, 100, 100, 180)):
        self.x = cord[0] / MPP
        self.y = cord[1] / MPP
        self.radius = r / MPP
        self.mass = mass
        self.vx = 0
        self.vy = 0.0
        self.ax = 0.0
        self.ay = 0.0
        self.color = color
        self.fill_color = fill_color
        self.rotation = 0
        self.rotation_degrees = 0
        self.angular_velocity = 0
        self.draw_tag = None
        self._prev_vx = 0.0
        self._prev_vy = 0.0

    def update(self, dt: float, gravity: float, bounce: float,
               friction: float, table_line, width: int, mpp: float):
        self._prev_vx = self.vx
        self._prev_vy = self.vy

        self.vy += (gravity) * dt

        self.x += self.vx * dt
        self.y += self.vy * dt

        if dt != 0:
            self.ax = (self.vx - self._prev_vx) / dt
            self.ay = (self.vy - self._prev_vy) / dt

        collision, normal, depth = self.check_line_collision(table_line)
        if collision:
            self.resolve_line_collision(table_line, normal, depth, bounce, friction)

        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -bounce
        elif self.x + self.radius > width:
            self.x = width - self.radius
            self.vx *= -bounce

        self.rotation += self.angular_velocity * dt
        self.rotation_degrees = math.degrees(self.rotation)

    def check_line_collision(self, line):
        line_vec_x = line.x2 - line.x1
        line_vec_y = line.y2 - line.y1
        line_len_sq = line_vec_x**2 + line_vec_y**2
        if line_len_sq == 0:
            return False, (0, 0), 0

        point_vec_x = self.x - line.x1
        point_vec_y = self.y - line.y1
        t = max(0, min(1, (point_vec_x * line_vec_x + point_vec_y * line_vec_y) / line_len_sq))
        proj_x = line.x1 + t * line_vec_x
        proj_y = line.y1 + t * line_vec_y
        dx = self.x - proj_x
        dy = self.y - proj_y
        dist = math.sqrt(dx**2 + dy**2)

        if dist <= self.radius:
            if dist == 0:
                normal_x = -line_vec_y / math.sqrt(line_len_sq)
                normal_y = line_vec_x / math.sqrt(line_len_sq)
            else:
                normal_x = dx / dist
                normal_y = dy / dist
            depth = self.radius - dist
            return True, (normal_x, normal_y), depth
        return False, (0, 0), 0

    def resolve_line_collision(self, line, normal, depth, bounce, friction):
        normal_x, normal_y = normal
        self.x += normal_x * depth
        self.y += normal_y * depth

        vel_normal = self.vx * normal_x + self.vy * normal_y
        vel_tangent_x = self.vx - vel_normal * normal_x
        vel_tangent_y = self.vy - vel_normal * normal_y

        new_vel_normal_x = -vel_normal * bounce * normal_x
        new_vel_normal_y = -vel_normal * bounce * normal_y

        new_vel_tangent_x = vel_tangent_x * friction
        new_vel_tangent_y = vel_tangent_y * friction

        self.vx = new_vel_normal_x + new_vel_tangent_x
        self.vy = new_vel_normal_y + new_vel_tangent_y

    def setup_physics(self, table_line, gravity, mpp):
        from .calculations import PhysicsVariables, PhysicsCalculations
        self.physics_vars = PhysicsVariables(self, table_line, gravity, mpp)
        self.physics_calc = PhysicsCalculations(self, table_line, gravity, mpp)

    def draw(self, drawlist_tag: str):
        self.draw_tag = f"ball_{id(self)}"
        dpg.draw_circle([self.x, self.y], self.radius, color=self.color,
                        fill=self.fill_color, parent=drawlist_tag, tag=self.draw_tag)

    def update_draw(self):
        if self.draw_tag and dpg.does_item_exist(self.draw_tag):
            dpg.configure_item(self.draw_tag, center=[self.x, self.y], radius=self.radius)

    def get_center(self):
        return self.x, self.y

    def get_velocity_at_point(self, point_x, point_y):
        return self.vx, self.vy

    def check_collision_with_ball(self, other_ball):
        dx = other_ball.x - self.x
        dy = other_ball.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        min_distance = self.radius + other_ball.radius
        if distance < min_distance and distance > 0:
            overlap = min_distance - distance
            normal_x = dx / distance
            normal_y = dy / distance
            return True, (normal_x, normal_y), overlap
        return False, (0, 0), 0

    def resolve_collision_with_ball(self, other_ball, normal, overlap, bounce):
        separation_x = normal[0] * (overlap / 2)
        separation_y = normal[1] * (overlap / 2)
        self.x -= separation_x
        self.y -= separation_y
        other_ball.x += separation_x
        other_ball.y += separation_y

        rel_vx = other_ball.vx - self.vx
        rel_vy = other_ball.vy - self.vy
        rel_vel_normal = rel_vx * normal[0] + rel_vy * normal[1]

        if rel_vel_normal > 0:
            return

        e = bounce
        j = -(1 + e) * rel_vel_normal
        j /= (1 / self.mass + 1 / other_ball.mass)

        impulse_x = j * normal[0]
        impulse_y = j * normal[1]

        self.vx -= impulse_x / self.mass
        self.vy -= impulse_y / self.mass
        other_ball.vx += impulse_x / other_ball.mass
        other_ball.vy += impulse_y / other_ball.mass


class Line:
    def __init__(self, p1: Tuple[float, float] = (-20, 0),
                 p2: Tuple[float, float] = (20, 0),
                 color: Tuple[int, int, int] = (100, 100, 100),
                 thickness: int = 5):
        self.x1 = p1[0] / MPP
        self.y1 = p1[1] / MPP
        self.x2 = p2[0] / MPP
        self.y2 = p2[1] / MPP
        self.color = color
        self.thickness = thickness
        self.rotation = 0
        self.rotation_degrees = 0
        self.draw_tag = None

    def draw(self, drawlist_tag: str):
        self.draw_tag = f"line_{id(self)}"
        dpg.draw_line([self.x1, self.y1], [self.x2, self.y2],
                      color=self.color, thickness=self.thickness,
                      parent=drawlist_tag, tag=self.draw_tag)

    def update_draw(self):
        if self.draw_tag and dpg.does_item_exist(self.draw_tag):
            dpg.configure_item(self.draw_tag, p1=[self.x1, self.y1], p2=[self.x2, self.y2])
