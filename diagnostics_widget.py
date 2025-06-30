import os
import time
import threading
import requests
from customtkinter import CTk, CTkLabel
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw

class DiagnosticsWidget:
    def __init__(self):
        self.root = CTk()
        self.root.title("VoidCat Diagnostics")
        self.root.geometry("300x200")
        self.root.attributes("-topmost", True)

        self.status_label = CTkLabel(self.root, text="Status: Unknown", font=("Arial", 14))
        self.status_label.pack(pady=10)

        self.documents_label = CTkLabel(self.root, text="Documents Loaded: 0", font=("Arial", 14))
        self.documents_label.pack(pady=10)

        self.last_query_label = CTkLabel(self.root, text="Last Query: N/A", font=("Arial", 14))
        self.last_query_label.pack(pady=10)

        self.total_queries_label = CTkLabel(self.root, text="Total Queries: 0", font=("Arial", 14))
        self.total_queries_label.pack(pady=10)

        self.polling_thread = threading.Thread(target=self.poll_diagnostics, daemon=True)
        self.polling_thread.start()

    def poll_diagnostics(self):
        while True:
            try:
                response = requests.get("http://127.0.0.1:8002/diagnostics")
                if response.status_code == 200:
                    data = response.json()
                    self.status_label.configure(text=f"Status: {data['status']}")
                    self.documents_label.configure(text=f"Documents Loaded: {data['documents_loaded']}")
                    self.last_query_label.configure(text=f"Last Query: {data['last_query_timestamp']}")
                    self.total_queries_label.configure(text=f"Total Queries: {data['total_queries_processed']}")
            except Exception as e:
                self.status_label.configure(text="Status: Error")
                self.documents_label.configure(text="Documents Loaded: N/A")
                self.last_query_label.configure(text="Last Query: N/A")
                self.total_queries_label.configure(text="Total Queries: N/A")
            time.sleep(5)

    def run(self):
        self.root.mainloop()

class SystemTray:
    def __init__(self, widget):
        self.widget = widget
        self.icon = Icon("VoidCat Diagnostics", self.create_icon(), menu=self.create_menu())

    def create_icon(self):
        image = Image.new("RGB", (64, 64), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 64, 64), fill="black")
        draw.text((10, 20), "VC", fill="white")
        return image

    def create_menu(self):
        return Menu(
            MenuItem("Show Widget", self.show_widget),
            MenuItem("Exit", self.exit_application)
        )

    def show_widget(self):
        self.widget.root.deiconify()

    def exit_application(self):
        self.widget.root.destroy()
        self.icon.stop()

    def run(self):
        self.icon.run()

if __name__ == "__main__":
    widget = DiagnosticsWidget()
    tray = SystemTray(widget)

    threading.Thread(target=tray.run, daemon=True).start()
    widget.run()
