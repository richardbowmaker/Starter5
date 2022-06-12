

import Parsers as Parsers
import StatementData as StatementData
import Logger as Logger
import Database as Database
import sys
import tkinter as tk
from tkinter import messagebox as mb
from tkinter import ttk
from tkinter import filedialog as fd
from pathlib import Path


# -----------------------------------------------------------------------
# displayable values for the all tree
def values_all_tree(entry: StatementData.StatementEntry) -> []:
    return [entry.type_str, entry.amount_str, entry.balance_str, entry.date_str,
            entry.description, entry.week_no_str, entry.included_summary, entry.seq_no_str]


# -----------------------------------------------------------------------
# displayable values for the weekly summary entry tree parent row
def values_summary_weekly_tree(summary: StatementData.StatementSummary) -> []:
    return [summary.summary_id, summary.summary_date_str, summary.total_str, summary.transactions_str]


# -----------------------------------------------------------------------
# displayable values for the weekly summary entry tree child row
def child_values_summary_weekly_tree(entry: StatementData.StatementEntry) -> []:
    return ['', '', '', '', entry.type_str, entry.amount_str, entry.balance_str, entry.date_str,
            entry.description, entry.included_summary, entry.seq_no_str]


# -----------------------------------------------------------------------
# displayable values for the monthly summary entry tree parent row
def values_summary_monthly_tree(summary: StatementData.StatementSummary) -> []:
    return [summary.summary_id, summary.total_str, summary.transactions_str]


