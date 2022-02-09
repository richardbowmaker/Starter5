
from tkinter import *
from StatementEntry import *
import csv

def add(x, y):
    return x + y


if __name__ == "__main__":

    try:

        with open("E:/_Ricks/Python/Starter5/statement.txt") as f:
            contents = f.readlines()
            print(contents)

    except:

        print("No such file")

    gui = Tk()
    gui.configure(background="white")
    gui.geometry("400x400")
    gui.title("Spend reckoner")
    mylist = Listbox(gui, height=20, width=120, selectmode=SINGLE)

    # for l in contents:
    #    mylist.insert(END, l)

    s = contents[1]

    # tokenise string
    ss = s.split(',', 7)
    for t in ss:
        mylist.insert(END, t)

    # mylist.insert(0, add(1, 2))

    # string to int

    mylist.pack()
    # gui.mainloop()

    a_string = "12"

    try:
        an_integer = int(a_string)
        print(an_integer)
    except ValueError:
        print("Catch Error")

    x = add(1, 2)
    print(x)

    a = 12.34
    ass = '{:.2f}'.format(a)
    print(ass)

    se1_1 = StatementEntry()
    csvstr = "Santander Current Account, -100.00, 13475.17, Mon 13/12/2021, 362, 142, BILL PAYMENT VIA FASTER PAYMENT TO R J BOWMAKER, REFERENCE, CASHPLUS"
    se1_1.from_csv(csvstr, 1.1)
    print("v1.10: ", csvstr)
    print("parsed: ", se1_1.to_csv())

    se1_2 = StatementEntry()
    csvstr = "\"Cashplus\",\" -£1.10\",\" £48481.19\",\" 10/8/2021 Tue\",\" 344\",\" 240\",\" *\",\"\",\" CARD PAYMENT, , TO MIPERMIT\""
    se1_2.from_csv(csvstr, 1.2)
    print("v1.20: ", csvstr)
    print("parsed: ", se1_2.to_csv())













