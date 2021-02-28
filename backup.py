from datetime import date 
import shutil
def take_bkp(src_file_name,bkp_file_name=None,src_file_loc="",bkp_file_loc=""):
    # Source file name
    src_file=src_file_name + src_file_loc

    # Fetching Today's(Current Day) date
    today=date.today()
    date_format = today.strftime("%d_%b_%Y_")

    # Modified the name of the backup file
    if bkp_file_name is None or not bkp_file_name:
        bkp_file_name=src_file_name
        bkp_file=bkp_file_loc + date_format + bkp_file_name
    else:
        bkp_file=bkp_file_loc + date_format + bkp_file_name

    # Create the Backup Copy of the source file
    shutil.copy2(src_file,bkp_file)

    # Success Message
    print("Backup Successfull....")


import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
subject="Backup"
msg=MIMEMultipart()
msg["From"]="noreplskyevo@gmail.com"
msg["To"]="foodomystery@gmail.com"
msg["Subject"]=subject

body = "Backup of your data send by Skyevo@pvt.ltd for more inquiry visit our site\nhttps://skyevo.in/\nThis is an autogenerated email so don't reply to it."
msg.attach(MIMEText(body,"plain"))

filename="area.json"
attacment=open(filename,"rb")
part=MIMEBase("application","octet-stream")
part.set_payload((attacment).read())
encoders.encode_base64(part)
part.add_header("Content-Discomposition","attachment;filename="+"Backup")

msg.attach(part)

text=msg.as_string()

server = smtplib.SMTP("smtp.gmail.com",587)
server.starttls()
server.login("noreplskyevo@gmail.com","noreply@#$3898")

server.sendmail("noreplskyevo@gmail.com","foodomystery@gmail.com",text)
server.quit()    