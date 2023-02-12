"""
Main program for qPCR analysis application
"""

__author__ = 'Maitreya Venkataswamy'

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import logging
from datetime import datetime

from backend import load_data, compute
from frontend import make_barplot



class MainFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid()

        file_select_frame = tk.LabelFrame(
            self,
            text='Select File'
        )
        file_select_frame.grid()

        load_button = ttk.Button(
            file_select_frame,
            text='Open file',
            command=self.func
        )
        load_button.grid(row=0, column=0)

        self.selected_file_label = ttk.Label(
            file_select_frame
        )
        self.selected_file_label.grid(row=0, column=1)

    # TODO: Rename and refactor
    def func(self):
        filename = fd.askopenfilename(
            title='Open qPCR data file',
            initialdir='.',
            filetypes=[('Excel files', '*.xlsx')]
        )

        self.selected_file_label['text'] = filename
        
        if not filename:
            logging.debug('No file was selected')
            return
        logging.debug(f'File "{filename}" was selected')

        df = load_data(filename)
        logging.debug('Loaded data from file')

        if df is None:
            return

        df = compute(df)
        
        for primer in df.target.unique():
            make_barplot(df, primer)

        import matplotlib.pyplot as plt
        plt.show()
        


class App(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.grid()
        root.geometry("800x600")
        MainFrame(self)


if __name__ == '__main__':
    #now_str = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    #log_filename = f'qpcr_app_{now_str}.log'
    logging.basicConfig(
        #filename=log_filename,
        #encoding='utf-8',
        level=logging.DEBUG
    )

    logging.info('Starting application')
    root = tk.Tk()
    root.title("qPCR Analysis")
    myapp = App(root)
    myapp.mainloop()
    logging.info('Application was closed')