"""
TOOLBAR - lib
@author: Mattias Måhl
@Created: 2016
"""

from tkinter import *
from collections import OrderedDict
from PIL import Image, ImageTk

class Tooltip(object):
    """
    Defines and creates tooltips connected to tkinter objects.
    """
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)
        self.tw = None

    def enter(self, event=None):
        """
        Displays the tooltip when mouse enters the widget.
        """
        x = y = 0
        z, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tw = Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify="left",
                      background='yellow', relief="solid",
                      borderwidth=1, font=("times", "8", "normal"))
        label.pack(ipadx=1)

    def close(self, event=None):
        """
        Removes the tooltip when mouse leaves the widgetarea.
        """
        if self.tw:
            self.tw.destroy()


class Toolbar(object):
    def __init__(self, parent):
        self.frame = Frame(parent, height=25, bd=1, relief=RAISED)

    def show(self):
        self.frame.pack(side=TOP, fill=X)
    
    def add(self, *, wtype=None, widget=None, gfxpath=None, tooltip=None, command=None):
        if wtype:
            if wtype=="button":
                tmpaddimg = Image.open(gfxpath)
                addimg = ImageTk.PhotoImage(tmpaddimg)
                addbutton = Button(self.frame, height=20, width=20, image=addimg, relief=FLAT)
                if command: addbutton.config(command=command)
                addbutton.image=addimg
                addbutton.pack(side=LEFT, padx=2, pady=2)
                if tooltip: addbutton_ttp = Tooltip(addbutton,tooltip)
            elif wtype=="separator":
                Label(self.frame, text="|", font=("times", "12", "normal")).pack(side=LEFT, padx=4, pady=2)
