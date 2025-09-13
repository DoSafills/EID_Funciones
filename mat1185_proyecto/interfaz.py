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

class AnalizadorMatematicoGUI:
    def __init__(self, ventana_principal):
        # Configuracion inicial de la ventana
        self.ventana = ventana_principal
        self._configurar_ventana()
        
        # Estado del analizador
        self.analizador_actual = None
        self.evaluacion_actual = None
        self.esta_procesando = False
        
        # Crear la interfaz
        self._crear_interfaz_completa()
        self._configurar_atajos_teclado()
    
    def _configurar_ventana(self):
        self.ventana.title("Analizador de Funciones Matematicas")
        self.ventana.geometry("1200x700")
        self.ventana.resizable(True, True)
        
        self.ventana.grid_columnconfigure(0, weight=1)
        self.ventana.grid_rowconfigure(0, weight=1)

    def _crear_interfaz_completa(self):
        # Marco principal que contiene todo
        marco_principal = ctk.CTkFrame(self.ventana)
        marco_principal.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Crear todas las secciones
        self._crear_seccion_entrada(marco_principal)
        self._crear_seccion_progreso(marco_principal)
        self._crear_seccion_contenido(marco_principal)
        self._crear_barra_estado(marco_principal)
    
    def _crear_seccion_entrada(self, contenedor):
        # Seccion superior con entrada de funcion y botones
        seccion_entrada = ctk.CTkFrame(contenedor)
        seccion_entrada.pack(fill="x", padx=10, pady=5)
        
        # Campo para ingresar la funcion
        etiqueta_funcion = ctk.CTkLabel(seccion_entrada, text="f(x) =", 
                                       font=ctk.CTkFont(size=14, weight="bold"))
        etiqueta_funcion.pack(side="left", padx=5)
        
        self.entrada_funcion = ctk.CTkEntry(seccion_entrada, placeholder_text="x^2", width=200)
        self.entrada_funcion.pack(side="left", padx=5)
        self.entrada_funcion.insert(0, "x^2")
        
        # Campo para valor de x
        etiqueta_x = ctk.CTkLabel(seccion_entrada, text="x =", 
                                 font=ctk.CTkFont(size=12))
        etiqueta_x.pack(side="left", padx=(15, 5))
        
        self.entrada_x = ctk.CTkEntry(seccion_entrada, width=80, placeholder_text="2")
        self.entrada_x.pack(side="left", padx=5)
        
        # Botones de accion
        self._crear_botones_accion(seccion_entrada)
    
    def _crear_botones_accion(self, contenedor):
        # Botones principales de funcionalidad
        self.boton_analizar = ctk.CTkButton(contenedor, text="Analizar", width=80, 
                                          command=self.procesar_analisis)
        self.boton_analizar.pack(side="left", padx=5)
        
        self.boton_evaluar = ctk.CTkButton(contenedor, text="Evaluar", width=80, 
                                         command=self.procesar_evaluacion)
        self.boton_evaluar.pack(side="left", padx=5)
        
        self.boton_graficar = ctk.CTkButton(contenedor, text="Graficar", width=80, 
                                          command=self.procesar_grafica)
        self.boton_graficar.pack(side="left", padx=5)
        
        self.boton_resolver = ctk.CTkButton(contenedor, text="Resolver", width=80, 
                                          command=self.procesar_resolucion)
        self.boton_resolver.pack(side="left", padx=5)
        
        self.boton_limpiar = ctk.CTkButton(contenedor, text="Limpiar", width=80, 
                                         command=self.limpiar_todo)
        self.boton_limpiar.pack(side="right", padx=5)
    
    def _crear_seccion_progreso(self, contenedor):
        # Barra de progreso que aparece cuando se procesa algo
        self.marco_progreso = ctk.CTkFrame(contenedor)
        
        self.etiqueta_progreso = ctk.CTkLabel(self.marco_progreso, text="")
        self.etiqueta_progreso.pack(side="left", padx=10)
        
        self.barra_progreso = ctk.CTkProgressBar(self.marco_progreso, width=300)
        self.barra_progreso.pack(side="left", padx=10, pady=10)
        self.barra_progreso.set(0)
        
        # Inicialmente oculta
        self.marco_progreso.pack_forget()
    
    def _crear_seccion_contenido(self, contenedor):
        # Area principal dividida en dos columnas
        marco_contenido = ctk.CTkFrame(contenedor)
        marco_contenido.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Columna izquierda: Analisis y resolucion
        self._crear_columna_texto(marco_contenido)
        
        # Columna derecha: Grafica
        self._crear_columna_grafica(marco_contenido)
    
    def _crear_columna_texto(self, contenedor):
        columna_izquierda = ctk.CTkFrame(contenedor)
        columna_izquierda.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Seccion de analisis
        titulo_analisis = ctk.CTkLabel(columna_izquierda, text="Analisis", 
                                      font=ctk.CTkFont(size=12, weight="bold"))
        titulo_analisis.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.area_analisis = scrolledtext.ScrolledText(columna_izquierda, height=12, 
                                                      bg="#1a1a1a", fg="#ffffff", 
                                                      font=("Consolas", 9), wrap=tk.WORD)
        self.area_analisis.pack(fill="both", expand=True, padx=10, pady=(0, 5))
        
        # Seccion de resolucion paso a paso
        titulo_resolucion = ctk.CTkLabel(columna_izquierda, text="Resolucion Paso a Paso", 
                                        font=ctk.CTkFont(size=12, weight="bold"))
        titulo_resolucion.pack(anchor="w", padx=10, pady=(5, 5))
        
        self.area_resolucion = scrolledtext.ScrolledText(columna_izquierda, height=8, 
                                                        bg="#1a1a1a", fg="#ffffff",
                                                        font=("Consolas", 9), wrap=tk.WORD)
        self.area_resolucion.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def _crear_columna_grafica(self, contenedor):
        columna_derecha = ctk.CTkFrame(contenedor)
        columna_derecha.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Encabezado de la grafica con controles
        self._crear_controles_grafica(columna_derecha)
        
        # Area de la grafica
        self._crear_area_grafica(columna_derecha)
    
    def _crear_controles_grafica(self, contenedor):
        encabezado_grafica = ctk.CTkFrame(contenedor)
        encabezado_grafica.pack(fill="x", padx=10, pady=(10, 5))
        
        titulo_grafica = ctk.CTkLabel(encabezado_grafica, text="Grafica", 
                                     font=ctk.CTkFont(size=12, weight="bold"))
        titulo_grafica.pack(side="left", padx=5)
        
        # Controles para el rango de x
        etiqueta_rango = ctk.CTkLabel(encabezado_grafica, text="X:", 
                                     font=ctk.CTkFont(size=10))
        etiqueta_rango.pack(side="left", padx=(10, 2))
        
        self.entrada_x_min = ctk.CTkEntry(encabezado_grafica, width=40, height=20)
        self.entrada_x_min.pack(side="left", padx=1)
        self.entrada_x_min.insert(0, "-10")
        
        etiqueta_hasta = ctk.CTkLabel(encabezado_grafica, text="a", 
                                     font=ctk.CTkFont(size=10))
        etiqueta_hasta.pack(side="left", padx=2)
        
        self.entrada_x_max = ctk.CTkEntry(encabezado_grafica, width=40, height=20)
        self.entrada_x_max.pack(side="left", padx=1)
        self.entrada_x_max.insert(0, "10")
    
    def _crear_area_grafica(self, contenedor):
        # Configurar matplotlib para el tema oscuro
        self.figura = Figure(figsize=(6, 8), facecolor='#212121', tight_layout=True)
        self.ejes = self.figura.add_subplot(111, facecolor='#2b2b2b')
        self.ejes.tick_params(colors='white', labelsize=8)
        self.ejes.xaxis.label.set_color('white')
        self.ejes.yaxis.label.set_color('white')
        self.ejes.title.set_color('white')
        
        # Canvas para mostrar la grafica
        self.lienzo = FigureCanvasTkAgg(self.figura, master=contenedor)
        self.lienzo.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def _crear_barra_estado(self, contenedor):
        # Barra de estado en la parte inferior
        self.barra_estado = ctk.CTkLabel(contenedor, text="Listo", 
                                        font=ctk.CTkFont(size=10))
        self.barra_estado.pack(side="bottom", padx=10, pady=5)
    
    def _configurar_atajos_teclado(self):
        # Atajos de teclado para mejor experiencia de usuario
        self.entrada_funcion.bind('<Return>', lambda e: self.procesar_analisis())
        self.entrada_x.bind('<Return>', lambda e: self.procesar_evaluacion())

    # =============================================================================
    # GESTION DE PROGRESO Y ESTADOS
    # =============================================================================
    
    def mostrar_progreso(self, mensaje="Procesando..."):
        """Muestra la barra de progreso con un mensaje"""
        self.etiqueta_progreso.configure(text=mensaje)
        self.barra_progreso.set(0)
        self.marco_progreso.pack(fill="x", padx=10, pady=5, before=self.area_analisis.master.master)
        self._desactivar_botones()

    def ocultar_progreso(self):
        """Oculta la barra de progreso"""
        self.marco_progreso.pack_forget()
        self._activar_botones()

    def _desactivar_botones(self):
        """Desactiva todos los botones durante el procesamiento"""
        self.boton_analizar.configure(state="disabled")
        self.boton_evaluar.configure(state="disabled")
        self.boton_graficar.configure(state="disabled")
        self.boton_resolver.configure(state="disabled")

    def _activar_botones(self):
        """Activa todos los botones despues del procesamiento"""
        self.boton_analizar.configure(state="normal")
        self.boton_evaluar.configure(state="normal")
        self.boton_graficar.configure(state="normal")
        self.boton_resolver.configure(state="normal")

    def actualizar_progreso(self, valor):
        """Actualiza el valor de la barra de progreso (0.0 a 1.0)"""
        self.barra_progreso.set(valor)
        
    def cambiar_estado(self, mensaje):
        """Cambia el mensaje de la barra de estado"""
        self.barra_estado.configure(text=mensaje)
    
    # =============================================================================
    # PROCESAMIENTO PRINCIPAL DE FUNCIONES
    # =============================================================================

    def procesar_analisis(self):
        """Analiza la funcion matematica ingresada"""
        if self.esta_procesando:
            return
        
        texto_funcion = self.entrada_funcion.get().strip()
        if not texto_funcion:
            self.cambiar_estado("Error: Ingresa una funcion")
            messagebox.showwarning("Advertencia", "Por favor ingresa una funcion")
            return

        self.esta_procesando = True

        def tarea_analisis():
            try:
                self.ventana.after(0, lambda: self.actualizar_progreso(0.2))
                time.sleep(0.1)
                
                self.analizador_actual = FunctionAnalyzer(texto_funcion)
                self.ventana.after(0, lambda: self.actualizar_progreso(0.5))
                time.sleep(0.1)
                
                resultado = self.analizador_actual.analyze()
                self.ventana.after(0, lambda: self.actualizar_progreso(0.8))
                time.sleep(0.1)
                
                resultado_formateado = self._formatear_resultado_analisis(resultado)
                
                def actualizar_interfaz():
                    self.area_analisis.delete("1.0", "end")
                    self.area_analisis.insert("end", resultado_formateado)
                    self.actualizar_progreso(1.0)
                    self.ventana.after(300, self.ocultar_progreso)
                    self.cambiar_estado("Análisis completado")
                    self.esta_procesando = False
                
                self.ventana.after(0, actualizar_interfaz)
                
            except Exception as e:
                def mostrar_error():
                    self.ocultar_progreso()
                    self.cambiar_estado(f"Error: {str(e)}")
                    messagebox.showerror("Error", f"Error al analizar: {str(e)}")
                    self.esta_procesando = False
                
                self.ventana.after(0, mostrar_error)

        self.mostrar_progreso("Analizando funcion...")
        hilo = threading.Thread(target=tarea_analisis)
        hilo.daemon = True
        hilo.start()

    def procesar_evaluacion(self):
        """Evalua la funcion en un punto especifico"""
        if self.esta_procesando:
            return
        
        if not self.analizador_actual:
            self.cambiar_estado("Error: Primero analiza una funcion")
            messagebox.showwarning("Advertencia", "Primero debes analizar una funcion")
            return
        
        texto_x = self.entrada_x.get().strip()
        if not texto_x:
            self.cambiar_estado("Error: Ingresa un valor de x")
            messagebox.showwarning("Advertencia", "Por favor ingresa un valor de x")
            return

        self.esta_procesando = True

        def tarea_evaluacion():
            try:
                self.ventana.after(0, lambda: self.actualizar_progreso(0.3))
                time.sleep(0.1)
                
                resultado = self.analizador_actual.evaluate_at(texto_x)
                self.evaluacion_actual = resultado
                
                self.ventana.after(0, lambda: self.actualizar_progreso(0.8))
                time.sleep(0.1)
                
                if resultado.get('error'):
                    texto_evaluacion = f"\n{'='*30}\nEVALUACIÓN:\n{resultado['error']}\n"
                else:
                    texto_evaluacion = f"\n{'='*30}\nEVALUACIÓN:\nf({texto_x}) = {resultado['numeric']}\nPar ordenado: {resultado['ordered_pair']}\n"
                
                def actualizar_interfaz():
                    self.area_analisis.insert("end", texto_evaluacion)
                    self.area_analisis.see("end")
                    self.actualizar_progreso(1.0)
                    self.ventana.after(300, self.ocultar_progreso)
                    self.cambiar_estado("Evaluación completada")
                    self.esta_procesando = False
                
                self.ventana.after(0, actualizar_interfaz)
                
            except Exception as e:
                def mostrar_error():
                    self.ocultar_progreso()
                    self.cambiar_estado(f"Error al evaluar: {str(e)}")
                    messagebox.showerror("Error", f"Error al evaluar: {str(e)}")
                    self.esta_procesando = False
                
                self.ventana.after(0, mostrar_error)

        self.mostrar_progreso("Evaluando funcion...")
        hilo = threading.Thread(target=tarea_evaluacion)
        hilo.daemon = True
        hilo.start()

    def procesar_grafica(self):
        """Genera y muestra la grafica de la funcion"""
        if not self.analizador_actual:
            self.cambiar_estado("Error: Primero analiza una funcion")
            messagebox.showwarning("Advertencia", "Primero debes analizar una funcion")
            return

        def tarea_grafica():
            try:
                try:
                    x_minimo = float(self.entrada_x_min.get() or -10)
                    x_maximo = float(self.entrada_x_max.get() or 10)
                    if x_minimo >= x_maximo:
                        x_minimo, x_maximo = -10, 10
                except:
                    x_minimo, x_maximo = -10, 10
                
                self.ventana.after(0, lambda: self.actualizar_progreso(0.2))
                
                funcion_numerica = lambdify(self.analizador_actual.var, self.analizador_actual.expr, modules=["math"])
                
                self.ventana.after(0, lambda: self.actualizar_progreso(0.4))
                time.sleep(0.2)
                
                puntos_total = 200
                valores_x = [x_minimo + i * (x_maximo - x_minimo) / puntos_total for i in range(puntos_total + 1)]
                valores_y = []
                
                for i, x in enumerate(valores_x):
                    try:
                        y = funcion_numerica(x)
                        if abs(y) > 1e6:
                            y = None
                        valores_y.append(y)
                    except:
                        valores_y.append(None)
                    
                    if i % 50 == 0:
                        progreso = 0.4 + (i / len(valores_x)) * 0.4
                        self.ventana.after(0, lambda p=progreso: self.actualizar_progreso(p))

                self.ventana.after(0, lambda: self.actualizar_progreso(0.9))
                
                def actualizar_grafica():
                    self.ejes.clear()
                    self.ejes.set_facecolor('#2b2b2b')
                    
                    datos_validos = [(x, y) for x, y in zip(valores_x, valores_y) if y is not None]
                    if datos_validos:
                        x_validos, y_validos = zip(*datos_validos)
                        self.ejes.plot(x_validos, y_validos, color='#1f77b4', linewidth=2)
                    
                    self.ejes.axhline(0, color="white", alpha=0.5, linewidth=1)
                    self.ejes.axvline(0, color="white", alpha=0.5, linewidth=1)
                    self.ejes.grid(True, alpha=0.3, color='white', linestyle='--')
                    self.ejes.set_xlim(x_minimo, x_maximo)
                    self.ejes.set_xlabel('x', color='white')
                    self.ejes.set_ylabel('f(x)', color='white')
                    self.ejes.set_title(f'f(x) = {self.analizador_actual.expr}', color='white')
                    
                    if self.evaluacion_actual and x_minimo <= float(self.evaluacion_actual['x']) <= x_maximo:
                        x_eval = float(self.evaluacion_actual['x'])
                        y_eval = float(self.evaluacion_actual['numeric'])
                        self.ejes.plot(x_eval, y_eval, 'ro', markersize=6)
                    
                    self.lienzo.draw()
                    self.actualizar_progreso(1.0)
                    self.ventana.after(500, self.ocultar_progreso)
                    self.cambiar_estado("Gráfica completada")
                
                self.ventana.after(0, actualizar_grafica)
                
            except Exception as e:
                def mostrar_error():
                    self.ocultar_progreso()
                    self.cambiar_estado(f"Error al graficar: {str(e)}")
                    messagebox.showerror("Error", f"Error al graficar: {str(e)}")
                
                self.ventana.after(0, mostrar_error)

        self.mostrar_progreso("Generando grafica...")
        hilo = threading.Thread(target=tarea_grafica)
        hilo.daemon = True
        hilo.start()

    def procesar_resolucion(self):
        """Genera la resolucion paso a paso"""
        if not self.analizador_actual:
            self.cambiar_estado("Error: Primero analiza una funcion")
            messagebox.showwarning("Advertencia", "Primero debes analizar una funcion")
            return

        def tarea_resolucion():
            try:
                self.ventana.after(0, lambda: self.actualizar_progreso(0.3))
                time.sleep(0.3)
                
                analisis = self.analizador_actual.analyze()
                
                self.ventana.after(0, lambda: self.actualizar_progreso(0.7))
                time.sleep(0.3)
                
                texto_explicacion = build_explanation(self.analizador_actual, analisis, self.evaluacion_actual)
                
                def actualizar_interfaz():
                    self.area_resolucion.delete("1.0", "end")
                    self.area_resolucion.insert("end", texto_explicacion)
                    self.actualizar_progreso(1.0)
                    self.ventana.after(500, self.ocultar_progreso)
                    self.cambiar_estado("Resolución completada")
                
                self.ventana.after(0, actualizar_interfaz)
                
            except Exception as e:
                def mostrar_error():
                    self.ocultar_progreso()
                    self.cambiar_estado(f"Error en resolucion: {str(e)}")
                    messagebox.showerror("Error", f"Error al resolver paso a paso: {str(e)}")
                
                self.ventana.after(0, mostrar_error)

        self.mostrar_progreso("Generando resolucion...")
        hilo = threading.Thread(target=tarea_resolucion)
        hilo.daemon = True
        hilo.start()
    
    # =============================================================================
    # UTILIDADES Y LIMPIEZA
    # =============================================================================

    def limpiar_todo(self):
        """Limpia toda la interfaz y reinicia el estado"""
        self.area_analisis.delete("1.0", "end")
        self.area_resolucion.delete("1.0", "end")
        self.ejes.clear()
        self.ejes.set_facecolor('#2b2b2b')
        self.lienzo.draw()
        self.analizador_actual = None
        self.evaluacion_actual = None
        self.esta_procesando = False
        self.cambiar_estado("Listo")

    def _formatear_resultado_analisis(self, resultado):
        """Formatea el resultado del analisis para mostrar en la interfaz"""
        lineas = []
        lineas.append("ANALISIS DE LA FUNCION")
        lineas.append("=" * 30)
        lineas.append(f"Expresion: {self.analizador_actual.expr}")
        lineas.append("")
        lineas.append(f"Dominio: {resultado['domain']}")
        lineas.append(f"Rango: {resultado['range']}")
        lineas.append("")
        
        if resultado['x_intercepts']:
            lineas.append("Intersecciones con eje X:")
            for intercepcion in resultado['x_intercepts']:
                lineas.append(f"  x = {intercepcion}")
        else:
            lineas.append("Sin intersecciones con eje X")
        
        if resultado['y_intercept'] is not None:
            lineas.append(f"\nInterseccion con eje Y: f(0) = {resultado['y_intercept']}")
        else:
            lineas.append("\nSin interseccion con eje Y")
        
        return "\n".join(lineas)
