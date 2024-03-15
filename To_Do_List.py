#! /usr/bin/env python3
#  -*- coding: utf-8 -*-
#
# GUI module generated by PAGE version 8.0
#  in conjunction with Tcl version 8.6
#    Feb 12, 2024 04:30:03 PM EST  platform: Windows NT

import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
import os.path
import psycopg2

_location = os.path.dirname(__file__)

import To_Do_List_support

_bgcolor = '#d9d9d9'
_fgcolor = '#000000'
_tabfg1 = 'black' 
_tabfg2 = 'white' 
_bgmode = 'light' 
_tabbg1 = '#d9d9d9' 
_tabbg2 = 'gray40' 

_style_code_ran = 0

# Load DB info so changes in the future only require changing one place.]

db_name = "to_do_list"
db_host = "localhost"
db_user = "postgres"
db_passwd = ""
db_port = "5432"

def _style_code():
    global _style_code_ran
    if _style_code_ran: return        
    try: To_Do_List_support.root.tk.call('source',
                os.path.join(_location, 'themes', 'default.tcl'))
    except: pass
    style = ttk.Style()
    style.theme_use('default')
    style.configure('.', font = "TkDefaultFont")
    if sys.platform == "win32":
       style.theme_use('winnative')    
    _style_code_ran = 1

