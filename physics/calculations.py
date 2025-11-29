import math
from .objects import Ball

class PhysicsVariables:
    def __init__(self, ball, table_line, gravity, mpp):
        # Ссылка на объект шара и параметры для вычислений
        self._ball = ball
        self._table_line = table_line
        self._gravity = gravity
        self._mpp = mpp

    @property
    def kinetic_energy(self):
        """Кинетическая энергия (Ek)"""
        v_m = math.sqrt(self._ball.vx**2 + self._ball.vy**2) * self._mpp
        return 0.5 * self._ball.mass * v_m**2

    @property
    def potential_energy(self):
        """Потенциальная энергия (Ep)"""
        # Высота от линии стола (предполагаем, что y=0 это верх экрана)
        # Проекция центра шара на линию
        line_vec_x = self._table_line.x2 - self._table_line.x1
        line_vec_y = self._table_line.y2 - self._table_line.y1
        line_len_sq = line_vec_x**2 + line_vec_y**2
        if line_len_sq == 0:
            h_px = 0
        else:
            point_vec_x = self._ball.x - self._table_line.x1
            point_vec_y = self._ball.y - self._table_line.y1
            t = max(0, min(1, (point_vec_x * line_vec_x + point_vec_y * line_vec_y) / line_len_sq))
            proj_x = self._table_line.x1 + t * line_vec_x
            proj_y = self._table_line.y1 + t * line_vec_y
            h_px = self._ball.y - proj_y - self._ball.radius
        h_m = h_px * self._mpp
        # Предполагаем, что h=0 на линии стола
        return self._ball.mass * self._gravity * h_m if h_m > 0 else 0

    @property
    def total_energy(self):
        """Полная механическая энергия (E)"""
        return self.kinetic_energy + self.potential_energy

    @property
    def momentum(self):
        """Импульс (kg*m/s)"""
        v_m = math.sqrt(self._ball.vx**2 + self._ball.vy**2) * self._mpp
        return self._ball.mass * v_m

    @property
    def gravity_force(self):
        """Сила тяжести (Fтяж)"""
        return self._ball.mass * self._gravity

    @property
    def velocity_magnitude(self):
        """Величина скорости в м/с"""
        return math.sqrt(self._ball.vx**2 + self._ball.vy**2) * self._mpp

    @property
    def acceleration(self):
        """Ускорение (м/с^2)"""
        return math.sqrt(self._ball.ax**2 + self._ball.ay**2) * self._mpp

    @property
    def elastic_force(self):
        """Сила упругости при столкновении с линией (N) - упрощенная модель"""
        # Проверяем столкновение с линией
        collision, _, _ = self._ball.check_line_collision(self._table_line)
        if collision:
            # Сила пропорциональна нормальной скорости и массе
            v_normal = math.sqrt(self._ball.vx**2 + self._ball.vy**2) * self._mpp
            return v_normal * self._ball.mass * 10  # Упрощенный коэффициент
        return 0.0

    @property
    def friction_force(self):
        """Сила трения (Ff)"""
        # F_friction = mu * N, где N - нормальная сила (масса * g для горизонтальной поверхности)
        friction_coefficient = 0.1  # Упрощенный коэффициент трения
        normal_force = self.gravity_force
        return friction_coefficient * normal_force

class PhysicsCalculations:
    def __init__(self, ball, table_line, gravity, mpp):
        self._physics_vars = PhysicsVariables(ball, table_line, gravity, mpp)

    @property
    def kinetic_energy(self):
        return self._physics_vars.kinetic_energy

    @property
    def potential_energy(self):
        return self._physics_vars.potential_energy

    @property
    def total_energy(self):
        return self._physics_vars.total_energy

    @property
    def momentum(self):
        return self._physics_vars.momentum

    @property
    def gravity_force(self):
        return self._physics_vars.gravity_force

    @property
    def velocity_magnitude(self):
        return self._physics_vars.velocity_magnitude

    @property
    def acceleration(self):
        return self._physics_vars.acceleration

    @property
    def elastic_force(self):
        return self._physics_vars.elastic_force

    @property
    def friction_force(self):
        return self._physics_vars.friction_force