"""
Created 2016-04-12
@author: Mattias Måhl
"""
from tkinter import *
from settingsdialog import *
import tkinter as tk
import codecs
import configparser
import os.path
from PIL import Image, ImageTk


class frm_main(tk.Tk):
    """Start object to render the application window.\n
    use:\n
    import libs.frm_main as mainwindow\n
    if __name__ == "__main__":\n
         app = mainwindow.App()\n
         app.mainloop()\n\n
    """
    settings = configparser.ConfigParser()
    settings_file = "../conf/settings.ini"
    
    def __init__(self):
        tk.Tk.__init__(self)
        self.wm_state('zoomed')
        self.mainframe = tk.Frame(master=self, bg="green")
        self.mainframe.pack(expand=True, fill=BOTH)
        self.bind_all("<Control-x>", self.quit)
        self.bind_all("<Control-a>", self.add_target)
        self.createWidgets()
        
        #checks if the settings_file exists, if not it creates it with defaults.
        if os.path.isfile(self.settings_file):
            self.settings.read(self.settings_file)
        else:
            print("No settings file - reverting to standard and saving file to conf/settings.ini")
            self.settings['DEFAULT'] = { 'community': 'public',
                                    'community_password': 'public' }
            self.settings['userdata'] = {}
            _save_settings_to_file()

    def quit(self, *event):
        self.destroy()

    def add_target(self):
        pass
    
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

        #--start-- help menu build
        hlpmenu = tk.Menu(self.menubar, tearoff=0)
        hlpmenu.add_command(label="Help", command=self._help_menu_help)
        hlpmenu.add_command(label="About", command=self._help_menu_about)
        #--end-- help menu build
        
        #--start-- adding menus to main menu
        self.menubar.add_cascade(label="File", menu=filemenu)
        self.menubar.add_cascade(label="Help", menu=hlpmenu)
        #--end-- adding menus to main menu
        try:
            self.config(menu=self.menubar)
        except AttributeError:
            print("this faild!!!!")
            # master is a toplevel window (Python 1.4/Tkinter 1.63)
            tk.call(self, "config", "-menu", self.menubar)

            
        # create Toolbar
        self.toolbarframe = Frame(self.mainframe, height=20, bd=1, relief=RAISED)
        self.addimg = Image.open("../gfx/add.png")
        addimg = ImageTk.PhotoImage(self.addimg)
        addbutton = Button(self.toolbarframe, height=20, width=20, image=addimg, relief=FLAT)
        addbutton.image=addimg
        addbutton.pack(side=LEFT, padx=2, pady=2)
        self.toolbarframe.pack(side=TOP, fill=X)


        # create Statusbar
        self.status = StringVar()
        self.statusbar = Label(self, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W)
        self.statusbar.pack(side=BOTTOM, fill=X)
        self.status.set("Idle")
        
        #create input boxes:
        self.inputframe = Frame(self.mainframe, width=50, bd=1, relief=GROOVE, padx=12, pady=12)
        Label(self.inputframe, text="Targets to look for:", pady=2).pack()
        self.list_targets = Listbox(self.inputframe)
        self.list_targets.pack()
        Label(self.inputframe, text="Hosts to scan:", pady=2).pack()
        self.list_hosts = Listbox(self.inputframe)
        self.list_hosts.pack()
        self.inputframe.pack(side=RIGHT, fill=Y)

        
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
    app=frm_main()
    app.mainloop()
