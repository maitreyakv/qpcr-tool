"""
Main program for qPCR analysis application
"""

__author__ = 'Maitreya Venkataswamy'

import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import logging
from datetime import datetime
from tabulate import tabulate
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk
)
import matplotlib.pyplot as plt

from backend import load_data, compute
from frontend import make_barplot


class PlotViewer(ttk.Notebook):
    def __init__(self, parent):
        super().__init__(parent)
        self.clear()

    def clear(self):
        for tab in self.tabs():
            self.forget(tab)

    def add_plot(self, fig, tab_title):
        plot_frame = ttk.Frame()
        canvas = FigureCanvasTkAgg(fig, plot_frame)
        canvas.draw()
        canvas.get_tk_widget().grid()  #.pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(canvas, plot_frame, pack_toolbar=False)
        toolbar.update()
        toolbar.grid()  #.pack(side=tk.BOTTOM, fill=tk.X)

        self.add(plot_frame, text=tab_title)


class PrimerAvgFrame(ttk.LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text='Primer Avg. Values')
        self.primers = {}

    def clear(self):
        for child in self.winfo_children():
            child.destroy()
        self.primers = {}

    def add_primer(self, primer_name):
        primer_label = ttk.Label(self, text=primer_name + ' avg value')
        primer_label.grid(padx=5, pady=5)
        primer_entry = ttk.Entry(self)
        primer_entry.grid(padx=5, pady=5)
        self.primers[primer_name] = (primer_label, primer_entry)

    def get_primer_avg(self):
        return {
            primer_name: float(primer[1].get())
            for primer_name, primer
            in self.primers.items()
        }


class MainFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(padx=5, pady=5)

        self.df = None

        file_frame = ttk.LabelFrame(self, text='Data File')
        file_frame.grid(
            row=0, column=0, padx=5, pady=5, columnspan=2, sticky = tk.W+tk.E
        )
        load_button = ttk.Button(
            file_frame,
            text='Open file',
            command=self.load_qpcr_data
        )
        load_button.grid(row=0, column=0, padx=5, pady=5)
        self.warn_nan = tk.IntVar()
        self.warn_nan_checkbutton = ttk.Checkbutton(
            file_frame, text='Warn missing data', variable=self.warn_nan
        )
        self.warn_nan_checkbutton.grid(row=1, column=0, padx=5, pady=5)
        self.selected_file_label = ttk.Label(file_frame)
        self.selected_file_label.grid(row=0, column=1, padx=5, pady=5)

        self.primer_avg_frame = PrimerAvgFrame(self)
        self.primer_avg_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.plots = PlotViewer(self)
        self.plots.grid(row=1, column=1, padx=5, pady=5)

        compute_button = ttk.Button(
            self,
            text='Compute',
            command=self.compute_and_plot
        )
        compute_button.grid(row=2, column=0, padx=5, pady=5)

    def warn_nan_cq(self):
        if not self.warn_nan.get():
            return
        primer_control = self.df.target.mode().iloc[0]
        for (sample, primer), dfs in self.df.groupby(['sample', 'target']):
            if not primer == primer_control:
                if dfs.cq.isna().any():
                    tk.messagebox.showwarning(
                        title='Missing Data!',
                        message=f'{sample} - {primer}\n' + tabulate(
                            dfs[['well_position', 'cq']], 
                            tablefmt='psql', 
                            showindex=False
                        )
                    )

    # TODO: Rename and refactor
    def load_qpcr_data(self):
        self.plots.clear()
        self.primer_avg_frame.clear()

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

        self.df = load_data(filename)
        logging.info('Loaded data from file')

        control_primer = self.df.target.mode().iloc[0]
        for primer in self.df.target.unique():
            if not primer == control_primer:
                self.primer_avg_frame.add_primer(primer)

        self.warn_nan_cq()

    def compute_and_plot(self):
        self.plots.clear()
        try:
            primer_avg = self.primer_avg_frame.get_primer_avg()
        except ValueError as e:
            tk.messagebox.showerror(
                message='Error parsing average primer values!'
            )
            return

        self.df = compute(self.df, primer_avg)

        control_primer = self.df.target.mode().iloc[0]
        for p in self.df.target.unique():
            if not p == control_primer:
                fig = make_barplot(self.df, p)
                self.plots.add_plot(fig, p)
        

class App(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.grid()
        root.geometry("850x750")
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