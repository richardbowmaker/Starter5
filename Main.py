
import tkinter as tk
from tkinter import ttk
import StatementData as StatementData
import Logger as Logger
import sys
import Database as Database


# -----------------------------------------------------------------------
# displayable values for the all tree
def values_all_tree(entry: StatementData.StatementEntry) -> []:
    return [entry.entry_type_str, entry.amount_str, entry.balance_str, entry.date_str,
            entry.description, entry.week_no_str, entry.included_weekly_str, entry.included_monthly_str,
            entry.seq_no_str]


# -----------------------------------------------------------------------
# displayable values for the weekly summary entry tree parent row
def values_summary_weekly_tree(summary: StatementData.StatementSummary) -> []:
    return [summary.summary_id, summary.summary_date_str, summary.total_str, summary.transactions_str]


# -----------------------------------------------------------------------
# displayable values for the weekly summary entry tree child row
def child_values_summary_weekly_tree(entry: StatementData.StatementEntry) -> []:
    return ['', '', '', '', entry.entry_type_str, entry.amount_str, entry.balance_str, entry.date_str,
            entry.description, entry.included_weekly_str, entry.included_monthly_str, entry.seq_no_str]


# -----------------------------------------------------------------------
# displayable values for the monthly summary entry tree parent row
def values_summary_monthly_tree(summary: StatementData.StatementSummary) -> []:
    return [summary.summary_id, summary.total_str, summary.transactions_str]


# -----------------------------------------------------------------------
# displayable values for the monthly summary entry tree child row
def child_values_summary_monthly_tree(entry: StatementData.StatementEntry) -> []:
    return ['', '', '', entry.entry_type_str, entry.amount_str, entry.balance_str, entry.date_str,
            entry.description, entry.included_weekly_str, entry.included_monthly_str, entry.seq_no_str]


# -----------------------------------------------------------------------
# patch tree view tags;
# see https://stackoverflow.com/questions/56331001/python-tkinter-treeview-colors-are-not-updating
def fixed_map(style: ttk.Style, option):
    # Returns the style map for 'option' with any styles starting with
    # ("!disabled", "!selected", ...) filtered out

    # style.map() returns an empty list for missing options, so this should
    # be future-safe
    return [elm for elm in style.map("Treeview", query_opt=option)
            if elm[:2] != ("!disabled", "!selected")]


# -----------------------------------------------------------------------
# create the tree view
# columns is a list of tuples, ['column_name', column_width]
#
def create_tree(frame: tk.Frame, columns: list = []) -> ttk.Treeview:

    # horizontal and vertical scroll bara
    scroll_v = tk.Scrollbar(frame, orient=tk.VERTICAL)
    scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
    scroll_h = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
    scroll_h.pack(side=tk.BOTTOM, fill=tk.X)

    # weekly tree view
    tree = ttk.Treeview(frame, columns=[c[0] for c in columns], show='tree headings',
                        yscrollcommand=scroll_v.set,
                        xscrollcommand=scroll_h.set)
    tree.pack(fill=tk.BOTH, expand=True)
    tree.column('#0', minwidth=25, width=25, stretch=False)

    for n in range(len(columns)):
        tree.column(n, minwidth=columns[n][2], width=columns[n][2], stretch=False)
        tree.heading(columns[n][0], text=columns[n][1])

    # configure scroll bars
    scroll_v.config(command=tree.yview)
    scroll_h.config(command=tree.xview)

    # entries that are not part of the weekly budget are greyed out
    tree.tag_configure('excluded', foreground='grey')

    return tree


# -----------------------------------------------------------------------
# populate weekly summary tree
def populate_all_entries_tree(tree: ttk.Treeview) -> None:
    for entry in StatementData.statement_entries:
        tree.insert('', tk.END, values=values_all_tree(entry), open=False)


# -----------------------------------------------------------------------
# populate weekly summary tree
def populate_weekly_summaries_tree(tree: ttk.Treeview) -> None:

    iid = 0
    for summary in StatementData.weekly_summaries:
        tree.insert('', tk.END, iid=iid, values=values_summary_weekly_tree(summary), open=False)
        piid = iid
        iid += 1

        for entry in summary.entries:
            if entry.included_weekly:
                tags = ()
            else:
                tags = ('excluded',)

            tree.insert('', tk.END, iid=iid, values=child_values_summary_weekly_tree(entry), open=False, tags=tags)
            tree.move(iid, piid, iid - piid)
            iid += 1


# -----------------------------------------------------------------------
# populate weekly summary tree
def populate_monthly_summaries_tree(tree: ttk.Treeview) -> None:

    iid = 0
    for summary in StatementData.monthly_summaries:
        tree.insert('', tk.END, iid=iid, values=values_summary_monthly_tree(summary), open=False)
        piid = iid
        iid += 1

        for entry in summary.entries:
            if entry.included_monthly:
                tags = ()
            else:
                tags = ('excluded',)

            tree.insert('', tk.END, iid=iid, values=child_values_summary_monthly_tree(entry), open=False, tags=tags)
            tree.move(iid, piid, iid - piid)
            iid += 1


# # -----------------------------------------------------------------------
# def on_timer() -> None:
class ClipboardHandler:

    def __init__(self, window: tk.Tk):
        self._window = window
        self._window.clipboard_clear()
        self._window.clipboard_append('')
        self._window.after(1000, self.on_timer)

    def on_timer(self) -> None:
        s = self._window.clipboard_get()

        if len(s) > 0:
            Logger.log_info(f'clipboard {s}')
            self._window.clipboard_clear()
            self._window.clipboard_append('')

        self._window.after(1000, self.on_timer)


# -----------------------------------------------------------------------
# initialise GUI
def run_ui():

    window = tk.Tk()
    window.geometry("1200x600")

    style = ttk.Style()
    style.map("Treeview",
              foreground=fixed_map(style, "foreground"),
              background=fixed_map(style, "background"))

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
    # set up the logger in frame 3

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

    # read the statement entries from file
    StatementData.read_file('E:\\_Ricks\\Python\\Starter5\\statement_v130.txt')
    StatementData.generate_weekly_summaries()
    StatementData.generate_monthly_summaries()
    # StatementData.write_file('E:\\_Ricks\\Python\\Starter5\\statement_v130.txt')

    # all entries tree
    columns = [['type',        'Type',         175],
               ['amount',      'Amount',        75],
               ['balance',     'Balance',       75],
               ['date',        'Date',          75],
               ['description', 'Description',  200],
               ['week_no',     'Week',          50],
               ['weekly',      'Weekly',        25],
               ['monthly',     'Monthly',       25],
               ['seq_no',      'Seq',           40]]

    tree_all = create_tree(tab_all, columns)
    populate_all_entries_tree(tree_all)

    # weekly summary tree view
    columns = [['week_no',      'Week',          50],
               ['wdate',        'Date',         100],
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

    tree_weekly = create_tree(tab_weekly, columns)
    populate_weekly_summaries_tree(tree_weekly)

    # monthly summary tree view
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

    tree_monthly = create_tree(tab_monthly, columns)
    populate_monthly_summaries_tree(tree_monthly)

    # start the timer
    ClipboardHandler(window)

    window.mainloop()


# -----------------------------------------------------------------------
# main
if __name__ == "__main__":
    run_ui()


















