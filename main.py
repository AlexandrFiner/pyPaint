from tkinter import *
from tkinter.messagebox import *
from src.paint import *


# выход из программы
def close_win():
    if askyesno("Выход", "Вы уверены?"):
        root.destroy()


# вывод справки
def about():
    showinfo("Контакты", "vk.com/alexfiner")


# функция для создания главного окна
def main():
    global root
    root = Tk()
    root.geometry("800x600+300+300")
    app = Paint(root)
    m = Menu(root)
    root.config(menu=m)

    fm = Menu(m)
    m.add_cascade(label="Файл", menu=fm)
    fm.add_command(label="Выход", command=close_win)

    hm = Menu(m)
    m.add_cascade(label="Справка", menu=hm)
    hm.add_command(label="О программе", command=about)
    root.mainloop()


if __name__ == "__main__":
    main()
