import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import subprocess
import re
import sqlite3
import base64
import io
import win32print
import win32api
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas

# Global variables
attachment_path = ""
attachment_paths = []
aanslagnummer = ""
language_flag = 0
form_id = 0

if len(sys.argv) != 2:
    sys.exit(1)

language_param = sys.argv[1]
if(language_param != "English"):
    language_flag = 1

def update_checkboxes(index):
    for i, var in enumerate(checkbox_vars):
        if i != index:
            var.set(0)

def clear_grid(row_index, col_index):
    for child in content_frame.winfo_children():
        grid_info = child.grid_info()
        if grid_info and grid_info['row'] == row_index:
            if col_index == -1 or grid_info.get('column') == col_index:
                child.grid_remove()

def clear_all_field():
    voornaam_entry.delete(0, tk.END)
    achternaam_entry.delete(0, tk.END)
    emailadres_entry.delete(0, tk.END)
    adres_entry.delete(0, tk.END)
    cribnummer_entry.delete(0, tk.END)
    aanslagnummer_entry.delete(0, tk.END)
    dagtekening_entry.delete(0, tk.END)
    telefoonnummer_entry.delete(0, tk.END)
    bezwaar = text_bezwaar.delete("1.0", "end-1c")

    # Place entry fields and labels
    labels = [ttk.Label(content_frame, text=text, style="FieldLabel.TLabel") for text in labels_texts]  # Voeg deze regel toe
    for i, label in enumerate(labels):
        clear_grid(8 + i, 1)
        entries[label.cget("text")].grid(row=8 + i, column=1, padx=30, pady=5, sticky="w")

    update_checkboxes(-1)
    
    global attachment_paths
    remove_list = []
    for path in attachment_paths:
        remove_list.append(path)
    for path in remove_list:
        remove_attachment(path)

    update_form_id()

def create_submit_update_button(cnt):
    style = ttk.Style()
    style.configure("Custom.TButton", font=("Helvetica", 14))

    submit_button_txt = "Submit"
    if(language_flag):
        submit_button_txt = "Verstuur uw bezwaar"
    submit_button = ttk.Button(content_frame, text=submit_button_txt, command=submit_form, style="Custom.TButton", width=56)
    submit_button.grid(row=20 + cnt, column=0, columnspan=2, padx=(30, 30), pady=(10, 10), sticky="w")

def attach_file():
    global attachment_path, attachment_paths

    cnt = 0
    for path in attachment_paths:
        cnt += 1

    file_paths = filedialog.askopenfilenames()
    if file_paths:
        clear_grid(18, 1)
        for i in range(cnt + 3):
            clear_grid(19 + i, -1)
        
        attachment_paths.extend(file_paths)
        update_attachment_label()

def remove_attachment(path):
    global attachment_paths

    if(attachment_paths.count(path) > 0):
        attachment_paths.pop(attachment_paths.index(path))

    cnt = 0
    for path in attachment_paths:
        cnt += 1
    clear_grid(18, 1)
    for i in range(cnt + 3):
        clear_grid(19 + i, -1)

    update_attachment_label()

def update_attachment_label():
    cnt = 0
    if attachment_paths:
        for path in attachment_paths:
            filename = os.path.basename(path)

            attachment_frame = ttk.Frame(content_frame, style = "Custom.TFrame")
            attachment_frame.grid(row=18 + cnt, column=1, padx=30, pady=5, sticky="w")

            attachment_files = ttk.Label(attachment_frame, text=filename, style="FieldLabel.TLabel")
            attachment_files.pack(side=tk.LEFT)  # Pack the label to the left within the frame

            remove_button_txt = "Remove"
            if(language_flag):
                remove_button_txt = "Verwijder Bijlage"
            remove_button = ttk.Button(attachment_frame, text=remove_button_txt, command=lambda path=path: remove_attachment(path))
            remove_button.pack(side=tk.LEFT, padx=(10, 0)) 

            cnt += 1
        cnt -= 1
    else:
        attachment_files_txt = "No"
        if(language_flag):
            attachment_files_txt = "Geen"
        attachment_files = ttk.Label(content_frame, text=attachment_files_txt, foreground="white", background="#154273", font=("Helvetica", 12))
        attachment_files.grid(row=18, column=1, padx=(30, 30), pady=(5, 5), sticky="w")
    create_submit_update_button(cnt)

