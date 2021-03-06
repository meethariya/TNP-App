from kivy.uix.screenmanager import Screen
from database import show_alert_dialog
from decouple import config
import random as r
import flags
import smtplib
import bcrypt
from email.message import EmailMessage
from mysql.connector.errors import InterfaceError
class ForgotPass(Screen):
    def __init__(self, **kw):
        super(ForgotPass, self).__init__(**kw)
    
    def send_mail(self):
        self.officer_email = self.ids.email.text
        # my_db, my_cursor = db_connector()
        my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
        # pinging database to check for network connection
        try:
            my_db.ping(reconnect=True,attempts=1)
        except InterfaceError:
            show_alert_dialog(self,"Unable to connect to remote database, due to weak network. Try reconnect after sometime")
            return
        my_cursor.execute(f"select id from officer where email ='{self.officer_email}';")
        records = my_cursor.fetchall()
        if records:
            # send mail to officer for otp verification
            self.officer_id = records[0][0]
            # preparing mail message
            msg = EmailMessage()
            msg['from'] = config("email")
            msg['to'] = self.officer_email
            msg['subject'] = "WIT TNP"
            self.otp=""
            # generating OTP
            for _ in range(6):
                self.otp+=str(r.randint(1,9))
            msg.set_content(f"Your OTP to reset password is {self.otp}. Please use it before switching to another page")
            try:
                # logging in to mail
                with smtplib.SMTP_SSL('smtp.gmail.com',465) as server:
                    server.login(config("email"),config("email_password"))
                    server.send_message(msg)
                    show_alert_dialog(self,'OTP sent to mail id. (Check spam as well!)')
            except Exception:
                show_alert_dialog(self,'Couldnt send OTP due to an error')

        else:
            show_alert_dialog(self,'No such officer exists')
        
    def verify(self):
        # verify OTP
        if self.ids.otp.text == self.otp:
            self.ids.new_pass.disabled = False
            self.ids.new_pass.line_color_normal = flags.app.theme_cls.primary_color
            self.ids.confirm_pass.disabled = False
            self.ids.confirm_password.line_color_normal = flags.app.theme_cls.primary_color
            self.ids.change.disabled = False
            show_alert_dialog(self,'Email verified')
        else:
            show_alert_dialog(self,'Incorrect OTP')

    def change_password(self):
        if self.ids.new_pass.text == self.ids.confirm_pass.text:
            self.password = self.ids.new_pass.text
            # generating hashed key of password to store in database
            hashed = bcrypt.hashpw(self.password.encode('ascii'),bcrypt.gensalt()).decode('ascii')
            # my_db, my_cursor = db_connector()
            my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
            # pinging database to check for network connection
            try:
                my_db.ping(reconnect=True,attempts=1)
            except InterfaceError:
                show_alert_dialog(self,"Unable to connect to remote database, due to weak network. Try reconnect after sometime")
                return
            # updating database
            my_cursor.execute(f"update officer set password = '{hashed}' where id = {self.officer_id};")
            my_db.commit()
            show_alert_dialog(self,'Password changed successfully')
            # changing screen
            self.manager.callback()
        else:
            show_alert_dialog(self,'Both password do not match')