class mainWindow:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
           
        # Names of all To Do Lists in the DB      lbox_listNames
        #                                            -selectList
        # New To Do List name                     txt_listName
        # Button to add new list                  btn_newList
        #                                            -newListClick
        # Button to delete a list                 btn_deleteList
        #                                            -deleteListClick
        # Display the selected list               lbox_displayList
        #                                            -selectActivity
        # Selected activity name                  txt_Activity
        # Selected activity notes                 txt_notes
        # Whether selected activity is complete   cb_completion
        # Add a new activity                      btn_addActivity
        #                                            -addActivityClick
        # Remove activity from list               btn_removeActivity
        #                                            -removeActivityClick
        # Save changes to selected activity       btn_save
        #                                            -saveClick

        def check_exists():
            # check if the database exists and return True/False
            does_exist = False
            
            try:
                conn = psycopg2.connect(host=db_host, user=db_user, password=db_passwd, port=db_port)
                cursor = conn.cursor()
                
                cursor.execute("SELECT exists(SELECT datname FROM pg_catalog.pg_database WHERE datname = '{}')".format(db_name))
                does_exist = cursor.fetchone()[0]   
                            
                cursor.close()
                conn.close()
                
            except(Exception, psycopg2.DatabaseError) as error:
                print(error)
            
            return(does_exist)
        
        def create_db():
            # create the database and two tables
            conn = psycopg2.connect(host = db_host,
                                    user = db_user,
                                    password = db_passwd,
                                    port = db_port)
            conn.autocommit = True
            cursor = conn.cursor()
                
            try:
                cursor.execute("CREATE DATABASE {} WITH OWNER = postgres ENCODING = 'UTF8' LC_COLLATE = 'English_United States.1252' LC_CTYPE = 'English_United States.1252' LOCALE_PROVIDER = 'libc' TABLESPACE = pg_default CONNECTION LIMIT = -1 IS_TEMPLATE = False;".format(db_name))
                cursor.close()
                conn.close()
                conn2 = psycopg2.connect(database = db_name,
                                         host = db_host,
                                         user = db_user,
                                         password = db_passwd,
                                         port = db_port)
                conn2.autocommit = True
                cursor2 = conn2.cursor()
                cursor2.execute('CREATE TABLE IF NOT EXISTS public.list_names(list_id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( CYCLE INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ), names text COLLATE pg_catalog."default" NOT NULL, CONSTRAINT list_names_pkey PRIMARY KEY (list_id))')
                cursor2.execute('CREATE TABLE IF NOT EXISTS public.list_activities(list_id integer NOT NULL, completed boolean DEFAULT false, activity_name text COLLATE pg_catalog."default" NOT NULL, notes text COLLATE pg_catalog."default" DEFAULT \'None\'::text, CONSTRAINT list_activities_pkey PRIMARY KEY (list_id, activity_name), CONSTRAINT "List_Index" FOREIGN KEY (list_id) REFERENCES public.list_names (list_id) MATCH SIMPLE ON UPDATE CASCADE ON DELETE CASCADE)')
                cursor2.close()
                conn2.close()
            except (psycopg2.DatabaseError, Exception) as error:
                print(error)
                    
            cursor.close()
            conn.close()

                
        def load_lists():
            #This function loads the list names to the screen
            db_exists = check_exists()
            
            if db_exists == False:
                create_db()
                                
            conn = psycopg2.connect(database = db_name,
                                    host = db_host,
                                    user = db_user,
                                    password = db_passwd,
                                    port = db_port)
            cursor = conn.cursor()
        
            cursor.execute("SELECT names FROM list_names")
            names = cursor.fetchall()
            name_list = []
            
            for i in names:
                name_list.append('{}'.format(i[0]))
                
            var = tk.Variable(value=name_list)
        
            if self.lbox_listNames:
                self.lbox_listNames.configure(listvariable = var)

            cursor.close()
            conn.close()
        
        def load_activities():
            #This function loads the activity names to the screen
            if self.lbox_displayList:
                conn = psycopg2.connect(database = db_name,
                                        host = db_host,
                                        user = db_user,
                                        password = db_passwd,
                                        port = db_port)
                cursor = conn.cursor()
        
                txt_string = self.lbl_list.cget("text")
                list_name = txt_string.split(": ")
                selectedList = list_name[1]
                act_list = []
                
                if selectedList != '':
                    cursor.execute("SELECT list_id FROM list_names WHERE names = '{}'".format(selectedList))
                    ids = cursor.fetchone()
                    selectedId = ids[0]
            
                    cursor.execute("SELECT activity_name FROM list_activities WHERE list_id = {}".format(selectedId))
                    activities = cursor.fetchall()
                
                    for i in activities:
                        act_list.append('{}'.format(i[0]))
                        
                var2 = tk.Variable(value=act_list)
                self.lbox_displayList.configure(listvariable=var2)
        
                cursor.close()
                conn.close()
            
        def selectList(event):
            #Select which list to display
            db_not_empty = self.lbox_listNames.get(0, END)
            ids = self.lbox_listNames.curselection()
                
            if db_not_empty and ids:
                selectedIndex = ids[0]
                selectedList = self.lbox_listNames.get(selectedIndex)
                self.lbl_list.configure(text='''Things To Do: '''+selectedList)
                load_activities()
                if self.tch69.get() == 1:
                    self.cb_completion.invoke()
                self.txt_Activity.delete('1.0', END)
                self.txt_notes.delete('1.0', END)

        def newListClick():
            #This will take the list name from the text box and create a new list in the DB
            newName = self.txt_listName.get("1.0", 'end-1c')
            
            list_names = list(self.lbox_listNames.get(0, END))
            for i in list_names:
                if i == newName:
                    not_present = False
                    self.txt_listName.delete('1.0', END)
                    break
                else:
                    not_present = True
            
            if newName and not_present:
                #create a new list in DB
                conn = psycopg2.connect(database = db_name,
                                        host = db_host,
                                        user = db_user,
                                        password = db_passwd,
                                        port = db_port)
                cursor = conn.cursor()
                
                try:
                    cursor.execute("INSERT INTO list_names(names) VALUES ('{}')".format(newName))
                    conn.commit()   
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                finally:
                    pass
                
                load_lists()
                self.txt_listName.delete('1.0', END)
                
                cursor.close()
                conn.close()
                
        def deleteListClick():
            #Delete a To Do List from the DB
            indices = self.lbox_listNames.curselection()
            
            if indices:
                conn = psycopg2.connect(database = db_name,
                                        host = db_host,
                                        user = db_user,
                                        password = db_passwd,
                                        port = db_port)
                cursor = conn.cursor()
                
                selectedIndex = indices[0]
                selectedList = self.lbox_listNames.get(selectedIndex)
            
                try:
                    cursor.execute("DELETE FROM list_names WHERE names = '{}'".format(selectedList))
                    conn.commit()   
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                finally:
                    pass
                    
                self.lbox_listNames.delete(selectedIndex)
                self.lbl_list.configure(text='''Things To Do: ''')
                load_activities()
                if self.tch69.get() == 1:
                    self.cb_completion.invoke()
                self.txt_Activity.delete('1.0', END)
                self.txt_notes.delete('1.0', END)
                
                cursor.close()
                conn.close()

        def selectActivity(event):
            #Select which activity to display
            list_not_empty = self.lbox_displayList.get(0,END)
            selectedIndex = self.lbox_displayList.curselection()
            
            if list_not_empty and selectedIndex:
                conn = psycopg2.connect(database = db_name,
                                        host = db_host,
                                        user = db_user,
                                        password = db_passwd,
                                        port = db_port)
                cursor = conn.cursor()
                
                selectedActivity = self.lbox_displayList.get(selectedIndex[0])
                cursor.execute("SELECT completed FROM list_activities WHERE activity_name = '{}'".format(selectedActivity))
                completed = cursor.fetchone()[0]
                
                if completed and self.tch69.get() == 0:
                    self.cb_completion.invoke()
                elif not completed and self.tch69.get() == 1:
                    self.cb_completion.invoke()
            
                cursor.execute("SELECT notes FROM list_activities WHERE activity_name = '{}'".format(selectedActivity))
                notes = cursor.fetchone()[0]
                self.txt_notes.delete('1.0', END)
                self.txt_notes.insert('1.0', notes)

                self.txt_Activity.delete('1.0', END)
                self.txt_Activity.insert('1.0', selectedActivity)
            
                cursor.close()
                conn.close()

        def addActivityClick():
            #This will add the info in Completed, Activity, & Notes as a new activity in the DB
            newActivity = self.txt_Activity.get("1.0", 'end-1c')
            
            activity_names = list(self.lbox_displayList.get(0, END))
            if len(activity_names) > 0:
                for i in activity_names:
                    if i == newActivity:
                        not_present = False
                        
                        if self.tch69.get() == 1:
                            self.cb_completion.invoke()
                            
                        self.txt_Activity.delete('1.0', END)
                        self.txt_notes.delete('1.0', END)
                        
                        break
                    else:
                        not_present = True
            else:
                not_present = True
                
            txt_string = self.lbl_list.cget("text")
            list_name = txt_string.split(": ")
            
            if newActivity and not_present and len(list_name) > 1:
                #create new activity in DB
                conn = psycopg2.connect(database = db_name,
                                        host = db_host,
                                        user = db_user,
                                        password = db_passwd,
                                        port = db_port)
                cursor = conn.cursor()
                
                selectedList = list_name[1]
                
                cursor.execute("SELECT list_id FROM list_names WHERE names = '{}'".format(selectedList))
                ids = cursor.fetchone()
                selectedId = ids[0]
                
                if self.tch69.get() == 0:
                    completed = False
                else:
                    completed = True
                
                notes = self.txt_notes.get('1.0', 'end-1c')
                
                try:
                    if len(notes) == 0:
                        cursor.execute("INSERT INTO list_activities(list_id, activity_name, completed) VALUES ({}, '{}', {})".format(selectedId, newActivity, completed))
                    else:
                        cursor.execute("INSERT INTO list_activities(list_id, activity_name, completed, notes) VALUES ({}, '{}', {}, '{}')".format(selectedId, newActivity, completed, notes))
                    conn.commit()   
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                finally:
                    pass
                
                load_activities()
                self.txt_Activity.delete('1.0', END)
                if self.tch69.get() == 1:
                    self.cb_completion.invoke()
                self.txt_notes.delete('1.0', END)
                
                cursor.close()
                conn.close()
                
        def removeActivityClick():
            #delete an activity from a To Do List
            indices = self.lbox_displayList.curselection()
            
            if indices:
                conn = psycopg2.connect(database = db_name,
                                        host = db_host,
                                        user = db_user,
                                        password = db_passwd,
                                        port = db_port)
                cursor = conn.cursor()

                selectedIndex = indices[0]
                selectedActivity = self.lbox_displayList.get(selectedIndex)
            
                try:
                    cursor.execute("DELETE FROM list_activities WHERE activity_name = '{}'".format(selectedActivity))
                    conn.commit()
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                finally:
                    pass
                    
                self.lbox_displayList.delete(selectedIndex)
                
                if self.tch69.get() == 1:
                    self.cb_completion.invoke()
                self.txt_notes.delete('1.0', END)
                self.txt_Activity.delete('1.0', END)
                
                cursor.close()
                conn.close()

        def saveClick():
            #This will save updates to an activity selected from the To Do List
            activity = self.txt_Activity.get('1.0', 'end-1c')
            
            activity_names = self.lbox_displayList.get(0, END)
            not_present = True

            for i in activity_names:
                if i == activity:
                    not_present = False
                    break
                else:
                    not_present = True
                    
            if activity and not not_present:
                conn = psycopg2.connect(database = db_name,
                                        host = db_host,
                                        user = db_user,
                                        password = db_passwd,
                                        port = db_port)
                cursor = conn.cursor()
                
                try:
                    completed = bool(self.tch69.get())
                    notes = self.txt_notes.get('1.0', 'end-1c')
                    activity = self.txt_Activity.get('1.0', 'end-1c')
                               
                    cursor.execute("UPDATE list_activities SET completed = {}, notes = '{}' WHERE activity_name = '{}'".format(completed, notes, activity))
                    conn.commit()
                except (Exception, psycopg2.DatabaseError) as error:
                    print(error)
                finally:
                    pass
                
                load_activities()
                self.txt_Activity.delete('1.0', END)
                if self.tch69.get() == 1:
                    self.cb_completion.invoke()
                self.txt_notes.delete('1.0', END)
                    
                cursor.close()
                conn.close()
        
        top.geometry("1024x851+251+100")
        top.minsize(120, 1)
        top.maxsize(2564, 1401)
        top.resizable(1,  1)
        top.title("To Do Lists")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="#000000")

        self.top = top
        self.tch69 = tk.IntVar()

        self.lbl_list = tk.Label(self.top)
        self.lbl_list.place(relx=0.02, rely=0.224, height=29, width=233)
        self.lbl_list.configure(activebackground="#d9d9d9")
        self.lbl_list.configure(activeforeground="black")
        self.lbl_list.configure(anchor='w')
        self.lbl_list.configure(background="#d9d9d9")
        self.lbl_list.configure(compound='left')
        self.lbl_list.configure(disabledforeground="#a3a3a3")
        self.lbl_list.configure(font="-family {Segoe UI} -size 9")
        self.lbl_list.configure(foreground="#000000")
        self.lbl_list.configure(highlightbackground="#d9d9d9")
        self.lbl_list.configure(highlightcolor="#000000")
        self.lbl_list.configure(text='''Things To Do''')

        self.lbl_notes = tk.Label(self.top)
        self.lbl_notes.place(relx=0.284, rely=0.438, height=24, width=70)
        self.lbl_notes.configure(activebackground="#d9d9d9")
        self.lbl_notes.configure(activeforeground="black")
        self.lbl_notes.configure(anchor='w')
        self.lbl_notes.configure(background="#d9d9d9")
        self.lbl_notes.configure(compound='left')
        self.lbl_notes.configure(disabledforeground="#a3a3a3")
        self.lbl_notes.configure(font="-family {Segoe UI} -size 9")
        self.lbl_notes.configure(foreground="#000000")
        self.lbl_notes.configure(highlightbackground="#d9d9d9")
        self.lbl_notes.configure(highlightcolor="#000000")
        self.lbl_notes.configure(text='''Notes''')

        _style_code()
        self.TSeparator1 = ttk.Separator(self.top)
        self.TSeparator1.place(relx=0.029, rely=0.673,  relwidth=0.529)

        self.lbox_displayList = ScrolledListBox(self.top, selectmode=tk.SINGLE)
        self.lbox_displayList.place(relx=0.02, rely=0.259, relheight=0.388
                , relwidth=0.216)
        self.lbox_displayList.configure(background="white")
        self.lbox_displayList.configure(cursor="xterm")
        self.lbox_displayList.configure(disabledforeground="#a3a3a3")
        self.lbox_displayList.configure(font="TkFixedFont")
        self.lbox_displayList.configure(foreground="black")
        self.lbox_displayList.configure(highlightbackground="#d9d9d9")
        self.lbox_displayList.configure(highlightcolor="#d9d9d9")
        self.lbox_displayList.configure(selectbackground="#d9d9d9")
        self.lbox_displayList.configure(selectforeground="black")
        self.lbox_displayList.bind('<<ListboxSelect>>', selectActivity)

        self.lbl_listNames = tk.Label(self.top)
        self.lbl_listNames.place(relx=0.02, rely=0.022, height=30, width=100)
        self.lbl_listNames.configure(activebackground="#d9d9d9")
        self.lbl_listNames.configure(activeforeground="black")
        self.lbl_listNames.configure(anchor='w')
        self.lbl_listNames.configure(background="#d9d9d9")
        self.lbl_listNames.configure(compound='left')
        self.lbl_listNames.configure(disabledforeground="#a3a3a3")
        self.lbl_listNames.configure(font="-family {Segoe UI} -size 9")
        self.lbl_listNames.configure(foreground="#000000")
        self.lbl_listNames.configure(highlightbackground="#d9d9d9")
        self.lbl_listNames.configure(highlightcolor="#000000")
        self.lbl_listNames.configure(text='''To Do Lists''')

        self.lbox_listNames = tk.Listbox(self.top, selectmode=tk.SINGLE)
        self.lbox_listNames.place(relx=0.02, rely=0.056, relheight=0.148
                , relwidth=0.216)
        self.lbox_listNames.configure(background="white")
        self.lbox_listNames.configure(disabledforeground="#a3a3a3")
        self.lbox_listNames.configure(font="TkFixedFont")
        self.lbox_listNames.configure(foreground="#000000")
        self.lbox_listNames.configure(highlightbackground="#d9d9d9")
        self.lbox_listNames.configure(highlightcolor="#000000")
        self.lbox_listNames.configure(selectbackground="#d9d9d9")
        self.lbox_listNames.configure(selectforeground="black")
        self.lbox_listNames.bind('<<ListboxSelect>>', selectList)
        load_lists()

        self.btn_addActivity = tk.Button(self.top, command=addActivityClick)
        self.btn_addActivity.place(relx=0.361, rely=0.611, height=25, width=55)
        self.btn_addActivity.configure(activebackground="#d9d9d9")
        self.btn_addActivity.configure(activeforeground="black")
        self.btn_addActivity.configure(background="#d9d9d9")
        self.btn_addActivity.configure(disabledforeground="#a3a3a3")
        self.btn_addActivity.configure(font="-family {Segoe UI} -size 9")
        self.btn_addActivity.configure(foreground="#000000")
        self.btn_addActivity.configure(highlightbackground="#d9d9d9")
        self.btn_addActivity.configure(highlightcolor="#000000")
        self.btn_addActivity.configure(text='''Add''')

        self.btn_save = tk.Button(self.top, command=saveClick)
        self.btn_save.place(relx=0.502, rely=0.611, height=26, width=55)
        self.btn_save.configure(activebackground="#d9d9d9")
        self.btn_save.configure(activeforeground="black")
        self.btn_save.configure(background="#d9d9d9")
        self.btn_save.configure(disabledforeground="#a3a3a3")
        self.btn_save.configure(font="-family {Segoe UI} -size 9")
        self.btn_save.configure(foreground="#000000")
        self.btn_save.configure(highlightbackground="#d9d9d9")
        self.btn_save.configure(highlightcolor="#000000")
        self.btn_save.configure(text='''Save''')

        self.txt_notes = tk.Text(self.top)
        self.txt_notes.place(relx=0.361, rely=0.435, relheight=0.112
                , relwidth=0.195)
        self.txt_notes.configure(background="white")
        self.txt_notes.configure(font="TkTextFont")
        self.txt_notes.configure(foreground="black")
        self.txt_notes.configure(highlightbackground="#d9d9d9")
        self.txt_notes.configure(highlightcolor="#000000")
        self.txt_notes.configure(insertbackground="#000000")
        self.txt_notes.configure(selectbackground="#d9d9d9")
        self.txt_notes.configure(selectforeground="black")
        self.txt_notes.configure(wrap="word")

        self.lbl_activity = tk.Label(self.top)
        self.lbl_activity.place(relx=0.284, rely=0.36, height=23, width=70)
        self.lbl_activity.configure(activebackground="#d9d9d9")
        self.lbl_activity.configure(activeforeground="black")
        self.lbl_activity.configure(anchor='w')
        self.lbl_activity.configure(background="#d9d9d9")
        self.lbl_activity.configure(compound='left')
        self.lbl_activity.configure(disabledforeground="#a3a3a3")
        self.lbl_activity.configure(font="-family {Segoe UI} -size 9")
        self.lbl_activity.configure(foreground="#000000")
        self.lbl_activity.configure(highlightbackground="#d9d9d9")
        self.lbl_activity.configure(highlightcolor="#000000")
        self.lbl_activity.configure(text='''Activity''')

        self.txt_Activity = tk.Text(self.top)
        self.txt_Activity.place(relx=0.361, rely=0.36, relheight=0.028
                , relwidth=0.192)
        self.txt_Activity.configure(background="white")
        self.txt_Activity.configure(font="TkTextFont")
        self.txt_Activity.configure(foreground="black")
        self.txt_Activity.configure(highlightbackground="#d9d9d9")
        self.txt_Activity.configure(highlightcolor="#000000")
        self.txt_Activity.configure(insertbackground="#000000")
        self.txt_Activity.configure(selectbackground="#d9d9d9")
        self.txt_Activity.configure(selectforeground="black")
        self.txt_Activity.configure(wrap="word")

        self.lbl_listName = tk.Label(self.top)
        self.lbl_listName.place(relx=0.284, rely=0.079, height=24, width=70)
        self.lbl_listName.configure(activebackground="#d9d9d9")
        self.lbl_listName.configure(activeforeground="black")
        self.lbl_listName.configure(anchor='w')
        self.lbl_listName.configure(background="#d9d9d9")
        self.lbl_listName.configure(compound='left')
        self.lbl_listName.configure(disabledforeground="#a3a3a3")
        self.lbl_listName.configure(font="-family {Segoe UI} -size 9")
        self.lbl_listName.configure(foreground="#000000")
        self.lbl_listName.configure(highlightbackground="#d9d9d9")
        self.lbl_listName.configure(highlightcolor="#000000")
        self.lbl_listName.configure(text='''List''')

        self.txt_listName = tk.Text(self.top)
        self.txt_listName.place(relx=0.361, rely=0.079, relheight=0.028
                , relwidth=0.193)
        self.txt_listName.configure(background="white")
        self.txt_listName.configure(font="TkTextFont")
        self.txt_listName.configure(foreground="black")
        self.txt_listName.configure(highlightbackground="#d9d9d9")
        self.txt_listName.configure(highlightcolor="#000000")
        self.txt_listName.configure(insertbackground="#000000")
        self.txt_listName.configure(selectbackground="#d9d9d9")
        self.txt_listName.configure(selectforeground="black")
        self.txt_listName.configure(wrap="word")

        self.lbl_completion = tk.Label(self.top)
        self.lbl_completion.place(relx=0.284, rely=0.282, height=24, width=67)
        self.lbl_completion.configure(activebackground="#d9d9d9")
        self.lbl_completion.configure(activeforeground="black")
        self.lbl_completion.configure(anchor='w')
        self.lbl_completion.configure(background="#d9d9d9")
        self.lbl_completion.configure(compound='left')
        self.lbl_completion.configure(disabledforeground="#a3a3a3")
        self.lbl_completion.configure(font="-family {Segoe UI} -size 9")
        self.lbl_completion.configure(foreground="#000000")
        self.lbl_completion.configure(highlightbackground="#d9d9d9")
        self.lbl_completion.configure(highlightcolor="#000000")
        self.lbl_completion.configure(text='''Completed''')

        self.cb_completion = ttk.Checkbutton(self.top)
        self.cb_completion.place(relx=0.361, rely=0.281, relwidth=0.053
                , relheight=0.0, height=24)
        self.cb_completion.configure(variable=self.tch69)
        self.cb_completion.configure(compound='left')

        self.btn_newList = tk.Button(self.top, command=newListClick)
        self.btn_newList.place(relx=0.361, rely=0.147, height=25, width=75)
        self.btn_newList.configure(activebackground="#d9d9d9")
        self.btn_newList.configure(activeforeground="black")
        self.btn_newList.configure(background="#d9d9d9")
        self.btn_newList.configure(disabledforeground="#a3a3a3")
        self.btn_newList.configure(font="-family {Segoe UI} -size 9")
        self.btn_newList.configure(foreground="#000000")
        self.btn_newList.configure(highlightbackground="#d9d9d9")
        self.btn_newList.configure(highlightcolor="#000000")
        self.btn_newList.configure(text='''New List''')

        self.btn_deleteList = tk.Button(self.top, command=deleteListClick)
        self.btn_deleteList.place(relx=0.483, rely=0.147, height=26, width=75)
        self.btn_deleteList.configure(activebackground="#d9d9d9")
        self.btn_deleteList.configure(activeforeground="black")
        self.btn_deleteList.configure(background="#d9d9d9")
        self.btn_deleteList.configure(disabledforeground="#a3a3a3")
        self.btn_deleteList.configure(font="-family {Segoe UI} -size 9")
        self.btn_deleteList.configure(foreground="#000000")
        self.btn_deleteList.configure(highlightbackground="#d9d9d9")
        self.btn_deleteList.configure(highlightcolor="#000000")
        self.btn_deleteList.configure(text='''Delete''')

        self.btn_removeActivity = tk.Button(self.top, command=removeActivityClick)
        self.btn_removeActivity.place(relx=0.432, rely=0.611, height=26
                , width=55)
        self.btn_removeActivity.configure(activebackground="#d9d9d9")
        self.btn_removeActivity.configure(activeforeground="black")
        self.btn_removeActivity.configure(background="#d9d9d9")
        self.btn_removeActivity.configure(disabledforeground="#a3a3a3")
        self.btn_removeActivity.configure(font="-family {Segoe UI} -size 9")
        self.btn_removeActivity.configure(foreground="#000000")
        self.btn_removeActivity.configure(highlightbackground="#d9d9d9")
        self.btn_removeActivity.configure(highlightcolor="#000000")
        self.btn_removeActivity.configure(text='''Remove''')

