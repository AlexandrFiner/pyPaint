import tkinter.simpledialog
from tkinter import *
from tkinter import colorchooser
from utils import *


class Paint(Frame):
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
        self.buttons_color = []
        self.buttons_size = []
        self.buttons_mode = []
        self.current_action = EVENT_NONE
        self.line_hovered = None
        self.line_coords = (0, 0, 0, 0)
        self.current_mode = MODE_MAKE_LINES
        self.setUI()

    def update_item_points(self, line):
        z1, z2 = 0.0, 0.0
        if line in self.points:
            z1, z2 = self.points[line][4], self.points[line][5]

        self.points[self.current_line] = [
            self.canv.coords(line)[0],
            self.canv.coords(line)[1],
            self.canv.coords(line)[2],
            self.canv.coords(line)[3],
            z1,
            z2
        ]

    def click_on_line(self, event):
        if self.current_mode == MODE_MOVE_LINES:
            if self.current_action == EVENT_NONE:
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

        if self.current_mode == MODE_INPUT_3D:
            self.current_line = event.widget.find_withtag('current')[0]
            z = tkinter.simpledialog.askfloat('Ввод', 'Введите Z координату')
            print(z)
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
            pass

    def mouse_motion(self, event):
        self.cursor_text.config(text="({x}, {y})".format(x=event.x, y=event.y))

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

                self.canv.coords(self.current_line,
                                 self.line_coords[0] + move[0],
                                 self.line_coords[1] + move[1],
                                 self.line_coords[2] + move[0],
                                 self.line_coords[3] + move[1]
                                 )

    def draw_line_end(self, event):
        if self.current_mode == MODE_MAKE_LINES:
            if self.current_action == EVENT_DRAW_LINE:
                self.current_action = EVENT_NONE
                x1, y1 = self.cursor_start
                x, y = event.x, event.y
                self.canv.coords(self.current_line, x1, y1, x, y)
                self.update_item_points(self.current_line)
                self.lines.append(self.current_line)

        if self.current_mode == MODE_MOVE_LINES:
            if self.current_action == EVENT_MOVE_LINE:
                self.current_action = EVENT_NONE
                x1, y1 = self.cursor_start
                x, y = event.x, event.y

                move = x-x1, y-y1

                self.canv.coords(self.current_line,
                                 self.line_coords[0] + move[0],
                                 self.line_coords[1] + move[1],
                                 self.line_coords[2] + move[0],
                                 self.line_coords[3] + move[1]
                                 )

                self.update_item_points(self.current_line)


        print(self.points)
        print(self.lines)


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

    def clear_canv(self):
        self.canv.delete("all")
        self.points.clear()
        self.lines = []

    def setUI(self):
        self.parent.title("PyGame")
        self.pack(fill=BOTH, expand=1)

        self.columnconfigure(6, weight=1)
        self.rowconfigure(3, weight=1)

        # Создаем холст с белым фоном
        self.canv = Canvas(self, bg="white")
        self.canv.grid(row=3, column=0, columnspan=7, padx=5, pady=5, sticky=E + W + S + N)

        self.canv.bind("<ButtonPress-1>", self.draw_line_start)
        self.canv.bind("<B1-Motion>", self.draw_line_action)
        self.canv.bind("<ButtonRelease-1>", self.draw_line_end)
        self.canv.bind("<Motion>", self.mouse_motion)

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

        black_btn = Button(self, text="черный", width=10, command=lambda: self.set_color("black", black_btn))
        black_btn.grid(row=0, column=4)
        self.buttons_color.append(black_btn)

        my_color_btn = Button(self, text="Свой цвет", width=10, command=self.set_color_picker)
        my_color_btn.grid(row=0, column=5)

        clear_btn = Button(self, text="Очистить", width=10, command=self.clear_canv)
        clear_btn.grid(row=0, column=6, sticky=W)

        size_lab = Label(self, text="Размер линии: ")
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

        mode_del = Button(self, text="Ввод Z", width=10, command=lambda: self.set_mode(MODE_INPUT_3D, mode_del))
        mode_del.grid(row=2, column=4)
        self.buttons_mode.append(mode_del)

        self.cursor_text = Label(self, text="loading..")
        self.cursor_text.grid(row=4, column=0, sticky=W)
