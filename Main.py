

import Parsers as Parsers
import StatementData as StatementData
import Logger as Logger
import Database as Database

import datetime as datetime
import sys
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk


# -----------------------------------------------------------------------
# displayable values for the all tree
def values_all_tree(entry: StatementData.StatementEntry) -> []:
    return [entry.entry_type_str, entry.amount_str, entry.balance_str, entry.date_str,
            entry.description, entry.week_no_str, entry.included_summary, entry.seq_no_str]


# -----------------------------------------------------------------------
# displayable values for the weekly summary entry tree parent row
def values_summary_weekly_tree(summary: StatementData.StatementSummary) -> []:
    return [summary.summary_id, summary.summary_date_str, summary.total_str, summary.transactions_str]


# -----------------------------------------------------------------------
# displayable values for the weekly summary entry tree child row
def child_values_summary_weekly_tree(entry: StatementData.StatementEntry) -> []:
    return ['', '', '', '', entry.entry_type_str, entry.amount_str, entry.balance_str, entry.date_str,
            entry.description, entry.included_summary, entry.seq_no_str]


# -----------------------------------------------------------------------
# displayable values for the monthly summary entry tree parent row
def values_summary_monthly_tree(summary: StatementData.StatementSummary) -> []:
    return [summary.summary_id, summary.total_str, summary.transactions_str]


# -----------------------------------------------------------------------
# displayable values for the monthly summary entry tree child row
def child_values_summary_monthly_tree(entry: StatementData.StatementEntry) -> []:
    return ['', '', '', entry.entry_type_str, entry.amount_str, entry.balance_str, entry.date_str,
            entry.description, entry.included_summary, entry.seq_no_str]


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
    tree.tag_configure('new', background='light green')

    return tree


# -----------------------------------------------------------------------
# user interface main window