def validate_aanslagnummer(new_text):
    if not new_text:
        return True
    if new_text.isdigit() and len(new_text) <= 12:
        return True
    else:
        return False

def validate_telefoonnummer(new_text):
    if not new_text:
        return True

    formatted_var = ''
    if new_text[0] == '+':
        formatted_var = '+' + re.sub(r'\D', '', new_text)
    else: 
        formatted_var = re.sub(r'\D', '', new_text)

    telefoonnummer_var.set(formatted_var)
    telefoonnummer_entry.icursor(len(formatted_var))
    return True

def validate_dagtekening(new_text):
    if not new_text:
        return True

    cleaned_value = re.sub(r'\D', '', new_text)
    
    if len(cleaned_value) > 8:
        return False
    
    # Limit input to 8 characters (DDMMYYYY)
    cleaned_value = cleaned_value[:8]
    formatted_var = ''
    # Add a slash after the second and fourth digits (DD-MM-YYYY)
    if len(cleaned_value) < 3:
        formatted_var = cleaned_value
    if len(cleaned_value) > 2 and len(cleaned_value) < 5:
        formatted_var = re.sub(r'^(\d{2})(.*)$', r'\1-\2', cleaned_value)
    if len(cleaned_value) > 4:
        formatted_var = re.sub(r'^(\d{2})(\d{2})(.*)$', r'\1-\2-\3', cleaned_value)

    dagtekening_var.set(formatted_var)
    cursor_pos = len(formatted_var)
    dagtekening_entry.icursor(cursor_pos)

    return True

def validate_cribnummer(new_text):
    if not new_text:
        return True
    if new_text.isdigit() and len(new_text) <= 9:
        return True
    else:
        return False

def check_date(str):
    length = len(str)
    if length != 10:
        return False
    if str[2] != '-' or str[5] != '-':
        return False
    for i in range(length):
        if i == 2 or i == 5:
            continue
        if(not str[i].isdigit()):
            return False
    return True
 
def check_contact_number(str):
    length = len(str)
    if length == 0:
        return False
    for i in range(length):
        if not str[i].isdigit():
            if i > 0:
                return False
            if str[i] != '+':
                return False
            if length < 2:
                return False
    return True

def show_popup_error(error_message):
    # Create a top-level window for the pop-up
    popup_window = tk.Toplevel(root)
    popup_window.title("Error Message")
    popup_window.minsize(320, 100)

    # Create a Label to display the error message
    error_label = tk.Label(popup_window, text=error_message, foreground="red", font=("Helvetica", 12, "bold"))
    error_label.pack(padx=20, pady=10)

    # Function to handle "Accept" button click
    def accept_action():
        popup_window.destroy()

    # Create "Accept" button
    accept_button_txt = "Accept"
    if(language_flag):
        accept_button_txt = "Aanpassen"
    accept_button = tk.Button(popup_window, text=accept_button_txt, command=accept_action)
    accept_button.pack(padx=10, pady=10, anchor=tk.CENTER)

# def show_popup_print():
#     # Create a top-level window for the pop-up
#     popup_window = tk.Toplevel(root)
#     popup_window.title("Print")

#     first_name = last_name = email = contact_number = adres = cribnummer = ""
#     dagtekening = bezwaar = aanslagnummer = year = ""

#     if(language_flag):
#         first_name = entries["Voornaam:"].get()
#         last_name = entries["Achternaam:"].get()
#         email = entries["Emailadres:"].get()
#         contact_number = entries["Telefoonnummer:"].get()
#         adres = entries["Adres:"].get()
#         cribnummer = entries["Cribnummer:"].get()
#         dagtekening = entries["Dagtekening aanslag:"].get()
#         bezwaar = text_bezwaar.get("1.0", "end-1c")
#         aanslagnummer = aanslagnummer_entry.get()
#         year = jaar_var.get()
#     else:
#         first_name = entries["First name:"].get()
#         last_name = entries["Last name:"].get()
#         email = entries["Email address:"].get()
#         contact_number = entries["Phone number:"].get()
#         adres = entries["Address:"].get()
#         cribnummer = entries["Crib number:"].get()
#         dagtekening = entries["Assessment date:"].get()
#         bezwaar = text_bezwaar.get("1.0", "end-1c")
#         aanslagnummer = aanslagnummer_entry.get()
#         year = jaar_var.get()

