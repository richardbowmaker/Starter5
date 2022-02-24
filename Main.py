
import tkinter as tk
from tkinter import ttk
from StatementEntry import *
from Logger import *
import Data as Data

# -------------------------------------------
# logger functions

# def LogInfo(text: str) ->None:
#     logger.insert("end", text)



if __name__ == "__main__":

    # https://www.youtube.com/watch?v=-rVA37OVDs8

    window = tk.Tk()
    window.geometry("1000x600")

    # ----------------------------------------------------
    # frame1 has 3 data views in a tabbed control
    # tab1 = list of all statement entries
    # tab2 = tree view, weekly summary
    # tab3 = tree view, monthly summary

    frame1 = tk.Frame(master=window, width=300)
    frame1.pack(pady=20, fill=tk.BOTH, side=tk.LEFT, expand=True)
    frame2 = tk.Frame(master=window, width=400)
    frame2.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
    frame3 = tk.Frame(master=window, width=400, bg="blue")
    frame3.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

    # tab control
    tabs = ttk.Notebook(frame1, width=400)
    tab_all = ttk.Frame(tabs)
    tab_weekly = ttk.Frame(tabs)
    tab_monthly = ttk.Frame(tabs)
    tabs.add(tab_all, text='All')
    tabs.add(tab_weekly, text='Weekly')
    tabs.add(tab_monthly, text='Monthly')
    tabs.pack(fill=tk.BOTH, expand=True)

    # ---------------------------------------------------
    # frame3 has the logger

    # logger scroll bar
    logger_scroll = tk.Scrollbar(frame3)
    logger_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    logger = tk.Listbox(frame3, yscrollcommand=logger_scroll.set)
    logger.pack(fill=tk.BOTH, expand=True)

    # configure scroll bar
    logger_scroll.config(command=logger.yview)

    # initialise logger
    set_logger_listbox(logger)
    log_info('info')
    log_error('error')
    log_info('info')
    log_error('error')
    log_info('info')
    log_error('error')
    log_info('info')
    log_error('error')
    se = StatementEntry()
    log_info(se)

    # --------------------------------------------------
    #
    Data.read_file('E:\\_Ricks\\Python\\Starter5\\statement.txt')

    # --------------------------------------------------
    # all statement entries

    # weekly tree scroll bar
    tree_all_scroll = tk.Scrollbar(tab_weekly)
    tree_all_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    columns = [     ['type',        'Type',         175],
                    ['amount',      'Amount',        75],
                    ['balance',     'Balance',       75],
                    ['date',        'Date',          75],
                    ['description', 'Description',  200],
                    ['week_no',     'Week',          50],
                    ['weekly',      'Weekly',        25],
                    ['monthly',     'Monthly',       25],
                    ['seq_no',      'Seq',           40]]

    # weekly tree view
    tree_all = ttk.Treeview(tab_all, columns=[c[0] for c in columns], show='headings', yscrollcommand=tree_all_scroll.set)
    tree_all.pack(fill=tk.BOTH, expand=True)
    for n in range(len(columns)):
        tree_all.column(n, minwidth=columns[n][2], width=columns[n][2], stretch=False)
        tree_all.heading(columns[n][0], text=columns[n][1])

    # configure scroll bar
    tree_all_scroll.config(command=tree_all.yview)

    # add some data

    tree_all.insert('', tk.END, iid=0, values=Data.statement_entries[0].to_str_list(), open=False)

    # --------------------------------------------------
    # weekly summary tree view
    # weekly tree scroll bar
    tree_weekly_scroll = tk.Scrollbar(tab_weekly)
    tree_weekly_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # weekly tree view
    columns = ('first_name', 'last_name', 'email')
    tree_weekly = ttk.Treeview(tab_weekly, columns=columns, show='headings', yscrollcommand=tree_weekly_scroll.set)
    tree_weekly.pack(fill=tk.BOTH, expand=True)
    tree_weekly.column(0, minwidth=100, width=100, stretch=False)
    tree_weekly.column(1, minwidth=200, width=200, stretch=False)
    tree_weekly.column(2, minwidth=200, width=200, stretch=False)
    tree_weekly.heading('first_name', text='First Name')
    tree_weekly.heading('last_name', text='Last Name')
    tree_weekly.heading('email', text='Email')

    # configure scroll bar
    tree_weekly_scroll.config(command=tree_weekly.yview)

    # add some data
    contacts = []
    for n in range(1, 100):
        contacts.append((f'weekly {n}', f'last {n}', f'email{n}@example.com'))
    for contact in contacts:
        tree_weekly.insert('', tk.END, values=contact)

    # --------------------------------------------------
    # monthly summary tree view
    # monthly tree scroll bar
    tree_monthly_scroll = tk.Scrollbar(tab_monthly)
    tree_monthly_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # weekly tree view
    columns = ('first_name', 'last_name', 'email')
    tree_monthly = ttk.Treeview(tab_monthly, columns=columns, show='tree headings', yscrollcommand=tree_monthly_scroll.set)
    tree_monthly.pack(fill=tk.BOTH, expand=True)
    tree_monthly.column('#0', minwidth=25, width=25, stretch=False)
    tree_monthly.column(0, minwidth=100, width=100, stretch=False)
    tree_monthly.column(1, minwidth=200, width=200, stretch=False)
    tree_monthly.column(2, minwidth=200, width=200, stretch=False)
    tree_monthly.heading('first_name', text='First Name')
    tree_monthly.heading('last_name', text='Last Name')
    tree_monthly.heading('email', text='Email')

    # configure scroll bar
    tree_monthly_scroll.config(command=tree_monthly.yview)

    tree_monthly.insert('', tk.END, iid=0, values=('a one', 'two', 'three'), open=False)
    tree_monthly.insert('', tk.END, iid=1, values=('b one', 'two', 'three'), open=False)
    tree_monthly.insert('', tk.END, iid=2, values=('c one', 'two', 'three'), open=False)
    tree_monthly.insert('', tk.END, iid=3, values=('c one', 's-two', 's-three'), open=False)
    tree_monthly.move(3, 1, 0)

    # add some data
    # contacts = []
    # for n in range(1, 100):
    #     contacts.append((f'monthly {n}', f'last {n}', f'email{n}@example.com'))
    # for contact in contacts:
    #     tree_monthly.insert('', tk.END, values=contact)

    window.mainloop()
















