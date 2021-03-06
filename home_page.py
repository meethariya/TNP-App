from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivymd.uix.label import MDLabel
from kivymd.uix.selectioncontrol import MDCheckbox
from mysql.connector.errors import InterfaceError
from database import show_alert_dialog
import flags

class PreRegisterLabel(MDLabel):
    # pre register label
    text = StringProperty()


class EResourceTitle(MDLabel):
    # Eresources title label
    text = StringProperty()
    id = StringProperty()

class EResourceLabel(MDLabel):
    # Eresources label
    text = StringProperty()
    id = StringProperty()

class EResourceCheckbox(MDCheckbox):
    # Eresources checkbox
    id = StringProperty()

class AssessmentTitle(MDLabel):
    # Assessment title label
    text = StringProperty()
    id = StringProperty()

class AssessmentLabel(MDLabel):
    # Assessment label
    text = StringProperty()
    id = StringProperty()

class AssessmentCheckbox(MDCheckbox):
    # Assessment checkbox
    id = StringProperty()

class AnnouncementCheckbox(MDCheckbox):
    # Announcement checkbox
    id = StringProperty()

class AnnouncementTitle(MDLabel):
    # Announcement title label
    text = StringProperty()
    id = StringProperty()

class AnnouncementLabel(MDLabel):
    # Announcement label
    text = StringProperty()
    id = StringProperty()

class HomePage(Screen):
    # Home screen page
    def __init__(self, **kw):
        super(HomePage, self).__init__(**kw)

    def load_eresource(self):
        # loads e_resources screen
        # my_db, my_cursor = db_connector()
        my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
        # select branch by officer_branch
        branch = flags.app.officer_branch
        for key, value in flags.branch.items():
            if branch == value:
                branch = key
                break
        # lists all records in database
        query = f"select * from e_resources where branch = '{branch}';"
        try:
            my_db.ping(reconnect=True,attempts=1)
        except InterfaceError:
            show_alert_dialog(self,"Unable to connect to remote database, due to weak network. Try reconnect after sometime")
            return
        my_cursor.execute(query)
        self.eresources_records = my_cursor.fetchall()
        # creating reference for view_eresource screen to put dynamic data in table
        view_eresources_screen = self.manager.get_screen('view_eresources')
        view_eresources_screen.ids.grid.clear_widgets()
        self.checkbox_list = []
        # adding dynamic data to screen
        for i in range(len(self.eresources_records)):
            # checkbox, title, date, branch
            check = EResourceCheckbox(id=f'{i}')
            self.checkbox_list.append(check)
            view_eresources_screen.ids.grid.add_widget(check)
            view_eresources_screen.ids.grid.add_widget(EResourceTitle(id=f'{i}',text=f"[u][ref=world]{self.eresources_records[i][1]}[/ref][/u]"))
            view_eresources_screen.ids.grid.add_widget(EResourceLabel(id=f'{i}',text=f"{str(self.eresources_records[i][6])}"))
            view_eresources_screen.ids.grid.add_widget(EResourceLabel(id=f'{i}',text=f"{self.eresources_records[i][2]}"))
    
    def load_announcement(self):
        # loads announcement_resources screen
        # my_db, my_cursor = db_connector()
        my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
        # select branch by officer_branch
        branch = flags.app.officer_branch
        for key, value in flags.branch.items():
            if branch == value:
                branch = key
                break
        # lists all records in database
        query = f"select * from announcement where branch = '{branch}';"
        my_db.ping(reconnect=True)
        my_cursor.execute(query)
        self.announcement_records = my_cursor.fetchall()
        # creating reference for view_announcement screen to put dynamic data in table
        view_announcement_screen = self.manager.get_screen('view_announcement')
        view_announcement_screen.ids.grid.clear_widgets()
        self.checkbox_list = []
        for i in range(len(self.announcement_records)):
            # checkbox, title, date, branch
            check = AnnouncementCheckbox(id=f'{i}')
            self.checkbox_list.append(check)
            view_announcement_screen.ids.grid.add_widget(check)
            view_announcement_screen.ids.grid.add_widget(AnnouncementTitle(id=f'{i}',text=f"[u][ref=world]{self.announcement_records[i][1]}[/ref][/u]"))
            view_announcement_screen.ids.grid.add_widget(AnnouncementLabel(id=f'{i}',text=f"{str(self.announcement_records[i][3])}"))
            #view_announcement_screen.ids.grid.add_widget(AnnouncementLabel(id=f'{i}',text=f"{self.announcement_records[i][4]}"))
    
    def load_assessment(self):
        # loads assessments screen
        # my_db, my_cursor = db_connector()
        my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
        branch = flags.app.officer_branch
        for key, value in flags.branch.items():
            if branch == value:
                branch =key
                break
        query = f"select * from assessment where branch = {branch};"
        # pinging database to check for network connection
        try:
            my_db.ping(reconnect=True,attempts=1)
        except InterfaceError:
            show_alert_dialog(self,"Unable to connect to remote database, due to weak network. Try reconnect after sometime")
            return
        my_cursor.execute(query)
        self.assessments_records = my_cursor.fetchall()
        # creating reference for view_assessments screen to put dynamic data in table
        view_assessments_screen = self.manager.get_screen('view_assessments')
        view_assessments_screen.ids.grid.clear_widgets()
        self.assessment_checkbox_list = []
        # adding dynamic data to screen
        for i in range(len(self.assessments_records)):
            check = AssessmentCheckbox(id=f'{i}')
            self.assessment_checkbox_list.append(check)
            view_assessments_screen.ids.grid.add_widget(check)
            view_assessments_screen.ids.grid.add_widget(AssessmentTitle(id=f'{i}',text=f"[u][ref=world]{self.assessments_records[i][1]}[/ref][/u]"))
            view_assessments_screen.ids.grid.add_widget(AssessmentLabel(id=f'{i}',text=f"{str(self.assessments_records[i][7])}"))
            view_assessments_screen.ids.grid.add_widget(AssessmentLabel(id=f'{i}',text=f"{self.assessments_records[i][2]}"))

    def load_pre_register_students(self):
        # loads register student screen
        # my_db, my_cursor = db_connector()
        my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
        # select branch by officer_branch
        branch = flags.app.officer_branch
        for key, value in flags.branch.items():
            if branch == value:
                branch = key
                break
        # lists all records in database
        query = f"select enrollment_id from pre_registered where branch = '{branch}' and verify_status is null"
        # pinging database to check for network connection
        try:
            my_db.ping(reconnect=True,attempts=1)
        except InterfaceError:
            show_alert_dialog(self,"Unable to connect to remote database, due to weak network. Try reconnect after sometime")
            return
        my_cursor.execute(query)
        self.pre_register_students = my_cursor.fetchall()
        # creating reference for register_student screen to put dynamic data in table
        view_register_student = self.manager.get_screen('pre_register')
        view_register_student.ids.grid.clear_widgets()
        #print(self.register)
        for i in range(len(self.pre_register_students)):
            view_register_student.ids.grid.add_widget(PreRegisterLabel(text=str(self.pre_register_students[i][0])))