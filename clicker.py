import win32gui
import time
import random
import time
from AutoHotPy.InterceptionWrapper import InterceptionMouseState, InterceptionMouseStroke, InterceptionKeyStroke, \
    InterceptionKeyState
from AutoHotPy.AutoHotPy import AutoHotPy


class Clicker(AutoHotPy):

    def smooth_move(self, x, y):

        def draw_line(x1=0, y1=0, x2=0, y2=0):

            coordinates = []

            dx = x2 - x1
            dy = y2 - y1

            sign_x = 1 if dx > 0 else -1 if dx < 0 else 0
            sign_y = 1 if dy > 0 else -1 if dy < 0 else 0

            if dx < 0:
                dx = -dx
            if dy < 0:
                dy = -dy

            if dx > dy:
                pdx, pdy = sign_x, 0
                es, el = dy, dx
            else:
                pdx, pdy = 0, sign_y
                es, el = dx, dy

            x, y = x1, y1

            error, t = el / 2, 0

            coordinates.append([x, y])

            while t < el:
                error -= es
                if error < 0:
                    error += el
                    x += sign_x
                    y += sign_y
                else:
                    x += pdx
                    y += pdy
                t += 1
                coordinates.append([x, y])

            return coordinates

        flags, hcursor, (startX, startY) = win32gui.GetCursorInfo()
        coordinates = draw_line(startX, startY, x, y)
        x = 0
        for dot in coordinates:
            x += 1
            if x % 2 == 0 and x % 3 == 0:
                t = 0.01 / random.randrange(1, 9, 1)
                time.sleep(t)
            self.moveMouseToPosition(dot[0], dot[1])

    def left_click(self):

        stroke = InterceptionMouseStroke()
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN
        self.sendToDefaultMouse(stroke)
        time.sleep(0.02)
        stroke.state = InterceptionMouseState.INTERCEPTION_MOUSE_LEFT_BUTTON_UP
        self.sendToDefaultMouse(stroke)

    def press_key(self, key, pause=None, stop_event=None):

        if pause == 0:
            key.press()
            return

        stroke = InterceptionKeyStroke()
        stroke.code = key
        stroke.state = InterceptionKeyState.INTERCEPTION_KEY_DOWN
        self.sendToDefaultKeyboard(stroke)
        start_time = time.time()
        pause = random.random() if not pause else pause
        while time.time() < start_time +pause:
            if stop_event and stop_event():
                break
        stroke.state = InterceptionKeyState.INTERCEPTION_KEY_UP
        self.sendToDefaultKeyboard(stroke)
