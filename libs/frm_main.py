"""
File frm_amin.py
Created 2016-04-12
@author: Mattias Måhl
"""

from tkinter import *
import tkinter as tk
import codecs
import configparser
import os.path, os
from PIL import Image, ImageTk
from collections import OrderedDict as OD

if __name__ == "__main__":
    from toolbar import Tooltip, Toolbar
    from logwindow import Logwindow
    from datacollection_dlg import Collectdata
    from settingsdialog import Settings_dialog
else:
    from libs.toolbar import Tooltip, Toolbar
    from libs.logwindow import Logwindow
    from libs.datacollection_dlg import Collectdata
    from libs.settingsdialog import Settings_dialog

class frm_main(tk.Tk):
    """Start object to render the application window.\n
    use:\n
    import libs.frm_main as mainwindow\n
    if __name__ == "__main__":\n
         app = mainwindow()\n
         app.mainloop()\n\n
    """
    settings = configparser.ConfigParser()
    settings_file = "settings.ini"
    viewlogg = False
    gfxpath = "gfx/"
    
    def __init__(self, settingspath="conf/", gfxpath="gfx/"):
        tk.Tk.__init__(self)
        self.settings_file = os.path.join(settingspath, self.settings_file)
        self.gfxpath = gfxpath
		##        self.wm_state()
        self.wm_title("Tracemac 2.0")
        self.mainframe = tk.Frame(master=self, bg="white")
        self.minsize(width=800, height=640)
        self.mainframe.pack(expand=True, fill=BOTH)
        self.logg = Logwindow(self.mainframe)
        self.createWidgets()
        self.bind_all("<Control-x>", self.quit)
        self.bind_all("<Control-t>", self.list_add(widget=self.list_targets))
        self.bind_all("<Control-h>", self.list_add(widget=self.list_hosts))
        self.list_targets.insert(END, "1.1.1.1")
        
        
        #checks if the settings_file exists, if not it creates it with defaults.
        if os.path.isfile(self.settings_file):
            self.settings.read(self.settings_file)
        else:
            print("No settings file - reverting to standard and saving file to conf/settings.ini")
            self.settings['DEFAULT'] = { 'community': 'public',
                                    'community_password': 'public' }
            self.settings['userdata'] = {}
            self._save_settings_to_file()

    def quit(self, *event):
        """
        master frame destroy. Quits the application.
        """
        self.destroy()

    def list_add(self, widget=None):
        """add new target to list of targets"""
        datacol = Collectdata(self, title="Enter IP-addres", gfxpath=self.gfxpath)
        valid, ip, ip2, mask = datacol.show()
        widget.insert(END, ip)
        #TODO: add check to validate non-doubles!
        
        #call function to add data to widgets.

    def edit_item(self, widget=None):
        """Edits selected target"""
        #Need to check if anything is selected!
        curselec = widget.curselection()
        if curselec:
            index = int(curselec[0])
            curitem = widget.get(index)
            d = Collectdata(self, title="Edit target", edit=widget.get(curselec), gfxpath=self.gfxpath)
            valid, ip, ip2, mask = d.show()
            if ip is not curitem:
                try:
                    widget.delete(index)
                except:
                    pass
                widget.insert(index, ip)

    def delete_item(self, widget=None):
        try:
            curindex = widget.curselection()
            curtarget = widget.get(curindex)
            ret = messagebox.askyesnocancel(title="Delete?", message="Do you want to delete target:\n%s" % curtarget)
            if ret is True:
                try:
                    widget.delete(curindex)
                except:
                    pass
        except:
            messagebox.showinfo(title="Info", message="Nothing selected!")

    def createWidgets(self):
        """ Creates and lays out the widgets for the mainwindow."""
        # create Menus:
        self.menubar = tk.Menu(self.mainframe)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        mnuimport = tk.Menu(filemenu, tearoff=0)
        mnuimport.add_command(label="Target list", command=self._file_menu_import_target_list)
        mnuimport.add_command(label="Switch list", command=self._file_menu_import_switch_list)
        filemenu.add_command(label="New search", command=self._file_menu_new_search, underline=1)
        filemenu.add_cascade(label="Import", menu=mnuimport)
        filemenu.add_separator()
        filemenu.add_command(label="Settings", command=self._file_menu_settings, underline=0)
        filemenu.add_command(label="Exit", command=self.quit, underline=1, accelerator="Ctrl+X")
        #--end-- File menu build

        #--start-- edit menu build
        editmenu = Menu(self.menubar, tearoff=0)
        editmenu.add_command(label="Add target(s)", underline=4, accelerator="Ctrl-T", command=self._edit_menu_add_target_to_list)
        editmenu.add_command(label="Edit selected target", command=self._edit_menu_edit_selected_target)
        editmenu.add_command(label="Delete selected target", command=self._edit_menu_del_selected_target)
        editmenu.add_separator()
        editmenu.add_command(label="Add host(s)", underline=4, accelerator="Ctrl-H", command=self._edit_menu_add_host_to_list)
        editmenu.add_command(label="Edit selected host", command=self._edit_menu_edit_selected_host)
        editmenu.add_command(label="Delete selected host", command=self._edit_menu_del_selected_host)
        editmenu.add_separator()
        editmenu.add_command(label="Clear log window", command=self.logg.clear)
        #--end-- edit menu build

        #--start-- view menu
        viewmenu = Menu(self.menubar, tearoff=0)
        viewmenu.add_checkbutton(label="Show/hide Logg", onvalue=True, offvalue=False, variable=self.viewlogg, command=self._viewmenu_show_window_pane)
        #--end-- viewmenu
        
        #--start-- help menu build
        hlpmenu = tk.Menu(self.menubar, tearoff=0)
        hlpmenu.add_command(label="Help", command=self._help_menu_help)
        hlpmenu.add_command(label="About", command=self._help_menu_about)
        #--end-- help menu build
        
        #--start-- adding menus to main menu
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.menubar.add_cascade(label="Edit", menu=editmenu)
        self.menubar.add_cascade(label="View", menu=viewmenu)
        self.menubar.add_cascade(label="Help", menu=hlpmenu)
        #--end-- adding menus to main menu
        try:
            self.config(menu=self.menubar)
        except AttributeError:
            print("this faild!!!!")
            # master is a toplevel window (Python 1.4/Tkinter 1.63)
            tk.call(self, "config", "-menu", self.menubar)

        #create Toolbar
        toolbar = Toolbar(parent=self.mainframe)
        toolbar.add(wtype="button", gfxpath=self.gfxpath + "start.png",
                    tooltip="Start the search", command=self.addtext)
        toolbar.add(wtype="button", gfxpath=self.gfxpath + "new.png",
                    tooltip="Clears all results and start fresh")
        toolbar.add(wtype="separator")
