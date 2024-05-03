import tkinter as tk
from tkinter import ttk

def open_main_window(language):
    # Close the language selection dialog
    root.destroy()
    import form_select
    form_select.open_dialogue(language)

# Create the Tkinter Window for language selection
root = tk.Tk()
root.title("Select Language")
root.minsize(1108, 768)  # Adjust the dimensions as needed
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Function to handle button click
def language_selected(language):
    open_main_window(language)

# English Button
english_button = ttk.Button(root, text="English", command=lambda: language_selected("English"), width = 100)
english_button.pack(pady=(100, 50), ipady=50, anchor=tk.CENTER)

# Nederlands Button
nederlands_button = ttk.Button(root, text="Nederlands", command=lambda: language_selected("Nederlands"), width = 100)
nederlands_button.pack(pady=50, ipady=50, anchor=tk.CENTER)

root.mainloop()