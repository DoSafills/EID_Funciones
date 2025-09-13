import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sympy import lambdify
import threading
import time

from calculos import FunctionAnalyzer
from resolucion import build_explanation

class AnalyzerGUI:
    def __init__(self, root):
        self.root = root
        root.title("Analizador de Funciones")
        root.geometry("1200x700")
        root.resizable(True, True)
        
        # Configurar el grid principal
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        
        self._build_ui()
        self.current_analyzer = None
        self.current_eval = None
        self.is_processing = False  # Flag para prevenir operaciones concurrentes
        
        # Vincular eventos de teclado
        self._bind_keyboard_events()

    def _build_ui(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header compacto
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        # Entrada de función
        ctk.CTkLabel(header_frame, text="f(x) =", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=5)
        self.fn_entry = ctk.CTkEntry(header_frame, placeholder_text="x^2", width=200)
        self.fn_entry.pack(side="left", padx=5)
        self.fn_entry.insert(0, "x^2")
        
        # Evaluación
        ctk.CTkLabel(header_frame, text="x =", font=ctk.CTkFont(size=12)).pack(side="left", padx=(15, 5))
        self.x_entry = ctk.CTkEntry(header_frame, width=80, placeholder_text="2")
        self.x_entry.pack(side="left", padx=5)
        
        # Botones principales
        self.analyze_btn = ctk.CTkButton(header_frame, text="Analizar", width=80, command=self.on_analyze)
        self.analyze_btn.pack(side="left", padx=5)
        
        self.evaluate_btn = ctk.CTkButton(header_frame, text="Evaluar", width=80, command=self.on_evaluate)
        self.evaluate_btn.pack(side="left", padx=5)
        
        self.plot_btn = ctk.CTkButton(header_frame, text="Graficar", width=80, command=self.on_plot)
        self.plot_btn.pack(side="left", padx=5)
        
        self.resolve_btn = ctk.CTkButton(header_frame, text="Resolver", width=80, command=self.on_resolve)
        self.resolve_btn.pack(side="left", padx=5)
        
        self.clear_btn = ctk.CTkButton(header_frame, text="Limpiar", width=80, command=self.on_clear)
        self.clear_btn.pack(side="right", padx=5)
        
        # Frame para barra de progreso
        self.progress_frame = ctk.CTkFrame(main_frame)
        
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="")
        self.progress_label.pack(side="left", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, width=300)
        self.progress_bar.pack(side="left", padx=10, pady=10)
        self.progress_bar.set(0)
        
        # Inicialmente ocultar la barra de progreso
        self.progress_frame.pack_forget()
        
        # Contenido principal en dos columnas
        self.content_frame = ctk.CTkFrame(main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Columna izquierda - Texto
        left_frame = ctk.CTkFrame(self.content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Análisis
        ctk.CTkLabel(left_frame, text="Análisis", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        self.output = scrolledtext.ScrolledText(left_frame, height=12, bg="#1a1a1a", fg="#ffffff", 
                                              font=("Consolas", 9), wrap=tk.WORD)
        self.output.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        
        # Resolución
        ctk.CTkLabel(left_frame, text="Resolución Paso a Paso", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=10, pady=(5, 5))
        self.expl_output = scrolledtext.ScrolledText(left_frame, height=8, bg="#1a1a1a", fg="#ffffff",
                                                   font=("Consolas", 9), wrap=tk.WORD)
        self.expl_output.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Columna derecha - Gráfica
        right_frame = ctk.CTkFrame(self.content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Header de gráfica con controles
        graph_header = ctk.CTkFrame(right_frame)
        graph_header.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(graph_header, text="Gráfica", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=5)
        
        # Controles de rango
        ctk.CTkLabel(graph_header, text="X:", font=ctk.CTkFont(size=10)).pack(side="left", padx=(10, 2))
        self.x_min_entry = ctk.CTkEntry(graph_header, width=40, height=20)
        self.x_min_entry.pack(side="left", padx=1)
        self.x_min_entry.insert(0, "-10")
        
        ctk.CTkLabel(graph_header, text="a", font=ctk.CTkFont(size=10)).pack(side="left", padx=2)
        
        self.x_max_entry = ctk.CTkEntry(graph_header, width=40, height=20)
        self.x_max_entry.pack(side="left", padx=1)
        self.x_max_entry.insert(0, "10")
        
        # Matplotlib
        self.fig = Figure(figsize=(6, 8), facecolor='#212121', tight_layout=True)
        self.ax = self.fig.add_subplot(111, facecolor='#2b2b2b')
        self.ax.tick_params(colors='white', labelsize=8)
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Status bar minimalista
        self.status_bar = ctk.CTkLabel(main_frame, text="Listo", font=ctk.CTkFont(size=10))
        self.status_bar.pack(side="bottom", padx=10, pady=5)

    def _bind_keyboard_events(self):
        """Vincular eventos de teclado básicos"""
        self.fn_entry.bind('<Return>', lambda e: self.on_analyze())
        self.x_entry.bind('<Return>', lambda e: self.on_evaluate())

    def _show_progress(self, text="Procesando..."):
        """Mostrar barra de progreso con texto"""
        self.progress_label.configure(text=text)
        self.progress_bar.set(0)
        # Mostrar la barra de progreso antes del contenido principal
        self.progress_frame.pack(fill="x", padx=10, pady=5, before=self.content_frame)
        self._disable_buttons()

    def _hide_progress(self):
        """Ocultar barra de progreso"""
        self.progress_frame.pack_forget()
        self._enable_buttons()

    def _disable_buttons(self):
        """Deshabilitar botones durante operación"""
        self.analyze_btn.configure(state="disabled")
        self.evaluate_btn.configure(state="disabled")
        self.plot_btn.configure(state="disabled")
        self.resolve_btn.configure(state="disabled")

    def _enable_buttons(self):
        """Habilitar botones después de operación"""
        self.analyze_btn.configure(state="normal")
        self.evaluate_btn.configure(state="normal")
        self.plot_btn.configure(state="normal")
        self.resolve_btn.configure(state="normal")

    def _animate_progress(self, duration=1.5):
        """Animar barra de progreso de forma simplificada"""
        # Simplificar la animación para evitar conflictos
        self.progress_bar.set(0)
        # No hacer animación automática, dejar que cada operación maneje su progreso

    def on_analyze(self):
        # Prevenir múltiples operaciones concurrentes
        if self.is_processing:
            return
        
        fn_text = self.fn_entry.get().strip()
        if not fn_text:
            self.status_bar.configure(text="Error: Ingresa una función")
            messagebox.showwarning("Advertencia", "Por favor ingresa una función")
            return

        # Validar formato de función ANTES de analizar
        from sympy import sympify, Symbol
        try:
            expr = sympify(fn_text.replace('^', '**'))
            # Verificar que la expresión contenga la variable x
            if not expr.has(Symbol('x')):
                raise ValueError("La expresión debe contener la variable x.")
        except Exception:
            ejemplo = (
                "El formato de ingreso es incorrecto.\n\n"
                "Ejemplo de formato correcto:\n"
                "  x^2 + 3*x - 5\n"
                "  (x^2 + 1)/(x - 2)\n"
                "  log(x) + x^3"
            )
            messagebox.showerror("Formato incorrecto", ejemplo)
            self.status_bar.configure(text="Error: Formato de función incorrecto")
            return

        # Si pasa la validación, ahora sí crea el FunctionAnalyzer y analiza
        self.is_processing = True

        def analyze_task():
            try:
                # Simular pasos de análisis
                self.root.after(0, lambda: self.progress_bar.set(0.2))
                time.sleep(0.1)  # Reducir tiempo de sleep
                
                self.current_analyzer = FunctionAnalyzer(fn_text)
                self.root.after(0, lambda: self.progress_bar.set(0.5))
                time.sleep(0.1)
                
                res = self.current_analyzer.analyze()
                self.root.after(0, lambda: self.progress_bar.set(0.8))
                time.sleep(0.1)
                
                # Formatear resultado
                formatted_result = self._format_analysis_result(res)
                
                def update_ui():
                    self.output.delete("1.0", "end")
                    self.output.insert("end", formatted_result)
                    self.progress_bar.set(1.0)
                    self.root.after(300, self._hide_progress)
                    self.status_bar.configure(text="Análisis completado")
                    self.is_processing = False
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    self._hide_progress()
                    self.status_bar.configure(text=f"Error: {str(e)}")
                    messagebox.showerror("Error", f"Error al analizar: {str(e)}")
                    self.is_processing = False
                
                self.root.after(0, show_error)

        self._show_progress("Analizando función...")
        self._animate_progress(1.0)
        thread = threading.Thread(target=analyze_task)
        thread.daemon = True
        thread.start()

    def on_evaluate(self):
        # Prevenir múltiples operaciones concurrentes
        if self.is_processing:
            return
        
        # Validaciones tempranas antes del threading
        if not self.current_analyzer:
            self.status_bar.configure(text="Error: Primero analiza una función")
            messagebox.showwarning("Advertencia", "Primero debes analizar una función")
            return
        
        x_text = self.x_entry.get().strip()
        if not x_text:
            self.status_bar.configure(text="Error: Ingresa un valor de x")
            messagebox.showwarning("Advertencia", "Por favor ingresa un valor de x")
            return

        self.is_processing = True

        def evaluate_task():
            try:
                self.root.after(0, lambda: self.progress_bar.set(0.3))
                time.sleep(0.1)
                
                res = self.current_analyzer.evaluate_at(x_text)
                self.current_eval = res
                
                self.root.after(0, lambda: self.progress_bar.set(0.8))
                time.sleep(0.1)
                
                # Agregar resultado al final
                if res.get('error'):
                    eval_text = f"\n{'='*30}\nEVALUACIÓN:\n{res['error']}\n"
                else:
                    eval_text = f"\n{'='*30}\nEVALUACIÓN:\nf({x_text}) = {res['numeric']}\nPar ordenado: {res['ordered_pair']}\n"
                
                def update_ui():
                    self.output.insert("end", eval_text)
                    self.output.see("end")
                    self.progress_bar.set(1.0)
                    self.root.after(300, self._hide_progress)
                    self.status_bar.configure(text="Evaluación completada")
                    self.is_processing = False
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    self._hide_progress()
                    self.status_bar.configure(text=f"Error al evaluar: {str(e)}")
                    messagebox.showerror("Error", f"Error al evaluar: {str(e)}")
                    self.is_processing = False
                
                self.root.after(0, show_error)

        self._show_progress("Evaluando función...")
        self._animate_progress(0.5)
        thread = threading.Thread(target=evaluate_task)
        thread.daemon = True
        thread.start()

    def on_plot(self):
        # Validación temprana antes del threading
        if not self.current_analyzer:
            self.status_bar.configure(text="Error: Primero analiza una función")
            messagebox.showwarning("Advertencia", "Primero debes analizar una función")
            return

        def plot_task():
            try:
                # Obtener rango
                try:
                    x_min = float(self.x_min_entry.get() or -10)
                    x_max = float(self.x_max_entry.get() or 10)
                    if x_min >= x_max:
                        x_min, x_max = -10, 10
                except:
                    x_min, x_max = -10, 10
                
                self.root.after(0, lambda: self.progress_bar.set(0.2))
                
                f_num = lambdify(self.current_analyzer.var, self.current_analyzer.expr, modules=["math"])
                
                self.root.after(0, lambda: self.progress_bar.set(0.4))
                time.sleep(0.2)
                
                # Generar puntos
                num_points = 200
                xs = [x_min + i * (x_max - x_min) / num_points for i in range(num_points + 1)]
                ys = []
                
                for i, x in enumerate(xs):
                    try:
                        y = f_num(x)
                        if abs(y) > 1e6:
                            y = None
                        ys.append(y)
                    except:
                        ys.append(None)
                    
                    # Actualizar progreso durante cálculo de puntos
                    if i % 50 == 0:
                        progress = 0.4 + (i / len(xs)) * 0.4
                        self.root.after(0, lambda p=progress: self.progress_bar.set(p))

                self.root.after(0, lambda: self.progress_bar.set(0.9))
                
                def update_plot():
                    self.ax.clear()
                    self.ax.set_facecolor('#2b2b2b')
                    
                    # Plotear función
                    valid_data = [(x, y) for x, y in zip(xs, ys) if y is not None]
                    if valid_data:
                        valid_xs, valid_ys = zip(*valid_data)
                        self.ax.plot(valid_xs, valid_ys, color='#1f77b4', linewidth=2)
                    
                    # Configurar gráfica
                    self.ax.axhline(0, color="white", alpha=0.5, linewidth=1)
                    self.ax.axvline(0, color="white", alpha=0.5, linewidth=1)
                    self.ax.grid(True, alpha=0.3, color='white', linestyle='--')
                    self.ax.set_xlim(x_min, x_max)
                    self.ax.set_xlabel('x', color='white')
                    self.ax.set_ylabel('f(x)', color='white')
                    self.ax.set_title(f'f(x) = {self.current_analyzer.expr}', color='white')
                    
                    # Marcar punto evaluado si existe
                    if self.current_eval and x_min <= float(self.current_eval['x']) <= x_max:
                        eval_x = float(self.current_eval['x'])
                        eval_y = float(self.current_eval['numeric'])
                        self.ax.plot(eval_x, eval_y, 'ro', markersize=6)
                    
                    self.canvas.draw()
                    self.progress_bar.set(1.0)
                    self.root.after(500, self._hide_progress)
                    self.status_bar.configure(text="Gráfica completada")
                
                self.root.after(0, update_plot)
                
            except Exception as e:
                def show_error():
                    self._hide_progress()
                    self.status_bar.configure(text=f"Error al graficar: {str(e)}")
                    messagebox.showerror("Error", f"Error al graficar: {str(e)}")
                
                self.root.after(0, show_error)

        self._show_progress("Generando gráfica...")
        self._animate_progress(2.5)
        thread = threading.Thread(target=plot_task)
        thread.daemon = True
        thread.start()

    def on_resolve(self):
        # Validación temprana antes del threading
        if not self.current_analyzer:
            self.status_bar.configure(text="Error: Primero analiza una función")
            messagebox.showwarning("Advertencia", "Primero debes analizar una función")
            return

        def resolve_task():
            try:
                self.root.after(0, lambda: self.progress_bar.set(0.3))
                time.sleep(0.3)
                
                analysis = self.current_analyzer.analyze()
                
                self.root.after(0, lambda: self.progress_bar.set(0.7))
                time.sleep(0.3)
                
                text = build_explanation(self.current_analyzer, analysis, self.current_eval)
                
                def update_ui():
                    self.expl_output.delete("1.0", "end")
                    self.expl_output.insert("end", text)
                    self.progress_bar.set(1.0)
                    self.root.after(500, self._hide_progress)
                    self.status_bar.configure(text="Resolución completada")
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    self._hide_progress()
                    self.status_bar.configure(text=f"Error en resolución: {str(e)}")
                    messagebox.showerror("Error", f"Error al resolver paso a paso: {str(e)}")
                
                self.root.after(0, show_error)

        self._show_progress("Generando resolución...")
        self._animate_progress(1.5)
        thread = threading.Thread(target=resolve_task)
        thread.daemon = True
        thread.start()

    def on_clear(self):
        """Limpiar todos los campos"""
        self.output.delete("1.0", "end")
        self.expl_output.delete("1.0", "end")
        self.ax.clear()
        self.ax.set_facecolor('#2b2b2b')
        self.canvas.draw()
        self.current_analyzer = None
        self.current_eval = None
        self.is_processing = False
        self.status_bar.configure(text="Listo")

    def _format_analysis_result(self, result):
        expr_original = self.fn_entry.get().strip()
        lines = [f"Función ingresada: f(x) = {expr_original}"]
        lines.append("ANÁLISIS DE LA FUNCIÓN")
        lines.append("=" * 30)
        lines.append(f"Expresión: {self.current_analyzer.expr}")
        lines.append("")
        lines.append(f"Dominio: {result.get('domain')}")
        lines.append(f"Rango: {result.get('range')}")
        lines.append("")
        
        if result['x_intercepts']:
            lines.append("Intersecciones con eje X:")
            for intercept in result['x_intercepts']:
                lines.append(f"  x = {intercept}")
        else:
            lines.append("Sin intersecciones con eje X")
        
        if result['y_intercept'] is not None:
            lines.append(f"\nIntersección con eje Y: f(0) = {result['y_intercept']}")
        else:
            lines.append("\nSin intersección con eje Y")
        
        return "\n".join(lines)
