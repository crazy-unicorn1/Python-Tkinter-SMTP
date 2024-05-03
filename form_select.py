import tkinter as tk
from tkinter import ttk
import subprocess

# Create the Tkinter Window for language selection
        
def open_dialogue(language):
    global root
    root = tk.Tk()
    root.title("Select Form")
    root.minsize(1108, 768)  # Adjust the dimensions as needed
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    # Function to handle button click
    def form_selected(form_type):
        if(form_type == 1):
            root.destroy()
            subprocess.run(["python", "form_first.py", language])  # Pass the language as a command-line argument to main.py
        if(form_type == 2):
            root.destroy()
            subprocess.run(["python", "form_second.py", language])  # Pass the language as a command-line argument to main.py

    Assessment_button_txt = "Assessment Form"
    if language != "English":
        Assessment_button_txt = "bezwaarformulier"

    Assessment_button = ttk.Button(root, text=Assessment_button_txt, command=lambda: form_selected(1), width = 100)
    Assessment_button.pack(pady=(100, 10), ipady=20, anchor=tk.CENTER)

    button2 = ttk.Button(root, text="button2", command=lambda: form_selected(2), width = 100)
    button2.pack(pady=10, ipady=20, anchor=tk.CENTER)
    
    button3 = ttk.Button(root, text="button3", command=lambda: form_selected(3), width = 100)
    button3.pack(pady=10, ipady=20, anchor=tk.CENTER)
    button3.config(state="disabled")

    button4 = ttk.Button(root, text="button4", command=lambda: form_selected(4), width = 100)
    button4.pack(pady=10, ipady=20, anchor=tk.CENTER)
    button4.config(state="disabled")

    button5 = ttk.Button(root, text="button5", command=lambda: form_selected(5), width = 100)
    button5.pack(pady=10, ipady=20, anchor=tk.CENTER)
    button5.config(state="disabled")

    root.mainloop()