from tkinter import *
from src.Settings import BUTTON_FONT, LABEL_FONT, LEN
import re
from src.Enums import *
from src.CalculateOperation import Calculate
from tkinter import messagebox


class FormFor2dOperation(Toplevel):
    def __init__(self, mainapp, master=None):
        super().__init__(master=master)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.title("2D operations")
        self.geometry("600x400")
        self.resizable(False, False)
        self.mainapp = mainapp
        self.projection_mode = ProjectionMode.xy

        # projection mode buttons
        self.xy_button = Button(self, text="XY", font=BUTTON_FONT, relief=SUNKEN,
                                command=self._set_projection_xy)
        self.zy_button = Button(self, text="ZY", font=BUTTON_FONT,
                                command=self._set_projection_zy)
        self.xz_button = Button(self, text="XZ", font=BUTTON_FONT,
                                command=self._set_projection_xz)

        # transfer operation widgets
        self.transfer_m_entry = Entry(self, font=LABEL_FONT)
        self.transfer_n_entry = Entry(self, font=LABEL_FONT)

        # scale operation widgets
        self.scale_a_entry = Entry(self, font=LABEL_FONT)
        self.scale_b_entry = Entry(self, font=LABEL_FONT)

        # rotate operation widgets
        self.rotate_angle_scale = Scale(self, orient=HORIZONTAL, from_=-360, to=360, resolution=1, font=LABEL_FONT)

        # mirroring operation widgets
        self.abc_var = IntVar()
        self.abc_var.set(1)
        self.ord_var = IntVar()
        self.ord_var.set(1)
        self.mirror_check_button_abc = Checkbutton(self, text='по абсциссе', variable=self.abc_var, font=LABEL_FONT,
                                                   onvalue=-1, offvalue=1)
        self.mirror_check_button_ord = Checkbutton(self, text='по ординате', variable=self.ord_var, font=LABEL_FONT,
                                                   onvalue=-1, offvalue=1)

        # projection operation widgets
        self.projection_p_entry = Entry(self, font=LABEL_FONT)
        self.projection_q_entry = Entry(self, font=LABEL_FONT)

        # confirm changes button
        self.send_button = Button(self, text="Применить", font=BUTTON_FONT, command=self._confirm)

        # grid all widgets
        self._grid()
        self._set_defaults()

    def _check_entries(self):
        try:
            n = int(self.transfer_n_entry.get())
            m = int(self.transfer_m_entry.get())
            a = float(self.scale_a_entry.get())
            b = float(self.scale_b_entry.get())
            p = float(self.projection_p_entry.get())
            q = float(self.projection_q_entry.get())
        except:
            messagebox.showerror("Ошибка", f"Введите корректные значения в поля")

    def _confirm(self):
        self._check_entries()
        if self.mainapp.current_line is not None:
            Calculate.calculate_2d(
                [self.mainapp.current_line], self.projection_mode,
                int(self.transfer_m_entry.get()), int(self.transfer_n_entry.get()),  # m,n
                float(self.scale_a_entry.get()), float(self.scale_b_entry.get()),  # a,b
                int(self.rotate_angle_scale.get()),  # alpha
                self.abc_var.get(), self.ord_var.get(),  # z1,z2
                float(self.projection_p_entry.get()), int(self.projection_q_entry.get())  # p,q
            )
        elif len(self.mainapp.current_lines) != 0:
            Calculate.calculate_2d(
                self.mainapp.current_lines, self.projection_mode,
                int(self.transfer_m_entry.get()), int(self.transfer_n_entry.get()),  # m,n
                float(self.scale_a_entry.get()), float(self.scale_b_entry.get()),  # a,b
                int(self.rotate_angle_scale.get()),  # alpha
                self.abc_var.get(), self.ord_var.get(),  # z1,z2
                float(self.projection_p_entry.get()), int(self.projection_q_entry.get())  # p,q
            )
        self.mainapp.redraw_scene()
        self._on_closing()

    # grid
    def _grid(self):
        # projection mode buttons
        # self.xy_button.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky=NSEW)
        # self.zy_button.grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky=NSEW)
        # self.xz_button.grid(row=0, column=4, columnspan=2, padx=5, pady=5, sticky=NSEW)
        # transfer
        Label(self, text="Перемещение", font=LABEL_FONT).grid(row=1, column=0, columnspan=6, padx=5, pady=5,
                                                              sticky=NSEW)
        Label(self, text="m", font=LABEL_FONT).grid(row=2, column=0, padx=5, pady=5, sticky=NSEW)
        Label(self, text="n", font=LABEL_FONT).grid(row=2, column=3, padx=5, pady=5, sticky=NSEW)
        self.transfer_m_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.transfer_n_entry.grid(row=2, column=4, columnspan=2, padx=5, pady=5, sticky=NSEW)
        # scale
        Label(self, text="Масштабирование", font=LABEL_FONT).grid(row=3, column=0, columnspan=6, padx=5, pady=5,
                                                                  sticky=NSEW)
        Label(self, text="a", font=LABEL_FONT).grid(row=4, column=0, padx=5, pady=5, sticky=NSEW)
        Label(self, text="b", font=LABEL_FONT).grid(row=4, column=3, padx=5, pady=5, sticky=NSEW)
        self.scale_a_entry.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.scale_b_entry.grid(row=4, column=4, columnspan=2, padx=5, pady=5, sticky=NSEW)
        # rotate
        Label(self, text="Вращение", font=LABEL_FONT).grid(row=5, column=0, columnspan=6, padx=5, pady=5, sticky=NSEW)
        Label(self, text="Угол", font=LABEL_FONT).grid(row=6, column=0, padx=5, pady=5)
        self.rotate_angle_scale.grid(row=6, column=1, columnspan=5, padx=5, pady=5, sticky=NSEW)
        # mirror
        Label(self, text="Зеркалирование", font=LABEL_FONT).grid(row=7, column=0, columnspan=6, padx=5, pady=5,
                                                                 sticky=NSEW)
        self.mirror_check_button_abc.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky=NSEW)
        self.mirror_check_button_ord.grid(row=8, column=3, columnspan=3, padx=5, pady=5, sticky=NSEW)
        # project
        Label(self, text="Проецирование", font=LABEL_FONT).grid(row=9, column=0, columnspan=6, padx=5, pady=5,
                                                                sticky=NSEW)
        Label(self, text="p", font=LABEL_FONT).grid(row=10, column=0, padx=5, pady=5, sticky=NSEW)
        Label(self, text="q", font=LABEL_FONT).grid(row=10, column=3, padx=5, pady=5, sticky=NSEW)
        self.projection_p_entry.grid(row=10, column=1, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.projection_q_entry.grid(row=10, column=4, columnspan=2, padx=5, pady=5, sticky=NSEW)
        # confirm
        self.send_button.grid(row=11, column=0, columnspan=6, padx=5, pady=5, sticky=NSEW)

        for i in range(11):
            self.rowconfigure(i, weight=1, minsize=25)
        for i in range(5):
            self.columnconfigure(i, weight=1, minsize=50)

    def _set_defaults(self):
        self.transfer_m_entry.insert(-1, str(0))
        self.transfer_n_entry.insert(-1, str(0))
        self.scale_a_entry.insert(-1, str(1))
        self.scale_b_entry.insert(-1, str(1))
        self.projection_p_entry.insert(-1, str(0))
        self.projection_q_entry.insert(-1, str(0))

    def _set_projection_xy(self):
        self.projection_mode = ProjectionMode.xy
        self.xy_button.config(relief=SUNKEN)
        self.zy_button.config(relief=RAISED)
        self.xz_button.config(relief=RAISED)

    def _set_projection_zy(self):
        self.projection_mode = ProjectionMode.zy
        self.xy_button.config(relief=RAISED)
        self.zy_button.config(relief=SUNKEN)
        self.xz_button.config(relief=RAISED)

    def _set_projection_xz(self):
        self.projection_mode = ProjectionMode.xz
        self.xy_button.config(relief=RAISED)
        self.zy_button.config(relief=RAISED)
        self.xz_button.config(relief=SUNKEN)

    def _on_closing(self):
        self.grab_release()
        self.destroy()
