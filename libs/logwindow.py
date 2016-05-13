"""
File: logwindow.py
Authtor: Mattias Måhl
Created 2016-05-10
Logwindow to display logginoutput in a textview.
"""

from tkinter import *


class Logwindow(object):
    height=60
    bd=1
    relief=SUNKEN
    def __init__(self, parent):
        self.text = StringVar()
        self.frame = Frame(parent,
                           height=self.height,
                           bd=self.bd,
                           relief=self.relief)
        self.scrollbar = Scrollbar(self.frame)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.label = Text(self.frame,
                          wrap=WORD,
                          bd=0,
                          yscrollcommand=self.scrollbar.set,
                          state=DISABLED)
        self.scrollbar.config(command=self.label.yview)
        self.label.pack(fill=BOTH)

    def println(self, *text, prefix=None):
        before=""
        if prefix:
            before = ":: %s :: " % prefix
        if text:
            for t in text:
                self.label.configure(state=NORMAL)
                self.label.insert(END, "%s%s\n" % (before, t))
                self.label.configure(state=DISABLED)
                self.label.see('end')

    def clear(self, *args):
        self.label.configure(state=NORMAL)
        self.label.delete(1.0, END)
        self.label.configure(state=DISABLED)

    def show(self):
        self.frame.pack(side=BOTTOM, fill=X)

    def hide(self):
        self.frame.pack_forget()
