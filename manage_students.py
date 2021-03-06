from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import StringProperty
from kivymd.uix.label import MDLabel
from database import disable_toggler, show_alert_dialog
from mysql.connector.errors import InterfaceError
from datetime import date
import re
import flags

class StudentDialog(BoxLayout):
    def __init__(self, **kw):
        super(StudentDialog, self).__init__(**kw)
        # dropdown menu for pass year
        today = date.today()
        self.yearmenu_items = [
            {   
                "text": str(today.year),
                "viewclass": "OneLineListItem",
                "on_release": lambda x=str(today.year): self.yearmenu_callback(x),
            },
            {
                "text": str(today.year+1),
                "viewclass": "OneLineListItem",
                "on_release": lambda x=str(today.year+1): self.yearmenu_callback(x),
            },
            {
                "text": str(today.year+2),
                "viewclass": "OneLineListItem",
                "on_release": lambda x=str(today.year+2): self.yearmenu_callback(x),
            },
            {
                "text": str(today.year+3),
                "viewclass": "OneLineListItem",
                "on_release": lambda x=str(today.year+3): self.yearmenu_callback(x),
            },
        ]
        self.yearmenu = MDDropdownMenu(
            caller = self.ids.dialog_passyear,
            items=self.yearmenu_items,
            width_mult=4,
            max_height = 200
            )

        # menu_items 
        branchmenu_items = [
            {
                "text": "CSE",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="CSE": self.branchmenu_callback(x),
            },
            {
                "text": "IT",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="IT": self.branchmenu_callback(x),
            },
            {
                "text": "ENTC",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="ENTC": self.branchmenu_callback(x),
            },
            {
                "text": "Civil",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Civil": self.branchmenu_callback(x),
            },
            {
                "text": "Mech",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="Mech": self.branchmenu_callback(x),
            },
            {
                "text": "ELN",
                "viewclass": "OneLineListItem",
                "on_release": lambda x="ELN": self.branchmenu_callback(x),
            },
        ]
        # for dropdown menu
        self.branchmenu = MDDropdownMenu(
            caller = self.ids.dialog_branch,
            items=branchmenu_items,
            width_mult=4,
            max_height = 300
        )

    def yearmenu_callback(self, text_item):
        # callback menu for pass year
        self.ids.dialog_passyear.text = text_item
        self.yearmenu.dismiss()

    def branchmenu_callback(self, text_item):
        # callback menu for branch
        self.ids.dialog_branch.text = text_item
        self.branchmenu.dismiss()


class StudentTitle(MDLabel):
    # student title label
    text = StringProperty()
    id = StringProperty()

class StudentLabel(MDLabel):
    # student label
    text = StringProperty()
    id = StringProperty()

