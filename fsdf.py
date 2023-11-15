import sqlite3, xlsxwriter, sys, os
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image
import pandas as pd
from tkinter.messagebox import showerror, showinfo

accessoriess = ["№", "Модель", "Производитель", "Цена", "Описание", "Гарантия."]
accessory_saless = ["№", "Дата продажи", "Артикул", "Количесвто продаж", "Общее количество продаж."]
phoness = ["№", "Модель", "Производитель", "Цена", "Описание", "Гарантия"]
saless = ["№", "Дата продажи", "Артикул", "Количество продаж", "Общее количество продаж"]
stocks = ["№", "Артикул", "Дата поступления", "Номер документа", "Поставщик", "Количество", "Общее количество"]


class WindowMain(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('Салон сотовой связи')
        self.wm_iconbitmap()
        self.iconphoto(True, tk.PhotoImage(file="image1\\icon.png"))
        self.last_headers = None

        # Создание фрейма для отображения таблицы
        self.table_frame = ctk.CTkFrame(self, width=700, height=400)
        self.table_frame.grid(row=0, column=0, padx=5, pady=5)

        # Загрузка фона
        bg = ctk.CTkImage(Image.open("image1\\mobile_st_fon.jpg"), size=(700, 400))
        lbl = ctk.CTkLabel(self.table_frame, image=bg, text='Таблица не открыта', font=("Calibri", 40))
        lbl.place(relwidth=1, relheight=1)

        # Создание меню
        self.menu_bar = tk.Menu(self, background='#555', foreground='white')

        # Меню "Файл"
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.quit)
        self.menu_bar.add_cascade(label="Файл", menu=file_menu)

        # Меню "Таблицы"
        references_menu = tk.Menu(self.menu_bar, tearoff=0)
        references_menu.add_command(label="Аксессуары",
                                    command=lambda: self.show_table("SELECT * FROM accessories", accessoriess))
        references_menu.add_command(label="Продажи аксессуаров",
                                    command=lambda: self.show_table("SELECT * FROM accessory_sales", accessory_saless))
        references_menu.add_command(label="Смартфоны",
                                    command=lambda: self.show_table("SELECT * FROM phones", phoness))
        references_menu.add_command(label="Продажи смартвонов",
                                    command=lambda: self.show_table("SELECT * FROM sales", saless))
        references_menu.add_command(label="Поставки",
                                    command=lambda: self.show_table("SELECT * FROM stock", stocks))
        self.menu_bar.add_cascade(label="Таблицы", menu=references_menu)

        # Меню "Отчёты"
        reports_menu = tk.Menu(self.menu_bar, tearoff=0)
        reports_menu.add_command(label="Создать Отчёт", command=self.to_xlsx)
        self.menu_bar.add_cascade(label="Отчёты", menu=reports_menu)

        # Меню "Сервис"
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Руководство пользователя")
        help_menu.add_command(label="O программе")
        self.menu_bar.add_cascade(label="Сервис", menu=help_menu)

        # Настройка цветов меню
        file_menu.configure(bg='#555', fg='white')
        references_menu.configure(bg='#555', fg='white')
        reports_menu.configure(bg='#555', fg='white')
        help_menu.configure(bg='#555', fg='white')

        # Установка меню в главное окно
        self.config(menu=self.menu_bar)

        btn_width = 150
        pad = 5

        # Создание кнопок и виджетов для поиска и редактирования данных
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=0, column=1)
        ctk.CTkButton(btn_frame, text="добавить", width=btn_width, command=self.add).pack(pady=pad)
        ctk.CTkButton(btn_frame, text="удалить", width=btn_width, command=self.delete).pack(pady=pad)
        ctk.CTkButton(btn_frame, text="изменить", width=btn_width, command=self.change).pack(pady=pad)

        search_frame = ctk.CTkFrame(self)
        search_frame.grid(row=1, column=0, pady=pad)
        self.search_entry = ctk.CTkEntry(search_frame, width=300)
        self.search_entry.grid(row=0, column=0, padx=pad)
        ctk.CTkButton(search_frame, text="Поиск", width=20, command=self.search).grid(row=0, column=1, padx=pad)
        ctk.CTkButton(search_frame, text="Искать далее", width=20, command=self.search_next).grid(row=0, column=2,
                                                                                                  padx=pad)
        ctk.CTkButton(search_frame, text="Сброс", width=20, command=self.reset_search).grid(row=0, column=3, padx=pad)

    def search_in_table(self, table, search_terms, start_item=None):
        table.selection_remove(table.selection())  # Сброс предыдущего выделения

        items = table.get_children('')
        start_index = items.index(start_item) + 1 if start_item else 0

        for item in items[start_index:]:
            values = table.item(item, 'values')
            for term in search_terms:
                if any(term.lower() in str(value).lower() for value in values):
                    table.selection_add(item)
                    table.focus(item)
                    table.see(item)
                    return item  # Возвращаем найденный элемент

    def reset_search(self):
        if self.last_headers:
            self.table.selection_remove(self.table.selection())
        self.search_entry.delete(0, 'end')

    def search(self):
        if self.last_headers:
            self.current_item = self.search_in_table(self.table, self.search_entry.get().split(','))

    def search_next(self):
        if self.last_headers:
            if self.current_item:
                self.current_item = self.search_in_table(self.table, self.search_entry.get().split(','),
                                                         start_item=self.current_item)

    def to_xlsx(self):
        if self.last_headers == accessoriess:
            sql_query = "SELECT * FROM accessories"
            table_name = "accessories"
        elif self.last_headers == accessory_saless:
            sql_query = "SELECT * FROM accessory_sales"
            table_name = "accessory_sales"
        elif self.last_headers == phoness:
            sql_query = "SELECT * FROM phones"
            table_name = "phones"
        elif self.last_headers == saless:
            sql_query = "SELECT * FROM sales"
            table_name = "sales"
        elif self.last_headers == stocks:
            sql_query = "SELECT * FROM stock"
            table_name = "stock"
        else:
            return

        dir = sys.path[0] + "\\export"
        os.makedirs(dir, exist_ok=True)
        path = dir + f"\\{table_name}.xlsx"

        # Подключение к базе данных SQLite
        conn = sqlite3.connect("mobilee_store_db.db")
        cursor = conn.cursor()
        # Получите данные из базы данных
        cursor.execute(sql_query)
        data = cursor.fetchall()
        # Создайте DataFrame из данных
        df = pd.DataFrame(data, columns=self.last_headers)
        # Создайте объект writer для записи данных в Excel
        writer = pd.ExcelWriter(path, engine='xlsxwriter')
        # Запишите DataFrame в файл Excel
        df.to_excel(writer, 'Лист 1', index=False)
        # Сохраните результат
        writer.close()

        showinfo(title="Успешно", message=f"Данные экспортированы в {path}")

    def add(self):
        if self.last_headers == accessoriess:
            WindowAccessories("add")
        elif self.last_headers == accessory_saless:
            WindowAccessory_saless("add")
        elif self.last_headers == phoness:
            WindowPhoness("add")
        elif self.last_headers == saless:
            WindowSales("add")
        elif self.last_headers == stocks:
            WindowStocks("add")
        else:
            return

        self.withdraw()

    def delete(self):
        if self.last_headers:
            select_item = self.table.selection()
            if select_item:
                item_data = self.table.item(select_item[0])["values"]
            else:
                showerror(title="Ошибка", message="He выбранна запись")
                return
        else:
            return

        if self.last_headers == accessoriess:
            WindowAccessories("delete", item_data)
        elif self.last_headers == accessory_saless:
            WindowAccessory_saless("delete", item_data)
        elif self.last_headers == phoness:
            WindowPhoness("delete", item_data)
        elif self.last_headers == saless:
            WindowSales("delete", item_data)
        elif self.last_headers == stocks:
            WindowStocks("delete", item_data)
        else:
            return

        self.withdraw()

    def change(self):
        if self.last_headers:
            select_item = self.table.selection()
            if select_item:
                item_data = self.table.item(select_item[0])["values"]
            else:
                showerror(title="Ошибка", message="He выбранна запись")
                return
        else:
            return

        if self.last_headers == accessoriess:
            WindowAccessories("change", item_data)
        elif self.last_headers == accessory_saless:
            WindowAccessory_saless("change", item_data)
        elif self.last_headers == phoness:
            WindowPhoness("change", item_data)
        elif self.last_headers == saless:
            WindowSales("change", item_data)
        elif self.last_headers == stocks:
            WindowStocks("change", item_data)
        else:
            return

        self.withdraw()

    def show_table(self, sql_query, headers=None):
        # Очистка фрейма перед отображением новых данных
        for widget in self.table_frame.winfo_children(): widget.destroy()

        # Подключение к базе данных SQLite
        conn = sqlite3.connect("mobilee_store_db.db")
        cursor = conn.cursor()

        # Выполнение SQL-запроса
        cursor.execute(sql_query)
        self.last_sql_query = sql_query

        # Получение заголовков таблицы и данных
        if headers == None:  # если заголовки не были переданы используем те что в БД
            table_headers = [description[0] for description in cursor.description]
        else:  # иначе используем те что передали
            table_headers = headers
            self.last_headers = headers
        table_data = cursor.fetchall()

        # Закрытие соединения с базой данных
        conn.close()

        canvas = ctk.CTkCanvas(self.table_frame, width=865, height=480)
        canvas.pack(fill="both", expand=True)

        x_scrollbar = ttk.Scrollbar(self.table_frame, orient="horizontal", command=canvas.xview)
        x_scrollbar.pack(side="bottom", fill="x")

        canvas.configure(xscrollcommand=x_scrollbar.set)

        self.table = ttk.Treeview(self.table_frame, columns=table_headers, show="headings", height=23)
        for header in table_headers:
            self.table.heading(header, text=header)
            self.table.column(header,
                              width=len(header) * 10 + 15)  # установка ширины столбца исходя длины его заголовка
        for row in table_data: self.table.insert("", "end", values=row)

        canvas.create_window((0, 0), window=self.table, anchor="nw")

        self.table.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def update_table(self):
        self.show_table(self.last_sql_query, self.last_headers)

