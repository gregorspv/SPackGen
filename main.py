import os
import shutil
import tempfile
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Separator, Progressbar

import ffmpeg


class MainFrame(Frame):

    def __init__(self, isapp=True, name='spackgen'):
        Frame.__init__(self, name=name)
        self.pack(expand=Y, fill=BOTH)
        self.master.title('LR2 Soundpack Generator')
        self.isapp = isapp
        ##
        self.paths = []
        self.entries = []
        self.master.minsize(750, 410)
        ##
        self._create_widgets()

    def _create_widgets(self):
        MenuBar = Menu(self)
        FileMenu = Menu(MenuBar, tearoff=0)
        FileMenu.add_command(label="Clear", command=self._clear)
        FileMenu.add_command(label="Open", command=print)
        MenuBar.add_cascade(label="File", menu=FileMenu)
        self.master.config(menu=MenuBar)

        Panel = Frame(self)
        Panel.pack(side=TOP, fill=BOTH, expand=Y)

        for item in (['Menu', "menu.1"], ['Sandy Bay', "sandybay.2"], ['Sandy Bay BOSS', "sandybay.4"],
                     ['Dino Island', "dino.2"], ['Dino Island BOSS', "dino.4"], ['Mars', "mars.2"],
                     ['Mars BOSS', "mars.4"], ['Arctic', "arctic.2"], ['Arctic BOSS', "arctic.4"],
                     ['Xalax', "xalax.2"], ['Xalax BOSS', "xalax.4"]):
            frame = Frame(Panel)
            lbl = Label(frame, width=30, anchor="w", text='Select audio for {} '.format(item[0]))
            ent = Entry(frame, width=45)
            btn = Button(frame, text='Browse...',
                             command=lambda i="open", e=ent, item_holder=item: self._file_dialog(i, e, item_holder))
            lbl.pack(side=LEFT, fill=X)
            ent.pack(side=LEFT, expand=Y, fill=X)
            btn.pack(side=LEFT, padx=5)
            frame.pack(fill=X, padx=10, pady=3)

            ##
            self.entries.append(ent)

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

    def _generate(self):
        self.tempfolder = tempfile.mkdtemp()
        currentDirectory = os.getcwd()

        for entry in self.paths:
            try:

                (
                    ffmpeg
                        .input(entry[1].get())
                        .output(os.path.join(currentDirectory, self.tempfolder, "{0}{1}".format(entry[0][1][:-2], ".wav")), acodec="adpcm_ms", fflags="+bitexact")
                        .run(capture_stdout=True, capture_stderr=True)
                )

                os.rename(os.path.join(currentDirectory, self.tempfolder, "{0}{1}".format(entry[0][1][:-2], ".wav")), os.path.join(currentDirectory, self.tempfolder, "{0}".format(entry[0][1])))
                self.bar['value'] += 100 / (len(self.paths) + 1)
            except ffmpeg.Error as e:
                print('stdout:', e.stdout.decode('utf8'))
                print('stderr:', e.stderr.decode('utf8'))
                raise e

        self._create_archive()

    def _create_archive(self):
        shutil.make_archive(self._file_dialog('save', 0, 0), 'zip', self.tempfolder)
        shutil.rmtree(self.tempfolder)
        self.bar['value'] += 100 / (len(self.paths) + 1)

    def _clear(self):
        for entry in self.entries:
            entry.delete(0, END)


if __name__ == '__main__':
    try:
        frame = MainFrame()
        frame.mainloop()
    finally:
        if frame.tempfolder:
            shutil.rmtree(frame.tempfolder)