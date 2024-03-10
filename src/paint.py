import tkinter.simpledialog
import tkinter.filedialog
import tkinter.messagebox
import json
from tkinter import *
from tkinter import colorchooser
from utils import *
from src.geometry import Geometry
import math
from json import JSONEncoder, JSONDecoder
from src.TrimetricForm import TrimetricForm


class MyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Line) or isinstance(obj, Point):
            return obj.__dict__()
        else:
            return JSONEncoder.default(self, obj)


class Paint(Frame):
    CANVAS_WIDTH = 840
    CANVAS_HEIGHT = 525

    def __init__(self, parent):
        super().__init__()
        self.y_bar = None
        self.x_bar = None
        self.cursor_text = None
        self.canv = None
        self.parent = parent
        self.brush_size = None
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
        self.current_zero_coord = [0, 0]

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


        self._geometry_handler._angle_x = self.x_rotation_slider.get()
        self._geometry_handler._angle_y = self.y_rotation_slider.get()
        self._geometry_handler._angle_z = self.z_rotation_slider.get()
        rot_x, rot_y, rot_z = self._geometry_handler.calculate_rot_matrix(
            self._geometry_handler._angle_x,
            self._geometry_handler._angle_y,
            self._geometry_handler._angle_z,
        )
        x1, y1, z1 = self._geometry_handler.inverse_transform_point(coords[0], coords[1], rot_x, rot_y, rot_z)
        x2, y2, z2 = self._geometry_handler.inverse_transform_point(coords[2], coords[3], rot_x, rot_y, rot_z)

        self.points[line] = [
            x1,
            y1,
            z1,
            x2,
            y2,
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
            z = tkinter.simpledialog.askfloat('Ввод', 'Введите Z координату')
            self.points[self.current_line][4] = z
            self.points[self.current_line][5] = z

    def draw_line_start(self, event):
        if self.current_mode == MODE_MAKE_LINES:
            if self.current_action == EVENT_NONE:
                self.current_action = EVENT_DRAW_LINE
                x, y = event.x, event.y
                self.cursor_start = (x, y)
                self.current_line = self.canv.create_line(x, y, x, y, fill=self.color, width=self.brush_size.get())
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

    def save_project(self):
        data = dict()

        all_items = self.canv.find_all()
        lines = [item for item in all_items if self.canv.type(item) == "line"]

        for line in lines:
            data[line] = {
                "points": self.points[line],
                "color":  self.canv.itemcget(line, "fill"),
                "width":  self.canv.itemcget(line, "width"),
            }

        file_path = tkinter.filedialog.asksaveasfilename(
            filetypes=[('JSON File', '*.json')],
        )
        if file_path != "":
            try:
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, cls=MyEncoder)
                tkinter.messagebox.showinfo("Сохранение", "Файл успешно сохранен!")
            except Exception as e:
                tkinter.messagebox.showerror("Ошибка сохранения", "Ошибка при записи в файл!")
        else:
            tkinter.messagebox.showinfo("Сохранение", "Файл не был сохранен!")

    def decode_object(self, obj):
        # if 'p1' and 'p2' in obj:
        #     p1_dict = obj['p1']
        #     p2_dict = obj['p2']
        #     return Line(
        #         Point(
        #             p1_dict['x'],
        #             p1_dict['y'],
        #             p1_dict['z'],
        #             p1_dict['ok']
        #         ),
        #         Point(
        #             p2_dict['x'],
        #             p2_dict['y'],
        #             p2_dict['z'],
        #             p2_dict['ok']
        #         ),
        #         obj['color'],
        #         obj['width']
        #     )
        return obj


    def load_project(self):
        file_path = tkinter.filedialog.askopenfilename(
            filetypes=[('JSON File', '*.json')],
        )
        if file_path != "":
            try:
                self.canv.delete("all")
                self.points.clear()
                self.lines_in_group = []
                self.lines = []

                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file, object_hook=self.decode_object)
                    for (line, line_data) in data.items():
                        color = line_data['color']
                        width = line_data['width']

                        current_line = self.canv.create_line(line_data['points'][0], line_data['points'][1], line_data['points'][3], line_data['points'][4], fill=color, width=width)
                        self.lines.append(current_line)
                        self.points[current_line] = line_data['points']
                    # self.lines = json.load(file, object_hook=self.decode_object)

                self.reset_rotation()
                tkinter.messagebox.showinfo("Загрузка", "Файл успешно открыт!")
            except Exception as e:
                print(e)
                tkinter.messagebox.showerror("Ошибка загрузки", "Ошибка при чтении файла!")
        else:
            tkinter.messagebox.showinfo("Загрузка", "Файл не выбран!")

    def set_color(self, new_color, button):
        self.color = new_color
        for btn in self.buttons_color:
            btn['state'] = NORMAL
        button['state'] = DISABLED

    def set_color_picker(self):
        color_code = colorchooser.askcolor(title="Выбор цвета")
        self.color = color_code[1]
        for btn in self.buttons_color:
            btn['state'] = NORMAL

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

    def open_trimetric_form(self):
        if len(self.lines) != 0:
            form = TrimetricForm(self)
            form.grab_set()
        else:
            tkinter.messagebox.showerror("Ошибка", "Пустое полотно!")

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

        for line in self.lines:
            points = self.points[line]
            x1, y1 = self._geometry_handler.transform_point(([[points[0]], [points[1]], [points[2]]]), rot_x, rot_y, rot_z)
            x, y = self._geometry_handler.transform_point(([[points[3]], [points[4]], [points[5]]]), rot_x, rot_y, rot_z)
            self.canv.coords(line, x1, y1, x, y)

        pass

    def set_view_mode(self, mode):
        if mode == 1:
            pass
        if mode == 2:
            pass
        if mode == 3:
            pass

    def reset_rotation(self):
        self.x_rotation_slider.set(0)
        self.y_rotation_slider.set(0)
        self.z_rotation_slider.set(0)
        self.zoom_slider.set(1)
        self.change_slider()

    def setUI(self):
        # self.parent.minsize((1165, 630))

        self.parent.title("PyPaint")
        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(6, weight=1)
        self.rowconfigure(9, weight=1)

        # Создаем холст с белым фоном
        AREA = 10000
        self.canv = Canvas(self, bg="white", cursor="pencil", width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT,
                           scrollregion=(-AREA, -AREA, AREA, AREA))
        self._geometry_handler = Geometry(self.CANVAS_WIDTH, self.CANVAS_HEIGHT)

        # # scrollbars for canvas
        self.x_bar = Scrollbar(self.canv, orient=HORIZONTAL, cursor="fleur")
        # self.x_bar.pack(side=BOTTOM, fill=X)
        # self.x_bar.config(command=self.canv.xview)

        # self.y_bar = Scrollbar(self.canv, orient=VERTICAL, cursor="fleur")
        # self.y_bar.pack(side=RIGHT, fill=Y)
        # self.y_bar.config(command=self.canv.yview)

        self.canv.bind("<ButtonPress-1>", self.draw_line_start)
        self.canv.bind("<B1-Motion>", self.draw_line_action)
        self.canv.bind("<ButtonRelease-1>", self.draw_line_end)
        self.canv.bind("<Motion>", self.mouse_motion)
        # self.x_bar.bind("<B1-Motion>", self._update_zero_x_coord)
        # self.y_bar.bind("<B1-Motion>", self._update_zero_y_coord)

        # создаем метку для кнопок изменения цвета кисти
        color_lab = Label(self, text="Цвет: ")
        color_lab.grid(row=0, column=0, padx=6)

        red_btn = Button(self, text="Красный", width=10, command=lambda: self.set_color("red", red_btn))
        red_btn.grid(row=0, column=1)
        red_btn['state'] = DISABLED
        self.buttons_color.append(red_btn)

        green_btn = Button(self, text="Зеленый", width=10, command=lambda: self.set_color("green", green_btn))
        green_btn.grid(row=0, column=2)
        self.buttons_color.append(green_btn)

        blue_btn = Button(self, text="Синий", width=10, command=lambda: self.set_color("blue", blue_btn))
        blue_btn.grid(row=0, column=3)
        self.buttons_color.append(blue_btn)

        black_btn = Button(self, text="Черный", width=10, command=lambda: self.set_color("black", black_btn))
        black_btn.grid(row=0, column=4)
        self.buttons_color.append(black_btn)

        my_color_btn = Button(self, text="Свой цвет", width=10, command=self.set_color_picker)
        my_color_btn.grid(row=0, column=5)

        size_lab = Label(self, text="Размер линии: ")
        size_lab.grid(row=1, column=0, padx=5)
        self.brush_size = Scale(self, from_=1, to=10, orient=tkinter.HORIZONTAL, resolution=1)
        self.brush_size.set(2)
        self.brush_size.place(anchor="ne")
        self.brush_size.grid(row=1, column=1, columnspan=6, padx=5, pady=5, sticky=NSEW)


        mode_lab = Label(self, text="Режим: ")
        mode_lab.grid(row=2, column=0, padx=0)
        mode_draw = Button(self, text="Рисование", width=10, command=lambda: self.set_mode(MODE_MAKE_LINES, mode_draw))
        mode_draw.grid(row=2, column=1)
        mode_draw['state'] = DISABLED
        self.buttons_mode.append(mode_draw)

        mode_move = Button(self, text="Перемещение", width=10, command=lambda: self.set_mode(MODE_MOVE_LINES, mode_move))
        mode_move.grid(row=2, column=2)
        self.buttons_mode.append(mode_move)

        mode_del = Button(self, text="Удаление", width=10, command=lambda: self.set_mode(MODE_DELETE_LINES, mode_del))
        mode_del.grid(row=2, column=3)
        self.buttons_mode.append(mode_del)

        mode_input_z = Button(self, text="Ввод Z", width=10, command=lambda: self.set_mode(MODE_INPUT_3D, mode_input_z))
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

        preset = Label(self, text="Действия: ")
        preset.grid(row=5, column=0, padx=0)
        clear_btn = Button(self, text="Очистить", width=10, command=self.clear_canv)
        clear_btn.grid(row=5, column=1, sticky=W)
        trimetric_matrix_button = Button(self, text="Осмотр", width=10, command=self.open_trimetric_form)
        trimetric_matrix_button.grid(row=5, column=2, sticky=W)

        preset = Label(self, text="Файл: ")
        preset.grid(row=6, column=0, padx=0)
        one_btn = Button(self, text="Сохранить проект", width=10, command=self.save_project)
        one_btn.grid(row=6, column=1)
        one_btn = Button(self, text="Загрузить проект", width=10, command=self.load_project)
        one_btn.grid(row=6, column=2)

        self.canv.grid(row=7, column=0, columnspan=7, padx=5, pady=5, sticky=E + W + S + N)


        self.cursor_text = Label(self, text="loading..")
        self.cursor_text.grid(row=8, column=0, sticky=W)

    # render methods
    # redraw scene
    def redraw_scene(self):
        self.canvas.delete("all")
        # draw lines primitive
        for i in range(len(self.lines)):
            self._draw_line(self.lines[i])

    def _draw_line(self, line):
        if isinstance(line, Line):
            canvas_x1, canvas_y1 = self._get_canvas_coord_from_projection_point(line.p1)
            canvas_x2, canvas_y2 = self._get_canvas_coord_from_projection_point(line.p2)
            # drawing line
            self.canvas.create_line(
                canvas_x1,
                canvas_y1,
                canvas_x2,
                canvas_y2,
                width=line.width,
                fill="red" if (self.current_line == line or line in self.current_lines)
                              and self.work_mode != WorkingMode.add_mode else line.color,
                smooth=True
            )
            # drawing line text
            if self.line_text_flag:
                canvas_p1_projection = self._get_canvas_coord_from_projection_point(line.p1)
                canvas_p2_projection = self._get_canvas_coord_from_projection_point(line.p2)
                anchor_p1 = self._get_line_text_anchor(canvas_p1_projection)
                anchor_p2 = self._get_line_text_anchor(canvas_p2_projection)
                opt1 = self._get_line_text_options(line.p1, anchor_p1)
                opt2 = self._get_line_text_options(line.p2, anchor_p2)
                self.canvas.create_text(canvas_p1_projection[0], canvas_p1_projection[1], opt1)
                self.canvas.create_text(canvas_p2_projection[0], canvas_p2_projection[1], opt2)

    # transit zero coord by x-scrollbar
    def _update_zero_x_coord(self, event):
        self.current_zero_coord[0] = int(self.x_bar.get()[0] * 2 * MAXX + MINX)

    # transit zero coord by y_scrollbar
    def _update_zero_y_coord(self, event):
        self.current_zero_coord[1] = int(self.y_bar.get()[0] * 2 * MAXY + MINY)