#     # Create a Label to display the mail content
#     pdf_content = ""
#     pdf_content += "Voornaam: " + first_name + "\n"
#     pdf_content += "Achternaam: " + email + "\n"
#     pdf_content += "Telefoonnummer: " + contact_number + "\n"
#     pdf_content += "Adres: " + adres + "\n"
#     pdf_content += "Cribnummer: " + cribnummer + "\n"
#     pdf_content += "Wachtwoord: " + bezwaar + "\n"
#     pdf_content += "Aanslagnummer: " + aanslagnummer + "\n"
#     pdf_content += "Dagtekening aanslag: " + dagtekening + "\n"
#     pdf_content += "Jaar: " + year + "\n"
#     pdf_content += "Bijlage: "

#     count_attached_files = 0
#     for file_path in attachment_paths:
#         file_name = os.path.basename(file_path)  # Get the file name from the path
#         if count_attached_files > 0:
#             pdf_content += ", "
#         pdf_content += file_name
#         count_attached_files += 1
#     if(count_attached_files == 0):
#         pdf_content += "Geen"

#     # print_label = tk.Label(popup_window, text=pdf_content, foreground="blue", font=("Helvetica", 12, "bold"))
#     # print_label.pack(padx=20, pady=(20, 10), anchor="nw")
#     print_label = tk.Label(popup_window, text=pdf_content, foreground="black", font=("Helvetica", 12, "bold"), anchor="w", justify="left")
#     print_label.pack(padx=20, pady=(20, 10), anchor="nw")

#     def ok_action():
#         popup_window.destroy()
#         clear_all_field()

#     # Create "Accept" button
#     ok_button_txt = tk.Button(popup_window, text="OK", command=ok_action, width=20)
#     ok_button_txt.pack(padx=10, pady=10, anchor=tk.CENTER)

def create_pdf():
    first_name = last_name = email = contact_number = adres = cribnummer = ""
    dagtekening = bezwaar = aanslagnummer = year = ""

    if(language_flag):
        first_name = entries["Voornaam:"].get()
        last_name = entries["Achternaam:"].get()
        email = entries["Emailadres:"].get()
        contact_number = entries["Telefoonnummer:"].get()
        adres = entries["Adres:"].get()
        cribnummer = entries["Cribnummer:"].get()
        dagtekening = entries["Dagtekening aanslag:"].get()
        bezwaar = text_bezwaar.get("1.0", "end-1c")
        aanslagnummer = aanslagnummer_entry.get()
        year = jaar_var.get()
    else:
        first_name = entries["First name:"].get()
        last_name = entries["Last name:"].get()
        email = entries["Email address:"].get()
        contact_number = entries["Phone number:"].get()
        adres = entries["Address:"].get()
        cribnummer = entries["Crib number:"].get()
        dagtekening = entries["Assessment date:"].get()
        bezwaar = text_bezwaar.get("1.0", "end-1c")
        aanslagnummer = aanslagnummer_entry.get()
        year = jaar_var.get()

    # Create a Label to display the mail content
    pdf_content = ""
    pdf_content += "Voornaam: " + first_name + "\n"
    pdf_content += "Achternaam: " + last_name + "\n"
    pdf_content += "E-mail: " + email + "\n"
    pdf_content += "Telefoonnummer: " + contact_number + "\n"
    pdf_content += "Adres: " + adres + "\n"
    pdf_content += "Cribnummer: " + cribnummer + "\n"
    pdf_content += "Wachtwoord: " + bezwaar + "\n"
    pdf_content += "Aanslagnummer: " + aanslagnummer + "\n"
    pdf_content += "Dagtekening aanslag: " + dagtekening + "\n"
    pdf_content += "Jaar: " + year + "\n"
    pdf_content += "Bijlage: "

    count_attached_files = 0
    for file_path in attachment_paths:
        count_attached_files += 1
    pdf_content += f"{count_attached_files}\n"

    for file_path in attachment_paths:
        file_name = os.path.basename(file_path)  # Get the file name from the path
        pdf_content += "             " + file_name + "\n"
    
    # Define the path to save the PDF file
    pdf_path = "bezwaarformulieren.pdf"

    # Create a canvas (PDF object) with letter size (8.5x11 inches)
    pdf_canvas = Canvas(pdf_path, pagesize=letter)

    # Set font and font size
    pdf_canvas.setFont("Helvetica", 12)

    lines = pdf_content.split("\n")
    # Set the starting y-coordinate for the text
    y_position = 700
    # Loop through each line and draw it on the PDF canvas
    for line in lines:
        pdf_canvas.drawString(100, y_position, line)
        y_position -= 15  # Adjust the y-coordinate for the next line

    # Save the PDF file
    pdf_canvas.save()

