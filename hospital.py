import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import sqlite3, os, re
from PIL import Image, ImageTk
from datetime import datetime

class DoctorInformationSystem:
    def __init__(self, root):
        self.root = root
        self.root['bg']='gainsboro'
        image = Image.open("med.jpg")
        photo = ImageTk.PhotoImage(image)
        self.root.wm_iconphoto(False, photo)
        self.root.title("Прием специалистов")
        self.root.geometry('450x550')
        self.root.resizable(width=False, height=False) 
        self.get_specialties()
        self.conn = sqlite3.connect("doctors.db")
        self.c = self.conn.cursor()

        help_image = Image.open("vop.png")
        help_image = help_image.resize((30, 30), Image.LANCZOS) 
        help_photo = ImageTk.PhotoImage(help_image)
        help_button = tk.Button(self.root, image=help_photo, command=self.create_help_window, borderwidth=0)
        help_button.image = help_photo
        help_button.pack(side=tk.TOP, anchor=tk.E)
        
        self.admin_password = "admin123"
        self.flag=0

        self.main_menu = tk.Menu()

        file_menu = tk.Menu(tearoff=0)
        file_menu.add_command(label="Пользователь", command=self.switch_to_user_mode)
        file_menu.add_command(label="Администратор", command=self.switch_to_admin_mode)
        
        self.main_menu.add_cascade(label="Права доступа", menu=file_menu)

        self.root.config(menu=self.main_menu)
        
        self.search_label = tk.Label(self.root, text="Поиск по фамилии врача:", bg='gainsboro', font=('Montserrat', 11))
        self.search_label.pack()
        
        self.search_entry = tk.Entry(self.root)
        self.search_entry.pack()
        
        self.specialty_label = tk.Label(self.root, text="Выберите специальность:", bg='gainsboro', font=('Montserrat', 11))
        self.specialty_label.pack()
        
        self.specialties = self.get_specialties()
        self.specialty_combobox = ttk.Combobox(self.root, values=self.get_specialties())
        self.specialty_combobox.pack()
        
        self.search_button = tk.Button(self.root, text="Поиск", font=('Montserrat', 11), command=self.search_doctors)
        self.search_button.pack(ipadx=6, ipady=6, padx=5, pady=5)

        self.all_button = tk.Button(self.root, text="Все врачи", font=('Montserrat', 11), command=self.display_all_doctors)
        self.all_button.pack(ipadx=6, ipady=6, padx=5, pady=5)
        
        self.canvas = tk.Canvas(self.root, bg='paleturquoise')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollbar = tk.Scrollbar(self.root, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.doctors_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.doctors_frame, anchor="nw")
        
        self.display_all_doctors()

    def update_scrollregion(self):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def switch_to_user_mode(self):
        self.flag=0
        self.show_message("Режим пользователя", "Теперь вы в режиме пользователя.")
        self.main_menu.delete("Добавить")

    def switch_to_admin_mode(self):
        password = simpledialog.askstring("Пароль", "Введите пароль администратора:", show='*')
        if password == self.admin_password:
            self.flag=1
            self.show_message("Режим администратора", "Теперь вы в режиме администратора.")
            try:
                self.main_menu.index("Добавить")
            except tk.TclError:
                self.main_menu.add_cascade(label="Добавить", command=self.add_doctor)
        else:
            self.flag=0
            self.show_message("Ошибка", "Неверный пароль. Доступ запрещен.")
            self.main_menu.delete("Добавить")


    def show_message(self, title, message):
        messagebox.showinfo(title, message)

    def create_help_window(self):
        help_window = tk.Toplevel(self.root)
        help_window.title("Справочная информация")
        help_image = Image.open("vop.png")
        photo = ImageTk.PhotoImage(help_image)
        help_window.wm_iconphoto(False, photo)
        help_window.geometry('450x250')
        help_window.resizable(width=False, height=False) 
        
        tabControl = ttk.Notebook(help_window)

        tab1 = ttk.Frame(tabControl)
        tab2 = ttk.Frame(tabControl)
        tab3 = ttk.Frame(tabControl)

        tabControl.add(tab1, text='О программе')
        tabControl.add(tab2, text='Установка')
        tabControl.add(tab3, text='Пользовательский интерфейс')
        tabControl.pack(expand=1, fill="both")

        tab1_canvas = tk.Canvas(tab1)
        tab1_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tab1, orient=tk.VERTICAL, command=tab1_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tab1_canvas.configure(yscrollcommand=scrollbar.set)
        tab1_canvas.bind('<Configure>', lambda e: tab1_canvas.configure(scrollregion=tab1_canvas.bbox("all")))

        tab1_frame = ttk.Frame(tab1_canvas)
        tab1_canvas.create_window((0, 0), window=tab1_frame, anchor="nw")

        title_label = ttk.Label(tab1_frame, text="Работа выполнена студентом 21-ВТ-2 Шморгай Виолой", font=("Windspr", 10))
        title_label.pack(pady=(0, 15))

        description_label = ttk.Label(tab1_frame, text="У информационной системы поликлиники «Прием специалистов» есть следующие функции:", font=("Windspr", 9, "bold"), wraplength=400)
        description_label.pack(anchor="nw", fill="x")

        bullet = "\u2022"
        user_functions_label = ttk.Label(tab1_frame, text="Для пользователей:", font=("Windspr", 12))
        user_functions_label.pack(pady=(15, 5))
        
        user_function1_label = ttk.Label(tab1_frame, text=f"{bullet} Просмотр списка врачей: Выберите специальность из списка и/или введите ФИО в поле поиска.", wraplength=400)
        user_function1_label.pack(anchor="nw")
 
        user_function2_label = ttk.Label(tab1_frame, text=f"{bullet} Просмотр расписания врача: Нажмите на область, в которой находиться выбранный вами врач в списке.", wraplength=400)
        user_function2_label.pack(anchor="nw")

        admin_functions_label = ttk.Label(tab1_frame, text="Для администратора:", font=("Windspr", 12))
        admin_functions_label.pack(pady=(15, 5))

        admin_function1_label = ttk.Label(tab1_frame, text=f"{bullet} Добавление нового врача:")
        admin_function1_label.pack(anchor="nw")
        admin_function1_label1 = ttk.Label(tab1_frame, text="1. Выберите «Добавить врача» в меню.")
        admin_function1_label1.pack(anchor="nw", padx=50)
        admin_function1_label2 = ttk.Label(tab1_frame, text="2. Обязательно заполните поля ФИО и специализации, по необходимости заполните остальные поля.", wraplength=400)
        admin_function1_label2.pack(anchor="nw", padx=50)
        admin_function1_label3 = ttk.Label(tab1_frame, text="3. Нажмите кнопку «Сохранить».")
        admin_function1_label3.pack(anchor="nw", padx=50)

        admin_function2_label = ttk.Label(tab1_frame, text=f"{bullet} Редактирование информации о враче:")
        admin_function2_label.pack(anchor="nw")
        admin_function2_label1 = ttk.Label(tab1_frame, text="1. Найдите врача в списке и нажмите на него.")
        admin_function2_label1.pack(anchor="nw", padx=50)
        admin_function2_label2 = ttk.Label(tab1_frame, text="2. Нажмите на кнопку «Редактировать».")
        admin_function2_label2.pack(anchor="nw", padx=50)
        admin_function2_label3 = ttk.Label(tab1_frame, text="3. Измените нужные поля.")
        admin_function2_label3.pack(anchor="nw", padx=50)
        admin_function2_label4 = ttk.Label(tab1_frame, text="4. Нажмите кнопку «Сохранить».")
        admin_function2_label4.pack(anchor="nw", padx=50)

        admin_function3_label = ttk.Label(tab1_frame, text=f"{bullet} Удаление врача:")
        admin_function3_label.pack(anchor="nw")
        admin_function3_label1 = ttk.Label(tab1_frame, text="1. Найдите врача в списке и нажмите на него.", wraplength=400)
        admin_function3_label1.pack(anchor="nw", padx=50)
        admin_function3_label2 = ttk.Label(tab1_frame, text="2. Нажмите на кнопку «Удалить».")
        admin_function3_label2.pack(anchor="nw", padx=50)
        admin_function3_label3 = ttk.Label(tab1_frame, text="3. Подтвердите удаление.")
        admin_function3_label3.pack(anchor="nw", padx=50)

        tab2_frame = ttk.Frame(tab2)
        tab2_frame.pack(padx=20, pady=10) 

        treb_label = ttk.Label(tab2_frame, text=f"{bullet} Требования:")
        treb_label.pack(anchor="nw")
        treb_label1 = ttk.Label(tab2_frame, text="Операционная система: Windows, macOS, Linux.")
        treb_label1.pack(anchor="nw", padx=50)
        treb_label2 = ttk.Label(tab2_frame, text="Python 3.7 или выше.")
        treb_label2.pack(anchor="nw", padx=50)
        treb_label3 = ttk.Label(tab2_frame, text="Библиотеки: Tkinter, PIL, sqlite3.")
        treb_label3.pack(anchor="nw", padx=50)

        ust_label = ttk.Label(tab2_frame, text=f"{bullet} Запуск:")
        ust_label.pack(anchor="nw")
        ust_label1 = ttk.Label(tab2_frame, text="1. Найдите файл hospital.py.")
        ust_label1.pack(anchor="nw", padx=50)
        ust_label2 = ttk.Label(tab2_frame, text="2. Дважды щелкните по нему. ")
        ust_label2.pack(anchor="nw", padx=50)

        tab3_canvas = tk.Canvas(tab3)
        tab3_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tab3, orient=tk.VERTICAL, command=tab3_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tab3_canvas.configure(yscrollcommand=scrollbar.set)
        tab3_canvas.bind('<Configure>', lambda e: tab3_canvas.configure(scrollregion=tab3_canvas.bbox("all")))

        tab3_frame = ttk.Frame(tab3_canvas)
        tab3_canvas.create_window((0, 0), window=tab3_frame, anchor="nw")

        main_label = ttk.Label(tab3_frame, text=f"{bullet} Главное окно:")
        main_label.pack(anchor="nw")
        main_label1 = ttk.Label(tab3_frame, text="Содержит список врачей с ФИО и специальностью.")
        main_label1.pack(anchor="nw", padx=50)
        main_label2 = ttk.Label(tab3_frame, text="Позволяет фильтровать список по специальности.")
        main_label2.pack(anchor="nw", padx=50)
        main_label3 = ttk.Label(tab3_frame, text="Позволяет искать врача по ФИО.")
        main_label3.pack(anchor="nw", padx=50)

        form_see_label = ttk.Label(tab3_frame, text=f"{bullet} Форма просмотра врача:")
        form_see_label.pack(anchor="nw")
        form_see_label1 = ttk.Label(tab3_frame, text="Отображает ФИО, фото, специальность и расписание приёма врача.", wraplength=400)
        form_see_label1.pack(anchor="nw", padx=50)

        form_label = ttk.Label(tab3_frame, text=f"{bullet} Формы добавления и редактирования врача:")
        form_label.pack(anchor="nw")
        form_label1 = ttk.Label(tab3_frame, text="Позволяет вводить/изменять ФИО, выбирать фото, специальность, вводить ВУЗ, год окончания, дату приёма на работу.", wraplength=400)
        form_label1.pack(anchor="nw", padx=50)
        form_label2 = ttk.Label(tab3_frame, text="Позволяет настраивать расписание приёма по дням недели.")
        form_label2.pack(anchor="nw", padx=50)

        menu_label = ttk.Label(tab3_frame, text=f"{bullet} Меню:")
        menu_label.pack(anchor="nw")
        menu_label1 = ttk.Label(tab3_frame, text="Права доступа: Позволяет переключаться между режимом пользователя и режимом администратора (требуется пароль).", wraplength=400)
        menu_label1.pack(anchor="nw", padx=50)

    def add_doctor(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Добавить врача")
        add_window.geometry('900x300')
        add_window.resizable(width=False, height=False)
        
        name_label = tk.Label(add_window, text="ФИО:")
        name_label.grid(row=1, column=0)
        name_entry = tk.Entry(add_window)
        name_entry.grid(row=1, column=1)
        
        specialty_label = tk.Label(add_window, text="Специальность:")
        specialty_label.grid(row=2, column=0)
        specialty_entry = tk.Entry(add_window)
        specialty_entry.grid(row=2, column=1)
        
        university_label = tk.Label(add_window, text="Университет:")
        university_label.grid(row=3, column=0)
        university_entry = tk.Entry(add_window)
        university_entry.grid(row=3, column=1)
        
        graduation_year_label = tk.Label(add_window, text="Год окончания университета:")
        graduation_year_label.grid(row=4, column=0)
        graduation_year_entry = tk.Entry(add_window)
        graduation_year_entry.grid(row=4, column=1)
        
        start_date_label = tk.Label(add_window, text="Дата начала работы:")
        start_date_label.grid(row=5, column=0)
        start_date_entry = tk.Entry(add_window)
        start_date_entry.grid(row=5, column=1)

        ras_label = tk.Label(add_window, text="Расписание:")
        ras_label.grid(row=3, column=5)

        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        schedule_vars = {day: tk.StringVar(value="") for day in days}

        time_slots = [f"{hour:02d}:{minute:02d}" for hour in range(7, 21) for minute in range(0, 60, 20)]
        for i, day in enumerate(days):
            day_label = tk.Label(add_window, text=day)
            day_label.grid(row=6, column=2+i)
            
            listbox = tk.Listbox(add_window, selectmode=tk.MULTIPLE, exportselection=False, height=10) 
            listbox.config(width=10, height=5)

            for time_slot in time_slots:
                listbox.insert(tk.END, time_slot)

            listbox.grid(row=7, column=2+i, ipadx=6, ipady=6, padx=5, pady=5)
            schedule_vars[day] = listbox

        
        def select_photo():  
            photo_path = filedialog.askopenfilename(initialdir=".", title="Выбрать фото", 
                                                   filetypes=(("Image Files", "*.jpg;*.jpeg;*.png"),))
            if photo_path:
                try:
                    image = Image.open(photo_path)
                    image = image.resize((100, 100), Image.LANCZOS)
                    photo = ImageTk.PhotoImage(image)

                    if not hasattr(add_window, 'photo_label'):
                        add_window.photo_label = tk.Label(add_window, image=photo)
                        add_window.photo_label.image = photo  
                        add_window.photo_label.grid(row=7, column=1, rowspan=1)
                    else:
                        add_window.photo_label.configure(image=photo)
                        add_window.photo_label.image = photo 

                    add_window.photo_path = photo_path
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка при загрузке изображения: {e}")

        photo_button = tk.Button(add_window, text="Выбрать фото", command=select_photo)
        photo_button.grid(row=7, column=0)

        def save_doctor():
            name = name_entry.get()
            specialty = specialty_entry.get()
            university = university_entry.get()
            year_graduated = graduation_year_entry.get()
            start_date = start_date_entry.get()
            photo_path = getattr(add_window, "photo_path", "0.jpg")
            schedule_data = {}
            for day in days:
                listbox = schedule_vars[day]
                selected_indices = listbox.curselection()
                day_schedule = ", ".join(listbox.get(i) for i in selected_indices)
                schedule_data[day] = day_schedule

            if year_graduated:
                if not re.match(r"^\d{4}$", year_graduated):
                    messagebox.showerror("Ошибка", "Год окончания университета должен быть в формате 'гггг'.")
                    return
                try:
                    year_graduated_int = int(year_graduated)
                    current_year = int(datetime.now().year)
                    if not (current_year - 50 <= year_graduated_int <= current_year):
                        messagebox.showerror("Ошибка", "Год окончания университета не верно указан.")
                        return
                except ValueError:
                    messagebox.showerror("Ошибка", "Некорректный год окончания университета.")
                    return

            if start_date:
                if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", start_date):
                    messagebox.showerror("Ошибка", "Дата начала работы должна быть в формате 'дд.мм.гггг'.")
                    return
                try:
                    year = int(start_date[-4:])
                    current_year = int(datetime.now().year)
                    if not (current_year - 50 <= year <= current_year): 
                        messagebox.showerror("Ошибка", "Дата начала работы не верно указана.")
                        return
                    if year_graduated:
                        if year_graduated_int > year:
                            messagebox.showerror("Ошибка", "Год окончания университета должен быть раньше или совпадать с годом начала работы.")
                            return
                except ValueError:
                    messagebox.showerror("Ошибка", "Некорректная дата начала работы.")
                    return

            pattern = r"^[а-яА-ЯёЁ\s]+$"
            university_pattern = r"^[а-яА-ЯёЁ\.\s]+$"

            if university:
                if not re.match(university_pattern, university):
                    messagebox.showerror("Ошибка", "Неккоректный ввод университета")
            
            if len(name)==0 or len(specialty)==0:
                messagebox.showerror("Ошибка", "Поля ФИО и специальность должны быть заполнены")
            elif not re.match(pattern, name):
                messagebox.showerror("Ошибка", "Неккоректный ввод ФИО")
            elif not re.match(pattern, specialty):
                messagebox.showerror("Ошибка", "Неккоректный ввод специальности")
            else:
                messagebox.showinfo("Успех", "Информация о враче добавлена в базу данных.")
                conn = sqlite3.connect("doctors.db")
                c = conn.cursor()
                c.execute("INSERT INTO doctors (name, specialty, university, year_graduated, start_date, monday, tuesday, wednesday, thursday, friday, saturday, sunday, photo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (name, specialty, university, year_graduated, start_date,
                   schedule_data["Понедельник"], schedule_data["Вторник"], schedule_data["Среда"],schedule_data["Четверг"], schedule_data["Пятница"],
                   schedule_data["Суббота"], schedule_data["Воскресенье"], photo_path))
                conn.commit()
                self.update_specialty_combobox()
                conn.close()
                self.canvas.delete("all")
                self.display_doctors(self.c)
                self.update_scrollregion()
                add_window.destroy()

        save_button = tk.Button(add_window, text="Сохранить", command=save_doctor)
        save_button.grid(row=9, column=0)

    def get_specialties(self):
        conn = sqlite3.connect("doctors.db")
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY,
            name TEXT,
            specialty TEXT,
            university TEXT,
            year_graduated INTEGER,
            start_date TEXT,
            monday TEXT,
            tuesday TEXT,
            wednesday TEXT,
            thursday TEXT,
            friday TEXT,
            saturday TEXT,
            sunday TEXT,
            photo TEXT
        )''')

        c.execute("SELECT COUNT(*) FROM doctors ORDER BY name")
        result = c.fetchone()[0]

        if result == 0:
            doctors = [
                {
                "id": 1,
                "name": "Иванов Олег Васильевич",
                "specialty": "Терапевт",
                "university": "Сибирский государственный медицинский университет",
                "year_graduated": 2005,
                "start_date": "01.02.2006",
                "monday": ["09:00", "09:20", "09:40"],
                "tuesday": ["10:00", "10:20", "10:40"],
                "wednesday": ["09:00", "09:20", "09:40"],
                "thursday": ["10:00", "10:20", "10:40"],
                "friday": ["09:00", "09:20", "09:40"],
                "saturday": "",
                "sunday": "",
                "photo": "ivanov.jpg"
            },
            {
                "id": 2,
                "name": "Смирнова Елена Александровна",
                "specialty": "Невролог",
                "university": "Московская медицинская академия им. Сеченова",
                "year_graduated": 2007,
                "start_date": "05.06.2008",
                "monday": ["08:00", "08:20", "08:40"],
                "tuesday": ["09:00", "09:20", "09:40"],
                "wednesday": ["10:00", "10:20", "10:40"],
                "thursday": ["08:00", "08:20", "08:40"],
                "friday": ["09:00", "09:20", "09:40"],
                "saturday": "",
                "sunday": "",
                "photo": "smirnova.jpg"
            },
            {
                "id": 3,
                "name": "Козлов Артем Михайлович",
                "specialty": "Хирург",
                "university": "Санкт-Петербургская медицинская академия им. И.П. Павлова",
                "year_graduated": 2009,
                "start_date": "12.07.2010",
                "monday": ["10:00", "10:20", "10:40"],
                "tuesday": ["09:00", "09:20", "09:40"],
                "wednesday": ["11:00", "11:20", "11:40"],
                "thursday": ["10:00", "10:20", "10:40"],
                "friday": ["09:00", "09:20", "09:40"],
                "saturday": "",
                "sunday": "",
                "photo": "kozlov.jpg"
            },
            {
                "id": 4,
                "name": "Павлов Дмитрий Игоревич",
                "specialty": "Оториноларинголог",
                "university": "РНИМУ им. Н.И. Пирогова",
                "year_graduated": 2012,
                "start_date": "03.04.2013",
                "monday": ["08:00", "08:20", "08:40"],
                "tuesday": ["10:00", "10:20", "10:40"],
                "wednesday": ["08:00", "08:20", "08:40"],
                "thursday": ["09:00", "09:20", "09:40"],
                "friday": ["10:00", "10:20", "10:40"],
                "saturday": "",
                "sunday": "",
                "photo": "pavlov.jpg"
            },
            {
                "id": 5,
                "name": "Кузнецова Екатерина Петровна",
                "specialty": "Гинеколог",
                "university": "Первый МГМУ им. И.М. Сеченова",
                "year_graduated": 2006,
                "start_date": "20.08.2007",
                "monday": ["10:00", "10:20", "10:40"],
                "tuesday": ["08:00", "08:20", "08:40"],
                "wednesday": ["09:00", "09:20", "09:40"],
                "thursday": ["08:00", "08:20", "08:40"],
                "friday": ["10:00", "10:20", "10:40"],
                "saturday": "",
                "sunday": "",
                "photo": "kuznetsova.jpg"
            },
    {
    "id": 6,
    "name": "Соколова Мария Анатольевна",
    "specialty": "Педиатр",
    "university": "Башкирский государственный медицинский университет",
    "year_graduated": 2010,
    "start_date": "15.07.2011",
    "monday": ["09:00", "09:20", "09:40"],
    "tuesday": ["10:00", "10:20", "10:40"],
    "wednesday": ["09:00", "09:20", "09:40"],
    "thursday": ["08:00", "08:20", "08:40"],
    "friday": ["11:00", "11:20", "11:40"],
    "saturday": "",
    "sunday": "",
    "photo": "sokolova.jpg"
    },
    {
    "id": 7,
    "name": "Лебедев Андрей Николаевич",
    "specialty": "Офтальмолог",
    "university": "СПбГМУ им. акад. И.П. Павлова",
    "year_graduated": 2008,
    "start_date": "04.05.2009",
    "monday": ["08:00", "08:20", "08:40"],
    "tuesday": ["10:00", "10:20", "10:40"],
    "wednesday": ["08:00", "08:20", "08:40"],
    "thursday": ["09:00", "09:20", "09:40"],
    "friday": ["10:00", "10:20", "10:40"],
    "saturday": "-",
    "sunday": "-",
    "photo": "lebedev.jpg"
    },
    {
    "id": 8,
    "name": "Сидорова Ольга Сергеевна",
    "specialty": "Стоматолог",
    "university": "Медицинская академия им. П. И. Лонгина",
    "year_graduated": 2013,
    "start_date": "20.05.2014",
    "monday": ["09:00", "09:20", "09:40"],
    "tuesday": ["10:00", "10:20", "10:40"],
    "wednesday": ["09:00", "09:20", "09:40"],
    "thursday": ["08:00", "08:20", "08:40"],
    "friday": ["11:00", "11:20", "11:40"],
    "saturday": "",
    "sunday": "",
    "photo": "sidorova.jpg"
    },
    {
    "id": 9,
    "name": "Васильев Павел Игоревич",
    "specialty": "Кардиолог",
    "university": "Ростовская государственная медицинская университет",
    "year_graduated": 2011,
    "start_date": "10.08.2012",
    "monday": ["10:00", "10:20", "10:40"],
    "tuesday": ["09:00", "09:20", "09:40"],
    "wednesday": ["08:00", "08:20", "08:40"],
    "thursday": ["11:00", "11:20", "11:40"],
    "friday": ["09:00", "09:20", "09:40"],
    "saturday": "",
    "sunday": "",
    "photo": "vasiliev.jpg"
    },
    {
    "id": 10,
    "name": "Михайлов Алексей Дмитриевич",
    "specialty": "Психиатр",
    "university": "Медицинская академия им. И.И. Мечникова",
    "year_graduated": 2010,
    "start_date": "03.09.2011",
    "monday": ["08:00", "08:20", "08:40"],
    "tuesday": ["09:00", "09:20", "09:40"],
    "wednesday": ["10:00", "10:20", "10:40"],
    "thursday": ["08:00", "08:20", "08:40"],
    "friday":["09:00", "09:20", "09:40"],
    "saturday": "",
    "sunday": "",
    "photo": "mikhailov.jpg"
    },
    {
    "id": 11,
    "name": "Захарова Елизавета Алексеевна",
    "specialty": "Акушер-гинеколог",
    "university": "Первый МГМУ им. И.М. Сеченова",
    "year_graduated": 2008,
    "start_date": "15.06.2009",
    "monday": ["09:00", "09:20", "09:40"],
    "tuesday": ["10:00", "10:20", "10:40"],
    "wednesday": ["09:00", "09:20", "09:40"],
    "thursday": ["08:00", "08:20", "08:40"],
    "friday": ["11:00", "11:20", "11:40"],
    "saturday": "",
    "sunday": "",
    "photo": "zaharova.jpg"
    },
    {
    "id": 12,
    "name": "Поляков Александр Иванович",
    "specialty": "Травматолог-ортопед",
    "university": "Кубанский государственный медицинский университет",
    "year_graduated": 2013,
    "start_date": "10.07.2014",
    "monday": ["08:00", "08:20", "08:40"],
    "tuesday": ["10:00", "10:20", "10:40"],
    "wednesday": ["08:00", "08:20", "08:40"],
    "thursday": ["09:00", "09:20", "09:40"],
    "friday": ["10:00", "10:20", "10:40"],
    "saturday": "",
    "sunday": "",
    "photo": "polyakov.jpg"
    },
    {
    "id": 13,
    "name": "Антонова Ирина Петровна",
    "specialty": "Эндокринолог",
    "university": "Московский медицинский институт",
    "year_graduated": 2009,
    "start_date": "05.08.2010",
    "monday": ["09:00", "09:20", "09:40"],
    "tuesday": ["10:00", "10:20", "10:40"],
    "wednesday": ["08:00", "08:20", "08:40"],
    "thursday": ["11:00", "11:20", "11:40"],
    "friday": ["09:00", "09:20", "09:40"],
    "saturday": "",
    "sunday": "",
    "photo": "antonova.jpg"
    },
    {
    "id": 14,
    "name": "Григорьев Денис Владимирович",
    "specialty": "Уролог",
    "university": "Саратовская государственная медицинская университет",
    "year_graduated": 2012,
    "start_date": "03.05.2013",
    "monday": ["08:00", "08:20", "08:40"],
    "tuesday": ["10:00", "10:20", "10:40"],
    "wednesday": ["08:00", "08:20", "08:40"],
    "thursday": ["09:00", "09:20", "09:40"],
    "friday": ["10:00", "10:20", "10:40", "11:00"],
    "saturday": "",
    "sunday": "",
    "photo": "grigoriev.jpg"
    }
]
            for doctor in doctors:
                c.execute('''INSERT INTO doctors VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                doctor["id"],
                doctor["name"],
                doctor["specialty"],
                doctor["university"],
                doctor["year_graduated"],
                doctor["start_date"],
                ", ".join(doctor["monday"]),
                ", ".join(doctor["tuesday"]),
                ", ".join(doctor["wednesday"]),
                ", ".join(doctor["thursday"]),
                ", ".join(doctor["friday"]),
                ", ".join(doctor["saturday"]),
                ", ".join(doctor["sunday"]),
                doctor["photo"]
            ))
        c.execute("SELECT DISTINCT specialty FROM doctors ORDER BY specialty")
        specialties = [row[0] for row in c.fetchall()]
        
        conn.commit()
        conn.close()

        return specialties

    def update_specialty_combobox(self):
        self.specialties = self.get_specialties()
        self.specialty_combobox.config(values=self.specialties)
        self.specialty_combobox.update()

    def clear_canvas(self):
        for widget in self.canvas.winfo_children():
            widget.destroy()
    
    def search_doctors(self):
        search_name = self.search_entry.get()
        search_specialty = self.specialty_combobox.get()

        if not search_name and not search_specialty:
            return

        conn = sqlite3.connect("doctors.db")
        c = conn.cursor()

        if search_name and search_specialty:
            c.execute("SELECT * FROM doctors WHERE SUBSTR(name, 1, INSTR(name, ' ') - 1) LIKE ? AND specialty = ?", ('%' + search_name + '%', search_specialty))

        elif search_name:
            c.execute("SELECT * FROM doctors WHERE SUBSTR(name, 1, INSTR(name, ' ') - 1) LIKE ?", ('%' + search_name + '%',))

        elif search_specialty:
            c.execute("SELECT * FROM doctors WHERE specialty=?", (search_specialty,))

        self.clear_canvas()
        self.display_doctors(c)
        conn.close()

    def delete_doctor(self, idx, new_window):
        doctor_to_delete = self.doctors_data[idx]
        doctor_name = doctor_to_delete[1]
        confirmation = tk.messagebox.askyesno("Подтверждение удаления", f"Вы уверены, что хотите удалить информацию о враче {doctor_name}?")
        if confirmation:
            self.c.execute("DELETE FROM doctors WHERE name=?", (doctor_name,))
            self.conn.commit()
            del self.doctors_data[idx]
            new_window.destroy()
            self.canvas.delete("all")
            self.update_specialty_combobox()
            self.update_scrollregion()
            self.display_doctors(self.c) 
        
    def show_doctor_info(self, idx):
        conn = sqlite3.connect('doctors.db')
        c = conn.cursor()
        doctor = self.doctors_data[idx]
        doctor_name = doctor[1].replace("\n", " ")
        new_window = tk.Toplevel(self.root)
        new_window.title(doctor_name)

        if doctor[13] and os.path.exists(doctor[13]):
            photo_path = doctor[13]
            
        image = Image.open(photo_path)
        image = image.resize((200, 200), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        photo_label = tk.Label(new_window, image=photo)
        photo_label.image = photo
        photo_label.grid(row=0, column=0, rowspan=7)

        if self.flag==1:
            def select_photo():
                photo_path = filedialog.askopenfilename(initialdir=".", title="Выбрать фото", 
                                                   filetypes=(("Image Files", "*.jpg;*.jpeg;*.png"),))
                if not photo_path:
                    photo_path = doctor[13]
                    
                if photo_path:
                    try:
                        image = Image.open(photo_path)
                        image = image.resize((200, 200), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(image)

                        if not hasattr(new_window, 'photo_label'):
                            new_window.photo_label = tk.Label(new_window, image=photo)
                            new_window.photo_label.image = photo  
                            new_window.photo_label.grid(row=0, column=0, rowspan=7)
                        else:
                            new_window.photo_label.configure(image=photo)
                            new_window.photo_label.image = photo 

                        new_window.photo_path = photo_path
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Ошибка при загрузке изображения: {e}")

            photo_button = tk.Button(new_window, text="Выбрать фото", font=("Roboto", 10), command=select_photo)
            photo_button.grid(row=7, column=0)

            name_var = tk.StringVar(value=doctor[1])
            specialty_var = tk.StringVar(value=doctor[2])
            university_var = tk.StringVar(value=doctor[3])
            graduation_year_var = tk.StringVar(value=doctor[4])
            start_date_var = tk.StringVar(value=doctor[5])

            name_label = tk.Label(new_window, text="ФИО:")
            specialty_label = tk.Label(new_window, text="Специальность:")
            university_label = tk.Label(new_window, text="Университет:")
            graduation_year_label = tk.Label(new_window, text="Год окончания учебы:")
            start_date_label = tk.Label(new_window, text="Начало работы в поликлинике:")
            delete_button = tk.Button(new_window, text="Удалить", font=("Roboto", 10), command=lambda idx=idx: self.delete_doctor(idx, new_window))
        
            name_label.grid(row=8, column=0)
            specialty_label.grid(row=9, column=0)
            university_label.grid(row=10, column=0)
            graduation_year_label.grid(row=11, column=0)
            start_date_label.grid(row=12, column=0)
            delete_button.grid(row=13, column=1)

            name_entry = tk.Entry(new_window, width=40, textvariable=name_var)
            specialty_entry = tk.Entry(new_window, width=40, textvariable=specialty_var)
            university_entry = tk.Entry(new_window, width=40, textvariable=university_var)
            graduation_year_entry = tk.Entry(new_window, width=40, textvariable=graduation_year_var)
            start_date_entry = tk.Entry(new_window, width=40, textvariable=start_date_var)
            
            name_entry.grid(row=8, column=1)
            specialty_entry.grid(row=9, column=1)
            university_entry.grid(row=10, column=1)
            graduation_year_entry.grid(row=11, column=1)
            start_date_entry.grid(row=12, column=1)

            days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
            schedule_vars = []
            time_slots = [f"{hour:02d}:{minute:02d}" for hour in range(7, 22) for minute in range(0, 60, 20)]
            for i, day in enumerate(days):
                day_label = tk.Label(new_window, text=day.capitalize())  
                day_label.grid(row=6, column=2+i)

                listbox = tk.Listbox(new_window, selectmode=tk.MULTIPLE, exportselection=False, height=10)
                listbox.config(width=10, height=5)

                saved_times = doctor[i+6].split(", ")
                for j, time_slot in enumerate(time_slots):
                    listbox.insert(tk.END, time_slot)
                    if time_slot in saved_times:
                        listbox.selection_set(tk.END)

                listbox.grid(row=7, column=2+i, ipadx=6, ipady=6, padx=5, pady=5)
                schedule_vars.append(listbox)

            save_button = tk.Button(new_window, text="Сохранить", font=("Roboto", 10), command=lambda: save_changes(idx, schedule_vars))
            save_button.grid(row=13, column=2)

            def save_changes(idx, schedule_vars):
                new_schedule = []
                for listbox in schedule_vars:
                    selected_indices = listbox.curselection()
                    selected_times = [listbox.get(i) for i in selected_indices]
                    new_schedule.append(", ".join(selected_times)) 
                
                photo_path = getattr(new_window, "photo_path", doctor[13])
                name = name_entry.get()
                specialty = specialty_entry.get()
                university = university_entry.get()
                year_graduated = graduation_year_entry.get()
                start_date = start_date_entry.get()

                if year_graduated:
                    if not re.match(r"^\d{4}$", year_graduated):
                        messagebox.showerror("Ошибка", "Год окончания университета должен быть в формате 'гггг'.")
                        return
                    try:
                        year_graduated_int = int(year_graduated)
                        current_year = int(datetime.now().year)
                        if not (current_year - 50 <= year_graduated_int <= current_year):
                            messagebox.showerror("Ошибка", "Год окончания университета не верно указан.")
                            return
                    except ValueError:
                        messagebox.showerror("Ошибка", "Некорректный год окончания университета.")
                        return

                if start_date:
                    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", start_date):
                        messagebox.showerror("Ошибка", "Дата начала работы должна быть в формате 'дд.мм.гггг'.")
                        return
                    try:
                        year = int(start_date[-4:])
                        current_year = int(datetime.now().year)
                        if not (current_year - 50 <= year <= current_year):
                            messagebox.showerror("Ошибка", "Дата начала работы не верно указана.")
                            return
                    except ValueError:
                        messagebox.showerror("Ошибка", "Некорректная дата начала работы.")
                        return

                pattern = r"^[а-яА-ЯёЁ\s]+$"
                university_pattern = r"^[а-яА-ЯёЁ\.\s]+$"

                if university:
                    if not re.match(university_pattern, university):
                        messagebox.showerror("Ошибка", "Неккоректный ввод университета")
            
                if len(name)==0 or len(specialty)==0:
                    messagebox.showerror("Ошибка", "Поля ФИО и специальность должны быть заполнены")
                elif not re.match(pattern, name):
                    messagebox.showerror("Ошибка", "Неккоректный ввод ФИО")
                elif not re.match(pattern, specialty):
                    messagebox.showerror("Ошибка", "Неккоректный ввод специальности")
                else:
                    messagebox.showinfo("Успех", "Информация о враче добавлена в базу данных.")
                    conn = sqlite3.connect("doctors.db")
                    c = conn.cursor()
                    c.execute("""UPDATE doctors 
                         SET name=?, specialty=?, university=?, year_graduated=?, start_date=?,
                             monday=?, tuesday=?, wednesday=?, thursday=?, friday=?, saturday=?, sunday=?, photo=?
                         WHERE id=?""",
                      (name, specialty, university, year_graduated, start_date, 
                       *new_schedule,
                       photo_path, doctor[0]))
                    conn.commit()
                    self.update_specialty_combobox()
                    conn.close()
                    self.canvas.delete("all")
                    self.display_doctors(self.c)
                    self.update_scrollregion()
                    new_window.destroy()
            
        if self.flag==0:
            days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
            for i, day in enumerate(days):
                day_label = tk.Label(new_window, text=day)
                day_label.grid(row=i, column=1)

                schedule_text = doctor[6 + i]
                schedule_label = tk.Label(new_window, text=schedule_text)
                schedule_label.grid(row=i, column=2)       
            
    def display_doctors(self, c):
        self.doctors_data = c.fetchall()
        self.doctor_frames = {}
        for idx, doctor in enumerate(self.doctors_data):
            if doctor[13] and os.path.exists(doctor[13]):
                photo_path = doctor[13]
            else:
                photo_path = "0.jpg"

            image = Image.open(photo_path)
            image = image.resize((120, 120), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)

            doctor_frame = tk.Frame(self.canvas, bg="paleturquoise")
            doctor_frame.bind("<Button-1>", lambda event, idx=idx: self.show_doctor_info(idx))
            photo_label = tk.Label(doctor_frame, image=photo)
            photo_label.image = photo
            photo_label.bind("<Button-1>", lambda event, idx=idx: self.show_doctor_info(idx))
            photo_label.pack(side=tk.LEFT)

            doctor_name = doctor[1].replace("\n", " ")
            specialty = doctor[2].replace("\n", " ")
            doctor_info = tk.Label(doctor_frame, text=f"{doctor_name}\n{specialty}", font=("Roboto", 12), bg="paleturquoise")
            doctor_info.bind("<Button-1>", lambda event, idx=idx: self.show_doctor_info(idx))
            doctor_info.pack(side=tk.LEFT)
            
            self.canvas.create_window(0, idx * 120, window=doctor_frame, anchor="nw")

    def display_all_doctors(self):
        conn = sqlite3.connect('doctors.db')
        c = conn.cursor()
        c.execute('SELECT * FROM doctors ORDER BY name')
        self.clear_canvas()
        self.display_doctors(c)
        conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = DoctorInformationSystem(root)
    root.mainloop()
