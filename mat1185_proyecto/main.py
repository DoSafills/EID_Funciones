import customtkinter as ctk
from interfaz import AnalyzerGUI

if __name__ == "__main__":
    # Config customtkinter
    ctk.set_appearance_mode("system") 
    ctk.set_default_color_theme("blue")  
    root = ctk.CTk()
    app = AnalyzerGUI(root)
    root.mainloop()
