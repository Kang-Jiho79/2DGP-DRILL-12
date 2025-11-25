from pico2d import *

import random
import math

import common
import game_framework
import game_world
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector


# zombie Run Speed
PIXEL_PER_METER = (10.0 / 0.3)  # 10 pixel 30 cm
RUN_SPEED_KMPH = 10.0  # Km / Hour
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

# zombie Action Speed
TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 10.0

animation_names = ['Walk', 'Idle']


class Zombie:
    images = None

    def load_images(self):
        if Zombie.images == None:
            Zombie.images = {}
            for name in animation_names:
                Zombie.images[name] = [load_image("./zombie/" + name + " (%d)" % i + ".png") for i in range(1, 11)]
            Zombie.font = load_font('ENCR10B.TTF', 40)
            Zombie.marker_image = load_image('hand_arrow.png')


    def __init__(self, x=None, y=None):
        self.x = x if x else random.randint(100, 1180)
        self.y = y if y else random.randint(100, 924)
        self.load_images()
        self.dir = 0.0      # radian 값으로 방향을 표시
        self.speed = 0.0
        self.frame = random.randint(0, 9)
        self.state = 'Idle'
        self.ball_count = 0


        self.tx, self.ty = 1000, 1000
        # 여기를 채우시오.
        self.patrol_locations = [(43, 274), (1118, 274), (1050, 494), (575, 804), (235, 991), (575, 804), (1050, 494),
(1118, 274)]
        self.loc_no = 0

        self.build_behavior_tree()


    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50


    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION
        # fill here
        self.bt.run()


    def draw(self):
        if math.cos(self.dir) < 0:
            Zombie.images[self.state][int(self.frame)].composite_draw(0, 'h', self.x, self.y, 100, 100)
        else:
            Zombie.images[self.state][int(self.frame)].draw(self.x, self.y, 100, 100)
        self.font.draw(self.x - 10, self.y + 60, f'{self.ball_count}', (0, 0, 255))
        Zombie.marker_image.draw(self.tx+25, self.ty-25)
        draw_circle(self.x, self.y, int(7*PIXEL_PER_METER))



        draw_rectangle(*self.get_bb())

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'zombie:ball':
            self.ball_count += 1


    def set_target_location(self, x=None, y=None):
        # 여기를 채우시오.
        if x is None or y is None:
            raise ValueError("목적위치가 설정되어야합니다.")
        self.tx, self.ty = x, y
        return BehaviorTree.SUCCESS



    def distance_less_than(self, x1, y1, x2, y2, r):
        # 여기를 채우시오.
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) < (PIXEL_PER_METER * r)



    def move_little_to(self, tx, ty):
        # 여기를 채우시오.
        # frame_time을 이용해서 이동거리 계산
        distance = RUN_SPEED_PPS * game_framework.frame_time
        self.dir = math.atan2(ty - self.y, tx - self.x)
        self.x += distance * math.cos(self.dir)
        self.y += distance * math.sin(self.dir)
        pass



    def move_to(self, r=0.5):
        # 여기를 채우시오.
        self.state = 'Walk'
        self.move_little_to(self.tx, self.ty)
        if self.distance_less_than(self.tx, self.ty, self.x, self.y, r):
            self.state = 'Idle'
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING



    def set_random_location(self):
        # 여기를 채우시오.
        self.tx, self.ty = random.randint(100, 1180), random.randint(100, 924)
        return BehaviorTree.SUCCESS


    def is_boy_nearby(self, distance):
        # 여기를 채우시오.
        if self.distance_less_than(common.boy.x, common.boy.y, self.x, self.y, distance):
            self.state = 'Walk'
            return BehaviorTree.SUCCESS
        else:
            self.state = 'Idle'
            return BehaviorTree.FAIL


    def move_to_boy(self, r=0.5):
        # 여기를 채우시오.
        self.move_little_to(common.boy.x, common.boy.y)
        if self.distance_less_than(common.boy.x, common.boy.y, self.x, self.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING


    def get_patrol_location(self):
        # 여기를 채우시오.
        self.tx, self.ty = self.patrol_locations[self.loc_no]
        self.loc_no = (self.loc_no + 1) % len(self.patrol_locations)
        return BehaviorTree.SUCCESS

    def has_more_balls_than_boy(self):
        if self.ball_count > common.boy.ball_count:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def flee_to_boy(self, r=0.5):
        # 여기를 채우시오.
        self.state = 'Walk'
        distance = RUN_SPEED_PPS * game_framework.frame_time
        self.dir = math.atan2(self.y - common.boy.y, self.x - common.boy.x)
        self.x += distance * math.cos(self.dir)
        self.y += distance * math.sin(self.dir)
        if self.distance_less_than(common.boy.x, common.boy.y, self.x, self.y, r):
            self.state = 'Idle'
            return BehaviorTree.FAIL
        else:
            return BehaviorTree.RUNNING


    def build_behavior_tree(self):
        # 여기를 채우시오.

        a1 = Action("Set random location", self.set_random_location)
        a2 = Action("Move to target", self.move_to)
        wander = Sequence('Wander', a1, a2)

        c1 = Condition("Is nearby boy", self.is_boy_nearby, 7)
        c2 = Condition("has more than boy's ball", self.has_more_balls_than_boy)
        a3 = Action("Move to boy", self.move_to_boy)
        a4 = Action("Flee to boy", self.flee_to_boy)
        chase = Sequence('Chase', c2, a3)
        # self.bt = BehaviorTree(root)