from tkinter import *
from tkinter import ttk
import backend as back
from sqlite3 import *
import pandas as pd
import openpyxl
from docx import Document
from docx.shared import Inches




#  Главное окно
window = Tk()
window.title('subd')
window.minsize(700, 450)


frame_change = Frame(window, width=150, height=150, bg='white')  # блок для функционала субд
frame_view = Frame(window, width=150, height=150, bg='white')  # блок для просмотра базы данных
frame_change.place(relx=0, rely=0, relwidth=1, relheight=1)
frame_view.place(relx=0, rely=0.5, relwidth=1, relheight=0.5)


# порядок элементов
heads = ['id', 'name', 'expenses']
table = ttk.Treeview(frame_view, show='headings')  # дерево выполняющее свойство таблицы
table['columns'] = heads  # длина таблицы


# заголовки столбцов и их расположение
for header in heads:
    table.heading(header, text=header, anchor='center')
    table.column(header, anchor='center')


# добавление из бд в таблицу приложения
for row in back.information():
    table.insert('', END, values=row)
table.pack(expand=YES, fill=BOTH, side=LEFT)


# функция обновления таблицы
def refresh():
    with connect('database.db') as db:
        cursor = db.cursor()
        cursor.execute(''' SELECT * FROM table1 ''')
        [table.delete(i) for i in
        table.get_children()]
        [table.insert('', 'end', values=row) for row in cursor.fetchall()]


# функция обработчика событий по нажатию лкм
def on_select(event):
    global id_sel
    global set_col
    id_sel = table.item(table.focus())
    id_sel = id_sel.get('values')[0]
    col = table.identify_column(event.x)
    set_col = table.column(col)
    set_col = set_col.get('id')
table.bind('<ButtonRelease-1>', on_select)


# функция добавления новых записей
def form_submit():
    name = f_name.get()
    expenses = f_expenses.get()
    insert_inf = (name, expenses)
    with connect('database.db') as db:
        cursor = db.cursor()
        query = """ INSERT INTO table1(name, expenses) VALUES (?, ?)"""
        cursor.execute(query, insert_inf)
        db.commit()
        refresh()


# функция удалить
def delete():
    with connect('database.db') as db:
        cursor = db.cursor()
        id = id_sel
        cursor.execute('''DELETE FROM table1 WHERE id = ?''', (id,))
        db.commit()
        refresh()


# функция изменения дб
def changeDB():
    with connect('database.db') as db:
        cursor = db.cursor()
        id = id_sel
        whatchange = f_change.get()
        if set_col != 'id':
            cursor.execute("""Update table1 set""" + ' ' + set_col + """ = ? where id = ? """, (whatchange, id))
            db.commit()
            refresh()

# функция вывода данных в таблицу excel
def creatXlsx():
    with connect('database.db') as db:
        df = pd.read_sql('select * from table1', db)
        df.to_excel('out.xlsx', index=False)

# функция вывода данных в файл word
def creatDocs():
    with connect('database.db') as db:
        document = Document()
        df = pd.read_sql_query("SELECT * from table1", db)
        table = document.add_table(rows=len(df) + 1, cols=len(df.columns))
        for j, col in enumerate(df.columns):
            table.cell(0, j).text = col
        for i, row in df.iterrows():
            for j, value in enumerate(row):
                table.cell(i + 1, j).text = str(value)
        document.save('база_данных.docx')

# добавления новых имен в бд
l_name = ttk.Label(frame_change, text="Имя")
f_name = ttk.Entry(frame_change)
l_name.grid(row=0, column=0, sticky='w', padx=10, pady=10)
f_name.grid(row=0, column=1, sticky='w', padx=10, pady=10)


# добавления новых платежей в бд
l_expenses = ttk.Label(frame_change, text="Платеж")
f_expenses = ttk.Entry(frame_change)
l_expenses.grid(row=1, column=0, sticky='w', padx=10, pady=10)
f_expenses.grid(row=1, column=1, sticky='w', padx=10, pady=10)


#  изменения бд
l_change = ttk.Label(frame_change, text="Заменить на:")
f_change = ttk.Entry(frame_change)  # entry на что меняем прошлое имя в бд
l_change.grid(row=3, column=0, sticky='w', padx=10, pady=10)
f_change.grid(row=3, column=1, sticky='w', padx=10, pady=10)


#  кнопка добавить
btn_submit = ttk.Button(frame_change, text="Добавить", command=form_submit)
btn_submit.grid(row=0, column=3, columnspan=2, sticky='w', padx=10, pady=10)

#  кнопка удалить
btn_delete = ttk.Button(frame_change, text="Удалить", command=delete)
btn_delete.grid(row=1, column=3, columnspan=2, sticky='w', padx=10, pady=10)

#  кнопка изменить
but_change = ttk.Button(frame_change, text='Изменить', command=changeDB)
but_change.grid(row=3, column=3, columnspan=2, sticky='w', padx=10, pady=10)

#  кнопка вызывающая справку
btn_reference = ttk.Button(frame_change, text="Справка", command=back.show_info)
btn_reference.grid(row=4, column=0, sticky='w', padx=10, pady=10)


#  скроллбар
scrollpanel = ttk.Scrollbar(frame_view, command=table.yview)
table.configure(yscrollcommand=scrollpanel.set)
scrollpanel.pack(side=RIGHT, fill=Y)
table.pack(expand=YES, fill=BOTH)

#  кнопка выгрузки бд в excel
but_upload = ttk.Button(frame_change, text="Выгрузить в Excel", command=creatXlsx)
but_upload.grid(row=5, column=0, sticky='w', padx=10, pady=10)

#  кнопка выгрузки бл в word
but_upload = ttk.Button(frame_change, text="Выгрузить в Word", command=creatDocs)
but_upload.grid(row=5, column=2, sticky='w', padx=10, pady=10)


window.mainloop()
