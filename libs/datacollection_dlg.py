"""
file datacollection_dlg.py
Author Mattias Måhl
Created 2016-05-11
"""

print("datacollection: ", __name__)

from tkinter import *
from PIL import Image, ImageTk

if __name__ == "libs.datacollection_dlg":
    from libs.toolbar import Tooltip
else:
    from toolbar import Tooltip



class regexp_strings(object):
    ipv4 = "^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    short_mask = "^(?:(3[0-2]|[01]?[0-2][0-9]?|[1]?[0-9]?))$"

class Collectdata(object):
    Cancel=False
    def __init__(self, parent=None, title="Add target", edit=None, gfxpath="gfx/"):
        self.gfxpath=gfxpath
        if parent:
            self.rootdlg = Toplevel(parent)
        else:
            self.rootdlg = Tk()

        self.rootdlg.wm_title(title)
        self.rootdlg.columnconfigure(0, weight=1)
        self.rootdlg.rowconfigure(0, weight=1)
        self.frame = Frame(self.rootdlg, height=60, width=120)
        pad=5
        self.frame.grid(row=0, column=0, sticky=(N, E, W, S), padx=pad, pady=pad, ipadx=pad, ipady=pad)
        Label(self.frame, text="Enter your target host(s) or network:").grid(row=0, column=0, columnspan=2, sticky=W)
        self.data = StringVar()
        if edit: self.data.set(str(edit))
        tmpinfo = Image.open(self.gfxpath + "info.png")
        infoimg = ImageTk.PhotoImage(tmpinfo)
        lblimg = Label(self.frame, image=infoimg)
        lblimg.photo = infoimg
        lblimg.grid(row=0, column=2, sticky=E)
        infotb = Tooltip(lblimg, "Input takes a single IP, e.g. 127.0.0.1\nYou can also enter a network or a range\ne.g. 10.2.2.0/24 or 10.20.20.20-10.20.20.30")
        valhook = (self.rootdlg.register(self.onvalidate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.entry = Entry(self.frame,
                           textvariable=self.data,
                           validate='all',
                           validatecommand=valhook)
        self.entry.grid(row=1,
                        columnspan=3,
                        column=0,
                        sticky=(W, E))
        self.default_color = self.entry.cget('background')
        self.entry.focus()
        self.rootdlg.bind("<Return>", self.Collectiondata_OK)
        self.rootdlg.bind("<Escape>", self.Collectiondata_Cancel)
        btn1=Button(self.frame, text="Cancel", height=1, width=7, command=self.Collectiondata_Cancel)
        btn2=Button(self.frame, text="OK", height=1, width=7, command=self.Collectiondata_OK)
        btn1.grid(row=2, column=2, sticky=E)
        btn2.grid(row=2, column=0, sticky=W)
        self.rootdlg.update()
        self.rootdlg.minsize(self.rootdlg.winfo_width(), self.rootdlg.winfo_height())
        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(1, weight=1)
        
    def show(self):
        self.rootdlg.wait_window()
        if self.Cancel:
            return None, None, None, None
        else:
            return self.returnvalues

    def Collectiondata_OK(self, *event):
        
        data = self.validate(self.data.get(), returnvalues=True)
        if not data[0]:
            messagebox.showerror("Input error!", "Your information is not a valid input.\nPlease check your input.", parent=self.rootdlg)
        else:
            self.returnvalues = data
            self.rootdlg.destroy()

    def Collectiondata_Cancel(self, *event):
        self.Cancel=True
        self.rootdlg.destroy()

    def onvalidate(self, d,i,P,s,S,v,V,W):
        newcolor = 'IndianRed1' if not self.validate(P) else self.default_color
        self.rootdlg.nametowidget(W).configure(background=newcolor)
        return True

    @staticmethod
    def isIP(ip):
        if re.search(regexp_strings.ipv4, ip):
            return True
        else:
            return False
    @staticmethod
    def isMASK(mask):
        if re.search(regexp_strings.ipv4, mask) or (len(mask) < 3 and re.search(regexp_strings.short_mask, mask)):
            return True
        else:
            return False

    @staticmethod
    def validate(ip, returnvalues=False):
        #:TODO: check the mask if there is one, and add support for ranged input. e.g. 10.10.10.10-10.10.10.30
        valid=True
        sep = "/"
        net = net2 = mask = None
        
        if "-" in ip: sep = "-"
        if ("-" in ip) and ("/" in ip):
            if returnvalues:
                return False, None, None, None
            else:
                return False

        if sep == "/":
            try:
                net, mask = re.split(sep, ip)
            except:
                net = ip
        else:
            try:
                net, net2 = re.split(sep, ip)
            except:
                net = ip
        valid=Collectdata.isIP(net)
        if not valid:
            if returnvalues:
                return False, None, None, None
            else:
                return False
        
        try:
            valid = Collectdata.isIP(net2)
        except:
            pass
        try:
            valid = Collectdata.isMASK(mask)
        except:
            pass
        if returnvalues:
            return valid, net, net2, mask
        else:
            return valid

if __name__ == "__main__":
    f=Collectdata()
