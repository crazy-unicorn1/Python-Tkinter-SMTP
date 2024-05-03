import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
from datetime import datetime
from PIL import Image
import io
import win32print
import win32api
import os

def attach_file():
    global attachment_content
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")])  # Filter op afbeeldingstypen
    if file_path:
        try:
            # Probeer de afbeelding te openen en te verifiëren
            with Image.open(file_path) as img:
                img.verify()  # Verifieert de structuur van het bestand
            with open(file_path, "rb") as file:
                attachment_content = file.read()
        except (IOError, SyntaxError) as e:
            messagebox.showerror("Fout", f"Dit is geen geldig afbeeldingsbestand: {e}")

def submit_form():
    # Verkrijg de waarden uit de invoervelden
    cribnummer = entries["Cribnummer:"].get()
    id_nummer = entries["ID-Nummer:"].get()
    naam = entries["Naam:"].get()
    oud_adres = entries["Oud Adres:"].get()
    nieuw_adres = entries["Nieuw Adres:"].get()
    datum = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # Maak de databaseverbinding
    connection = sqlite3.connect("adreswijzigingen.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS openstaand (
            cribnummer TEXT,
            id_nummer TEXT,
            naam TEXT,
            oud_adres TEXT,
            nieuw_adres TEXT,
            bijlage BLOB,
            datum TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO openstaand (cribnummer, id_nummer, naam, oud_adres, nieuw_adres, bijlage, datum)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (cribnummer, id_nummer, naam, oud_adres, nieuw_adres, attachment_content, datum))
    connection.commit()
    connection.close()

    # Vraag om een geprint exemplaar
    result = messagebox.askquestion("Printaanvraag", "Wilt u een geprint exemplaar van uw verzoek?")
    if result == "yes":
        print_form()
    else:
        clear_form()

def clear_form():
    # Wis alle invoervelden
    for entry in entries.values():
        entry.delete(0, "end")

def print_form():
    # Bepaal het pad naar het PDF-bestand
    script_dir = os.path.dirname(os.path.realpath(__file__))
    pdf_path = os.path.join(script_dir, "adreswijziging_form.pdf")

    # Controleer of het PDF-bestand bestaat
    if os.path.exists(pdf_path):
        try:
            # Afdrukken van het PDF-bestand
            ##########################################################
            #win32api.ShellExecute(0, "print", pdf_path, None, ".", 0)
            ##########################################################
            pass
        except Exception as e:
            messagebox.showerror("Fout", f"Fout bij het afdrukken van het PDF-bestand: {e}")
    else:
        messagebox.showerror("Fout", "Het PDF-bestand 'adreswijziging_form.pdf' bestaat niet.")

# Creëer het hoofdvenster
root = tk.Tk()
root.title("Adreswijzigingsformulier")

# Labels en invoervelden
labels = ["Cribnummer:", "ID-Nummer:", "Naam:", "Oud Adres:", "Nieuw Adres:"]
entries = {}
for i, label_text in enumerate(labels):
    label = ttk.Label(root, text=label_text)
    label.grid(row=i, column=0, padx=5, pady=5, sticky="w")
    entry = ttk.Entry(root)
    entry.grid(row=i, column=1, padx=5, pady=5, sticky="ew")
    entries[label_text] = entry

# Bijlage toevoegen
attach_button = ttk.Button(root, text="Voeg Bijlage Toe", command=attach_file)
attach_button.grid(row=len(labels), column=0, columnspan=2, padx=5, pady=10, sticky="ew")

# Knop voor het indienen van het formulier
submit_button = ttk.Button(root, text="Indienen", command=submit_form)
submit_button.grid(row=len(labels)+1, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

# Geef de datum weer
date_label = ttk.Label(root, text="Datum: " + datetime.now().strftime("%d-%m-%Y"), font=("Helvetica", 10))
date_label.grid(row=len(labels) + 2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

# Start de hoofdloop van de GUI
root.mainloop()
