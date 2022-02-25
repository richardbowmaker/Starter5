
import tkinter as tk
from tkinter import ttk


def set_logger_listbox(lb: tk.Listbox) -> None:
    global list_box
    list_box = lb


def log_info(text: str) ->None:
    list_box.insert(tk.END, text)


def log_error(text: str) -> None:
    list_box.insert(tk.END, text)
    n = list_box.size()
    list_box.itemconfig(n - 1, {'fg': 'red'})