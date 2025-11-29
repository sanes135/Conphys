import math
from typing import List
from .objects import Ball, Line

class PhysicsSimulator:
    def __init__(self, objects: List, table_line: Line, width: int,
                 gravity: float = 9.8, bounce: float = 0.8,
                 friction: float = 0.999, mpp: float = 0.1):
        self.objects = objects
        self.table_line = table_line
        self.width = width
        self.gravity = gravity
        self.bounce = bounce
        self.friction = friction
        self.time_scale = 1.0
        self.t = 0.0
        self.mpp = mpp
        for obj in objects:
            if isinstance(obj, Ball):
                obj.setup_physics(table_line, gravity, mpp)

    def update(self, dt):
        scaled_dt = dt * self.time_scale
        self.t += scaled_dt
        for obj in self.objects:
            if isinstance(obj, Ball):
                obj.update(scaled_dt, self.gravity, self.bounce,
                           self.friction, self.table_line, self.width, self.mpp)

        self.check_and_resolve_collisions()

    def check_and_resolve_collisions(self):
        for i in range(len(self.objects)):
            for j in range(i + 1, len(self.objects)):
                obj1 = self.objects[i]
                obj2 = self.objects[j]

                # Пропускаем столкновения с Line
                if isinstance(obj1, Line) or isinstance(obj2, Line):
                    continue

                collision, normal, depth = self.check_collision_pair(obj1, obj2)
                if collision:
                    self.resolve_collision_pair(obj1, obj2, normal, depth)

    def check_collision_pair(self, obj1, obj2):
        if isinstance(obj1, Ball) and isinstance(obj2, Ball):
            return obj1.check_collision_with_ball(obj2)
        return False, (0, 0), 0

    def resolve_collision_pair(self, obj1, obj2, normal, depth):
        if isinstance(obj1, Ball) and isinstance(obj2, Ball):
            obj1.resolve_collision_with_ball(obj2, normal, depth, self.bounce)
            obj2.resolve_collision_with_ball(obj1, (-normal[0], -normal[1]), depth, self.bounce)

    def set_parameters(self, gravity, bounce, friction, time_scale, mpp):
        self.gravity = gravity
        self.bounce = bounce
        self.friction = friction
        self.time_scale = time_scale
        self.mpp = mpp
        for obj in self.objects:
            if isinstance(obj, Ball):
                obj.physics_vars._gravity = gravity
                obj.physics_calc._physics_vars._gravity = gravity
                obj.physics_vars._mpp = mpp
                obj.physics_calc._physics_vars._mpp = mpp

    def reset_time(self):
        self.t = 0.0