# The following code is added to facilitate the Scrolled widgets you specified.
class AutoScroll(object):
    '''Configure the scrollbars for a widget.'''
    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = ttk.Scrollbar(master, orient='vertical', command=self.yview)
        except:
            pass
        hsb = ttk.Scrollbar(master, orient='horizontal', command=self.xview)
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))
        self.grid(column=0, row=0, sticky='nsew')
        try:
            vsb.grid(column=1, row=0, sticky='ns')
        except:
            pass
        hsb.grid(column=0, row=1, sticky='ew')
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)
        # Copy geometry methods of master  (taken from ScrolledText.py)
        methods = tk.Pack.__dict__.keys() | tk.Grid.__dict__.keys() \
                  | tk.Place.__dict__.keys()
        for meth in methods:
            if meth[0] != '_' and meth not in ('config', 'configure'):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        '''Hide and show scrollbar as needed.'''
        def wrapped(first, last):
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)
        return wrapped

    def __str__(self):
        return str(self.master)

def _create_container(func):
    '''Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget.'''
    def wrapped(cls, master, **kw):
        container = ttk.Frame(master)
        container.bind('<Enter>', lambda e: _bound_to_mousewheel(e, container))
        container.bind('<Leave>', lambda e: _unbound_to_mousewheel(e, container))
        return func(cls, container, **kw)
    return wrapped

