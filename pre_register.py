from kivy.uix.screenmanager import Screen
from database import show_alert_dialog
import flags
from kivymd.uix.filemanager import MDFileManager
import os
import pandas as pd
from mysql.connector.errors import IntegrityError, InterfaceError

class PreRegister(Screen):
    def __init__(self, **kw):
        super(PreRegister, self).__init__(**kw)
        # loading file manager
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager = self.exit_manager,
            select_path = self.select_path,
            # preview = True
           ext=[".xlsx",".csv",".txt",".xls"]
        )
    def select_path(self, path):
        # select path of execl sheet
        # my_db, my_cursor = db_connector()
        my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
        #reading external file
        df=pd.read_excel(path)
        enroll=list(df['enrollment id'])
        already=[]
        #officer id in branch
        branch = flags.app.officer_branch
        for key, value in flags.branch.items():
            if branch == value:
                branch = key
                break   
        #checking if enrollment id is not in database   
        qu="insert into pre_registered (enrollment_id,branch) values (%s,%s);"
        # pinging database to check for network connection
        try:
            my_db.ping(reconnect=True,attempts=1)
        except InterfaceError:
            show_alert_dialog(self,"Unable to connect to remote database, due to weak network. Try reconnect after sometime")
            return
        for i in range(len(enroll)):
            try:
                val=(enroll[i],branch)
                my_cursor.execute(qu,val)
            except IntegrityError:
                already.append(enroll[i])
        my_db.commit()
        if len(already)==0:
            show_alert_dialog(self,'all the ids successfully added!!!')
        else:
            show_alert_dialog(self,f'All ids added except {already}')
        self.exit_manager()

    def file_manager_open(self):
        # creating folder if it dosent exist
        try:
            os.makedirs(f"C:\\Users\\{os.getlogin()}\\Downloads\\tnp")
        except FileExistsError:
            pass
        # opening file
        self.file_manager.show(f"C:\\Users\\{os.getlogin()}\\Downloads\\tnp")
        self.manager_open = True

    def manual_entry(self):
        # enter data manually for one enrollment id
        id = self.ids.manual_id.text
        branch = flags.app.officer_branch
        # select branch
        for key, value in flags.branch.items():
            if branch == value:
                branch = key
                break
        my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
        qur='insert into pre_registered(enrollment_id ,branch) values (%s,%s)'
        val=(id,branch)
        # pinging database to check for network connection
        try:
            my_cursor.execute(qur,val)
            show_alert_dialog(self,"student added successfully !!!")
        except IntegrityError:
            show_alert_dialog(self,"already in database!!!")
            #if already in database
        my_db.commit()
            
        self.ids.manual_id.text=""


    def exit_manager(self, *args):
        # exits file manager
        self.manager_open = False
        self.file_manager.close()