def print_form():
    create_pdf()

    # Bepaal het pad naar het PDF-bestand
    script_dir = os.path.dirname(os.path.realpath(__file__))
    pdf_path = os.path.join(script_dir, "bezwaarformulieren.pdf")

    print(pdf_path)

    # Controleer of het PDF-bestand bestaat
    if os.path.exists(pdf_path):
        try:
            # Afdrukken van het PDF-bestand
            win32api.ShellExecute(0, "print", pdf_path, None, ".", 0)
        except Exception as e:
            messagebox.showerror("Fout", f"Fout bij het afdrukken van het PDF-bestand: {e}")
    else:
        messagebox.showerror("Fout", "Het PDF-bestand 'bezwaarformulieren.pdf' bestaat niet.")

def show_popup_success():
    # Create a top-level window for the pop-up
    popup_window = tk.Toplevel(root)
    popup_window.title("Success")

    # Create a Label to display the error message
    success_label_txt = "Your objection has been sent successfully, \n You will immediately receive a copy at the email address you provided."
    if(language_flag):
        success_label_txt = "Uw bezwaar is succesvol verzonden, \n u ontvangt per direct een kopie op het door u opgegeven emailadres."
    success_label = tk.Label(popup_window, text=success_label_txt, foreground="blue", font=("Helvetica", 12, "bold"))
    success_label.pack(padx=20, pady=(20, 10))

    # Create a Label to display the error message
    pdf_content = "Do you want to make a copy of it in pdf?"
    if(language_flag):
        pdf_content = "Wilt u een geprint exemplaar van uw verzoek?"
    print_label = tk.Label(popup_window, text=pdf_content, foreground="#F38064", font=("Helvetica", 12, "bold"))
    print_label.pack(padx=20, pady=(7, 10))

    def ok_action():
        popup_window.destroy()
        print_form()
        clear_all_field()
        # show_popup_print()
    def no_action():
        popup_window.destroy()
        clear_all_field()

    # Create "OK/NO" button
    no_button = tk.Button(popup_window, text="NO", command=no_action, width=15)
    no_button.pack(padx=10, pady=10, side=tk.RIGHT)

    ok_button = tk.Button(popup_window, text="OK", command=ok_action, width=15)
    ok_button.pack(padx=10, pady=10, side=tk.RIGHT)

def update_form_id():
    global form_id
    form_id += 1
    clear_grid(1, 1)
    id_label = ttk.Label(content_frame, text="ID: " + str(form_id), foreground="white", background="#154273", font=("Helvetica", 14, "bold"))
    id_label.grid(row=1, column=1, columnspan=2, padx=(250, 0), pady=(10, 0), sticky="ew")

