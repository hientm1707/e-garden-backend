import smtplib, ssl
context = ssl.create_default_context()
def sendEmail(sender_username, sender_password, receiver,msg):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        try:
            smtp.starttls(context=context)
            smtp.login(sender_username, sender_password)
            smtp.sendmail(sender_username, receiver, msg)
            print('Successfully sent email to{}'.format(receiver))
            smtp.quit()
        except Exception as e:
            print('Could not send email!!!')
            print('Error message:{}'.format(e))
