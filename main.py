from tkinter import *
from tkinter.messagebox import *
from src.paint import *


# вывод справки
def about():
    showinfo("Контакты", "vk.com/alexfiner")


# функция для создания главного окна
def main():
    root = Tk()
    app = Paint(root)
    # root.geometry("{}x{}+0+0".format(1000, 1900))
    m = Menu(root)
    root.config(menu=m)

    hm = Menu(m)
    m.add_cascade(label="Справка", menu=hm)
    hm.add_command(label="О программе", command=about)
    root.mainloop()


if __name__ == "__main__":
    main()
