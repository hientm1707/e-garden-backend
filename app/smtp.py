import smtplib, ssl
context = ssl.create_default_context()
def sendEmail(sender_username, sender_password, receiver,msg):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls(context=context)
        smtp.login(sender_username, sender_password)
        smtp.sendmail(sender_username, receiver, msg)