class Main:

    def __init__(self):
        self._window = None
        self._tree_all = None
        self._tree_weekly = None
        self._tree_monthly = None
        self._clipboard = ''
        self._filename = 'E:\\_Ricks\\Python\\Starter5\\statement_v130.txt'

    # -----------------------------------------------------------------------
    # clipboard handler
    def on_timer(self) -> None:
        cb = self._window.clipboard_get()
        if cb != self._clipboard:
            self._clipboard = cb
            if Parsers.parse_statement(cb):
                Database.generate_weekly_summaries()
                Database.generate_monthly_summaries()
                self.populate_all_entries_tree()
                self.populate_weekly_summaries_tree()
                self.populate_monthly_summaries_tree()

        self._window.after(1000, self.on_timer)

    # -----------------------------------------------------------------------
    # window closing
    def on_close(self):
        if Database.get_is_dirty():
            res = mb.askyesno('Exit', f'Do you want to save to \'{self._filename}\'')
            if res:
                Database.write_file(self._filename)
        self._window.destroy()

    # -----------------------------------------------------------------------
    # populate weekly summary tree
    def populate_all_entries_tree(self) -> None:
        # clear tree
        self._tree_all.delete(*self._tree_all.get_children())
        for entry in Database.statement_entries:
            tags = ()
            if entry.is_new:
                tags = ('new',)

            self._tree_all.insert('', tk.END, values=values_all_tree(entry), open=False, tags=tags)

    # -----------------------------------------------------------------------
    # populate weekly summary tree
    def populate_weekly_summaries_tree(self) -> None:
        self._tree_weekly.delete(*self._tree_weekly.get_children())
        iid = 0
        for summary in Database.weekly_summaries:
            self._tree_weekly.insert('', tk.END, iid=iid, values=values_summary_weekly_tree(summary), open=False)
            piid = iid
            iid += 1

            for entry in summary.entries:
                tags = ()
                if not entry.included_weekly:
                    tags = ('excluded',)
                if entry.is_new:
                    tags += ('new',)

                self._tree_weekly.insert('', tk.END, iid=iid, values=child_values_summary_weekly_tree(entry),
                                         open=False, tags=tags)
                self._tree_weekly.move(iid, piid, iid - piid)
                iid += 1

    # -----------------------------------------------------------------------
    # populate weekly summary tree
    def populate_monthly_summaries_tree(self) -> None:
        self._tree_monthly.delete(*self._tree_monthly.get_children())
        iid = 0
        for summary in Database.monthly_summaries:
            self._tree_monthly.insert('', tk.END, iid=iid, values=values_summary_monthly_tree(summary), open=False)
            piid = iid
            iid += 1

            for entry in summary.entries:
                tags = ()
                if not entry.included_monthly:
                    tags = ('excluded',)
                if entry.is_new:
                    tags += ('new',)

                self._tree_monthly.insert('', tk.END, iid=iid, values=child_values_summary_monthly_tree(entry),
                                          open=False, tags=tags)
                self._tree_monthly.move(iid, piid, iid - piid)
                iid += 1

    # -----------------------------------------------------------------------
    # initialise GUI
    def run(self) -> None:

        self._window = tk.Tk()
        self._window.geometry("1200x600")

        panedwindow = ttk.Panedwindow(self._window, orient=tk.HORIZONTAL)
        panedwindow.pack(fill=tk.BOTH, expand=True)
        # Create Frams
        frame1 = ttk.Frame(panedwindow, width=400, height=300, relief=tk.SUNKEN)
        frame2 = ttk.Frame(panedwindow, width=100, height=400, relief=tk.SUNKEN)
        panedwindow.add(frame1, weight=4)
        panedwindow.add(frame2, weight=1)
    
        style = ttk.Style()
        style.map("Treeview",
                  foreground=fixed_map(style, "foreground"),
                  background=fixed_map(style, "background"))
    
        # ----------------------------------------------------
        # frame1 has 3 data views in a tabbed control
        # tab1 = list of all statement entries
        # tab2 = tree view, weekly summary
        # tab3 = tree view, monthly summary
    
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
        # set up the logger in frame 2
    
        # logger scroll bar
        logger_scroll = tk.Scrollbar(frame2)
        logger_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
        logger = tk.Listbox(frame2, yscrollcommand=logger_scroll.set)
        logger.pack(fill=tk.BOTH, expand=True)
    
        # configure scroll bar
        logger_scroll.config(command=logger.yview)
    
        # initialise logger
        Logger.set_logger_listbox(logger)
    
        Logger.log_info(f'Python version {sys.version_info[0]}.{sys.version_info[1]}')
    
        # read the statement entries from file
        Database.read_file(self._filename)
        Database.generate_weekly_summaries()
        Database.generate_monthly_summaries()

        # all entries tree
        columns = [['type',        'Type',         175],
                   ['amount',      'Amount',        75],
                   ['balance',     'Balance',       75],
                   ['date',        'Date',          75],
                   ['description', 'Description',  200],
                   ['week_no',     'Week',          50],
                   ['included',    'Included',      40],
                   ['seq_no',      'Seq',           40]]
    
        self._tree_all = create_tree(tab_all, columns)
        self.populate_all_entries_tree()
    
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
                   ['included',    'Included',       40],
                   ['seq_no',       'Seq',           40]]
    
        self._tree_weekly = create_tree(tab_weekly, columns)
        self.populate_weekly_summaries_tree()
    
        # monthly summary tree view
        columns = [['month',        'Month',         50],
                   ['total',        'Total',         75],
                   ['transactions', 'Transactions',  75],
                   ['type',         'Type',         175],
                   ['amount',       'Amount',        75],
                   ['balance',      'Balance',       75],
                   ['date',         'Date',          75],
                   ['description',  'Description',  200],
                   ['included',    'Included',       40],
                   ['seq_no',       'Seq',           40]]
    
        self._tree_monthly = create_tree(tab_monthly, columns)
        self.populate_monthly_summaries_tree()
    
        # start the timer
        self._window.after(1000, self.on_timer)

        self._window.protocol("WM_DELETE_WINDOW", self.on_close)
        self._window.mainloop()
    

# -----------------------------------------------------------------------
# main
if __name__ == "__main__":

    # root = tk.Tk()
    # root.geometry("1200x600")
    # # App Title
    # root.title("Python GUI Application ")
    # # ttk.Label(root, text="Separating widget").pack()
    # # Create Panedwindow
    # panedwindow = ttk.Panedwindow(root, orient=tk.HORIZONTAL)
    # panedwindow.pack(fill=tk.BOTH, expand=True)
    # # Create Frams
    # fram1 = ttk.Frame(panedwindow, width=400, height=300, relief=tk.SUNKEN)
    # fram2 = ttk.Frame(panedwindow, width=100, height=400, relief=tk.SUNKEN)
    # panedwindow.add(fram1, weight=4)
    # panedwindow.add(fram2, weight=1)
    # # Calling Main()
    # root.mainloop()

    ui = Main()
    ui.run()


