# -----------------------------------------------------------------------
# displayable values for the monthly summary entry tree child row
def child_values_summary_monthly_tree(entry: StatementData.StatementEntry) -> []:
    return ['', '', '', entry.type_str, entry.amount_str, entry.balance_str, entry.date_str,
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
def create_tree(frame: tk.Frame, columns: list = []) -> ttk.Treeview:

    # horizontal and vertical scroll bar
    scroll_v = tk.Scrollbar(frame, orient=tk.VERTICAL)
    scroll_v.pack(side=tk.RIGHT, fill=tk.Y)
    scroll_h = tk.Scrollbar(frame, orient=tk.HORIZONTAL)
    scroll_h.pack(side=tk.BOTTOM, fill=tk.X)

    # weekly tree view
    tree = ttk.Treeview(frame, columns=[c[0] for c in columns], show='tree headings',
                        yscrollcommand=scroll_v.set,
                        xscrollcommand=scroll_h.set)
    tree.pack(fill=tk.BOTH, expand=True)
    tree.column('#0', minwidth=60, width=60, stretch=False)

    for n in range(len(columns)):
        tree.column(n, minwidth=columns[n][2], width=columns[n][2], stretch=False)
        tree.heading(columns[n][0], text=columns[n][1])

    # configure scroll bars
    scroll_v.config(command=tree.yview)
    scroll_h.config(command=tree.xview)

    # entries that are not part of the weekly budget are greyed out
    tree.tag_configure('excluded', foreground='grey')
    tree.tag_configure('new', background='light green')
    tree.tag_configure('parsed', background='light green')

    return tree


# -----------------------------------------------------------------------
# user interface main window

class Main:

    def __init__(self):
        self._window = None
        self._tree_all = None
        self._tree_weekly = None
        self._tree_monthly = None
        self._tree_parsed_text = None
        self._tabs = None
        self._clipboard = ''
        self._filename = 'E:\\_Ricks\\Python\\Starter5\\statement.txt'

    # -----------------------------------------------------------------------
    # clipboard handler
    def on_timer(self) -> None:
        try:
            cb = self._window.clipboard_get()
            if cb != self._clipboard:
                self._clipboard = cb
                if Parsers.parse_statement(cb):
                    Database.generate_weekly_summaries()
                    Database.generate_monthly_summaries()
                    self.populate_all_entries_tree()
                    self.populate_weekly_summaries_tree()
                    self.populate_monthly_summaries_tree()
                    self.populate_parsed_text_tree()
                    self.log_yearly_spend()

        except tk.TclError as ex:
            # clipboard was empty
            pass

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
    def log_yearly_spend(self) -> None:
        Logger.log_info(
            f'Spend £{Database.yearly_spend:,.2f}, Budget £{Database.yearly_budget:,.2f}')
        Logger.log_info(
            f'Underspend £{Database.yearly_budget - Database.yearly_spend:,.2f} ({Database.yearly_spend * 100 / Database.yearly_budget:.0f}%)')

    # -----------------------------------------------------------------------
    # populate weekly summary tree
    def populate_all_entries_tree(self) -> None:
        # clear tree
        self._tree_all.delete(*self._tree_all.get_children())
        # for entry in Database.statement_entries:
        for entry in Database.statement_entries:
            tags = ()
            if entry.is_new:
                tags += ('new',)

            # store index into data collection as text attribute
            self._tree_all.insert('', tk.END, values=values_all_tree(entry), open=False, tags=tags,
                                  text=f'{entry.lookup}')

    # -----------------------------------------------------------------------
    # populate weekly summary tree
    def populate_weekly_summaries_tree(self) -> None:
        self._tree_weekly.delete(*self._tree_weekly.get_children())
        iid = 0
        for summary in Database.weekly_summaries:
            self._tree_weekly.insert('', tk.END, iid=iid, values=values_summary_weekly_tree(summary),
                                     open=False, text='')
            piid = iid
            iid += 1

            # for entry in Database.summary.entries:
            for entry in summary.entries:
                tags = ()
                if not entry.included_weekly or entry.user_excluded:
                    tags += ('excluded',)
                if entry.is_new:
                    tags += ('new',)

                self._tree_weekly.insert('', tk.END, iid=iid, values=child_values_summary_weekly_tree(entry),
                                         open=False, tags=tags, text=f'{entry.lookup}')
                self._tree_weekly.move(iid, piid, iid - piid)
                iid += 1

    # -----------------------------------------------------------------------
    # populate weekly summary tree
    def populate_monthly_summaries_tree(self) -> None:
        self._tree_monthly.delete(*self._tree_monthly.get_children())
        iid = 0
        for summary in Database.monthly_summaries:
            self._tree_monthly.insert('', tk.END, iid=iid, values=values_summary_monthly_tree(summary), open=False,
                                      text='')
            piid = iid
            iid += 1

            for entry in summary.entries:
                tags = ()
                if not entry.included_monthly or entry.user_excluded:
                    tags += ('excluded',)
                if entry.is_new:
                    tags += ('new',)

                self._tree_monthly.insert('', tk.END, iid=iid, values=child_values_summary_monthly_tree(entry),
                                          open=False, tags=tags, text=f'{entry.lookup}')
                self._tree_monthly.move(iid, piid, iid - piid)
                iid += 1

    # -----------------------------------------------------------------------
    # populate weekly summary tree
    def populate_parsed_text_tree(self) -> None:
        self._tree_parsed_text.delete(*self._tree_parsed_text.get_children())
        for t in Database.parsed_text:
            tags = ()
            if t[0]:
                tags = ('parsed',)
            self._tree_parsed_text.insert('', tk.END, values=[t[1]], tags=tags)
        self._tabs.SelectedIndex = 3

    # -----------------------------------------------------------------------

    def on_exit(self):
        self._window.destroy()

    # -----------------------------------------------------------------------

    def on_save(self):

        path = Path(self._filename)
        fn = fd.asksaveasfilename(parent=self._window,
                                  title="Select file to save to",
                                  initialfile=path.name,
                                  initialdir=path.parent,
                                  filetypes=(('text files', '*.txt'), ('all files', '*.*')))

        if len(fn) > 0:
            # save file
            self._filename = fn
            Database.write_file(fn)
            Database.set_dirty(False)

    # -----------------------------------------------------------------------

    def on_open(self):

        path = Path(self._filename)
        fn = fd.askopenfilename(parent=self._window,
                                title="Select a file to load",
                                initialfile=path.name,
                                initialdir=path.parent,
                                filetypes=(('text files', '*.txt'), ('all files', '*.*')))

        if len(fn) > 0:
            # load file
            self._filename = fn
            Database.load_database(fn)
            self.populate_all_entries_tree()
            self.populate_weekly_summaries_tree()
            self.populate_monthly_summaries_tree()
            self.log_yearly_spend()

    def on_toggle_exclude_entry(self):

        try:
            # get selected tab
            st = self._tabs.tab(self._tabs.select(), "text")
            Logger.log_info(f'tab {st}')

            tree = None
            if st == 'All':
                tree = self._tree_all
            elif st == 'Weekly':
                tree = self._tree_weekly
            elif st == 'Monthly':
                tree = self._tree_monthly
            else:
                return

            # get selected item for tree
            sel_items = tree.selection()

            if len(sel_items) > 0:
                # get index to Database.statement_entries collection
                item = sel_items[0]
                # get text attribute which will be the index of the selected
                # item in Database.statement_entries
                ixs = tree.item(item, "text")
                if len(ixs) > 0:

                    # get statement entry
                    ix = int(ixs)
                    entry = Database.statement_entries[ix]

                    # update user_excluded
                    Database.update_user_excluded(entry)

                    # refresh trees
                    self.populate_all_entries_tree()
                    self.populate_weekly_summaries_tree()
                    self.populate_monthly_summaries_tree()
                    self.log_yearly_spend()

        except AttributeError:
            Logger.log_info('No tab selected')
            pass
            # template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            # message = template.format(type(ex).__name__, ex.args)

    # -----------------------------------------------------------------------
    # initialise GUI
    def run(self) -> None:

        # https://docs.python.org/3/library/tkinter.ttk.html#notebook

        self._window = tk.Tk()
        self._window.geometry("1800x1000")
        self._window.title('Spend analyser')

        self._window.clipboard_clear()

        # menus
        menu_bar = tk.Menu(self._window)
        self._window.config(menu=menu_bar)

        # file menu
        file_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label='File', menu=file_menu)

        file_menu.add_command(label='Open', command=self.on_open)
        file_menu.add_command(label='Save', command=self.on_save)
        file_menu.add_command(label='Exit', command=self.on_exit)

        # edit menu
        edit_menu = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label='Edit', menu=edit_menu)

        edit_menu.add_command(label='Toggle exclude entry', command=self.on_toggle_exclude_entry)

        # splitter
        paned_window = ttk.Panedwindow(self._window, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        # Create Frames
        frame1 = ttk.Frame(paned_window, width=300, height=600, relief=tk.SUNKEN)
        frame2 = ttk.Frame(paned_window, width=100, height=600, relief=tk.SUNKEN)
        paned_window.add(frame1, weight=3)
        paned_window.add(frame2, weight=1)
    
        style = ttk.Style()
        style.map("Treeview",
                  foreground=fixed_map(style, "foreground"),
                  background=fixed_map(style, "background"))
    
        # ----------------------------------------------------
        # frame1 has 3 data views in a tabbed control
        # tab1 = list of all statement entries
        # tab2 = tree view, weekly summary
        # tab3 = tree view, monthly summary
        # tab4 = parsed data
    
        # tab control
        self._tabs = ttk.Notebook(frame1, width=400)
        tab_all = ttk.Frame(self._tabs)
        tab_weekly = ttk.Frame(self._tabs)
        tab_monthly = ttk.Frame(self._tabs)
        tab_parsed_text = ttk.Frame(self._tabs)
        self._tabs.add(tab_all, text='All')
        self._tabs.add(tab_weekly, text='Weekly')
        self._tabs.add(tab_monthly, text='Monthly')
        self._tabs.add(tab_parsed_text, text='Parsed data')
        self._tabs.pack(fill=tk.BOTH, expand=True)
    
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

        # workout current directory
        Logger.log_info(f'sys.path {sys.path}')
        Logger.log_info(f'sys.executable {sys.executable}')

        # read the statement entries from file
        Database.load_database(self._filename)

        # all entries tree
        columns = [['type',        'Type',         160],
                   ['amount',      'Amount',        75],
                   ['balance',     'Balance',       75],
                   ['date',        'Date',         100],
                   ['description', 'Description',  650],
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
                   ['type',         'Type',         160],
                   ['amount',       'Amount',        75],
                   ['balance',      'Balance',       75],
                   ['date',         'Date',         100],
                   ['description',  'Description',  650],
                   ['included',    'Included',       40],
                   ['seq_no',       'Seq',           40]]
    
        self._tree_weekly = create_tree(tab_weekly, columns)
        self.populate_weekly_summaries_tree()
    
        # monthly summary tree view
        columns = [['month',        'Month',         50],
                   ['total',        'Total',         75],
                   ['transactions', 'Transactions',  75],
                   ['type',         'Type',         160],
                   ['amount',       'Amount',        75],
                   ['balance',      'Balance',       75],
                   ['date',         'Date',         100],
                   ['description',  'Description',  650],
                   ['included',     'Included',      40],
                   ['seq_no',       'Seq',           40]]
    
        self._tree_monthly = create_tree(tab_monthly, columns)
        self.populate_monthly_summaries_tree()
        self.log_yearly_spend()

        # parsed data tree view
        columns = [['statement', 'Statement', 900]]

        self._tree_parsed_text = create_tree(tab_parsed_text, columns)

        # start the timer
        self._window.after(1000, self.on_timer)

        self._window.protocol("WM_DELETE_WINDOW", self.on_close)
        self._window.mainloop()
    

# -----------------------------------------------------------------------
# main
if __name__ == "__main__":

    ui = Main()
    ui.run()


















