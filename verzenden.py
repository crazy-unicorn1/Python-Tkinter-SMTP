import smtplib 
import ssl 
import os.path 
from email.message import EmailMessage 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage 
from email.mime.base import MIMEBase 
from email import encoders 
import sys 
import config 
 
# Check if enough arguments are passed 
attachment_paths = []
number_of_files = len(sys.argv) - 12

if len(sys.argv) < 12: 
    print("Usage: verzenden.py <first_name> <last_name> <email> <contact_number> <adres> <cribnummer> <password> <aanslagnummer> <dagtekening> <year> <selected_receiver> [attachment_path]") 
    sys.exit(1) 
 
# Get the arguments from the command line 
first_name, last_name, email, contact_number, adres, cribnummer, password, aanslagnummer, dagtekening, year, selected_receiver = sys.argv[1:12] 

# Get attachment_paths
for i in range(number_of_files):
    attachment_paths.append(sys.argv[12 + i])

# Define email sender and receiver 
email_sender = config.email_sender 
email_password = config.email_password
 
# Set the subject of the email 
subject = 'Nieuw bezwaar geregistreerd' 
 
# Create the HTML content for the email 
html_body = f""" 
<!DOCTYPE html> 
<html> 
<head> 
  <title>Bezwaarregistratie</title> 
</head> 
<body> 
  <div style="text-align: center;"> 
    <img src="cid:logo_image" alt="Logo" style="max-width: 500px;"><br> 
    <h1>Nieuw bezwaar geregistreerd</h1> 
    <ul style="text-align: left;padding-left: 50px;font-size: 16px;"> 
      <li>Voornaam: {first_name}</li> 
      <li>Achternaam: {last_name}</li> 
      <li>E-mail: {email}</li> 
      <li>Telefoonnummer: {contact_number}</li> 
      <li>Adres: {adres}</li> 
      <li>Cribnummer: {cribnummer}</li> 
      <li>Wachtwoord: {password}</li> 
      <li>Aanslagnummer: {aanslagnummer}</li> 
      <li>Dagtekening aanslag: {dagtekening}</li> 
      <li>Jaar: {year}</li> 
    </ul> 
  </div> 
</body> 
</html> 
""" 
 
# Create the multipart message 
# selected_receiver = "contractdeveloper0@gmail.com"

msg = MIMEMultipart() 
msg['From'] = email_sender 
msg['To'] = email 
msg['Bcc'] = selected_receiver
msg['Subject'] = subject 

# Attach the HTML content to the email 
msg.attach(MIMEText(html_body, 'html')) 

# Add the logo image as an attachment 
if os.path.exists('logo.png'): 
    with open('logo.png', 'rb') as image_file: 
        image_data = image_file.read() 
        image_part = MIMEImage(image_data, name='logo.png') 
        image_part.add_header('Content-ID', '<logo_image>') 
        msg.attach(image_part) 
 
for attachment_path in attachment_paths:
    if os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as file:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="{os.path.basename(attachment_path)}"'
            )
            msg.attach(part)

# Add SSL (layer of security) 
context = ssl.create_default_context() 
 
# Log in and send the email 
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp: 
    smtp.login(email_sender, email_password) 
    smtp.sendmail(email_sender, [email] + [selected_receiver], msg.as_string())
 
print("Email sent successfully!")