class ScrolledListBox(AutoScroll, tk.Listbox):
    '''A standard Tkinter Listbox widget with scrollbars that will
    automatically show/hide as needed.'''
    @_create_container
    def __init__(self, master, **kw):
        tk.Listbox.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)
    def size_(self):
        sz = tk.Listbox.size(self)
        return sz

import platform
def _bound_to_mousewheel(event, widget):
    child = widget.winfo_children()[0]
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        child.bind_all('<MouseWheel>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-MouseWheel>', lambda e: _on_shiftmouse(e, child))
    else:
        child.bind_all('<Button-4>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Button-5>', lambda e: _on_mousewheel(e, child))
        child.bind_all('<Shift-Button-4>', lambda e: _on_shiftmouse(e, child))
        child.bind_all('<Shift-Button-5>', lambda e: _on_shiftmouse(e, child))

def _unbound_to_mousewheel(event, widget):
    if platform.system() == 'Windows' or platform.system() == 'Darwin':
        widget.unbind_all('<MouseWheel>')
        widget.unbind_all('<Shift-MouseWheel>')
    else:
        widget.unbind_all('<Button-4>')
        widget.unbind_all('<Button-5>')
        widget.unbind_all('<Shift-Button-4>')
        widget.unbind_all('<Shift-Button-5>')

def _on_mousewheel(event, widget):
    if platform.system() == 'Windows':
        widget.yview_scroll(-1*int(event.delta/120),'units')
    elif platform.system() == 'Darwin':
        widget.yview_scroll(-1*int(event.delta),'units')
    else:
        if event.num == 4:
            widget.yview_scroll(-1, 'units')
        elif event.num == 5:
            widget.yview_scroll(1, 'units')

def _on_shiftmouse(event, widget):
    if platform.system() == 'Windows':
        widget.xview_scroll(-1*int(event.delta/120), 'units')
    elif platform.system() == 'Darwin':
        widget.xview_scroll(-1*int(event.delta), 'units')
    else:
        if event.num == 4:
            widget.xview_scroll(-1, 'units')
        elif event.num == 5:
            widget.xview_scroll(1, 'units')
def start_up():
    To_Do_List_support.main()

if __name__ == '__main__':
    To_Do_List_support.main()