class WindowAccessories(ctk.CTkToplevel):
    def __init__(self, operation, select_row=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())

        conn = sqlite3.connect("mobilee_store_db.db")

        conn.close

        if select_row:
            self.select_id_acc = select_row[0]
            self.select_model = select_row[1]
            self.select_manuf = select_row[2]
            self.select_price = select_row[3]
            self.select_opis = select_row[4]
            self.select_garand = select_row[5]

        if operation == "add":
            self.title("Добаление")
            ctk.CTkLabel(self, text="Добаление в таблицу 'Аксессуары'").grid(row=0, column=0, pady=5, padx=5,
                                                                             columnspan=2)

            ctk.CTkLabel(self, text="id Аксессуара").grid(row=1, column=0, pady=5, padx=5)
            self.id_acc = ctk.CTkEntry(self, width=300)
            self.id_acc.grid(row=1, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Модель").grid(row=2, column=0, pady=5, padx=5)
            self.model = ctk.CTkEntry(self, width=300)
            self.model.grid(row=2, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Производитель").grid(row=3, column=0, pady=5, padx=5)
            self.manuf = ctk.CTkEntry(self, width=300)
            self.manuf.grid(row=3, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Цена").grid(row=4, column=0, pady=5, padx=5)
            self.price = ctk.CTkEntry(self, width=300)
            self.price.grid(row=4, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Описание").grid(row=5, column=0, pady=5, padx=5)
            self.opis = ctk.CTkEntry(self, width=300)
            self.opis.grid(row=5, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Гарантия").grid(row=6, column=0, pady=5, padx=5)
            self.garand = ctk.CTkEntry(self, width=300)
            self.garand.grid(row=6, column=1, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=7, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Добавить", width=100, command=self.add).grid(row=7, column=1, pady=5, padx=5,
                                                                                   sticky="e")

        elif operation == "delete":
            self.title("Удаление")
            ctk.CTkLabel(self, text="Вы действиельно хотите\n удалить запись из таблицы 'Аксессуары'?"
                         ).grid(row=0, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkLabel(self, text=f"{self.select_id_acc}. {self.select_model}"
                         ).grid(row=1, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkButton(self, text="Нет", width=100, command=self.quit_win).grid(row=2, column=0, pady=5, padx=5,
                                                                                   sticky="w")
            ctk.CTkButton(self, text="Да", width=100, command=self.delete).grid(row=2, column=1, pady=5, padx=5,
                                                                                sticky="e")

        elif operation == "change":
            self.title("Изменение в таблице 'Аксессуары'")
            ctk.CTkLabel(self, text="Назввание поля").grid(row=0, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text="Текущее значение").grid(row=0, column=1, pady=5, padx=5)
            ctk.CTkLabel(self, text="Новое занчение").grid(row=0, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Модель").grid(row=1, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_model).grid(row=1, column=1, pady=5, padx=5)
            self.model = ctk.CTkEntry(self, width=300)
            self.model.grid(row=1, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Производитель").grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_manuf).grid(row=2, column=1, pady=5, padx=5)
            self.manuf = ctk.CTkEntry(self, width=300)
            self.manuf.grid(row=2, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Цена").grid(row=3, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_price).grid(row=3, column=1, pady=5, padx=5)
            self.price = ctk.CTkEntry(self, width=300)
            self.price.grid(row=3, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Описание").grid(row=4, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_opis).grid(row=4, column=1, pady=5, padx=5)
            self.opis = ctk.CTkEntry(self, width=300)
            self.opis.grid(row=4, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Гарантия").grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_garand).grid(row=5, column=1, pady=5, padx=5)
            self.garand = ctk.CTkEntry(self, width=300)
            self.garand.grid(row=5, column=2, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=6, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Сохранить", width=100, command=self.change).grid(row=6, column=2, pady=5, padx=5,
                                                                                       sticky="e")

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_id_acc = self.id_acc.get()
        new_model = self.model.get()
        new_manuf = self.manuf.get()
        new_price = self.price.get()
        new_opis = self.opis.get()
        new_garand = self.garand.get()

        if new_model != "" and new_manuf != "":
            try:
                conn = sqlite3.connect("mobilee_store_db.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO accessories (id, model, manufacturer, price, description, warranty_period) VALUES (?, ?, ?, ?, ?, ?)",
                    (new_id_acc, new_model, new_manuf, new_price, new_opis, new_garand))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("mobilee_store_db.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM accessories WHERE id = ?", (self.select_id_acc,))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_model = self.model.get() or self.select_model
        new_manuf = self.manuf.get() or self.select_manuf
        new_price = self.price.get() or self.select_price
        new_opis = self.opis.get() or self.select_opis
        new_garand = self.garand.get() or self.select_garand
        try:
            conn = sqlite3.connect("mobilee_store_db.db")
            cursor = conn.cursor()
            cursor.execute(f"""
                            UPDATE accessories SET (model, manufacturer, price, description, warranty_period) = (?, ?, ?, ?, ?)  WHERE id= {self.select_id_acc}
                        """, (new_model, new_manuf, new_price, new_opis, new_garand))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))


class WindowAccessory_saless(ctk.CTkToplevel):
    def __init__(self, operation, select_row=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())

        conn = sqlite3.connect("mobilee_store_db.db")

        conn.close

        if select_row:
            self.select_id_slyj_tel = select_row[0]
            self.select_id_predp = select_row[1]
            self.select_otdel = select_row[2]
            self.select_nomer_tel = select_row[3]
            self.select_qwer = select_row[4]

        if operation == "add":
            self.title("Добаление")
            ctk.CTkLabel(self, text="Добаление в таблицу 'Продажи аксессуаров'").grid(row=0, column=0, pady=5, padx=5,
                                                                           columnspan=2)

            ctk.CTkLabel(self, text="id проданного аксессуара").grid(row=1, column=0, pady=5, padx=5)
            self.id_slyj_tel = ctk.CTkEntry(self, width=300)
            self.id_slyj_tel.grid(row=1, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Дата продажи").grid(row=2, column=0, pady=5, padx=5)
            self.id_predp = ctk.CTkEntry(self, width=300)
            self.id_predp.grid(row=2, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Артикул").grid(row=3, column=0, pady=5, padx=5)
            self.otdel = ctk.CTkEntry(self, width=300)
            self.otdel.grid(row=3, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Кол-во продаж").grid(row=4, column=0, pady=5, padx=5)
            self.nomer_tel = ctk.CTkEntry(self, width=300)
            self.nomer_tel.grid(row=4, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Общее кол-во продаж").grid(row=5, column=0, pady=5, padx=5)
            self.qwer = ctk.CTkEntry(self, width=300)
            self.qwer.grid(row=5, column=1, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=6, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Добавить", width=100, command=self.add).grid(row=6, column=1, pady=5, padx=5, sticky="e")

        elif operation == "delete":
            self.title("Удаление")
            ctk.CTkLabel(self, text="Вы действиельно хотите\n удалить запись из таблицы 'Продажи аксессуаров'?"
                         ).grid(row=0, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkLabel(self, text=f"{self.select_id_slyj_tel}. {self.select_id_predp}"
                         ).grid(row=1, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkButton(self, text="Нет", width=100, command=self.quit_win).grid(row=2, column=0, pady=5, padx=5, sticky="w")
            ctk.CTkButton(self, text="Да", width=100, command=self.delete).grid(row=2, column=1, pady=5, padx=5, sticky="e")

        elif operation == "change":
            self.title("Изменение в таблице 'Продажи аксессуаров'")
            ctk.CTkLabel(self, text="Назввание поля").grid(row=0, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text="Текущее значение").grid(row=0, column=1, pady=5, padx=5)
            ctk.CTkLabel(self, text="Новое занчение").grid(row=0, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Дата продажи").grid(row=1, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_predp).grid(row=1, column=1, pady=5, padx=5)
            self.id_predp = ctk.CTkEntry(self, width=300)
            self.id_predp.grid(row=1, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Артикул").grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_otdel).grid(row=2, column=1, pady=5, padx=5)
            self.otdel = ctk.CTkEntry(self, width=300)
            self.otdel.grid(row=2, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Кол-во продаж").grid(row=3, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_nomer_tel).grid(row=3, column=1, pady=5, padx=5)
            self.nomer_tel = ctk.CTkEntry(self, width=300)
            self.nomer_tel.grid(row=3, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Общеее кол-во продаж").grid(row=4, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_qwer).grid(row=4, column=1, pady=5, padx=5)
            self.qwer = ctk.CTkEntry(self, width=300)
            self.qwer.grid(row=4, column=2, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Сохранить", width=100, command=self.change).grid(row=5, column=2, pady=5, padx=5,
                                                                                       sticky="e")

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_id_adres = self.id_slyj_tel.get()
        new_id_nomer_dom_tel = self.id_predp.get()
        new_nomer_dom_tel = self.otdel.get()
        new_id_slyjeb_telep = self.nomer_tel.get()
        new_qwer = self.qwer.get()

        if new_id_nomer_dom_tel != "" and new_nomer_dom_tel != "":
            try:
                conn = sqlite3.connect("mobilee_store_db.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO accessory_sales (id, sale_date, product_id, quantity_sold, total_sales_amount) VALUES (?, ?, ?, ?, ?)",
                    (new_id_adres, new_id_nomer_dom_tel, new_nomer_dom_tel, new_id_slyjeb_telep, new_qwer))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("mobilee_store_db.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM accessory_sales WHERE id = ?", (self.select_id_slyj_tel,))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_id_nomer_dom_tel = self.id_predp.get() or self.select_id_predp
        new_nomer_dom_tel = self.otdel.get() or self.select_otdel
        new_id_slyjeb_telep = self.nomer_tel.get() or self.select_nomer_tel
        new_qwer = self.qwer.get() or self.select_qwer
        try:
            conn = sqlite3.connect("mobilee_store_db.db")
            cursor = conn.cursor()
            cursor.execute(f"""
                        UPDATE accessory_sales SET (sale_date, product_id, quantity_sold, total_sales_amount) = (?, ?, ?, ?)  WHERE id = {self.select_id_slyj_tel}
                    """, (new_id_nomer_dom_tel, new_nomer_dom_tel, new_id_slyjeb_telep, new_qwer))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))


class WindowPhoness(ctk.CTkToplevel):
    def __init__(self, operation, select_row=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())

        conn = sqlite3.connect("mobilee_store_db.db")

        conn.close

        if select_row:
            self.select_id_nas_pynkta = select_row[0]
            self.select_name = select_row[1]
            self.select_id_tipa = select_row[2]
            self.select_id_ylizi = select_row[3]
            self.select_qwer = select_row[4]
            self.select_qwer1 = select_row[5]

        if operation == "add":
            self.title("Добаление")
            ctk.CTkLabel(self, text="Добаление в таблицу 'Смартфоны'").grid(row=0, column=0, pady=5, padx=5,
                                                                           columnspan=2)

            ctk.CTkLabel(self, text="id смартфона").grid(row=1, column=0, pady=5, padx=5)
            self.id_nas_pynkta = ctk.CTkEntry(self, width=300)
            self.id_nas_pynkta.grid(row=1, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Модель").grid(row=2, column=0, pady=5, padx=5)
            self.name = ctk.CTkEntry(self, width=300)
            self.name.grid(row=2, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Производитель").grid(row=3, column=0, pady=5, padx=5)
            self.id_tipa = ctk.CTkEntry(self, width=300)
            self.id_tipa.grid(row=3, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Цена").grid(row=4, column=0, pady=5, padx=5)
            self.id_ylizi = ctk.CTkEntry(self, width=300)
            self.id_ylizi.grid(row=4, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Описание").grid(row=5, column=0, pady=5, padx=5)
            self.qwer = ctk.CTkEntry(self, width=300)
            self.qwer.grid(row=5, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Гарантия").grid(row=6, column=0, pady=5, padx=5)
            self.qwer1 = ctk.CTkEntry(self, width=300)
            self.qwer1.grid(row=6, column=1, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=7, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Добавить", width=100, command=self.add).grid(row=7, column=1, pady=5, padx=5, sticky="e")

        elif operation == "delete":
            self.title("Удаление")
            ctk.CTkLabel(self, text="Вы действиельно хотите\n удалить запись из таблицы 'Смартфоны'?"
                         ).grid(row=0, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkLabel(self, text=f"{self.select_id_nas_pynkta}. {self.select_name}"
                         ).grid(row=1, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkButton(self, text="Нет", width=100, command=self.quit_win).grid(row=2, column=0, pady=5, padx=5, sticky="w")
            ctk.CTkButton(self, text="Да", width=100, command=self.delete).grid(row=2, column=1, pady=5, padx=5, sticky="e")

        elif operation == "change":
            self.title("Изменение в таблице 'Смартфоны'")
            ctk.CTkLabel(self, text="Назввание поля").grid(row=0, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text="Текущее значение").grid(row=0, column=1, pady=5, padx=5)
            ctk.CTkLabel(self, text="Новое занчение").grid(row=0, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Модель").grid(row=1, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_name).grid(row=1, column=1, pady=5, padx=5)
            self.name = ctk.CTkEntry(self, width=300)
            self.name.grid(row=1, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Производитель").grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_tipa).grid(row=2, column=1, pady=5, padx=5)
            self.id_tipa = ctk.CTkEntry(self, width=300)
            self.id_tipa.grid(row=2, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Цена").grid(row=3, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_ylizi).grid(row=3, column=1, pady=5, padx=5)
            self.id_ylizi = ctk.CTkEntry(self, width=300)
            self.id_ylizi.grid(row=3, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Описание").grid(row=4, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_qwer).grid(row=4, column=1, pady=5, padx=5)
            self.qwer = ctk.CTkEntry(self, width=300)
            self.qwer.grid(row=4, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Гарантия").grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_qwer1).grid(row=5, column=1, pady=5, padx=5)
            self.qwer1 = ctk.CTkEntry(self, width=300)
            self.qwer1.grid(row=5, column=2, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=6, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Сохранить", width=100, command=self.change).grid(row=6, column=2, pady=5, padx=5,
                                                                                       sticky="e")

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_id_adres = self.id_nas_pynkta.get()
        new_id_nomer_dom_tel = self.name.get()
        new_nomer_dom_tel = self.id_tipa.get()
        new_id_slyjeb_telep = self.id_ylizi.get()
        new_qwer = self.qwer.get()
        new_qwer1 = self.qwer1.get()


        if new_id_nomer_dom_tel != "" and new_nomer_dom_tel != "":
            try:
                conn = sqlite3.connect("mobilee_store_db.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO phones (id, model, manufacturer, price, description, warranty_period) VALUES (?, ?, ?, ?, ?, ?)",
                    (new_id_adres, new_id_nomer_dom_tel, new_nomer_dom_tel, new_id_slyjeb_telep, new_qwer, new_qwer1))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("mobilee_store_db.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM phones WHERE id = ?", (self.select_id_nas_pynkta,))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_id_nomer_dom_tel = self.name.get() or self.select_name
        new_nomer_dom_tel = self.id_tipa.get() or self.select_id_tipa
        new_id_slyjeb_telep = self.id_ylizi.get() or self.select_id_ylizi
        new_qwer = self.qwer.get() or self.select_qwer
        new_qwer1 = self.qwer1.get() or self.select_qwer1
        try:
            conn = sqlite3.connect("mobilee_store_db.db")
            cursor = conn.cursor()
            cursor.execute(f"""
                        UPDATE phones SET (model, manufacturer, price, description, warranty_period) = (?, ?, ?, ?, ?)  WHERE id = {self.select_id_nas_pynkta}
                    """, (new_id_nomer_dom_tel, new_nomer_dom_tel, new_id_slyjeb_telep, new_qwer, new_qwer1))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))


class WindowSales(ctk.CTkToplevel):
    def __init__(self, operation, select_row=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())

        conn = sqlite3.connect("mobilee_store_db.db")

        conn.close

        if select_row:
            self.select_id_adresa = select_row[0]
            self.select_id_tip_nas_pynkta = select_row[1]
            self.select_nas_pynkt = select_row[2]
            self.select_yliza = select_row[3]
            self.select_n_doma = select_row[4]

        if operation == "add":
            self.title("Добаление")
            ctk.CTkLabel(self, text="Добаление в таблицу 'Продажи смартфонов'").grid(row=0, column=0, pady=5, padx=5,
                                                                           columnspan=2)

            ctk.CTkLabel(self, text="id Проданного смартфона").grid(row=1, column=0, pady=5, padx=5)
            self.id_adres = ctk.CTkEntry(self, width=300)
            self.id_adres.grid(row=1, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Дата продажи").grid(row=2, column=0, pady=5, padx=5)
            self.adres = ctk.CTkEntry(self, width=300)
            self.adres.grid(row=2, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Артикул").grid(row=3, column=0, pady=5, padx=5)
            self.nas_punkt = ctk.CTkEntry(self, width=300)
            self.nas_punkt.grid(row=3, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Кол-во Продаж").grid(row=4, column=0, pady=5, padx=5)
            self.uliza = ctk.CTkEntry(self, width=300)
            self.uliza.grid(row=4, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Общее кол-во  продаж").grid(row=5, column=0, pady=5, padx=5)
            self.nom_dom = ctk.CTkEntry(self, width=300)
            self.nom_dom.grid(row=5, column=1, pady=5, padx=5)


            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=6, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Добавить", width=100, command=self.add).grid(row=6, column=1, pady=5, padx=5, sticky="e")

        elif operation == "delete":
            self.title("Удаление")
            ctk.CTkLabel(self, text="Вы действиельно хотите\n удалить запись из таблицы 'Продажи смартфонов'?"
                         ).grid(row=0, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkLabel(self, text=f"{self.select_id_adresa}. {self.select_id_tip_nas_pynkta}"
                         ).grid(row=1, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkButton(self, text="Нет", width=100, command=self.quit_win).grid(row=2, column=0, pady=5, padx=5, sticky="w")
            ctk.CTkButton(self, text="Да", width=100, command=self.delete).grid(row=2, column=1, pady=5, padx=5, sticky="e")

        elif operation == "change":
            self.title("Изменение в таблице 'Продажи смартфонов'")
            ctk.CTkLabel(self, text="Назввание поля").grid(row=0, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text="Текущее значение").grid(row=0, column=1, pady=5, padx=5)
            ctk.CTkLabel(self, text="Новое занчение").grid(row=0, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Дата продажи").grid(row=1, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_tip_nas_pynkta).grid(row=1, column=1, pady=5, padx=5)
            self.adres = ctk.CTkEntry(self, width=300)
            self.adres.grid(row=1, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Артикул").grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_nas_pynkt).grid(row=2, column=1, pady=5, padx=5)
            self.nas_punkt = ctk.CTkEntry(self, width=300)
            self.nas_punkt.grid(row=2, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Кол-во продаж").grid(row=3, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_yliza).grid(row=3, column=1, pady=5, padx=5)
            self.uliza = ctk.CTkEntry(self, width=300)
            self.uliza.grid(row=3, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Общее кол-во продаж").grid(row=4, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_n_doma).grid(row=4, column=1, pady=5, padx=5)
            self.nom_dom = ctk.CTkEntry(self, width=300)
            self.nom_dom.grid(row=4, column=2, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Сохранить", width=100, command=self.change).grid(row=5, column=2, pady=5, padx=5,
                                                                                       sticky="e")

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_id_adres = self.id_adres.get()
        new_id_nas_punkt = self.adres.get()
        new_nas_punkt = self.nas_punkt.get()
        new_uliza = self.uliza.get()
        new_n_doma = self.nom_dom.get()

        if new_id_nas_punkt != "" and new_nas_punkt != "":
            try:
                conn = sqlite3.connect("mobilee_store_db.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO sales (id, sale_date, product_id, quantity_sold, total_sales_amount) VALUES (?, ?, ?, ?, ?)",
                    (new_id_adres, new_id_nas_punkt, new_nas_punkt, new_uliza, new_n_doma))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("mobilee_store_db.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM sales WHERE id = ?", (self.select_id_adresa,))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_id_nas_punkt = self.adres.get() or self.select_id_tip_nas_pynkta
        new_nas_punkt = self.nas_punkt.get() or self.select_nas_pynkt
        new_uliza = self.uliza.get() or self.select_yliza
        new_n_doma = self.nom_dom.get() or self.select_n_doma
        try:
            conn = sqlite3.connect("mobilee_store_db.db")
            cursor = conn.cursor()
            cursor.execute(f"""
                        UPDATE sales SET (sale_date, product_id, quantity_sold, total_sales_amount) = (?, ?, ?, ?)  WHERE id = {self.select_id_adresa}
                    """, (new_id_nas_punkt, new_nas_punkt, new_uliza, new_n_doma))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

class WindowStocks(ctk.CTkToplevel):
    def __init__(self, operation, select_row=None):
        super().__init__()
        self.protocol('WM_DELETE_WINDOW', lambda: self.quit_win())

        conn = sqlite3.connect("mobilee_store_db.db")

        conn.close

        if select_row:
            self.select_id_nas_pynkta = select_row[0]
            self.select_name = select_row[1]
            self.select_id_tipa = select_row[2]
            self.select_id_ylizi = select_row[3]
            self.select_qwer = select_row[4]
            self.select_qwer1 = select_row[5]
            self.select_qwer2 = select_row[6]

        if operation == "add":
            self.title("Добаление")
            ctk.CTkLabel(self, text="Добаление в таблицу 'Поставки'").grid(row=0, column=0, pady=5, padx=5,
                                                                           columnspan=2)

            ctk.CTkLabel(self, text="id поставки").grid(row=1, column=0, pady=5, padx=5)
            self.id_nas_pynkta = ctk.CTkEntry(self, width=300)
            self.id_nas_pynkta.grid(row=1, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Артикул").grid(row=2, column=0, pady=5, padx=5)
            self.name = ctk.CTkEntry(self, width=300)
            self.name.grid(row=2, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Дата поступления").grid(row=3, column=0, pady=5, padx=5)
            self.id_tipa = ctk.CTkEntry(self, width=300)
            self.id_tipa.grid(row=3, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Номер документа").grid(row=4, column=0, pady=5, padx=5)
            self.id_ylizi = ctk.CTkEntry(self, width=300)
            self.id_ylizi.grid(row=4, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Поставщик").grid(row=5, column=0, pady=5, padx=5)
            self.qwer = ctk.CTkEntry(self, width=300)
            self.qwer.grid(row=5, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Кол-во").grid(row=6, column=0, pady=5, padx=5)
            self.qwer1 = ctk.CTkEntry(self, width=300)
            self.qwer1.grid(row=6, column=1, pady=5, padx=5)

            ctk.CTkLabel(self, text="Общее кол-во").grid(row=7, column=0, pady=5, padx=5)
            self.qwer2 = ctk.CTkEntry(self, width=300)
            self.qwer2.grid(row=7, column=1, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=8, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Добавить", width=100, command=self.add).grid(row=8, column=1, pady=5, padx=5, sticky="e")

        elif operation == "delete":
            self.title("Удаление")
            ctk.CTkLabel(self, text="Вы действиельно хотите\n удалить запись из таблицы 'Поставки'?"
                         ).grid(row=0, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkLabel(self, text=f"{self.select_id_nas_pynkta}. {self.select_name}"
                         ).grid(row=1, column=0, pady=5, padx=5, columnspan=2)

            ctk.CTkButton(self, text="Нет", width=100, command=self.quit_win).grid(row=2, column=0, pady=5, padx=5, sticky="w")
            ctk.CTkButton(self, text="Да", width=100, command=self.delete).grid(row=2, column=1, pady=5, padx=5, sticky="e")

        elif operation == "change":
            self.title("Изменение в таблице 'Поставки'")
            ctk.CTkLabel(self, text="Назввание поля").grid(row=0, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text="Текущее значение").grid(row=0, column=1, pady=5, padx=5)
            ctk.CTkLabel(self, text="Новое занчение").grid(row=0, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Артикул").grid(row=1, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_name).grid(row=1, column=1, pady=5, padx=5)
            self.name = ctk.CTkEntry(self, width=300)
            self.name.grid(row=1, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Дата поступления").grid(row=2, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_tipa).grid(row=2, column=1, pady=5, padx=5)
            self.id_tipa = ctk.CTkEntry(self, width=300)
            self.id_tipa.grid(row=2, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Номер документа").grid(row=3, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_id_ylizi).grid(row=3, column=1, pady=5, padx=5)
            self.id_ylizi = ctk.CTkEntry(self, width=300)
            self.id_ylizi.grid(row=3, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Поставщик").grid(row=4, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_qwer).grid(row=4, column=1, pady=5, padx=5)
            self.qwer = ctk.CTkEntry(self, width=300)
            self.qwer.grid(row=4, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Кол-во").grid(row=5, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_qwer1).grid(row=5, column=1, pady=5, padx=5)
            self.qwer1 = ctk.CTkEntry(self, width=300)
            self.qwer1.grid(row=5, column=2, pady=5, padx=5)

            ctk.CTkLabel(self, text="Общее кол-во").grid(row=6, column=0, pady=5, padx=5)
            ctk.CTkLabel(self, text=self.select_qwer2).grid(row=6, column=1, pady=5, padx=5)
            self.qwer2 = ctk.CTkEntry(self, width=300)
            self.qwer2.grid(row=6, column=2, pady=5, padx=5)

            ctk.CTkButton(self, text="Отмена", width=100, command=self.quit_win).grid(row=7, column=0, pady=5, padx=5)
            ctk.CTkButton(self, text="Сохранить", width=100, command=self.change).grid(row=7, column=2, pady=5, padx=5,
                                                                                       sticky="e")

    def quit_win(self):
        win.deiconify()
        win.update_table()
        self.destroy()

    def add(self):
        new_id_adres = self.id_nas_pynkta.get()
        new_id_nomer_dom_tel = self.name.get()
        new_nomer_dom_tel = self.id_tipa.get()
        new_id_slyjeb_telep = self.id_ylizi.get()
        new_qwer = self.qwer.get()
        new_qwer1 = self.qwer1.get()
        new_qwer2 = self.qwer2.get()


        if new_id_nomer_dom_tel != "" and new_nomer_dom_tel != "":
            try:
                conn = sqlite3.connect("mobilee_store_db.db")
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO stock (id, product_id, arrival_date, document_number, supplier, quantity, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (new_id_adres, new_id_nomer_dom_tel, new_nomer_dom_tel, new_id_slyjeb_telep, new_qwer, new_qwer1, new_qwer2))
                conn.commit()
                conn.close()
                self.quit_win()
            except sqlite3.Error as e:
                showerror(title="Ошибка", message=str(e))
        else:
            showerror(title="Ошибка", message="Заполните все поля")

    def delete(self):
        try:
            conn = sqlite3.connect("mobilee_store_db.db")
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM stock WHERE id = ?", (self.select_id_nas_pynkta,))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

    def change(self):
        new_id_nomer_dom_tel = self.name.get() or self.select_name
        new_nomer_dom_tel = self.id_tipa.get() or self.select_id_tipa
        new_id_slyjeb_telep = self.id_ylizi.get() or self.select_id_ylizi
        new_qwer = self.qwer.get() or self.select_qwer
        new_qwer1 = self.qwer1.get() or self.select_qwer1
        new_qwer2 = self.qwer2.get() or self.select_qwer2
        try:
            conn = sqlite3.connect("mobilee_store_db.db")
            cursor = conn.cursor()
            cursor.execute(f"""
                        UPDATE stock SET (product_id, arrival_date, document_number, supplier, quantity, total_amount) = (?, ?, ?, ?, ?, ?)  WHERE id = {self.select_id_nas_pynkta}
                    """, (new_id_nomer_dom_tel, new_nomer_dom_tel, new_id_slyjeb_telep, new_qwer, new_qwer1, new_qwer2))
            conn.commit()
            conn.close()
            self.quit_win()
        except sqlite3.Error as e:
            showerror(title="Ошибка", message=str(e))

if __name__ == "__main__":
    win = WindowMain()
    win.mainloop()