def submit_form():
    global attachment_paths, aanslagnummer
    # Retrieve values from the form using the entries dictionary
    
    first_name = last_name = email = contact_number = adres = cribnummer = ""
    dagtekening = bezwaar = aanslagnummer = year = ""

    if(language_flag):
        first_name = entries["Voornaam:"].get()
        last_name = entries["Achternaam:"].get()
        email = entries["Emailadres:"].get()
        contact_number = entries["Telefoonnummer:"].get()
        adres = entries["Adres:"].get()
        cribnummer = entries["Cribnummer:"].get()
        dagtekening = entries["Dagtekening aanslag:"].get()
    else:
        first_name = entries["First name:"].get()
        last_name = entries["Last name:"].get()
        email = entries["Email address:"].get()
        contact_number = entries["Phone number:"].get()
        adres = entries["Address:"].get()
        cribnummer = entries["Crib number:"].get()
        dagtekening = entries["Assessment date:"].get()
    bezwaar = text_bezwaar.get("1.0", "end-1c")
    aanslagnummer = aanslagnummer_entry.get()
    year = jaar_var.get()
    current_datetime = datetime.now()
    current_date_string = current_datetime.strftime("%Y-%m-%d")

    checkbox_selected_name = ""
    checkbox_names_dutch = ["Inkomstenbelasting", "Kansspelbelasting", "Loonbelasting", "Opbrengstbelasting", "Overdrachtsbelasting", "Vastgoedbelasting", "Winstbelasting", "Algemene bestedingsbelasting"]
    for index, var in enumerate(checkbox_vars):
        if var.get() == 1:
            checkbox_selected_name = checkbox_names_dutch[index]
            break

    error_field = ""

    if(language_flag == 0):
        if len(first_name) < 3:
            error_field += "First name must contain at least 3 letters\n"
        if len(last_name) < 3:
            error_field += "Last name must contain at least 3 letters\n"
        if len(adres) < 3:
            error_field += "Address name must contain at least 3 letters\n"
        if (not cribnummer.isdigit()) or len(cribnummer) != 9:        
            error_field += "Crib number must contain 9 numbers\n"
        if (not aanslagnummer.isdigit()) or len(aanslagnummer) != 12:        
            error_field += "Assessment number must contain 12 numbers\n"
        if not check_date(dagtekening):
            error_field += "Date format is incorrect - MM/DD/YYYY\n"
        if not check_contact_number(contact_number):
            error_field += "Phone number is incorrect, it must contain only numbers and one '+'\n"
        if len(email) == 0:
            error_field += "Email address is incorrect\n"
    else:
        if len(first_name) < 3:
            error_field += "De voornaam moet minimaal 3 letters bevatten\n"
        if len(last_name) < 3:
            error_field += "De achternaam moet minimaal 3 letters bevatten\n"
        if len(adres) < 3:
            error_field += "Adres moet minimaal 3 letters bevatten\n"
        if (not cribnummer.isdigit()) or len(cribnummer) != 9:        
            error_field += "Cribnummer moet uit 9 cijfers bestaan\n"
        if (not aanslagnummer.isdigit()) or len(aanslagnummer) != 12:        
            error_field += "Aanslagnummer moet 12 cijfers bevatten\n"
        if not check_date(dagtekening):
            error_field += "Dagtekening is onjuist - MM/DD/YYYY\n"
        if not check_contact_number(contact_number):
            error_field += "Telefoonnummer is onjuist, het mag alleen cijfers bevatten en één '+'\n"
        if len(email) == 0:
            error_field += "Emailadres is onjuist\n"

    # Determine selected receiver based on checkbox
    selected_receiver = None
    for index, var in enumerate(checkbox_vars):
        if var.get() == 1:
            selected_receiver = receivers[index]
            break

    if selected_receiver is None:
        if(language_flag == 0):
            error_field += "Receiver is not selected"
        else:
            error_field += "Ontvanger is niet geselecteerd"
    
    if len(error_field) > 0:
        show_popup_error(error_field)
        return 
    
    # Build arguments for subprocess
    args = ["python", "verzenden.py", first_name, last_name, email, contact_number, adres, cribnummer, bezwaar, aanslagnummer, dagtekening, year, selected_receiver]
    for path in attachment_paths:
        args.append(path)

    subprocess.run(args, check=True)
    
    # Update database
    connection = sqlite3.connect("bezwaarformulieren")
    current_year = datetime.now().strftime("%Y") # Get the name of the table
    cursor = connection.cursor()

    # Read files and encode to Base64
    global form_id

    cursor.execute(f"""
        INSERT INTO _{current_year} (Form_id, Checkbox_name, Jaar, Voornaam, Achternaam, Emailadres, Telefoonnummer, Adres, Cribnummer, Aanslagnummer, Dagtekening_aanslag, bezwaar_motivering, Datum)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (form_id, checkbox_selected_name, year, first_name, last_name, email, contact_number, adres, cribnummer, aanslagnummer, dagtekening, bezwaar, current_date_string))

    count_attached_files = 0
    for file_path in attachment_paths:
        count_attached_files += 1
        with open(file_path, "rb") as file:
            file_name = os.path.basename(file_path)  # Get the file name from the path
            encoded_data = base64.b64encode(file.read()).decode("utf-8")
            cursor.execute(f"""
                UPDATE _{current_year}
                SET File_name{count_attached_files} = ?, File_data{count_attached_files} = ?
                WHERE Form_id = ?
            """, (file_name, encoded_data, form_id))
    connection.commit()
    connection.close()

    show_popup_success()

# Create the Tkinter Window
root = tk.Tk()

# Set title
title_txt = "Tax authorities digital Objection form"
if(language_flag):
    title_txt = "Belastingdienst digitaal Bezwaarformulier"
root.title(title_txt)

# Set minimum window size
root.minsize(1108, 768)  # Adjust the dimensions as needed

# Create a frame with the custom style
style = ttk.Style()
style.configure("Custom.TFrame", background="#154273")

frame = ttk.Frame(root)
frame.grid(row=0, column=0, sticky="nsew")

# Create a Canvas and Scrollbar
canvas = tk.Canvas(frame)
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

# Create a Frame for Scrollable Content
content_frame = ttk.Frame(canvas, style="Custom.TFrame")

# Configure the Canvas and Scrollable Content Frame
content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Load logo
logo_image = tk.PhotoImage(file="logo.png")
logo_label = tk.Label(content_frame, image=logo_image, bg="#154273")
logo_label.grid(row=0, column=0, columnspan=2, sticky="ew")

# Labels and date
title_label = ttk.Label(content_frame, text="Bezwaarformulier / Objection form", foreground="white", background="#154273", font=("Helvetica", 16, "bold"))
title_label.grid(row=1, column=0, columnspan=2, padx=(30, 0), pady=(10, 0), sticky="ew")

# Get ID
current_year = datetime.now().strftime("%Y") # Get the name of the table
connection = sqlite3.connect("bezwaarformulieren")
cursor = connection.cursor()
cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS _{current_year} (
        Form_id INTEGER,
        Checkbox_name TEXT,
        Jaar INTEGER,
        Voornaam TEXT,
        Achternaam TEXT,
        Emailadres TEXT,
        Telefoonnummer TEXT,
        Adres TEXT,
        Cribnummer TEXT,
        Aanslagnummer TEXT,
        Dagtekening_aanslag TEXT,
        bezwaar_motivering TEXT,
        Datum TEXT,
        File_name1 TEXT,
        File_data1 TEXT,
        File_name2 TEXT,
        File_data2 TEXT,
        File_name3 TEXT,
        File_data3 TEXT,
        File_name4 TEXT,
        File_data4 TEXT,
        File_name5 TEXT,
        File_data5 TEXT
    )
    """)
