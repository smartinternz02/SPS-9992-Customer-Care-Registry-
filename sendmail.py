import smtplib
import os
SUBJECT = "Customer Care"
s = smtplib.SMTP('smtp.gmail.com', 587)


def sendmail(TEXT,email):
    print("successfully registered")
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("abzhelpdesk18@gmail.com", "nidhi252306")
    message  = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
    s.sendmail("nidhi2506agarwal@gmail.com", email, message)
    s.quit()

