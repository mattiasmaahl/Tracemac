"""
Created 2016-04-12
@author: Mattias Måhl
"""
from tkinter import *
import tkinter as tk
import codecs
import configparser
import os.path


class frm_main(tk.Tk):
    """Start object to render the application window.\n
    use:\n
    import libs.frm_main as mainwindow\n
    if __name__ == "__main__":\n
         app = mainwindow.App()\n
         app.mainloop()\n\n
    """
    settings = configparser.ConfigParser()
    
    def __init__(self):
        tk.Tk.__init__(self)
        self.my_frame = tk.Frame(master=self, width=300, height=200)
        self.my_frame.pack()
        self.menubar = tk.Menu(self.my_frame)
        self.createWidgets(self.my_frame)
        self.bind_all("<Control-q>", self.quit)
        settings_file = "../conf/settings.ini"
        
        #checks if the settings_file exists, if not it creates it with defaults.
        if os.path.isfile(settings_file):
            self.settings.read(settings_file)
        else:
            print("No settings file - reverting to standard and saving file to conf/settings.ini")
            self.settings['DEFAULT'] = { 'community': 'public',
                                    'community_password': 'public' }
            self.settings['userdata'] = {}
            with open(settings_file, 'w') as configfile:
                self.settings.write(configfile)

    def quit(self, *event):
        self.destroy()
    
    def _createMenus(self, frame=None):
        """
        private function _createMenus
        function to create mainwindow menus.
        commands to be set later.
        """
        # --start-- File menu build:
        filemenu = tk.Menu(self.menubar, tearoff=0)
        mnuimport = tk.Menu(filemenu, tearoff=0)
        mnuimport.add_command(label="Target list", command=self._file_menu_import_target_list)
        mnuimport.add_command(label="Switch list", command=self._file_menu_import_switch_list)
        filemenu.add_command(label="New search", command=self._file_menu_new_search, underline=1)
        filemenu.add_cascade(label="Import", menu=mnuimport)
        filemenu.add_separator()
        filemenu.add_command(label="Settings", command=self._file_menu_settings, underline=0)
        filemenu.add_command(label="Quit", command=self.quit, underline=0, accelerator="Ctrl+Q")
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

        
    def createWidgets(self, frame):
        """ Creates and lays out the widgets for the mainwindow."""
        #create Menus:
        self._createMenus(frame=frame)

        #create input boxes:
        

        
##        frame.canvas = tk.Canvas(frame, bg="white", width=400, height=400,
##                             bd=0, highlightthickness=0)
##        frame.canvas.grid(row="1", columnspan="2")
        
##        self.QUIT = tk.Button(frame,
##                              text="QUIT",
##                              fg="red",
##                              command=self.destroy)
##        self.QUIT.grid(column="1", row="0")

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
        print("help__about!!!!")
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
        settings_dialog = tk.Toplevel(self)
        settings_dialog.wm_title("Settings")
        settings_frame = tk.Frame(settings_dialog)
        settings_frame.grid(sticky=(N, S, E, W), padx=(3, 12), pady=(3, 12))
        settings_label=tk.Label(settings_frame, text="Settings:", font="Helvetica 20 underline bold")
        #settings_label.config(anchor=(E,W,S,N))
        settings_label.grid(columnspan=3, row=0, sticky=(E, W))
        entry = {}
        tk.Label(settings_frame, text="Defaults", font="Helvetica 8 italic underline").grid(row=1, column=2, sticky=W)
        
        row=1
        for section in self.settings.sections():
            txt = "Section: " + section
            tk.Label(settings_frame, text=txt, font="Helvetica 11 bold underline").grid(column=0, row = row, sticky=(N,W), columnspan=2)
            row += 1
            for key in self.settings[section]:
                #print(section, key, self.settings[section][key], row)
                tk.Label(settings_frame, text=key).grid(row=row, column=0, sticky=W)
                en = tk.Entry(settings_frame)
                en.insert(0, self.settings[section][key])
                en.grid(row=row, column=1, sticky=(E,W))
                data={key: en}
                entry[section]=data
                #entry[key].insert(0, self.settings[section][key])
                #print(self.settings[section][key])
                tk.Label(settings_frame, text=self.settings['DEFAULT'][key], font="Helvetica 8 italic").grid(row=row, column=2, sticky="W")
                row += 1
                print(row)
                
        print (entry)
        print (row)
        btn_Ok = tk.Button(settings_frame,
                           text="OK",
                           command=settings_dialog.destroy,
                           width=10)
        btn_Ok.grid(column=1, row=(row+1), sticky=E)
        btn_Cancel = tk.Button(settings_frame,
                               text="Cancel",
                               command=settings_dialog.destroy,
                               width=10)
        btn_Cancel.grid(column=2, row=(row+1), sticky=E)
        settings_dialog.columnconfigure(0, weight=1)
        settings_dialog.rowconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=1)
        settings_dialog.update()
        settings_dialog.minsize(settings_dialog.winfo_width(), settings_dialog.winfo_height())
        print(settings_dialog.winfo_height(), settings_dialog.winfo_width())
        settings_dialog.mainloop()


if __name__ == "__main__":
    app=frm_main()
    app.mainloop()