cursor.execute(f"SELECT MAX(Form_id) FROM _{current_year}")
max_form_id = cursor.fetchone()[0] 
if max_form_id != None: 
    form_id = max_form_id + 1
else:
    form_id = 1

connection.commit()
connection.close()

# display ID
id_label = ttk.Label(content_frame, text="ID: " + str(form_id), foreground="white", background="#154273", font=("Helvetica", 14, "bold"))
id_label.grid(row=1, column=1, columnspan=2, padx=(250, 0), pady=(10, 0), sticky="ew")

# Labels and date
date_label_txt = "Date: "
if(language_flag):
    date_label_txt = "Datum: "
today_date = datetime.now().strftime("%d-%m-%Y")
date_label = ttk.Label(content_frame, text=date_label_txt + today_date, foreground="white", background="#154273", font=("Helvetica", 12, "bold"))
date_label.grid(row=2, column=0, columnspan=2, padx=(30, 0), pady=(10, 0), sticky="ew")

# Style configuration for checkbox
style = ttk.Style()
style.configure("Custom.TCheckbutton", font=("Helvetica", 11))

# Checkboxes
checkbox_names = ["Income tax", "Gaming tax", "Payroll tax", "Income tax", "Transfer tax", "Real estate tax", "Profit tax", "General expenditure tax"]
if(language_flag):
    checkbox_names = ["Inkomstenbelasting", "Kansspelbelasting", "Loonbelasting", "Opbrengstbelasting", "Overdrachtsbelasting", "Vastgoedbelasting", "Winstbelasting", "Algemene bestedingsbelasting"]
