from tkinter import *
from src.Settings import BUTTON_FONT, LABEL_FONT, LEN
import re
from src.Enums import *
from src.CalculateOperation import Calculate
from tkinter import messagebox


class FormFor3dOperation(Toplevel):
    def __init__(self, mainapp, master=None):
        super().__init__(master=master)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.title("3D operations")
        self.geometry("700x475")
        self.resizable(False, False)
        self.mainapp = mainapp

        Label(self, text="Перемещение", font=LABEL_FONT). grid(row=0, column=0, columnspan=9, padx=5, pady=5, sticky=NSEW)
        Label(self, text="m", font=LABEL_FONT).grid(row=1, column=0, padx=5, pady=5, sticky=NSEW)
        Label(self, text="n", font=LABEL_FONT).grid(row=1, column=3, padx=5, pady=5, sticky=NSEW)
        Label(self, text="l", font=LABEL_FONT).grid(row=1, column=6, padx=5, pady=5, sticky=NSEW)
        self.entry_m = Entry(self, font=LABEL_FONT)
        self.entry_n = Entry(self, font=LABEL_FONT)
        self.entry_l = Entry(self, font=LABEL_FONT)
        self.entry_m.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.entry_n.grid(row=1, column=4, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.entry_l.grid(row=1, column=7, columnspan=2, padx=5, pady=5, sticky=NSEW)
        Label(self, text="Масштабирование", font=LABEL_FONT).grid(row=2, column=0, columnspan=9, padx=5, pady=5, sticky=NSEW)
        Label(self, text="a", font=LABEL_FONT).grid(row=3, column=0, padx=5, pady=5, sticky=NSEW)
        Label(self, text="b", font=LABEL_FONT).grid(row=3, column=3, padx=5, pady=5, sticky=NSEW)
        Label(self, text="c", font=LABEL_FONT).grid(row=3, column=6, padx=5, pady=5, sticky=NSEW)
        self.entry_a = Entry(self, font=LABEL_FONT)
        self.entry_b = Entry(self, font=LABEL_FONT)
        self.entry_c = Entry(self, font=LABEL_FONT)
        self.entry_a.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.entry_b.grid(row=3, column=4, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.entry_c.grid(row=3, column=7, columnspan=2, padx=5, pady=5, sticky=NSEW)
        Label(self, text="Вращение", font=LABEL_FONT).grid(row=4, column=0, columnspan=9, padx=5, pady=5, sticky=NSEW)
        Label(self, text="Угол", font=LABEL_FONT).grid(row=5, column=0, padx=5, pady=5)
        self.rotate_angle_scale = Scale(self, orient=HORIZONTAL, from_=-360, to=360, resolution=1, font=LABEL_FONT)
        self.rotate_angle_scale.grid(row=5, column=1, columnspan=8, padx=5, pady=5, sticky=NSEW)
        self.x_var = IntVar()
        self.x_var.set(0)
        self.y_var = IntVar()
        self.y_var.set(0)
        self.z_var = IntVar()
        self.z_var.set(0)
        self.check_x = Checkbutton(self, text='по x', variable=self.x_var, font=LABEL_FONT, onvalue=1, offvalue=0)
        self.check_y = Checkbutton(self, text='по y', variable=self.y_var, font=LABEL_FONT, onvalue=1, offvalue=0)
        self.check_z = Checkbutton(self, text='по z', variable=self.z_var, font=LABEL_FONT, onvalue=1, offvalue=0)
        self.check_x.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky=NSEW)
        self.check_y.grid(row=6, column=3, columnspan=3, padx=5, pady=5, sticky=NSEW)
        self.check_z.grid(row=6, column=6, columnspan=3, padx=5, pady=5, sticky=NSEW)
        Label(self, text="Зеркалирование", font=LABEL_FONT).grid(row=7, column=0, columnspan=9, padx=5, pady=5, sticky=NSEW)
        self.mirror_x = IntVar()
        self.mirror_x.set(1)
        self.mirror_y = IntVar()
        self.mirror_y.set(1)
        self.mirror_z = IntVar()
        self.mirror_z.set(1)
        self.mirror_check_button_x = Checkbutton(self, text='по x', variable=self.mirror_x, font=LABEL_FONT, onvalue=-1, offvalue=1)
        self.mirror_check_button_y = Checkbutton(self, text='по y', variable=self.mirror_y, font=LABEL_FONT, onvalue=-1, offvalue=1)
        self.mirror_check_button_z = Checkbutton(self, text='по z', variable=self.mirror_z, font=LABEL_FONT, onvalue=-1, offvalue=1)
        self.mirror_check_button_x.grid(row=8, column=0, columnspan=3, padx=5, pady=5, sticky=NSEW)
        self.mirror_check_button_y.grid(row=8, column=3, columnspan=3, padx=5, pady=5, sticky=NSEW)
        self.mirror_check_button_z.grid(row=8, column=6, columnspan=3, padx=5, pady=5, sticky=NSEW)
        Label(self, text="Проецирование", font=LABEL_FONT).grid(row=9, column=0, columnspan=9, padx=5, pady=5, sticky=NSEW)
        self.projection_p_entry = Entry(self, font=LABEL_FONT)
        self.projection_q_entry = Entry(self, font=LABEL_FONT)
        self.projection_s_entry = Entry(self, font=LABEL_FONT)
        Label(self, text="p", font=LABEL_FONT).grid(row=10, column=0, padx=5, pady=5, sticky=NSEW)
        Label(self, text="q", font=LABEL_FONT).grid(row=10, column=3, padx=5, pady=5, sticky=NSEW)
        Label(self, text="s", font=LABEL_FONT).grid(row=10, column=6, padx=5, pady=5, sticky=NSEW)
        self.projection_p_entry.grid(row=10, column=1, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.projection_q_entry.grid(row=10, column=4, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.projection_s_entry.grid(row=10, column=7, columnspan=2, padx=5, pady=5, sticky=NSEW)
        self.send_button = Button(self, text="Применить", font=BUTTON_FONT, command=self._send_form)
        self.send_button.grid(row=11, column=0, columnspan=9, padx=5, pady=5, sticky=NSEW)
        for i in range(9):
            self.columnconfigure(i, weight=1)
        self.rowconfigure(11, weight=1)
        self._set_defaults()

    def _check_values(self):
        try:
            int(self.entry_m.get())
            int(self.entry_n.get())
            int(self.entry_l.get())
            float(self.entry_a.get())
            float(self.entry_b.get())
            float(self.entry_c.get())
            float(self.projection_p_entry.get())
            float(self.projection_q_entry.get())
            float(self.projection_s_entry.get())
            return True
        except:
            return False

    def _set_defaults(self):
        self.entry_m.insert(-1, "0")
        self.entry_n.insert(-1, "0")
        self.entry_l.insert(-1, "0")
        self.entry_a.insert(-1, "1")
        self.entry_b.insert(-1, "1")
        self.entry_c.insert(-1, "1")
        self.projection_p_entry.insert(-1, "0")
        self.projection_q_entry.insert(-1, "0")
        self.projection_s_entry.insert(-1, "0")

    def _send_form(self):
        if self._check_values():
            lines = []
            if self.mainapp.current_line is not None:
                lines = [self.mainapp.current_line]
            elif len(self.mainapp.current_lines) != 0:
                lines = self.mainapp.current_lines
            Calculate.calculate_3d(
                lines,
                int(self.entry_m.get()),
                int(self.entry_n.get()),
                int(self.entry_l.get()),
                float(self.entry_a.get()),
                float(self.entry_b.get()),
                float(self.entry_c.get()),
                int(self.rotate_angle_scale.get()),
                self.x_var.get(), self.y_var.get(), self.z_var.get(),
                self.mirror_x.get(), self.mirror_y.get(), self.mirror_z.get(),
                float(self.projection_p_entry.get()),
                float(self.projection_q_entry.get()),
                float(self.projection_s_entry.get())
            )
            self.mainapp.redraw_scene()
            self._on_closing()
        else:
            messagebox.showerror("Ошибка!", "Введите корректные значения")

    def _on_closing(self):
        self.grab_release()
        self.destroy()