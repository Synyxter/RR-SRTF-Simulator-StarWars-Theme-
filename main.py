import customtkinter as ctk
from app.gui.main_view import MainView

def main():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    app = MainView()
    app.mainloop()

if __name__ == "__main__":
    main()
