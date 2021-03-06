from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty
from kivymd.uix.label import MDLabel
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import flags
import numpy as np
from mysql.connector.errors import InterfaceError
from database import show_alert_dialog

class InstituteTableTitleLabel(MDLabel):
    # institute table title label
    text = StringProperty()
class InstituteTableLabel(MDLabel):
    # institute table label
    text = StringProperty()


class InstituteAnalysis(Screen):
    def __init__(self, **kw):
        super(InstituteAnalysis,self).__init__(**kw)

    def prepare_graphs(self):
        # loads all graphs
        self.countplt()
        self.placedstat()
        self.lin()
        graphs=self.manager.get_screen('institute_graphs')
        # reload images
        for i in range(1,4):
            graphs.ids[str(i)].reload()

    def load_analysis(self):
        # load table for institute data
        for k,v in flags.branch.items():
            if v==flags.app.officer_branch:
                branch=k
                break
        my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
        # cleas table
        self.ids.grid.clear_widgets()
        # pinging database to check for network connection
        try:
            my_db.ping(reconnect=True,attempts=1)
        except InterfaceError:
            show_alert_dialog(self,"Unable to connect to remote database, due to weak network. Try reconnect after sometime")
            return
        # retriving list of packages
        my_cursor.execute('''select distinct(co.package)
                        from offer_letters as ol
                        inner join company as co on ol.company_id = co.company_id
                        inner join students as st on ol.enrollment_id = st.enrollment_id
                        where st.pass_year = year(curdate());''')
        packages = my_cursor.fetchall()
        for package in packages:
            # add package
            self.ids.grid.add_widget(InstituteTableTitleLabel(text=str(package[0])))
            # add offer count, placed count
            my_cursor.execute(f"select count(st.enrollment_id) as offers, (select count(std.enrollment_id) from offer_letters as ol inner join company as co on ol.company_id = co.company_id inner join students as std on ol.enrollment_id = std.enrollment_id where std.pass_year = year(curdate()) and co.package = {float(package[0])} and ol.finalised = '') as placed from offer_letters as ol inner join company as co on ol.company_id = co.company_id inner join students as st on ol.enrollment_id = st.enrollment_id where st.pass_year = year(curdate()) and co.package = {float(package[0])};")
            offer,placed = my_cursor.fetchall()[0]
            self.ids.grid.add_widget(InstituteTableLabel(text=str(offer)))
            self.ids.grid.add_widget(InstituteTableLabel(text=str(placed)))
            for branch in range(1,7):
                # count of students placed for given for package and branch
                my_cursor.execute(f"select count(st.enrollment_id) as offers from offer_letters as ol inner join company as co on ol.company_id = co.company_id inner join students as st on ol.enrollment_id = st.enrollment_id where st.pass_year = year(curdate()) and co.package = {float(package[0])} and st.branch={branch} and ol.finalised = '';")
                self.ids.grid.add_widget(InstituteTableLabel(text=str(my_cursor.fetchall()[0][0])))

    def countplt(self):
        # count plot for offer letters
        branch = {
            1 : "Civil",
            2 : "Mech",
            3 : "CSE",
            4 : "ENTC",
            5 : "ELN",
            6 : "IT"
            }
        my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
        dat=[]
        try:
            my_db.ping(reconnect=True,attempts=1)
        except InterfaceError:
            show_alert_dialog(self,"Unable to connect to remote database, due to weak network. Try reconnect after sometime")
            return
        my_cursor.execute('select st.branch, st.pass_year from offer_letters as ol inner join students as st on ol.enrollment_id=st.enrollment_id where st.pass_year between year(curdate())-3 and year(curdate());')
        for i in my_cursor:
            dat.append([branch[i[0]],i[1]])
        df=pd.DataFrame(dat,columns=['branch','year'])
        sns.countplot(x=df['branch'],hue=df['year'],palette='coolwarm')
        # plt.show()
        plt.title('Offer Letters per branch')
        plt.savefig("Graphs//inst_1.png")
        plt.close('all')
    
    def placedstat(self):
        # placed student details
        branch = {
            1 : "Civil",
            2 : "Mech",
            3 : "CSE",
            4 : "ENTC",
            5 : "ELN",
            6 : "IT"
            }
        my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
        brch=[]
        try:
            my_db.ping(reconnect=True,attempts=1)
        except InterfaceError:
            show_alert_dialog(self,"Unable to connect to remote database, due to weak network. Try reconnect after sometime")
            return
        my_cursor.execute('select branch from students where pass_year = year(curdate());')
        for i in my_cursor:
            brch.append([branch[i[0]],'Total Students'])
        my_cursor.execute("select branch from students where  enrollment_id  in (select  enrollment_id from offer_letters where finalised='') and pass_year = year(curdate()) ;")
        for i in my_cursor:    
            brch.append([branch[i[0]],'Placed Students'])
        df=pd.DataFrame(brch,columns=['Branch','Placed Status'])
        plt.figure(figsize=(10,6))
        plt.title('students placed per branch')
        sns.countplot(x=df['Branch'],hue=df['Placed Status'])
        # plt.show()
        plt.savefig("Graphs//inst_2.png")
        plt.close('all')

    def lin(self):
        # lineplot for min, max, avg packages
        branch = {
            1 : "Civil",
            2 : "Mech",
            3 : "CSE",
            4 : "ENTC",
            5 : "ELN",
            6 : "IT"
            }
        
        my_db, my_cursor = self.manager.my_db, self.manager.my_cursor
        dat=[]
        try:
            my_db.ping(reconnect=True,attempts=1)
        except InterfaceError:
            show_alert_dialog(self,"Unable to connect to remote database, due to weak network. Try reconnect after sometime")
            return
        my_cursor.execute(f'select co.package, count(co.package), st.branch from offer_letters as ol inner join students as st on ol.enrollment_id=st.enrollment_id inner join company as co on ol.company_id=co.company_id where st.pass_year = year(curdate()) group by st.branch, co.package;')
        for i in my_cursor:
            dat.append([i[0],i[1],branch[i[2]]])
        df=pd.DataFrame(dat,columns=['package','count','branch'])

        sns.lineplot(x='package',y='count',hue = 'branch',data=df,markers=True,style='branch')
        plt.title(f"Package Analysis\nmin:-{min(df['package'])}, max:-{max(df['package'])}, avg:- {np.mean(df['package'])}")
        plt.yticks(np.arange(max(df['count'])+5,step=5))
        plt.xlabel("Package")
        plt.ylabel("No. of packages")
        plt.legend()
        # plt.show()
        plt.savefig("Graphs//inst_3.png")
        plt.close('all')

class InstituteGraphs(Screen):
    # graph screen
    def __init__(self, **kw):
        super(InstituteGraphs, self).__init__(**kw)
