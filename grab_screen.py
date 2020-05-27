import numpy as np
import win32gui
import cv2
import PIL.ImageGrab as ImageGrab
import time


class WindowInfo:

    def __init__(self, title):

        self.title = title.lower()

        top_windows = []
        win32gui.EnumWindows(WindowInfo._window_enumeration_handler, top_windows)
        for window in top_windows:
            if window['title'] == self.title:
                self.hwnd = window['hwnd']
                break

        rect = win32gui.GetWindowRect(self.hwnd)
        self.rect = rect
        self.box = (self.rect[0]+8, self.rect[1]+31, self.rect[2]-8, self.rect[3]-8)
        self.width = rect[2] - rect[0]
        self.height = rect[3] - rect[1]
        box_center_x = int(self.box[0] + round((self.box[2]-self.box[0])/2))
        box_center_y = int(self.box[1] + round((self.box[3]-self.box[1])/2))
        self.box_center = (box_center_x, box_center_y)

    def _window_enumeration_handler(hwnd, top_windows):
        """Add window title and ID to array."""
        if win32gui.IsWindowVisible(hwnd):
            top_windows.append({'hwnd': hwnd, 'title': win32gui.GetWindowText(hwnd).lower()})


class WindowGrabber:

    def __init__(self, window_name, image_show=False):

        self.window_info = WindowInfo(window_name)
        self.setForegroundWindow()
        self.image_show = image_show

    def show_video(self):

        while True:

            cv2.imshow('window', self.original_image)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break

    def imshow(self, image, wait=5):
        cv2.imshow('window', image)
        if cv2.waitKey(wait*100) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
        # time.sleep(wait)

    def setForegroundWindow(self):
        try:
            win32gui.SetForegroundWindow(self.window_info.hwnd)
        except:
            pass
            # raise ('Не удалось установить окно BSFG текущим.')

    @property
    def original_image(self):
        return cv2.cvtColor(np.array(ImageGrab.grab(self.window_info.box), dtype='uint8'), cv2.COLOR_BGR2RGB)

    def get_contours_with_color(self, hsv_min, hsv_max):

        hsv = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
        processed_image = cv2.inRange(self.original_image, np.array(hsv_min, np.uint8), np.array(hsv_max, np.uint8))
        kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
        processed_image = cv2.morphologyEx(processed_image, cv2.MORPH_CLOSE, kernel1)
        kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
        processed_image = cv2.erode(processed_image, kernel2, iterations=1)
        processed_image = cv2.dilate(processed_image, kernel1, iterations=1)
        contours, hierarchy = cv2.findContours(processed_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if self.image_show:
            self.imshow(processed_image)

        return contours

    def get_contour_center(self, contour):

        x_l = list(contour[contour[:, :, 0].argmin()][0])
        x_r = list(contour[contour[:, :, 0].argmax()][0])
        x_m = int(round((x_r[0] + x_l[0])/2, 0))
        x = x_m + self.window_info.box[0]

        y = x_l[1] + self.window_info.box[1]

        return x,y

    def get_widget_coordinates(self, image, template):

        img_gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)
        widget_coordinates = tuple()
        if np.count_nonzero(loc) == 2:
            for pt in zip(*loc[::-1]):
                widget_coordinates = (pt[0], pt[1])

        return widget_coordinates

    @staticmethod
    def get_square_area(x1, y1, x2, y2):
        box = (x1, y1, x2, y2)
        return cv2.cvtColor(np.array(ImageGrab.grab(box), dtype='uint8'), cv2.COLOR_BGR2RGB)



