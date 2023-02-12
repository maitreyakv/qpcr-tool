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


class PlotViewer(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(padx=5, pady=5)

    def clear(self):
        for tab in self.tabs():
            self.forget(tab)

    def add_plot(self, fig, tab_title):
        from matplotlib.backends.backend_tkagg import (
            FigureCanvasTkAgg, NavigationToolbar2Tk
        )

        plot_frame = ttk.Frame()
        canvas = FigureCanvasTkAgg(fig, plot_frame)
        canvas.draw()
        canvas.get_tk_widget().grid()  #.pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.grid()  #.pack(side=tk.BOTTOM, fill=tk.X)

        self.add(plot_frame, text=tab_title)


class MainFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(padx=5, pady=5)

        file_select_frame = tk.LabelFrame(
            self,
            text='Select File'
        )
        file_select_frame.grid(padx=5, pady=5)

        load_button = ttk.Button(
            file_select_frame,
            text='Open file',
            command=self.func
        )
        load_button.grid(row=0, column=0, padx=5, pady=5)

        self.selected_file_label = ttk.Label(
            file_select_frame
        )
        self.selected_file_label.grid(row=0, column=1, padx=5, pady=5)

        self.plots = PlotViewer(self)


    # TODO: Rename and refactor
    def func(self):
        self.plots.clear()

        filename = fd.askopenfilename(
            title='Open qPCR data file',
            initialdir='.',
            filetypes=[('Excel files', '*.xlsx')]
        )

        self.selected_file_label['text'] = filename
        
        if not filename:
            logging.info('No file was selected')
            return
        logging.info(f'File "{filename}" was selected')

        df = load_data(filename)
        logging.info('Loaded data from file')

        if df is None:
            return

        df = compute(df)
        print(df)

        for p in df.target.unique():
            fig = make_barplot(df, p)
            self.plots.add_plot(fig, p)
        


class App(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.grid()
        root.geometry("1000x800")
        MainFrame(self)


if __name__ == '__main__':
    #now_str = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
    #log_filename = f'qpcr_app_{now_str}.log'
    logging.basicConfig(
        #filename=log_filename,
        #encoding='utf-8',
        level=logging.INFO
    )

    logging.info('Starting application')
    root = tk.Tk()
    root.title("qPCR Analysis")
    myapp = App(root)
    myapp.mainloop()
    logging.info('Application was closed')