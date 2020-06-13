import smtplib
from socket import gaierror


class Mailer:
    def __init__(self, config):
        self.port = config["port"]
        self.server = config["server"]
        self.login = config["login"]
        self.password = config["password"]
        self.sender = config["sender"]
        self.receiver = config["receiver"]

    def send_mail(self, message):
        mail_content = f"""\
To: {self.receiver}
From: {self.sender}
Subject: Property Alert

{message}"""

        try:
            with smtplib.SMTP_SSL(self.server, self.port) as server:
                server.ehlo()
                server.login(self.login, self.password)
                server.sendmail(self.sender, self.receiver, mail_content)

            print("Email sent.")

        except (gaierror, ConnectionRefusedError):
            print("Failed to connect to the server. Bad connection settings?")
        except smtplib.SMTPServerDisconnected:
            print("Failed to connect to the server. Wrong user/password?")
        except smtplib.SMTPException as e:
            print("SMTP error occurred: " + str(e))