class ManageStudents(Screen):
    def __init__(self, **kw):
        super(ManageStudents, self).__init__(**kw)
    
    def load_students(self,year):
        # loads students screen

        # changing color of button pressed
        for i in range(4):
            if i == year:
                self.ids[str(year)].md_bg_color = flags.app.theme_cls.primary_color
            else:
                self.ids[str(i)].md_bg_color = flags.app.theme_cls.accent_color
        # my_db, my_cursor = db_connector()
        my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
        # select branch by officer_branch
        branch = flags.app.officer_branch
        for key, value in flags.branch.items():
            if branch == value:
                branch = key
                break
        # pinging database to check for network connection
        try:
            my_db.ping(reconnect=True,attempts=1)
        except InterfaceError:
            show_alert_dialog(self,"Unable to connect to remote database, due to weak network. Try reconnect after sometime")
            return
        # lists all records in database
        query = f"select * from students where branch = '{branch}' and pass_year = {date.today().year+year};"
        my_cursor.execute(query)
        self.student_records = my_cursor.fetchall()
        # adding dynamic data to screen
        self.ids.grid.clear_widgets()
        for i in range(len(self.student_records)):
            # enrollmentid, name, email
            self.ids.grid.add_widget(StudentTitle(id=f'{i}',text=f"[u][ref=world]{self.student_records[i][0]}[/ref][/u]"))
            self.ids.grid.add_widget(StudentLabel(id=f'{i}',text=f"{str(self.student_records[i][1])}"))
            self.ids.grid.add_widget(StudentLabel(id=f'{i}',text=f"{self.student_records[i][3]}"))

    def full_details(self,id):
        # shows all details of student in a dialog box
        self.id = int(id)
        # create insatance of dialog box,  fill in data and disable everything
        self.dialog_data = StudentDialog()
        self.dialog_data.ids.dialog_name.text = self.student_records[self.id][1]
        self.dialog_data.ids.dialog_phone.text = self.student_records[self.id][2]
        self.dialog_data.ids.dialog_email.text = self.student_records[self.id][3]
        self.dialog_data.ids.dialog_passyear.text = self.student_records[self.id][5]
        self.dialog_data.ids.dialog_branch.text = flags.branch[self.student_records[self.id][6]]
        self.all_id = ['dialog_name','dialog_phone','dialog_email','dialog_passyear','dialog_branch']
        # disabling data
        disable_toggler(self.dialog_data,self.all_id,True)
        # shows all details of student in a dialog box
        self.detail_dialog = MDDialog(
            title=str(self.student_records[self.id][0]),
            type="custom",
            content_cls=self.dialog_data,
            buttons=[
                    MDRoundFlatButton(text="CANCEL",on_press=self.dismiss_dialog),
                    MDRoundFlatButton(text="SAVE", on_press= self.save_dialog),
                ]
        )
        self.detail_dialog.open()

    def dismiss_dialog(self,instance):
        # dismiss dialog
        self.detail_dialog.dismiss()

    def edit_student(self):
        # enables all input fields to edit students
        disable_toggler(self.dialog_data,self.all_id,False)

    def save_dialog(self,instance):
        # if widgets are not disabled, modify the database
        if not self.dialog_data.ids.dialog_name.disabled:
            self.stud_name = self.dialog_data.ids.dialog_name.text
            # checking name constraint
            if len(self.stud_name)==0 or len(self.stud_name) > 60:
                show_alert_dialog(self.dialog_data,"enter name in length range 1 to 60")
                return
            self.phone = self.dialog_data.ids.dialog_phone.text
            # checking phone number constraint
            if len(self.phone) != 10:
                show_alert_dialog(self.dialog_data,"enter 10 digit phone number")
                return
            try:
                phone = int(self.phone)
            except ValueError:
                show_alert_dialog(self.dialog_data,"enter valid phone number")
                return
            self.email = self.dialog_data.ids.dialog_email.text
            # checking email constraint
            if len(self.email)<1 or len(self.email)>60: # email length
                show_alert_dialog(self,"Please enter an email")
                return 
            if  not re.match(r"([a-zA-Z0-9_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)",self.email): # email validation
                show_alert_dialog(self,"Please enter valid email!!")
                return
            self.passyear = self.dialog_data.ids.dialog_passyear.text
            self.branch = self.dialog_data.ids.dialog_branch.text
            # matching dept name with db number
            for k,v in flags.branch.items():
                if v==self.branch:
                    self.branch=k
                    break
            # connecting to database
            # my_db, my_cursor = db_connector()
            my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
            # pinging database to check for network connection
            try:
                my_db.ping(reconnect=True,attempts=1)
            except InterfaceError:
                show_alert_dialog(self,"Unable to connect to remote database, due to weak network. Try reconnect after sometime")
                return
            query = f"UPDATE students SET stud_name = %s, stud_phone_no = %s, stud_email = %s,pass_year = %s, branch = %s WHERE enrollment_id = {self.student_records[self.id][0]}"
            values = (self.stud_name,self.phone, self.email, self.passyear, self.branch)
            my_cursor.execute(query,values)
            my_db.commit()
            # closing dialog
            self.dismiss_dialog(self.detail_dialog)
            # showing message as modified successfully
            show_alert_dialog(self,"Modified Student")
            # going to home_screen
            self.manager.callback()
        else:
            # else close dialog
            self.dismiss_dialog(self.detail_dialog)