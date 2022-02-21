
# from tkinter import *
# from tkinter.ttk import *

import tkinter as tk
from tkinter import ttk
from StatementEntry import *

# class Example(Frame):
#
#     def __init__(self):
#         super().__init__()
#         self.initUI()
#
#
#     def initUI(self):
#
#         self.master.title("Review")
#         self.pack(fill=BOTH, expand=True)
#
#         frame1 = Frame(self)
#         frame1.pack(fill=X)
#
#         lbl1 = Label(frame1, text="Title", width=6)
#         lbl1.pack(side=LEFT, padx=5, pady=5)
#
#         entry1 = Entry(frame1)
#         entry1.pack(fill=X, padx=5, expand=True)
#
#         frame2 = Frame(self)
#         frame2.pack(fill=X)
#
#         lbl2 = Label(frame2, text="Author", width=6)
#         lbl2.pack(side=LEFT, padx=5, pady=5)
#
#         entry2 = Entry(frame2)
#         entry2.pack(fill=X, padx=5, expand=True)
#
#         frame3 = Frame(self)
#         frame3.pack(fill=BOTH, expand=True)
#
#         # lbl3 = Label(frame3, text="Review", width=6)
#         # lbl3.pack(side=LEFT, anchor=N, padx=5, pady=5)
#         #
#         # txt = Text(frame3)
#         # txt.pack(fill=BOTH, pady=5, padx=5, expand=True)
#
#         #----------------------------------------------
#         # treeview https://www.pythontutorial.net/tkinter/tkinter-treeview/
#
#         columns = ('first_name', 'last_name', 'email')
#         tree = Treeview(frame3, columns=columns, show='headings')
#         tree.pack(fill=BOTH, expand=True)
#
#         tree.heading('first_name', text='First Name')
#         tree.heading('last_name', text='Last Name')
#         tree.heading('email', text='Email')
#
#         # add some data
#         contacts = []
#         for n in range(1, 100):
#             contacts.append((f'first {n}', f'last {n}', f'email{n}@example.com'))
#         for contact in contacts:
#             tree.insert('', END, values=contact)
#
#         # add a scrollbar
#         scrollbar = Scrollbar(frame3, orient=VERTICAL)
#         tree.configure(yscroll=scrollbar.set)
#         scrollbar.pack(fill=BOTH, expand=True)

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

if __name__ == "__main__":

    # https://www.youtube.com/watch?v=-rVA37OVDs8

    window = tk.Tk()
    window.geometry("600x600+300+300")

    # container = tk.Frame(window, width=400, bg="green")
    # canvas = tk.Canvas(container, width=200, height=600, bg="red")
    #
    # scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    # scrollable_frame = ttk.Frame(canvas, width=200, height=600)
    #
    # scrollable_frame.bind(
    #     "<Configure>",
    #     lambda e: canvas.configure(
    #         scrollregion=canvas.bbox("all")
    #     )
    # )
    #
    # canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    # canvas.configure(yscrollcommand=scrollbar.set)
    #
    # # for i in range(50):
    # #     ttk.Label(scrollable_frame, text="Sample scrolling label", width=200).pack()
    #
    # columns = ('first_name', 'last_name', 'email')
    # tree = ttk.Treeview(scrollable_frame, columns=columns, show='headings', height=600)
    #
    # tree.heading('first_name', text='First Name')
    # tree.heading('last_name', text='Last Name')
    # tree.heading('email', text='Email')
    #
    #
    # container.pack(fill=tk.BOTH, expand=True)
    # canvas.pack(side="left", fill=tk.BOTH, expand=True)
    # scrollbar.pack(side="right", fill=tk.Y)
    # tree.pack(fill=tk.BOTH, expand=True)
    #
    # # add some data
    # contacts = []
    # for n in range(1, 100):
    #     contacts.append((f'first {n}', f'last {n}', f'email{n}@example.com'))
    # for contact in contacts:
    #     tree.insert('', tk.END, values=contact)


    # frame
    frame1 = tk.Frame(master=window)
    frame1.pack(pady=20, fill=tk.BOTH, side=tk.LEFT, expand=True)

    # scroll bar
    tree_scroll = tk.Scrollbar(frame1)
    tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    # tree view
    columns = ('first_name', 'last_name', 'email')
    tree = ttk.Treeview(frame1, columns=columns, show='headings', yscrollcommand=tree_scroll.set)
    tree.pack(fill=tk.BOTH, expand=True)

    # configure scroll bar
    tree_scroll.config(command=tree.yview)

    tree.heading('first_name', text='First Name')
    tree.heading('last_name', text='Last Name')
    tree.heading('email', text='Email')

    # add some data
    contacts = []
    for n in range(1, 100):
        contacts.append((f'first {n}', f'last {n}', f'email{n}@example.com'))
    for contact in contacts:
        tree.insert('', tk.END, values=contact)

    frame2 = tk.Frame(master=window, width=400, bg="yellow")
    frame2.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

    frame3 = tk.Frame(master=window, width=400, bg="blue")
    frame3.pack(fill=tk.BOTH, side=tk.TOP, expand=True)

    window.mainloop()














