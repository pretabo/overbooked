import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import time

def update_text_area(text_area, text):
    text_area.config(state='normal')
    text_area.insert(tk.END, text + "\n")
    text_area.see(tk.END)
    text_area.config(state='disabled')
    text_area.update_idletasks()

def log_messages(text_area):
    for i in range(5):
        text_area.after(0, update_text_area, text_area, f"Log {i+1}")
        time.sleep(1)

root = tk.Tk()
text_area = ScrolledText(root, state='disabled')
text_area.pack()

threading.Thread(target=log_messages, args=(text_area,), daemon=True).start()

root.mainloop()
