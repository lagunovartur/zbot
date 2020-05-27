from grab_screen import WindowGrabber
import numpy as np
import cv2
import time
import pandas as pd
import win32gui
import win32con
import pyglet
import random


class Bot:

    def __init__(self, clicker, stop_event):

        self.window_grabber = WindowGrabber('Battles for Glory', False)
        self.sound_alarm = pyglet.media.load('alarm.mp3')
        self.clicker = clicker
        self.stop_event = stop_event
        self.mob_count = 0
        self.last_mob_death_time = time.time()

    def check_state_decorator(method_to_decorate):

        def wrapper(self,*args,**kwargs):

            if self.stop_event.is_set():
                return False


            if self.last_mob_death_time + 300 < time.time():
                self.send_signal()
                return False

            return method_to_decorate(self, *args, **kwargs)

        return wrapper

    @property
    def target_hp(self):

        def get_target_bar_coordinates():
            return self.window_grabber.get_widget_coordinates(
                self.window_grabber.original_image,
                cv2.imread('img/target_bar.png', 0)
            )

        target_widget_coordinates = get_target_bar_coordinates()

        if not target_widget_coordinates:
            print('target_hp None')
            return None

        hp_box = (
            self.window_grabber.window_info.box[0] + target_widget_coordinates[0] - 137,
            self.window_grabber.window_info.box[1] + target_widget_coordinates[1] + 27,
            self.window_grabber.window_info.box[0] + target_widget_coordinates[0] + 13,
            self.window_grabber.window_info.box[1] + target_widget_coordinates[1] + 31
        )

        pil_image_hp = self.window_grabber.get_square_area(*hp_box)
        # self.window_grabber.imshow(pil_image_hp,50)

        hp_color = [68, 70, 128]
        filled_red_pixels = 0
        pixels = pil_image_hp[(hp_box[3]-hp_box[1])//2].tolist()
        for pixel in pixels:
            if (pixel[0] <= 120)\
                    and (pixel[1] <= 120) \
                    and (pixel[2] > 120):
                filled_red_pixels += 1

        percent_hp = round(100 * filled_red_pixels / (hp_box[2] - hp_box[0]))
        print('target_hp:', percent_hp)
        return percent_hp

    @property
    def self_hp(self):

        def get_self_hp_bar_coordinates():

            return (self.window_grabber.get_widget_coordinates(
                self.window_grabber.original_image,
                cv2.imread('img/self_hp_bar1.png', 0)
            ))\
            or\
            (self.window_grabber.get_widget_coordinates(
                self.window_grabber.original_image,
                cv2.imread('img/self_hp_bar2.png', 0)
            ))

        self_hp_bar_coordinates = get_self_hp_bar_coordinates()

        if not self_hp_bar_coordinates:
            print('self_hp:',None)
            return None

        hp_box = (
            self.window_grabber.window_info.box[0] + self_hp_bar_coordinates[0] - 2,
            self.window_grabber.window_info.box[1] + self_hp_bar_coordinates[1],
            self.window_grabber.window_info.box[0] + self_hp_bar_coordinates[0] + 148,
            self.window_grabber.window_info.box[1] + self_hp_bar_coordinates[1] + 7
        )

        pil_image_hp = self.window_grabber.get_square_area(*hp_box)

        black_pixels = 0
        total_pixels = 0
        pixels = pil_image_hp[(hp_box[3]-hp_box[1])//2].tolist()
        for idx, pixel in enumerate(pixels):

            if pixel[0] >= 180 and pixel[1] >= 180 and pixel[2] >= 180:
                continue

            if pixel[0] <= 35and pixel[1] <= 35and pixel[2] <= 35:
                black_pixels += 1

            total_pixels +=1

            if idx == 6 and black_pixels == 7:
                print('self_hp:', 0)
                return 0

        percent_hp = round(100 - black_pixels / total_pixels *100)
        print('self_hp:', percent_hp)
        return percent_hp

    def set_target(self):
        return self.set_next_target() or self.set_cursor_target()

    @check_state_decorator
    def set_next_target(self, pause=1):
        print('next_target')
        self.clicker.press_key(self.clicker.F1, pause)
        target_hp = self.target_hp
        return bool(target_hp)

    def set_cursor_target(self, max_contours=5):

        def get_target_arrow_coordinates():
            return self.window_grabber.get_widget_coordinates(
                self.window_grabber.original_image,
                cv2.imread('img/target_arrow.png', 0)
            )

        if self.target_hp:
            return True

        contours = self.window_grabber.get_contours_with_color((240, 240, 240), (255, 255, 255))
        centers = {'x': [], 'y': [], 'd': []}
        for contour in contours:
            contour_center = self.window_grabber.get_contour_center(contour)
            window_center = self.window_grabber.window_info.box_center
            distance = round(((window_center[0] - contour_center[0]) ** 2 +
                              (window_center[1] - contour_center[1]) ** 2) ** 0.5)
            centers['x'].append(contour_center[0])
            centers['y'].append(contour_center[1])
            centers['d'].append(distance)
        centers = pd.DataFrame(centers)
        centers = centers.sort_values(by='d')

        for idx, point in centers.iterrows():
            self.clicker.smooth_move(point['x'], point['y'])
            for y in range(int(point['y']), int(float(point['y'])) + 100, 10):
                self.clicker.smooth_move(point['x'], y)
                time.sleep(0.1)
                if get_target_arrow_coordinates():
                    self.clicker.left_click()
                    if self.target_hp:
                        return True
                    else:
                        self.clicker.ESC.press()
            if idx == max_contours:
                break

        return False

    def attack(self, pause=0.2):
        print('attack')
        self.clicker.press_key(pause)

    @check_state_decorator
    def pick_up_drop(self, max_count = 5, pause=0.3):
        for count in range(max_count):
            print('pick_up_drop')
            self.clicker.press_key(self.clicker.F3, pause)

    @check_state_decorator
    def go_to_selected_target(self, pause=2):
        if self.target_hp != 0:
            return False
        print('go to')
        self.clicker.press_key(self.clicker.F2, pause)
        return True

    @check_state_decorator
    def sweep(self, pause=1):
        print('sweep')
        self.clicker.press_key(self.clicker.F4, pause)

    def send_signal(self):

        def exiter(duration):
            pyglet.app.exit

        self.sound_alarm.play()
        pyglet.clock.schedule_once(exiter, self.sound_alarm.duration)
        pyglet.app.run()

    def go_somewhere(self, pause=None, angle=None, stop_event=None):
        pause = random.randint(5, 15) if not pause else pause
        angle = random.randint(-180, 180) if not angle else angle
        while not self.stop_event.is_set():
            self.turn(angle, stop_event)
            self.go(pause,stop_event)
            if stop_event:
                if stop_event():
                    break
            else:
                break

    def turn(self, angle, stop_event=None):
        start_time = time.time()
        round_time = 6.55
        angle_time = abs(round_time / 360 * angle)
        print('turn ',angle)
        key = self.clicker.D if angle > 0 else self.clicker.A
        self.clicker.press_key(key, angle_time, stop_event)

    @check_state_decorator
    def go(self, pause, stop_event=None):
        print('go ',pause)
        self.clicker.press_key(self.clicker.W, pause, stop_event)
        self.clicker.press_key(self.clicker.S, 0.1)

    def get_target_areas(self):

        areas = {'angle':[], 'area': []}

        angle = 0
        dx = 360 / 24
        while angle <= 360:
            contours = self.window_grabber.get_contours_with_color((240, 240, 240), (255, 255, 255))
            contoursArea = sum(map(lambda contour: cv2.contourArea(contour),contours))
            areas['angle'].append(angle if angle <= 180 else angle - 360)
            areas['area'].append(contoursArea)
            angle += dx
            self.turn(dx)

        areas = pd.DataFrame(areas)
        areas = areas.sort_values(by='area', ascending=False)

        return  areas

