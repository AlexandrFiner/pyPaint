import tkinter.simpledialog
from tkinter import *
from tkinter import colorchooser
from utils import *
from src.geometry import Geometry
import math


class Paint(Frame):
    CANVAS_WIDTH = 840
    CANVAS_HEIGHT = 525

    def __init__(self, parent):
        super().__init__()
        self.cursor_text = None
        self.canv = None
        self.parent = parent
        self.brush_size = 2
        self.color = "red"
        self.cursor_start = (0, 0)
        self.current_line = None
        self.points = dict()
        self.lines = []
        self.lines_in_group = []
        self.buttons_color = []
        self.buttons_size = []
        self.buttons_mode = []
        self.current_action = EVENT_NONE
        self.line_hovered = None
        self.line_coords = (0, 0, 0, 0)
        self.current_mode = MODE_MAKE_LINES
        self.selector_box = None
        self.center_point = (0, 0)

        self._geometry_handler = None
        self.x_rotation_slider = None
        self.y_rotation_slider = None
        self.z_rotation_slider = None
        self.zoom_slider = None

        self.setUI()

    def draw_rectangle(self, start, end, **opts):
        """Draw the rectangle"""
        return self.canv.create_rectangle(*(list(start) + list(end)), **opts)

    def hit_test(self, start, end, tags=None, ignoretags=None, ignore=[]):
        def groups(glist, numPerGroup=2):
            result = []

            i = 0
            cur = []
            for item in glist:
                if not i < numPerGroup:
                    result.append(cur)
                    cur = []
                    i = 0

                cur.append(item)
                i += 1

            if cur:
                result.append(cur)

            return result

        def average(points):
            aver = [0, 0]

            for point in points:
                aver[0] += point[0]
                aver[1] += point[1]

            return aver[0] / len(points), aver[1] / len(points)

        """
        Check to see if there are items between the start and end
        """
        ignore = set(ignore)
        ignore.update([self.selector_box])

        # first filter all of the items in the canvas
        if isinstance(tags, str):
            tags = [tags]

        if tags:
            tocheck = []
            for tag in tags:
                tocheck.extend(self.canv.find_withtag(tag))
        else:
            tocheck = self.canv.find_all()
        tocheck = [x for x in tocheck if x != self.selector_box]
        if ignoretags:
            if not hasattr(ignoretags, '__iter__'):
                ignoretags = [ignoretags]
            tocheck = [x for x in tocheck if x not in self.canv.find_withtag(it) for it in ignoretags]

        self.selector_items = tocheck

        # then figure out the box
        xlow = min(start[0], end[0])
        xhigh = max(start[0], end[0])

        ylow = min(start[1], end[1])
        yhigh = max(start[1], end[1])

        items = []
        for item in tocheck:
            if item not in ignore:
                x, y = average(groups(self.canv.coords(item)))
                if (xlow < x < xhigh) and (ylow < y < yhigh):
                    items.append(item)

        return items

    def select_action(self, start, end):
        items = self.hit_test(start, end)
        self.ungroup_lines()
        for lineId in self.selector_items:
            if lineId in items:
                self.lines_in_group.append(lineId)
                self.canv.itemconfig(lineId, dash=(4, 1))

    def update_item_points(self, line):
        z1, z2 = 0.0, 0.0
        if line in self.points:
            z1, z2 = self.points[line][2], self.points[line][5]

        coords = self.canv.coords(line)


        self._geometry_handler._zoom = self.zoom_slider.get()
        self._geometry_handler._angle_x = self.x_rotation_slider.get()
        self._geometry_handler._angle_y = self.y_rotation_slider.get()
        self._geometry_handler._angle_z = self.z_rotation_slider.get()

        rot_x, rot_y, rot_z = self._geometry_handler.calculate_rot_matrix(
            0 - self._geometry_handler._angle_x,
            0 - self._geometry_handler._angle_y,
            0 - self._geometry_handler._angle_z,
        )

        x1, y1 = self._geometry_handler.transform_point(([
            [coords[0]],
            [coords[1]],
            [z1]
        ]), rot_x, rot_y, rot_z)
        print(x1, y1)

        self.points[line] = [
            coords[0],
            coords[1],
            z1,
            coords[2],
            coords[3],
            z2
        ]

    def click_on_line(self, event):
        if self.current_mode == MODE_MOVE_LINES:
            if self.current_action == EVENT_NONE and not self.lines_in_group:
                x, y = event.x, event.y
                self.cursor_start = (x, y)
                self.current_line = event.widget.find_withtag('current')[0]
                self.line_coords = self.canv.coords(self.current_line)
                self.current_action = EVENT_MOVE_LINE

        if self.current_mode == MODE_DELETE_LINES:
            self.current_line = event.widget.find_withtag('current')[0]
            self.canv.delete(self.current_line)
            self.points.pop(self.current_line)
            self.lines.remove(self.current_line)
            if self.current_line in self.lines_in_group:
                self.lines_in_group.remove(self.current_line)

        if self.current_mode == MODE_INPUT_3D:
            self.current_line = event.widget.find_withtag('current')[0]
            z = tkinter.simpledialog.askfloat('????????', '?????????????? Z ????????????????????')
            self.points[self.current_line][4] = z
            self.points[self.current_line][5] = z

    def draw_line_start(self, event):
        if self.current_mode == MODE_MAKE_LINES:
            if self.current_action == EVENT_NONE:
                self.current_action = EVENT_DRAW_LINE
                x, y = event.x, event.y
                self.cursor_start = (x, y)
                self.current_line = self.canv.create_line(x, y, x, y, fill=self.color, width=self.brush_size)
                self.canv.tag_bind(self.current_line, '<Button-1>', self.click_on_line)

        if self.current_mode == MODE_MOVE_LINES:
            if self.current_action == EVENT_NONE and self.lines_in_group:
                x, y = event.x, event.y
                self.cursor_start = (x, y)
                self.current_action = EVENT_MOVE_LINE

        if self.current_mode == MODE_SELECTION_TOOL:
            if self.current_action == EVENT_NONE:
                x, y = event.x, event.y
                self.cursor_start = (x, y)
                self.current_action = EVENT_SELECT_LINES

    def draw_line_action(self, event):
        self.cursor_text.config(text="({x}, {y})".format(x=event.x, y=event.y))

        if self.current_mode == MODE_MAKE_LINES:
            if self.current_action == EVENT_DRAW_LINE:
                x1, y1 = self.cursor_start
                x, y = event.x, event.y
                self.canv.coords(self.current_line, x1, y1, x, y)

        if self.current_mode == MODE_MOVE_LINES:
            if self.current_action == EVENT_MOVE_LINE:
                x1, y1 = self.cursor_start
                x, y = event.x, event.y

                move = x-x1, y-y1

                if not self.lines_in_group:
                    self.canv.coords(self.current_line,
                                     self.line_coords[0] + move[0],
                                     self.line_coords[1] + move[1],
                                     self.line_coords[2] + move[0],
                                     self.line_coords[3] + move[1]
                                     )
                else:
                    print(x1, y1, x, y)
                    for lineId in self.lines_in_group:
                        line_coords = self.points[lineId]
                        self.canv.coords(lineId,
                                         line_coords[0] + move[0],
                                         line_coords[1] + move[1],
                                         line_coords[3] + move[0],
                                         line_coords[4] + move[1]
                                         )

        if self.current_mode == MODE_SELECTION_TOOL:
            if self.current_action == EVENT_SELECT_LINES:
                if self.selector_box is not None:
                    self.canv.delete(self.selector_box)

                self.selector_box = self.draw_rectangle(self.cursor_start, (event.x, event.y), fill="", outline="black", width=2, dash=(2, 6))
                self.select_action(self.cursor_start, (event.x, event.y))

    def draw_line_end(self, event):
        if self.current_mode == MODE_MAKE_LINES:
            if self.current_action == EVENT_DRAW_LINE:
                self.current_action = EVENT_NONE
                x1, y1 = self.cursor_start
                x, y = event.x, event.y
                self.canv.coords(self.current_line, x1, y1, x, y)
                if abs(x-x1) < 2 and abs(y-y1) < 2:
                    self.canv.delete(self.current_line)
                else:
                    self.update_item_points(self.current_line)
                    self.lines.append(self.current_line)

        if self.current_mode == MODE_MOVE_LINES:
            if self.current_action == EVENT_MOVE_LINE:
                self.current_action = EVENT_NONE

                x1, y1 = self.cursor_start
                x, y = event.x, event.y

                move = x - x1, y - y1
                if not self.lines_in_group:
                    self.canv.coords(self.current_line,
                                     self.line_coords[0] + move[0],
                                     self.line_coords[1] + move[1],
                                     self.line_coords[2] + move[0],
                                     self.line_coords[3] + move[1]
                                     )

                    self.update_item_points(self.current_line)
                else:
                    for lineId in self.lines_in_group:
                        line_coords = self.points[lineId]
                        self.canv.coords(lineId,
                                         line_coords[0] + move[0],
                                         line_coords[1] + move[1],
                                         line_coords[3] + move[0],
                                         line_coords[4] + move[1]
                                         )

                        self.update_item_points(lineId)

        if self.current_mode == MODE_SELECTION_TOOL:
            if self.current_action == EVENT_SELECT_LINES:
                self.current_action = EVENT_NONE
                if self.selector_box is not None:
                    self.canv.delete(self.selector_box)
                self.selector_box = None

    def mouse_motion(self, event):
        self.cursor_text.config(text="({x}, {y})".format(x=event.x, y=event.y))
        # if self.current_mode == MODE_SELECTION_TOOL:
        #     self.canv.delete('no')
        #     self.canv.create_line(event.x, 0, event.x, 1000, dash=(3, 2), tags='no')
        #     self.canv.create_line(0, event.y, 1000, event.y, dash=(3, 2), tags='no')

    def set_color(self, new_color, button):
        self.color = new_color
        for btn in self.buttons_color:
            btn['state'] = NORMAL
        button['state'] = DISABLED

    def set_color_picker(self):
        color_code = colorchooser.askcolor(title="?????????? ??????????")
        self.color = color_code[1]
        for btn in self.buttons_color:
            btn['state'] = NORMAL

    def set_brush_size(self, new_size, button):
        self.brush_size = new_size
        for btn in self.buttons_size:
            btn['state'] = NORMAL
        button['state'] = DISABLED

    def set_mode(self, mode, button):
        self.current_mode = mode
        for btn in self.buttons_mode:
            btn['state'] = NORMAL
        button['state'] = DISABLED
        # self.canv.delete('no')

    def clear_canv(self):
        self.canv.delete("all")
        self.points.clear()
        self.lines_in_group = []
        self.lines = []

    def group_lines(self):
        for lineId in self.lines:
            self.lines_in_group.append(lineId)
            self.canv.itemconfig(lineId, dash=(4, 1))

    def ungroup_lines(self):
        self.lines_in_group = []
        for lineId in self.lines:
            self.canv.itemconfig(lineId, dash=())

    def change_slider(self, *args):
        self._geometry_handler._zoom = self.zoom_slider.get()
        self._geometry_handler._angle_x = self.x_rotation_slider.get()
        self._geometry_handler._angle_y = self.y_rotation_slider.get()
        self._geometry_handler._angle_z = self.z_rotation_slider.get()

        rot_x, rot_y, rot_z = self._geometry_handler.calculate_rot_matrix(
            self._geometry_handler._angle_x,
            self._geometry_handler._angle_y,
            self._geometry_handler._angle_z,
        )
        # self.canv.delete("all")
        for line in self.lines:
            points = self.points[line]
            print(points)
            x1, y1 = self._geometry_handler.transform_point(([[points[0]], [points[1]], [points[2]]]), rot_x, rot_y, rot_z)
            x, y = self._geometry_handler.transform_point(([[points[3]], [points[4]], [points[5]]]), rot_x, rot_y, rot_z)
            self.canv.coords(line, x1, y1, x, y)
            # self.canv.create_line(x, y, x1, y1, fill=self.color, width=self.brush_size)
                # print(x1, y1, x, y)
        # self.canv.delete("all")

        pass

    def reset_rotation(self):
        self.x_rotation_slider.set(0)
        self.y_rotation_slider.set(0)
        self.z_rotation_slider.set(0)
        self.zoom_slider.set(1)
        self.change_slider()

    def setUI(self):
        # self.parent.minsize((1165, 630))

        self.parent.title("PyGame")
        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(6, weight=1)
        self.rowconfigure(5, weight=1)

        # ?????????????? ?????????? ?? ?????????? ??????????
        self.canv = Canvas(self, bg="white", width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT)
        self.canv.grid(row=5, column=0, columnspan=7, padx=5, pady=5, sticky=E + W + S + N)
        self._geometry_handler = Geometry(self.CANVAS_WIDTH, self.CANVAS_HEIGHT)

        self.canv.bind("<ButtonPress-1>", self.draw_line_start)
        self.canv.bind("<B1-Motion>", self.draw_line_action)
        self.canv.bind("<ButtonRelease-1>", self.draw_line_end)
        self.canv.bind("<Motion>", self.mouse_motion)

        # ?????????????? ?????????? ?????? ???????????? ?????????????????? ?????????? ??????????
        color_lab = Label(self, text="????????: ")
        color_lab.grid(row=0, column=0, padx=6)

        red_btn = Button(self, text="??????????????", width=10, command=lambda: self.set_color("red", red_btn))
        red_btn.grid(row=0, column=1)
        red_btn['state'] = DISABLED
        self.buttons_color.append(red_btn)

        green_btn = Button(self, text="??????????????", width=10, command=lambda: self.set_color("green", green_btn))
        green_btn.grid(row=0, column=2)
        self.buttons_color.append(green_btn)

        blue_btn = Button(self, text="??????????", width=10, command=lambda: self.set_color("blue", blue_btn))
        blue_btn.grid(row=0, column=3)
        self.buttons_color.append(blue_btn)

        black_btn = Button(self, text="????????????", width=10, command=lambda: self.set_color("black", black_btn))
        black_btn.grid(row=0, column=4)
        self.buttons_color.append(black_btn)

        my_color_btn = Button(self, text="???????? ????????", width=10, command=self.set_color_picker)
        my_color_btn.grid(row=0, column=5)

        clear_btn = Button(self, text="????????????????", width=10, command=self.clear_canv)
        clear_btn.grid(row=0, column=6, sticky=W)

        size_lab = Label(self, text="???????????? ??????????: ")
        size_lab.grid(row=1, column=0, padx=5)
        one_btn = Button(self, text="2x", width=10, command=lambda: self.set_brush_size(2, one_btn))
        one_btn.grid(row=1, column=1)
        one_btn['state'] = DISABLED
        self.buttons_size.append(one_btn)

        two_btn = Button(self, text="5x", width=10, command=lambda: self.set_brush_size(5, two_btn))
        two_btn.grid(row=1, column=2)
        self.buttons_size.append(two_btn)

        five_btn = Button(self, text="7x", width=10, command=lambda: self.set_brush_size(7, five_btn))
        five_btn.grid(row=1, column=3)
        self.buttons_size.append(five_btn)

        seven_btn = Button(self, text="10x", width=10, command=lambda: self.set_brush_size(10, seven_btn))
        seven_btn.grid(row=1, column=4)
        self.buttons_size.append(seven_btn)

        ten_btn = Button(self, text="20x", width=10, command=lambda: self.set_brush_size(20, ten_btn))
        ten_btn.grid(row=1, column=5)
        self.buttons_size.append(ten_btn)

        twenty_btn = Button(self, text="50x", width=10, command=lambda: self.set_brush_size(50, twenty_btn))
        twenty_btn.grid(row=1, column=6, sticky=W)
        self.buttons_size.append(twenty_btn)

        mode_lab = Label(self, text="??????????: ")
        mode_lab.grid(row=2, column=0, padx=0)
        mode_draw = Button(self, text="??????????????????", width=10, command=lambda: self.set_mode(MODE_MAKE_LINES, mode_draw))
        mode_draw.grid(row=2, column=1)
        mode_draw['state'] = DISABLED
        self.buttons_mode.append(mode_draw)

        mode_move = Button(self, text="??????????????????????", width=10, command=lambda: self.set_mode(MODE_MOVE_LINES, mode_move))
        mode_move.grid(row=2, column=2)
        self.buttons_mode.append(mode_move)

        mode_del = Button(self, text="????????????????", width=10, command=lambda: self.set_mode(MODE_DELETE_LINES, mode_del))
        mode_del.grid(row=2, column=3)
        self.buttons_mode.append(mode_del)

        mode_input_z = Button(self, text="???????? Z", width=10, command=lambda: self.set_mode(MODE_INPUT_3D, mode_input_z))
        mode_input_z.grid(row=2, column=4)
        self.buttons_mode.append(mode_input_z)

        # mode_select_all = Button(self, text="Group", width=10, command=self.group_lines)
        # mode_select_all.grid(row=2, column=5)

        mode_select_all = Button(self, text="Group", width=10, command=lambda: self.set_mode(MODE_SELECTION_TOOL, mode_select_all))
        mode_select_all.grid(row=2, column=5)
        self.buttons_mode.append(mode_select_all)

        mode_ungroup = Button(self, text="Ungroup", width=10, command=self.ungroup_lines)
        mode_ungroup.grid(row=2, column=6, sticky=W)

        slider_x = Label(self, text="X Rotation:", width=10)
        slider_x.grid(row=3, column=0)
        self.x_rotation_slider = Scale(self, from_=-math.pi, to=math.pi, orient=tkinter.HORIZONTAL, resolution=0.01, showvalue=False, command=self.change_slider)
        self.x_rotation_slider.set(0)
        self.x_rotation_slider.place(anchor="ne")
        self.x_rotation_slider.grid(row=3, column=1)

        slider_y = Label(self, text="Y Rotation:", width=10)
        slider_y.grid(row=3, column=2)
        self.y_rotation_slider = Scale(self, from_=-math.pi, to=math.pi, orient=tkinter.HORIZONTAL, resolution=0.01, showvalue=False, command=self.change_slider)
        self.y_rotation_slider.set(0)
        self.y_rotation_slider.place(anchor="ne")
        self.y_rotation_slider.grid(row=3, column=3)

        slider_z = Label(self, text="Z Rotation:", width=10)
        slider_z.grid(row=3, column=4)
        self.z_rotation_slider = Scale(self, from_=-math.pi, to=math.pi, orient=tkinter.HORIZONTAL, resolution=0.01, showvalue=False, command=self.change_slider)
        self.z_rotation_slider.set(0)
        self.z_rotation_slider.place(anchor="ne")
        self.z_rotation_slider.grid(row=3, column=5)

        reset_rotation_btn = Button(self, text="Reset rotation", width=10, command=self.reset_rotation)
        reset_rotation_btn.grid(row=3, column=6, sticky=W)

        slider_zoom = Label(self, text="Zoom:", width=10)
        slider_zoom.grid(row=4, column=0)
        self.zoom_slider = Scale(self, from_=1, to=20, orient=tkinter.HORIZONTAL, resolution=0.001, showvalue=False, command=self.change_slider)
        self.zoom_slider.set(0)
        self.zoom_slider.place(anchor="ne")
        self.zoom_slider.grid(row=4, column=1)


        self.cursor_text = Label(self, text="loading..")
        self.cursor_text.grid(row=6, column=0, sticky=W)
