from tkinter import *
from src.Primitives import *
import numpy
from src.Settings import *
import re
from src.CalculateOperation import Calculate


class TrimetricForm(Toplevel):
    def __init__(self, mainapp, master=None):
        super().__init__(master=master)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.title("Trimetric")
        self.geometry("1500x1000")
        self.resizable(False, False)
        self.lines = []
        for i in mainapp.lines:
            self.lines.append(
                Line(
                    Point(
                        i.p1.x,
                        i.p1.y,
                        i.p1.z,
                        i.p1.ok
                    ),
                    Point(
                        i.p2.x,
                        i.p2.y,
                        i.p2.z,
                        i.p2.ok
                    ),
                    i.color,
                    i.width
                )
            )
        check = (self.register(self._is_valid), "%P")

        # objects
        self.field = Canvas(self, bg=CANVAS_BG_COLOR, scrollregion=(MINX, MINY, MAXX, MAXY))
        self.scroll_x = Scrollbar(self.field, orient=HORIZONTAL, command=self.field.xview, cursor="fleur")
        self.scroll_y = Scrollbar(self.field, orient=VERTICAL, command=self.field.yview, cursor="fleur")
        self.scroll_x.pack(side=BOTTOM, fill=X)
        self.scroll_y.pack(side=RIGHT, fill=Y)
        self.field.config(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)

        self.phi_scale = Scale(self, orient=HORIZONTAL, from_=-360, to=360, resolution=1, font=LABEL_FONT)
        self.tetta_scale = Scale(self, orient=HORIZONTAL, from_=-360, to=360, resolution=1, font=LABEL_FONT)
        self.camera_entry = Entry(self, validate="key", validatecommand=check, font=LABEL_FONT)

        # grid
        self.field.grid(row=0, column=0, columnspan=8, rowspan=4, padx=5, pady=5, sticky=NSEW)
        self.phi_scale.grid(row=0, column=8, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.tetta_scale.grid(row=1, column=8, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.camera_entry.grid(row=2, column=8, columnspan=2, padx=5, pady=5, sticky=NSEW)
        Label(self, text="phi", font=LABEL_FONT).grid(
            row=0, column=10, padx=5, pady=5, sticky=NSEW)
        Label(self, text="tetta", font=LABEL_FONT).grid(
            row=1, column=10, padx=5, pady=5, sticky=NSEW)
        Label(self, text="Zc", font=LABEL_FONT).grid(
            row=2, column=10, padx=5, pady=5, sticky=NSEW)
        self.rowconfigure(3, weight=1)
        self.columnconfigure(0, weight=1)

        # binds
        self.phi_scale.bind("<B1-Motion>", self._slider)
        self.tetta_scale.bind("<B1-Motion>", self._slider)
        self._set_defaults()
        self._redraw_scene()

    def _set_defaults(self):
        self.phi_scale.set(45)
        self.tetta_scale.set(35)
        self.camera_entry.insert(-1, "1000")

    def _slider(self, event):
        self._redraw_scene()

    def _redraw_scene(self):
        self.field.delete("all")
        copy = []
        for i in self.lines:
            copy.append(
                Line(
                    Point(
                        i.p1.x,
                        i.p1.y,
                        i.p1.z,
                        i.p1.ok
                    ),
                    Point(
                        i.p2.x,
                        i.p2.y,
                        i.p2.z,
                        i.p2.ok
                    ),
                    i.color,
                    i.width
                )
            )
        Calculate.trimetric_matrix(copy, int(self.phi_scale.get()), int(self.tetta_scale.get()),
                                   int(self.camera_entry.get()))
        for i in copy:
            self.field.create_line(
                i.p1.x,
                i.p1.y,
                i.p2.x,
                i.p2.y,
                width=i.width,
                fill=i.color,
                smooth=True
            )

    @staticmethod
    def _is_valid(value):
        return True if re.match("^-$|^$|-?(0|[1-9]\d*)(?<!-0)$", value) is not None else False

    def _on_closing(self):
        self.grab_release()
        self.destroy()