##        toolbar.add(wtype="button", gfxpath=self.gfxpath + "addtarget.png",
##                    tooltip="Add target or a range of targets to targetslist", command=self.list_add)
##        toolbar.add(wtype="button", gfxpath=self.gfxpath + "addhost.png",
##                    tooltip="Add a host or range of hosts to hostslist")
##        toolbar.add(wtype="separator")
        toolbar.add(wtype="button", gfxpath=self.gfxpath + "exit.png",
                    tooltip="Exits the program. (Ctrl-X)", command=self.quit)
        toolbar.show()

        # create Statusbar
        self.status = StringVar()
        self.statusbar = Label(self, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W)
        self.statusbar.pack(side=BOTTOM, fill=X)
        self.status.set("Idle")
        
        #create input boxes:
        self.inputframe = Frame(self.mainframe, width=50, bd=1, relief=GROOVE, padx=12, pady=12)
        Label(self.inputframe, text="Targets to look for:", pady=2).pack()
        self.list_targets = Listbox(self.inputframe, selectmode=BROWSE)
        self.list_targets.pack(side=TOP, pady=5)
        self.list_targets_toolbar = Toolbar(parent=self.inputframe)
        self.list_targets_toolbar.add(wtype="button", gfxpath=self.gfxpath + "addtarget.png",
                                      tooltip="Add new target", command=lambda: self.list_add(widget=self.list_targets))
        self.list_targets_toolbar.add(wtype="button", gfxpath=self.gfxpath + "edit.png",
                                      tooltip="Edit selected target", command=lambda: self.edit_item(widget=self.list_targets))
        self.list_targets_toolbar.add(wtype="button", gfxpath=self.gfxpath + "trash.png",
                                      tooltip="Delete selected target", command=lambda: self.delete_item(widget=self.list_targets))
        self.list_targets_toolbar.show()
        Frame(self.inputframe, height=2, bd=1, relief=SUNKEN).pack(fill=X, padx=0, pady=10)
        Label(self.inputframe, text="Hosts to scan:", pady=2).pack()
        self.list_hosts = Listbox(self.inputframe, selectmode=BROWSE)
        self.list_hosts.pack(side=TOP, pady=5)
        self.list_hosts_toolbar = Toolbar(parent=self.inputframe)
        self.list_hosts_toolbar.add(wtype="button", gfxpath=self.gfxpath + "addhost.png",
                                    tooltip="Add new host", command=lambda: self.list_add(self.list_hosts))
        self.list_hosts_toolbar.add(wtype="button", gfxpath=self.gfxpath + "edit.png",
                                    tooltip="Edit selected host", command=lambda: self.edit_item(widget=self.list_hosts))
        self.list_hosts_toolbar.add(wtype="button", gfxpath=self.gfxpath + "trash.png",
                                    tooltip="Delete selected host", command=lambda: self.delete_item(widget=self.list_hosts))
        self.list_hosts_toolbar.show()
        self.inputframe.pack(side=RIGHT, fill=Y)

        # display Logwindow
        
        #self.logg.show()



    def addtext(self, *args):
            self.logg.println("test", "text2", "text3")
            self.logg.println("test", "text2", "text3", prefix="switch1")

    def _viewmenu_show_window_pane(self, *args):
        print(self.viewlogg)
        self.viewlogg = not self.viewlogg
        if self.viewlogg:
            self.logg.show()
        else:
            self.logg.hide()
    
    def _edit_menu_add_target_to_list(self):
        self.list_add(widget=self.list_targets)
    def _edit_menu_del_selected_target(self):
        self.delete_item(widget=self.list_targets)
    def _edit_menu_edit_selected_target(self):
        self.edit_item(widget=self.list_targets)
    def _edit_menu_add_host_to_list(self): pass
    def _edit_menu_del_selected_host(self): pass
    def _edit_menu_edit_selected_host(self): pass
    
    def _file_menu_import_target_list(self):
        """
        private function _file_menu_import_target_list
        opens Dialog to open a file containing a list of ip-adresses or MAC-adresses either separated with comma (,) or one line per target.
        TODO: figure out how to do this.
        """
        pass
    
    def _file_menu_import_switch_list(self):
        """
        private function _file_menu_import_switch_list
        opens Dialog to open a file containing a list of ip-adresses either separated with comma (,) or new-line (\\n)
        TODO: figure out how to do this.
        """
        pass
    
    def _file_menu_new_search(self):
        """
        function _file_menu_new_search
        clears all current settings and unloads any files imported.
        """
        pass
    
    def _help_menu_help(self):
        """
        private function _help_menu_help
        display help-window
        TODO: everything!
        """
        pass
    
    def _help_menu_about(self):
        """
        private function _help_menu_about
        Display Aoutdialog popupwindow.
        """
        about_dialog = tk.Toplevel(self)
        about_dialog.wm_title("About Tracemac v2.0")
        about_frame = tk.Frame(about_dialog, width=200, height=300)
        about_frame.pack()

        with codecs.open("texts\\about.txt", "r", "utf8") as f:
            about_text= f.read()

        about_label=tk.Label(about_frame, text=about_text)
        about_label.config(anchor="center")
        about_label.grid(columnspan="3", row="0")
        
        about_btn_OK = tk.Button(about_frame,
                                 text="OK",
                                 command=about_dialog.destroy,
                                 width="30")
        about_btn_OK.grid(column="1", row="1")
        about_dialog.mainloop()
        print("and then some!!!")
    
    def _file_menu_settings(self):
        """
        private function _file_menu_settings
        Display settingsdialog popupwindow.
        """
        settings_dialog = Settings_dialog(self, self.settings)
        return_val, changed = settings_dialog.show()
        if changed:
            self._save_settings_to_file()
    
    def _save_settings_to_file(self):
        with open(self.settings_file, 'w') as configfile:
                self.settings.write(configfile)

if __name__ == "__main__":
    app=frm_main(settingspath="../conf/", gfxpath="../gfx/")
    app.mainloop()
