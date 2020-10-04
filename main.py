import os
import shutil
import tempfile
from tkinter import *
from tkinter import filedialog
from tkinter.simpledialog import askstring
from tkinter.ttk import Separator, Progressbar
from tkinter import messagebox

import ffmpeg
import zipfile


class MainFrame(Frame):

    def __init__(self, window, isapp=True, name='spackgen'):
        Frame.__init__(self, window, name=name)
        self.pack(expand=Y, fill=BOTH)
        self.master.title('LR2 Soundpack Generator')
        self.isapp = isapp
        ##
        self.paths = [] # this keeps track of what entries to include in the pack BUT it does not get updated if user only changes text field!!
        self.entries = [] # is filled with (item, entry) after _create_widgets is run; self.paths is a subset of self.entries
        self.master.minsize(750, 410)
        self.switcherdir = "" # this should be stored somehow? config file?
        ##
        self._create_widgets()

        self._temps = [] # holder for temporary folders

    def _create_widgets(self):
        MenuBar = Menu(self)

        FileMenu = Menu(MenuBar, tearoff=0)
        FileMenu.add_command(label="New", command=self._clear)
        FileMenu.add_command(label="Open", command=lambda: self._open_existing(False)) # I have no idea what the shouldreturn argument was for, might be leftover from some previous paradigm
        MenuBar.add_cascade(label="File", menu=FileMenu)

        SwitcherMenu = Menu(MenuBar, tearoff=0)
        SwitcherMenu.add_command(label="Configure", command=lambda: self._switcher("configure"))
        SwitcherMenu.add_command(label="Switch", command=lambda: self._switcher("switch"))
        SwitcherMenu.add_command(label="Backup (zip)", command=lambda: self._switcher("backup-z"))
        SwitcherMenu.add_command(label="Backup (folder)", command=lambda: self._switcher("backup-f"))
        MenuBar.add_cascade(label="Switcher", menu=SwitcherMenu)

        self.master.config(menu=MenuBar)

        Panel = Frame(self)
        Panel.pack(side=TOP, fill=BOTH, expand=Y)

        for item in (['Menu', "menu.1"], ['Sandy Bay', "sandybay.2"], ['Sandy Bay BOSS', "sandybay.4"],
                     ['Dino Island', "dino.2"], ['Dino Island BOSS', "dino.4"], ['Mars', "mars.2"],
                     ['Mars BOSS', "mars.4"], ['Arctic', "arctic.2"], ['Arctic BOSS', "arctic.4"],
                     ['Xalax', "xalax.2"], ['Xalax BOSS', "xalax.4"]):
            frame = Frame(Panel)
            lbl = Label(frame, width=30, anchor="w", text='Select audio for {} '.format(item[0]))
            # ent is displaying file location
            ent = Entry(frame, width=45)
            btn = Button(frame, text='Browse...',
                             command=lambda e=ent, i=item : self._file_dialog("open", e, i)) # why doesn't ("open", ent, item) work???
            lbl.pack(side=LEFT, fill=X)
            ent.pack(side=LEFT, expand=Y, fill=X)
            btn.pack(side=LEFT, padx=5)
            frame.pack(fill=X, padx=10, pady=3)

            ##
            self.entries.append((item, ent))

        Separator(self.master, orient=HORIZONTAL).pack(side="top", fill="x", padx=10)

        buttonGenerate = Button(text="Generate", command=self._generate)
        buttonGenerate.pack(side=LEFT)

        self.bar = Progressbar(orient="horizontal", length=500)
        self.bar.pack(side=BOTTOM, fill="x", padx=10, pady=5)

    def _file_dialog(self, type, ent, item):
        # triggered when the user clicks a 'Browse' button
        if type == 'open':
            fn = None
            opts = {'initialfile': ent.get(), 'filetypes': [], 'title': 'Select a file to open...'}

            fn = filedialog.askopenfilename(**opts)

            if fn:
                ent.delete(0, END)
                ent.insert(END, fn)
                self.paths.append((item, ent))
        elif type == 'save':
            opts = {'initialfile': "pack", 'filetypes': [("Zip archive", "*.zip")],
                    'title': 'Select a file to save...'}
            return filedialog.asksaveasfilename(**opts)
        elif type == 'open_':
            opts = {'filetypes': [("Zip archive", "*.zip")], 'title': 'Select a pack to open...'}

            return filedialog.askopenfilename(**opts)
        elif type == 'switcher':
            opts = {'filetypes': [("Windows executable", "*.exe")], 'title': 'Select Switcher...'}

            return filedialog.askopenfilename(**opts)

    def _generate(self):
        self.tempfolder = tempfile.mkdtemp()
        self._temps.append(self.tempfolder)
        currentDirectory = os.getcwd() # but why?

        for entry in self.paths:
            try:

                (
                    ffmpeg
                        .input(entry[1].get())
                        .output(os.path.join(currentDirectory, self.tempfolder, "{0}{1}".format(entry[0][1][:-2], ".wav")), acodec="adpcm_ms", fflags="-bitexact")
                        .run(capture_stdout=True, capture_stderr=True)
                )

                os.rename(os.path.join(currentDirectory, self.tempfolder, "{0}{1}".format(entry[0][1][:-2], ".wav")), os.path.join(currentDirectory, self.tempfolder, "{0}".format(entry[0][1])))
                self.bar['value'] += 100 / (len(self.paths) + 1)
            except ffmpeg.Error as e:
                print('stdout:', e.stdout.decode('utf8'))
                print('stderr:', e.stderr.decode('utf8'))
                raise e

        self._create_archive()
        shutil.rmtree(self.tempfolder)
        self._temps.pop()

    def _create_archive(self):
        shutil.make_archive(self._file_dialog('save', 0, 0), 'zip', self.tempfolder)
        self.bar['value'] += 100 / (len(self.paths) + 1)

    def _clear(self):
        for entry in self.entries:
            entry[1].delete(0, END)

        # clean up extracted zip
        for tempfolder in frame._temps:
            shutil.rmtree(tempfolder)

    def _open_existing(self, shouldreturn):
        zippath = self._file_dialog('open_', 0,0)

        if shouldreturn == True:
            return zippath
        else:
            with zipfile.ZipFile(zippath) as zippack:
                self._clear()

                self.importedtemp = tempfile.mkdtemp()
                self._temps.append(self.importedtemp)

                zippack.extractall(path=self.importedtemp)

                for entry in self.entries:
                    if os.path.exists(os.path.join(self.importedtemp, entry[0][1])):
                        entry[1].insert(END, os.path.join(self.importedtemp, entry[0][1]))

                        self.paths.append(entry) # append to self.paths (iterated by _generate() )

    def _switcher(self, param):
        if (param != "configure" and self.switcherdir == ""):
            messagebox.showwarning("Warning", "Switcher directory not set! \nSet now?")
            self._switcher("configure")
            messagebox.showwarning("Warning", "Continuing with previous operation: {0}".format(param))
            self._switcher(param)
        elif param == "configure":
            self.switcherdir = self._file_dialog('switcher', 0,0)
            messagebox.showwarning("Notice", "Set LR2 music directory then enter exit to configure subutility.")
            os.system(self.switcherdir)
        elif param == "switch":
            desiredpack = askstring("Prompt", "Enter pack name (must be located in LR2 music folder): ")
            os.system("{0} switch {1}".format(self.switcherdir, desiredpack))
        elif param == "backup-z":
            os.system("{0} backup zip".format(self.switcherdir))
        elif param == "backup-f":
            os.system("{0} backup folder".format(self.switcherdir))


def on_closing():
    # clean up temps on user close
    for tempfolder in frame._temps:
        shutil.rmtree(tempfolder)
    root.destroy()


if __name__ == '__main__':
    try:
        root = Tk()
        frame = MainFrame(root)
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
    except Exception as e:
        if frame:
            for tempfolder in frame._temps:
                shutil.rmtree(tempfolder)
        messagebox.showerror("Error", e)
