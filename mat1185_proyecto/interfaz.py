import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sympy import lambdify
import math, traceback

from calculos import FunctionAnalyzer
from resolucion import build_explanation

class AnalyzerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Analizador de Funciones - MAT1185")
        self._build_ui()
        self.current_analyzer = None
        self.current_eval = None

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(column=0, row=0, sticky="nsew")

        ttk.Label(frm, text="Función f(x):").grid(column=0, row=0, sticky="w")
        self.fn_entry = ttk.Entry(frm, width=40)
        self.fn_entry.grid(column=1, row=0, columnspan=2)
        self.fn_entry.insert(0, "x^2")

        ttk.Label(frm, text="Evaluar en x:").grid(column=0, row=1, sticky="w")
        self.x_entry = ttk.Entry(frm, width=20)
        self.x_entry.grid(column=1, row=1, sticky="w")

        ttk.Button(frm, text="Analizar", command=self.on_analyze).grid(column=2, row=1)
        ttk.Button(frm, text="Evaluar", command=self.on_evaluate).grid(column=3, row=1)
        ttk.Button(frm, text="Graficar", command=self.on_plot).grid(column=2, row=2)
        ttk.Button(frm, text="Resolver paso a paso", command=self.on_resolve).grid(column=3, row=2)
        ttk.Button(frm, text="Limpiar salida", command=self.on_clear).grid(column=2, row=3)

        self.output = scrolledtext.ScrolledText(frm, width=80, height=10)
        self.output.grid(column=0, row=4, columnspan=4)

        self.expl_output = scrolledtext.ScrolledText(frm, width=80, height=10)
        self.expl_output.grid(column=0, row=5, columnspan=4)

        self.fig = Figure(figsize=(5,4))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=frm)
        self.canvas.get_tk_widget().grid(column=4, row=0, rowspan=6)

    def on_analyze(self):
        fn_text = self.fn_entry.get().strip()
        self.current_analyzer = FunctionAnalyzer(fn_text)
        res = self.current_analyzer.analyze()
        self.output.insert("end", str(res)+"\n")

    def on_evaluate(self):
        if not self.current_analyzer: return
        x_text = self.x_entry.get().strip()
        res = self.current_analyzer.evaluate_at(x_text)
        self.current_eval = res
        self.output.insert("end", str(res)+"\n")

    def on_resolve(self):
        if not self.current_analyzer: return
        analysis = self.current_analyzer.analyze()
        text = build_explanation(self.current_analyzer, analysis, self.current_eval)
        self.expl_output.delete("1.0", "end")
        self.expl_output.insert("end", text)

    def on_plot(self):
        if not self.current_analyzer: return
        analysis = self.current_analyzer.analyze()
        f_num = lambdify(self.current_analyzer.var, self.current_analyzer.expr, modules=["math"])
        xs = [i/2 for i in range(-20, 21)]
        ys = [f_num(x) for x in xs]

        self.ax.clear()
        self.ax.plot(xs, ys, label=str(self.current_analyzer.expr))
        self.ax.axhline(0, color="black")  # eje X
        self.ax.axvline(0, color="black")  # eje Y
        self.ax.legend()
        self.canvas.draw()

    def on_clear(self):
        self.output.delete("1.0", "end")
        self.expl_output.delete("1.0", "end")
        self.ax.clear()
        self.canvas.draw()
