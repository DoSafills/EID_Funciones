import customtkinter as ctk
from interfaz import AnalyzerGUI

if __name__ == "__main__":
    # Configurar el tema de customtkinter
    ctk.set_appearance_mode("system")  # Modes: system (default), light, dark
    ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
    
    root = ctk.CTk()
    app = AnalyzerGUI(root)
    root.mainloop()
