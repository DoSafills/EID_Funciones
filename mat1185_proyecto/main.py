import customtkinter as ctk
from interfaz import AnalizadorMatematicoGUI

if __name__ == "__main__":
    # Configuracion de la apariencia
    ctk.set_appearance_mode("system") 
    ctk.set_default_color_theme("blue")  
    
    # Crear la ventana principal
    ventana_principal = ctk.CTk()
    
    # Inicializar la aplicacion
    aplicacion = AnalizadorMatematicoGUI(ventana_principal)
    
    # Ejecutar el bucle principal
    ventana_principal.mainloop()