checkbox_vars = []
receivers = ["marcjan.db@hotmail.com", "marcjan.db@hotmail.com", "expert126dev@gmail.com", "receiver4@example.com", "receiver5@example.com", "receiver6@example.com", "receiver7@example.com", "receiver8@gmail.com"]
for i, name in enumerate(checkbox_names):
    var = tk.IntVar(value=1 if i == 2 else 0)
    checkbox_vars.append(var)
    chk = ttk.Checkbutton(content_frame, text=name, variable=var, onvalue=1, offvalue=0, command=lambda i=i: update_checkboxes(i), style='Custom.TCheckbutton')
    chk.grid(row=3 + i//2, column=i%2, padx=30, pady=5, sticky="w")
    
# Style configuration for labels
style = ttk.Style()
style.configure("FieldLabel.TLabel", foreground="white", background="#154273", font=("Helvetica", 12))

# Entry fields and labels
cribnummer_var = tk.StringVar()
cribnummer_var.trace("w", lambda name, index, mode, sv=cribnummer_var: validate_cribnummer(sv.get()))

dagtekening_var = tk.StringVar()
dagtekening_var.trace("w", lambda name, index, mode, sv=dagtekening_var: validate_dagtekening(sv.get()))

telefoonnummer_var = tk.StringVar()
telefoonnummer_var.trace("w", lambda name, index, mode, sv=telefoonnummer_var: validate_telefoonnummer(sv.get()))

aanslagnummer_var = tk.StringVar()
aanslagnummer_var.trace("w", lambda name, index, mode, sv=aanslagnummer_var: validate_aanslagnummer(sv.get()))

labels_texts = ["First name:", "Last name:", "Email address:", "Phone number:", "Address:", "Crib number:", "Assessment number:", "Assessment date:"]
if(language_flag):
    labels_texts = ["Voornaam:", "Achternaam:", "Emailadres:", "Telefoonnummer:", "Adres:", "Cribnummer:", "Aanslagnummer:", "Dagtekening aanslag:"]

entries = {
    "First name:": ttk.Entry(content_frame),
    "Last name:": ttk.Entry(content_frame),
    "Email address:": ttk.Entry(content_frame),
    "Phone number:": ttk.Entry(content_frame, textvariable=telefoonnummer_var, validate="key", validatecommand=(content_frame.register(validate_telefoonnummer), "%P")),
    "Address:": ttk.Entry(content_frame),
    "Crib number:": ttk.Entry(content_frame, textvariable=cribnummer_var, validate="key", validatecommand=(content_frame.register(validate_cribnummer), "%P")),
    "Assessment number:": ttk.Entry(content_frame, textvariable=aanslagnummer_var, validate="key", validatecommand=(content_frame.register(validate_aanslagnummer), "%P")),
    "Assessment date:": ttk.Entry(content_frame, textvariable=dagtekening_var, validate="key", validatecommand=(content_frame.register(validate_dagtekening), "%P"))
}
if(language_flag):
    entries = {
        "Voornaam:": ttk.Entry(content_frame),
        "Achternaam:": ttk.Entry(content_frame),
        "Emailadres:": ttk.Entry(content_frame),
        "Telefoonnummer:": ttk.Entry(content_frame, textvariable=telefoonnummer_var, validate="key", validatecommand=(content_frame.register(validate_telefoonnummer), "%P")),
        "Adres:": ttk.Entry(content_frame),
        "Cribnummer:": ttk.Entry(content_frame, textvariable=cribnummer_var, validate="key", validatecommand=(content_frame.register(validate_cribnummer), "%P")),
        "Aanslagnummer:": ttk.Entry(content_frame, textvariable=aanslagnummer_var, validate="key", validatecommand=(content_frame.register(validate_aanslagnummer), "%P")),
        "Dagtekening aanslag:": ttk.Entry(content_frame, textvariable=dagtekening_var, validate="key", validatecommand=(content_frame.register(validate_dagtekening), "%P"))
    }

# Create entry field for Aanslagnummer
voornaam_entry = achternaam_entry = emailadres_entry = adres_entry = cribnummer_entry = aanslagnummer_entry = dagtekening_entry = telefoonnummer_entry = ttk.Entry(content_frame)
if(language_flag == 0):
    voornaam_entry = entries["First name:"]
    achternaam_entry = entries["Last name:"]
    emailadres_entry = entries["Email address:"]
    adres_entry = entries["Address:"]
    cribnummer_entry = entries["Crib number:"]
    aanslagnummer_entry = entries["Assessment number:"]
    dagtekening_entry = entries["Assessment date:"]
    telefoonnummer_entry = entries["Phone number:"]
else:
    voornaam_entry = entries["Voornaam:"]
    achternaam_entry = entries["Achternaam:"]
    emailadres_entry = entries["Emailadres:"]
    adres_entry = entries["Adres:"]
    cribnummer_entry = entries["Cribnummer:"]
    aanslagnummer_entry = entries["Aanslagnummer:"]
    dagtekening_entry = entries["Dagtekening aanslag:"]
    telefoonnummer_entry = entries["Telefoonnummer:"]

voornaam_entry.insert(0, "John")
achternaam_entry.insert(0, "Roger")
emailadres_entry.insert(0, "john@gmail.com")
adres_entry.insert(0, "aaa bbb 111 ccc")
cribnummer_entry.insert(0, "111111111")
aanslagnummer_entry.insert(0, "111111111111")
dagtekening_entry.insert(0, "11-11-1111")
telefoonnummer_entry.insert(0, "+1111111111")

# Place entry fields and labels
labels = [ttk.Label(content_frame, text=text, style="FieldLabel.TLabel") for text in labels_texts]  # Voeg deze regel toe
for i, label in enumerate(labels):
    label.grid(row=8 + i, column=0, padx=30, pady=5, sticky="w")
    entries[label.cget("text")].grid(row=8 + i, column=1, padx=30, pady=5, sticky="w")

# Text widget for "Uw bezwaar en motivering" met knop voor het toevoegen van bijlage
label_bezwaar_txt = "Your objection and reason:"
if(language_flag):
    label_bezwaar_txt = "Uw bezwaar en motivering:"
label_bezwaar = ttk.Label(content_frame, text=label_bezwaar_txt, style="FieldLabel.TLabel")
label_bezwaar.grid(row=16, column=0, padx=30, pady=5, sticky="w")
text_bezwaar = tk.Text(content_frame, height=4, width=40)
text_bezwaar.grid(row=16, column=1, padx=30, pady=5, sticky="w")

# Knop voor het toevoegen van bijlage
attach_button_txt = "Add the attachment"
if(language_flag):
    attach_button_txt = "Voeg Bijlage Toe"
attach_button = ttk.Button(content_frame, text=attach_button_txt, command=attach_file)
attach_button.grid(row=17, column=1, padx=30, pady=5, sticky="w")

# Label om de geselecteerde bijlage weer te geven
attachment_label_txt = "Selected attachment"
if(language_flag):
    attachment_label_txt = "Geselecteerde bijlage"
attachment_label = ttk.Label(content_frame, text=attachment_label_txt, style="FieldLabel.TLabel")
attachment_label.grid(row=18, column=0, padx=30, pady=5, sticky="w")

attachment_files_txt = "No"
if(language_flag):
    attachment_files_txt = "Geen"
attachment_files = ttk.Label(content_frame, text=attachment_files_txt, foreground="white", background="#154273", font=("Helvetica", 12))
attachment_files.grid(row=18, column=1, padx=(30, 30), pady=(5, 5), sticky="w")

# Dropdown menu for "Over het jaar"
label_jaar_txt = "Over the year:"
if(language_flag):
    label_jaar_txt = "Over het jaar:"
label_jaar = ttk.Label(content_frame, text=label_jaar_txt, style="FieldLabel.TLabel")
label_jaar.grid(row=7, column=0, padx=30, pady=5, sticky="w")
jaartallen = [str(jaar) for jaar in range(2015, 2031)]
jaar_var = tk.StringVar()
jaar_combobox = ttk.Combobox(content_frame, textvariable=jaar_var, values=jaartallen, state="readonly")
jaar_combobox.set(jaartallen[0])
jaar_combobox.grid(row=7, column=1, padx=30, pady=5, sticky="w")

create_submit_update_button(0)
# Create Window Resizing Configuration
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)

content_frame.rowconfigure(0, weight=1)
content_frame.columnconfigure(0, weight=1)
content_frame.columnconfigure(1, weight=8)

# Pack Widgets onto the Window
canvas.create_window((0, 0), window=content_frame, anchor="nw")
canvas.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

# Bind the Canvas to Mousewheel Events
def _on_mousewheel(event):
   canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind_all("<MouseWheel>", _on_mousewheel)

# Run the Tkinter Event Loop
root.mainloop()