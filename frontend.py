import os
import tkinter as tk
import webbrowser
from os.path import basename
from pathlib import Path
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.ttk import Progressbar, Separator
from typing import List

import icon


class MainWindow(tk.Frame):
    def __init__(self, split_pdf, master=None, reverse_on_even: bool = True, add_blank_if_needed: bool = False):
        tk.Frame.__init__(self)
        self.split_pdf = split_pdf
        self.master = master or self.master
        self.grid(sticky=tk.NSEW, padx=10, pady=5)

        _row, _column = 1, 1
        tk.Label(self, text='File:').grid(row=_row, column=_column, sticky=tk.W, padx=(0, 10), pady=5)
        _column += 1
        self.input_file_value = tk.StringVar()
        self.input_file = tk.Entry(self, width=70, textvariable=self.input_file_value)
        self.input_file.grid(row=_row, column=_column, sticky=tk.EW, columnspan=2, pady=5)
        _column += 2
        self.input_file_button = tk.Button(self, text='Browse', command=self.input_file_button_command)
        self.input_file_button.grid(row=_row, column=_column, sticky=tk.EW, padx=(10, 0), pady=5)

        _row, _column = 2, 1
        _column += 1
        self.reverse_on_even_checkbutton_value = tk.IntVar(value=int(reverse_on_even))
        self.reverse_on_even_checkbutton = tk.Checkbutton(
            self,
            text='Reverse on even',
            variable=self.reverse_on_even_checkbutton_value
        )
        self.reverse_on_even_checkbutton.grid(row=_row, column=_column, sticky=tk.W)
        _column += 1
        self.add_blank_if_needed_checkbutton_value = tk.IntVar(value=int(add_blank_if_needed))
        self.add_blank_if_needed_checkbutton = tk.Checkbutton(
            self,
            text='Add blank if needed',
            variable=self.add_blank_if_needed_checkbutton_value
        )
        self.add_blank_if_needed_checkbutton.grid(row=_row, column=_column, sticky=tk.EW)

        _row, _column = 3, 1
        tk.Label(self, text='Output Directory:').grid(row=_row, column=_column, sticky=tk.W, padx=(0, 10), pady=5)
        _column += 1

        self.output_directory_value = tk.StringVar()
        self.output_directory = tk.Entry(self, width=70, textvariable=self.output_directory_value, state=tk.DISABLED)
        self.output_directory.grid(row=_row, column=_column, sticky=tk.EW, columnspan=2, pady=5)
        _column += 2
        self.output_directory_button = tk.Button(self, text='Browse', command=self.output_directory_button_command)
        self.output_directory_button.grid(row=_row, column=_column, sticky=tk.EW, padx=(10, 0), pady=5)

        separator = Separator(self, orient=tk.HORIZONTAL)
        separator.place(relx=0, rely=0.57, relwidth=1, relheight=1)

        _row, _column = 4, 1
        self.progress_bar = Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress_bar.grid(row=_row, column=_column, sticky=tk.EW, columnspan=3, pady=(20, 5))
        _column += 3

        self.start_button_value = tk.StringVar(value='Start')
        self.start_button = tk.Button(self, command=self.start_button_command, textvariable=self.start_button_value)
        self.start_button.grid(row=_row, column=_column, sticky=tk.NSEW, rowspan=1, padx=(10, 0), pady=(20, 5))

        _row, _column = 5, 1
        self.status_label_value = tk.StringVar()
        self.status_label = tk.Label(self, textvariable=self.status_label_value)
        self.status_label.grid(row=_row, column=_column, sticky=tk.W, columnspan=2, pady=5)
        _column += 2
        self.open_pdfs_button = tk.Button(
            self,
            text='Open PDFs',
            command=self.open_pdfs_button_command,
            state=tk.DISABLED
        )
        self.open_pdfs_button.grid(row=_row, column=_column, sticky=tk.NS + tk.E, rowspan=1, ipadx=10, pady=5)
        _column += 1
        self.open_directory_button = tk.Button(self, text='Open Directory ', command=self.open_directory_button_command)
        self.open_directory_button.grid(row=_row, column=_column, sticky=tk.NSEW, rowspan=1, padx=(10, 0), pady=5)

        self.is_custom_output: bool = False
        self.output_dir_path: Path = Path()
        self.output_filename: str = ''
        self.result_files: List[str] = []

    def _input_file_button_command(self):
        if not self.validate_input():
            return

        self.output_filename = basename(self.input_file_value.get()).rsplit('.',  maxsplit=1)[0]
        if not self.is_custom_output:
            self.output_dir_path = Path(self.input_file_value.get()).parent
        self.set_output_directory_path()

    def input_file_button_command(self):
        self.input_file_value.set(str(Path(askopenfilename(filetypes=[('pdf', '*.pdf')])).absolute()))
        self._input_file_button_command()

    def output_directory_button_command(self):
        self.output_dir_path = Path(askdirectory())
        self.set_output_directory_path()
        if not self.validate_output():
            return
        self.is_custom_output = True

    def get_output_directory_path(self):
        if self.output_dir_path.is_dir():
            return f'{self.output_dir_path.absolute()}{os.sep}{basename(self.output_filename)}'.rstrip(os.sep)
        return ''

    def set_output_directory_path(self):
        self.output_directory_value.set(self.get_output_directory_path())

    def start_button_command(self):
        if self.open_pdfs_button['state'] == tk.DISABLED:
            self._input_file_button_command()
            if not self.validate():
                return

            self.input_file['state'] = tk.DISABLED
            self.input_file_button['state'] = tk.DISABLED
            self.reverse_on_even_checkbutton['state'] = tk.DISABLED
            self.add_blank_if_needed_checkbutton['state'] = tk.DISABLED
            self.output_directory_button['state'] = tk.DISABLED

            self.show_status('Processing...')

            if not os.path.exists(self.output_directory_value.get()):
                os.mkdir(self.output_directory_value.get())

            self.result_files = self.split_pdf(
                input_file_path=self.input_file_value.get(),
                output_dir_path=self.get_output_directory_path(),
                output_filename=self.output_filename,
                reverse_on_even=bool(self.reverse_on_even_checkbutton_value.get()),
                add_blank_if_needed=bool(self.add_blank_if_needed_checkbutton_value.get()),
                progress_func=self.set_progress
            )

            self.set_progress(100)

            self.open_pdfs_button['state'] = tk.NORMAL
            self.show_status('Done!', color='#047D1A')
            self.start_button_value.set('Split Other')
        elif self.open_pdfs_button['state'] == tk.NORMAL:
            self.restart()

    def open_pdfs_button_command(self):
        for file in self.result_files:
            webbrowser.open_new(file)

    def open_directory_button_command(self):
        if not os.path.isdir(self.output_directory_value.get()):
            self.show_error('Wrong Output Directory')
            return
        os.startfile(self.output_directory_value.get())

    def set_progress(self, value: int):
        self.progress_bar['value'] = value
        self.master.update_idletasks()

    def restart(self):
        self.input_file_value.set('')
        self.output_directory_value.set('')
        self.show_status('')
        self.start_button_value.set('Start')
        self.set_progress(0)
        self.input_file['state'] = tk.NORMAL
        self.input_file_button['state'] = tk.NORMAL
        self.output_directory_button['state'] = tk.NORMAL
        self.reverse_on_even_checkbutton['state'] = tk.NORMAL
        self.add_blank_if_needed_checkbutton['state'] = tk.NORMAL
        self.open_pdfs_button['state'] = tk.DISABLED

    def validate_input(self):
        if not os.path.isfile(self.input_file_value.get()):
            self.show_error('Wrong Input File')
            return False
        if not self.input_file_value.get().lower().endswith('.pdf'):
            self.show_error('Wrong file')
            return False
        return True

    def validate_output(self):
        if not self.output_dir_path.is_dir() or not self.output_dir_path.exists():
            self.show_error('Wrong Output Directory')
            return False
        return True

    def validate(self):
        return self.validate_input() and self.validate_output()

    def show_error(self, message):
        self.show_status(message=message, color='#f00')

    def show_status(self, message, color: str = '#000'):
        self.status_label['fg'] = color
        self.status_label_value.set(message)


def main(split_pdf=lambda *x: x):
    root = tk.Tk()
    MainWindow(master=root.master, split_pdf=split_pdf)
    root.eval('tk::PlaceWindow . center')
    root.iconphoto(True, tk.PhotoImage(data=icon.icon))
    root.title('PDF Splitter')
    root.resizable(False, False)
    root.mainloop()


if __name__ == '__main__':
    main()
