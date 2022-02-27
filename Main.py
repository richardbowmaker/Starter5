
import tkinter as tk
from tkinter import ttk
import StatementData as StatementData
import Logger as Logger
import sys


# -----------------------------------------------------------------------
# displayable values for the all tree
def values_all_tree(entry: StatementData.StatementEntry) -> []:
    return [entry.entry_type_str, entry.amount_str, entry.balance_str, entry.date_str,
            entry.description, entry.week_no_str, entry.included_weekly_str, entry.included_monthly_str,
            entry.seq_no_str]


# -----------------------------------------------------------------------
# displayable values for the summary entry tree parent row
def values_summary_tree(summary: StatementData.StatementSummary) -> []:
    return [summary.summary_id, summary.summary_date_str, summary.total_str, summary.transactions_str]


# -----------------------------------------------------------------------
# displayable values for the summary entry tree child row
def child_values_summary_tree(entry: StatementData.StatementEntry) -> []:
    return ['', '', '', '', entry.entry_type_str, entry.amount_str, entry.balance_str, entry.date_str,
            entry.description, entry.included_weekly_str, entry.included_monthly_str, entry.seq_no_str]


# -----------------------------------------------------------------------
# main
if __name__ == "__main__":

    # https://www.youtube.com/watch?v=-rVA37OVDs8

    window = tk.Tk()
    window.geometry("1200x600")

    # ----------------------------------------------------
    # frame1 has 3 data views in a tabbed control
    # tab1 = list of all statement entries
    # tab2 = tree view, weekly summary
    # tab3 = tree view, monthly summary

    frame1 = tk.Frame(master=window, width=600)
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
    Logger.set_logger_listbox(logger)

    Logger.log_info(f'Python version {sys.version_info[0]}.{sys.version_info[1]}')

    # --------------------------------------------------
    #
    StatementData.read_file('E:\\_Ricks\\Python\\Starter5\\statement_v130.txt')
    StatementData.generate_weekly_summaries()
    # StatementData.write_file('E:\\_Ricks\\Python\\Starter5\\statement_v130.txt')
    # --------------------------------------------------
    # all tree scroll bar
    tree_all_scroll = tk.Scrollbar(tab_all)
    tree_all_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    columns = [['type',        'Type',         175],
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
    for entry in StatementData.statement_entries:
        tree_all.insert('', tk.END, values=values_all_tree(entry), open=False)

    # --------------------------------------------------
    # weekly summary tree view
    # weekly tree scroll bar
    tree_weekly_scroll = tk.Scrollbar(tab_weekly)
    tree_weekly_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    columns = [['week_no',      'Week',          50],
               ['wdate',        'Date',          100],
               ['total',        'Total',         75],
               ['transactions', 'Transactions',  75],
               ['type',         'Type',         175],
               ['amount',       'Amount',        75],
               ['balance',      'Balance',       75],
               ['date',         'Date',         100],
               ['description',  'Description',  200],
               ['weekly',       'Weekly',        25],
               ['monthly',      'Monthly',       25],
               ['seq_no',       'Seq',           40]]

    # weekly tree view
    tree_weekly = ttk.Treeview(tab_weekly, columns=[c[0] for c in columns], show='tree headings',
                               yscrollcommand=tree_weekly_scroll.set)
    tree_weekly.pack(fill=tk.BOTH, expand=True)
    tree_weekly.column('#0', minwidth=25, width=25, stretch=False)
    for n in range(len(columns)):
        tree_weekly.column(n, minwidth=columns[n][2], width=columns[n][2], stretch=False)
        tree_weekly.heading(columns[n][0], text=columns[n][1])

    # configure scroll bar
    tree_weekly_scroll.config(command=tree_weekly.yview)

    # populate the tree
    iid = 0
    for summary in StatementData.weekly_summaries:
        tree_weekly.insert('', tk.END, iid=iid, values=values_summary_tree(summary), open=False)
        piid = iid
        iid += 1

        for entry in summary.entries:
            if entry.included_weekly:
                tags = ('weekly',)
            else:
                tags = ('',)
            tree_weekly.insert('', tk.END, iid=iid, values=child_values_summary_tree(entry), open=False)
            tree_weekly.move(iid, piid, iid - piid)
            iid += 1


    # --------------------------------------------------
    # monthly summary tree view
    # monthly tree scroll bar
    tree_monthly_scroll = tk.Scrollbar(tab_monthly)
    tree_monthly_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    columns = [['month',        'Month',         50],
               ['total',        'Total',         75],
               ['transactions', 'Transactions',  75],
               ['type',         'Type',         175],
               ['amount',       'Amount',        75],
               ['balance',      'Balance',       75],
               ['date',         'Date',          75],
               ['description',  'Description',  200],
               ['weekly',       'Weekly',        25],
               ['monthly',      'Monthly',       25],
               ['seq_no',       'Seq',           40]]

    # weekly tree view
    tree_monthly = ttk.Treeview(tab_monthly, columns=[c[0] for c in columns], show='headings',
                                yscrollcommand=tree_monthly_scroll.set)
    tree_monthly.pack(fill=tk.BOTH, expand=True)
    for n in range(len(columns)):
        tree_monthly.column(n, minwidth=columns[n][2], width=columns[n][2], stretch=False)
        tree_monthly.heading(columns[n][0], text=columns[n][1])

    # configure scroll bar
    tree_monthly_scroll.config(command=tree_monthly.yview)

    # tree_monthly.insert('', tk.END, iid=0, values=('a one', 'two', 'three'), open=False)
    # tree_monthly.insert('', tk.END, iid=1, values=('b one', 'two', 'three'), open=False)
    # tree_monthly.insert('', tk.END, iid=2, values=('c one', 'two', 'three'), open=False)
    # tree_monthly.insert('', tk.END, iid=3, values=('c one', 's-two', 's-three'), open=False)
    # tree_monthly.move(3, 1, 0)

    window.mainloop()

















