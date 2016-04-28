import tkinter as tk
from tkinter import *

class Settings_dialog(object):
    settings        = None
    settings_backup = None
    frame           = None
    dialog          = None
    entry           = {}
    changed         = False
    
    def __init__(self, parent, settings):
        self.dialog = tk.Toplevel(parent)
        self.dialog.wm_title("Settings")
        self.frame = tk.Frame(self.dialog)
        self.frame.grid(sticky=(N, S, E, W), padx=(3, 12), pady=(3, 12))
        tk.Label(self.frame, text="Settings:", font="Helvetica 20 underline bold").grid(columnspan=3, row=0, sticky=(E, W))
        tk.Label(self.frame, text="Defaults", font="Helvetica 8 italic underline").grid(row=1, column=2, sticky=W)
        row=1
        self.settings = settings
        for section in self.settings.sections():
            txt = "Section: " + section
            tk.Label(self.frame, text=txt, font="Helvetica 11 bold underline").grid(column=0, row = row, sticky=(N,W), columnspan=2)
            row += 1
            self.entry[section] = {}
            for key in self.settings[section]:
                tk.Label(self.frame, text=key).grid(row=row, column=0, sticky=W)
                en = tk.Entry(self.frame)
                en.insert(0, self.settings[section][key])
                en.grid(row=row, column=1, sticky=(E,W))
                self.entry[section][key] = en
                tk.Label(self.frame, text=self.settings['DEFAULT'][key], font="Helvetica 8 italic").grid(row=row, column=2, sticky="W")
                row += 1
                                
        btn_Ok = tk.Button(self.frame,
                           text="OK",
                           command=self.on_click_ok,
                           width=10)
        btn_Ok.grid(column=1, row=(row+1), sticky=E)
        btn_Cancel = tk.Button(self.frame,
                               text="Cancel",
                               command=self.on_click_cancel,
                               width=10)
        btn_Cancel.grid(column=2, row=(row+1), sticky=E)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        self.dialog.update()
        self.dialog.minsize(self.dialog.winfo_width(), self.dialog.winfo_height())

    def on_click_cancel(self):
        self.dialog.destroy()

    def on_click_ok(self):
        for sections in self.entry:
            for keys in self.entry[sections]:
                entry = self.entry[sections][keys].get()
                self.settings[sections][keys] = entry
        self.changed = True
        self.dialog.destroy()
    
    def show(self):
        self.dialog.wait_window()
        return self.settings, self.changed
