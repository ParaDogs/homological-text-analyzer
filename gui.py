import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.scrolledtext as scrolledtext
import tkinter.messagebox as mbox

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
matplotlib.use("TkAgg")

from text_analyzer import *

def clear_window(window):
    for el in window.winfo_children():
        el.destroy()

class InputTextWindow():
    def __init__(self, text):
        clear_window(root)
        self.text = text # text for analysis

        self.label_text_file_path = tk.Label(root, text="Укажите путь к текстовому файлу", width=75)
        self.label_text_file_path.grid(row=0, column=0)

        self.button_browse_text_file = tk.Button(root, text="Обзор...", command=self.browse_text_file)
        self.button_browse_text_file.grid(row=0, column=1)

        self.text_area = scrolledtext.ScrolledText(root, undo=True, width=78)
        self.text_area.insert(tk.END, self.text)
        self.text_area.grid(row=1, column=0, columnspan=2)

        self.button_confirm_text_input = tk.Button(root, text="Подтвердить", command=self.confirm_text_input)
        self.button_confirm_text_input.grid(row=2, column=0)

    def browse_text_file(self):
        filename = filedialog.askopenfilename()
        self.label_text_file_path.configure(text=filename)
        file = open(filename, 'r')
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(tk.END, file.read())
        file.close()

    def confirm_text_input(self):
        self.text = self.text_area.get(1.0, tk.END)
        SelectTokenizationTextMethodWindow(self)

class SelectTokenizationTextMethodWindow():
    def __init__(self, inputTextWindow):
        clear_window(root)
        self.inputTextWindow = inputTextWindow

        self.label_header = tk.Label(root, text="Выберите способ разбиения текста")
        self.label_header.grid(row=0, column=0)

        self.method = tk.IntVar()
        self.method.set(1)
        self.radiobutton_sentences = tk.Radiobutton(root, text="По предложениям", variable=self.method, value=0)
        self.radiobutton_paragraph = tk.Radiobutton(root, text="По абзацам", variable=self.method, value=1)
        self.radiobutton_sentences.grid(row=1, column=0, sticky="w")
        self.radiobutton_paragraph.grid(row=2, column=0, sticky="w")

        self.button_next = tk.Button(root, text="Подтвердить", command=self.confirm) 
        self.button_back = tk.Button(root, text="Назад", command=self.back)
        self.button_next.grid(row=3, column=0)
        self.button_back.grid(row=4, column=0)

    def confirm(self):
        InputDiameterDeltaWindow(self)

    def back(self):
        InputTextWindow(self.inputTextWindow.text)

class InputDiameterDeltaWindow():
    def __init__(self, selectTokenizationTextMethodWindow):
        clear_window(root)
        self.selectTokenizationTextMethodWindow = selectTokenizationTextMethodWindow
        self.delta = 0.5

        self.label_header = tk.Label(root, text="Введите шаг изменения диаметров симплексов")
        self.label_header.grid(row=0, column=0)

        self.str_delta = tk.StringVar()
        self.entry_delta = tk.Entry(root, textvariable=self.str_delta)
        self.entry_delta.insert(tk.END, "0.5")
        self.entry_delta.grid(row=1, column=0, sticky="w")

        self.label_diameter_interval = tk.Label(root)
        self.label_diameter_interval.grid(row=2, column=0)

        self.button_next = tk.Button(root, text="Подтвердить", command=self.confirm) 
        self.button_back = tk.Button(root, text="Назад", command=self.back)
        self.button_next.grid(row=3, column=0)
        self.button_back.grid(row=4, column=0)

    def confirm(self):
        try:
            self.delta = float(self.str_delta.get())
            if self.delta > 0:
                self.label_diameter_interval.configure(text="Список диаметров: " + str([self.delta*i for i in range(1,6)]))
                self.button_next = tk.Button(root, text="Далее", command=self.next)
                self.button_next.grid(row=6, column=0)
            else:
                mbox.showwarning("Ошибка", "Шаг изменения диаметра должен быть положительным числом!")
        except ValueError:
            mbox.showwarning("Ошибка", "Шаг изменения диаметра должен быть положительным числом!")
            
    def next(self):
        VizualizationBarcodesWindow(self)

    def back(self):
        SelectTokenizationTextMethodWindow(self.selectTokenizationTextMethodWindow.inputTextWindow)

class VizualizationBarcodesWindow():
    def __init__(self, inputDiameterDeltaWindow):
        clear_window(root)
        self.inputDiameterDeltaWindow = inputDiameterDeltaWindow
        # data barcodes for text
        if self.inputDiameterDeltaWindow.selectTokenizationTextMethodWindow.method.get() == 0:
            split_method = 'sentence'
        else:
            split_method = 'paragraph'
        text = Text(self.inputDiameterDeltaWindow.selectTokenizationTextMethodWindow.inputTextWindow.text, split_method)

        interval_list = [self.inputDiameterDeltaWindow.delta*i for i in range(1,6)]
        betti_0_numbers = []
        betti_1_numbers = []
        for diameter in interval_list:
            ts = TokenSpace(text.tokenize(), angular_distance, diameter)
            betti_0_numbers += [ts.betti_number_0]
            betti_1_numbers += [ts.betti_number_1] 

        frame_left = tk.LabelFrame(root, text="График зависимости 0-ых чисел Бетти от диаметра симплексов")
        frame_right = tk.LabelFrame(root, text="График зависимости 1-ых чисел Бетти от диаметра симплексов")
        frame_bottom = tk.Frame(root)
        frame_left.pack(side=tk.LEFT)
        frame_right.pack(side=tk.RIGHT)
        frame_bottom.pack(side=tk.BOTTOM)

        f_0 = Figure(figsize=(5,5), dpi=100)
        a_0 = f_0.add_subplot(111)
        a_0.plot(interval_list, betti_0_numbers)

        canvas_0 = FigureCanvasTkAgg(f_0, frame_left)
        canvas_0.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar_0 = NavigationToolbar2Tk(canvas_0, frame_left)
        toolbar_0.update()
        canvas_0._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        f_1 = Figure(figsize=(5,5), dpi=100)
        a_1 = f_1.add_subplot(111)
        a_1.plot(interval_list, betti_1_numbers)

        canvas_1 = FigureCanvasTkAgg(f_1, frame_right)
        canvas_1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toolbar_1 = NavigationToolbar2Tk(canvas_1, frame_right)
        toolbar_1.update()
        canvas_1._tkcanvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        self.button_back = tk.Button(frame_bottom, text="Новый анализ", command=self.back)
        self.button_back.pack(side=tk.BOTTOM)
    
    def back(self):
        InputTextWindow("")
        
root = tk.Tk()
root.title("Text Analyzer")
root.resizable(False, False)

InputTextWindow("")

tk.mainloop()