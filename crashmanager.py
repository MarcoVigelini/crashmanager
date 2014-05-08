# Copyright 2009, Marco Vigelini
# This file contains the logic of the application crashmanager.
# The graphical user interface is defined into the file crashmanagergui.py

from PySide import QtCore, QtGui
from PySide.QtGui import *
from PySide.QtCore import *
import crashmanagergui
import sys, time
import os
import shutil
import cx_Oracle
import csv
import time
import subprocess
import select


SUCCESS = 0
FAIL = 255
ORA_ERROR_FOUND = -2
sql_stmt = "" # global variable containing the sql statement to be executed

class Thread(QThread):
    dataReady = Signal(object)

    #def __init__(self, parent = None):
    #    QThread.__init__(self, parent)
    #    self._continue = True;

    #def stop(self):
    #    self._continue = False;
    #    time.sleep(2)

    def run(self):
        #filename = '/var/log/syslog'
        is_first_time = True
        filename = '/tmp/test.txt'
        f = subprocess.Popen(['tail','-F',filename], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p = select.poll()
        p.register(f.stdout)

        #while self._continue:
        while True:
            if p.poll(1):
                #self.previus_data = self.data
                self.data = f.stdout.readline()
                if is_first_time:
                    previous_data = self.data
                    is_first_time = False
                    print "Uguali:", self.data, type(self.data), previous_data
                elif previous_data != self.data:
                    # this will add a ref to self.data and avoid the destruction 
                    self.dataReady.emit(self.data) 
                    print "Differenti:", self.data, type(self.data), previous_data
                    previous_data = self.data
            time.sleep(1)


class MyThread(QThread):
        def __init__(self, parent = None):
                QThread.__init__(self, parent)
                self.exiting = False

        def run(self):
            while self.exiting==False:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)


class crashmanager(QtGui.QMainWindow, crashmanagergui.Ui_MainWindow):
    """
    crashmanager is inherited from both QtGui.QMainWindow and crashmanagergui.Ui_MainWindow
    """
    def __init__(self,parent=None):
        """
            Initialization of the class. Call the __init__ for the super classes
        """
        super(crashmanager,self).__init__(parent)
        self.setupUi(self)
        self.connectActions()
        self.data = ""
        self._continue = True

        #self.thread = MyThread()
        self.thread = Thread()
        self.thread.dataReady.connect(self.get_data, Qt.QueuedConnection)
        self.thread.start()

    def main(self):
        self.show()

        # tail -f of the alert log
#        self.cm_tail_alert_log()

    def connectActions(self):
        """
        Connect the user interface controls to the logic
        """
        #self.cmdWrite.clicked.connect(self.myprint)      
        self.pushButton.clicked.connect(self.push_button_clicked)
        self.pushButton_2.clicked.connect(self.greetings)

        # radioButtons connected to the "Complete Recovery" (first) tab
        # First column of radioButtons
        self.radioButton_NONSYSTEMDATA.clicked.connect(self.radio_button_selected)
        self.radioButton_TEMPORARYDATA.clicked.connect(self.radio_button_selected)
        self.radioButton_SYSTEMDATA.clicked.connect(self.radio_button_selected)
        self.radioButton_UNDODATA.clicked.connect(self.radio_button_selected)
        self.radioButton_ALLDATA.clicked.connect(self.radio_button_selected)

        # Second column of radioButtons
        self.radioButton_READONLYTBS.clicked.connect(self.radio_button_selected)
        self.radioButton_10.clicked.connect(self.radio_button_selected) #TBD INDEX
        self.radioButton_21.clicked.connect(self.radio_button_selected) #TBD INDEX
        #self.radioButton_10.setEnabled(False)
        #self.radioButton_21.setEnabled(False)
        self.radioButton_NONSYSTEMTBS.clicked.connect(self.radio_button_selected)
        self.radioButton_TEMPORARYTBS.clicked.connect(self.radio_button_selected)
        self.radioButton_SYSTEMTBS.clicked.connect(self.radio_button_selected)
        self.radioButton_UNDOTBS.clicked.connect(self.radio_button_selected)

        # Third column of radioButtons
        self.radioButton_SPFILE.clicked.connect(self.radio_button_selected)

        # radioButtons connected to the "Incomplete Recovery" (second) tab
        self.radioButton_22.clicked.connect(self.radio_button_selected)
        self.radioButton_23.clicked.connect(self.radio_button_selected)
        self.radioButton_24.clicked.connect(self.radio_button_selected)
        self.radioButton_25.clicked.connect(self.radio_button_selected)
        self.radioButton_26.clicked.connect(self.radio_button_selected)
        self.radioButton_27.clicked.connect(self.radio_button_selected)
        self.radioButton_28.clicked.connect(self.radio_button_selected)
        self.radioButton_29.clicked.connect(self.radio_button_selected)
        self.radioButton_30.clicked.connect(self.radio_button_selected)
        self.radioButton_31.clicked.connect(self.radio_button_selected)
        self.radioButton_32.clicked.connect(self.radio_button_selected)
        self.radioButton_33.clicked.connect(self.radio_button_selected)
        self.radioButton_34.clicked.connect(self.radio_button_selected)

        # radioButtons connected to the "Flashback Recovery" (third) tab
        self.radioButton_35.clicked.connect(self.radio_button_selected)
        self.radioButton_36.clicked.connect(self.radio_button_selected)
        self.radioButton_37.clicked.connect(self.radio_button_selected)
        self.radioButton_38.clicked.connect(self.radio_button_selected)
        self.radioButton_39.clicked.connect(self.radio_button_selected)
        self.radioButton_40.clicked.connect(self.radio_button_selected)
        self.radioButton_41.clicked.connect(self.radio_button_selected)
        self.radioButton_42.clicked.connect(self.radio_button_selected)
        self.radioButton_43.clicked.connect(self.radio_button_selected)
        self.radioButton_44.clicked.connect(self.radio_button_selected)
        self.radioButton_45.clicked.connect(self.radio_button_selected)
        self.radioButton_46.clicked.connect(self.radio_button_selected)
        self.radioButton_47.clicked.connect(self.radio_button_selected)

        # radioButtons connected to the "Control File" (fourth) tab
        self.radioButton_7.clicked.connect(self.radio_button_selected)
        self.radioButton_8.clicked.connect(self.radio_button_selected)
        # ...

        # radioButtons connected to the "Redo Log" (fifth) tab
        self.radioButton_15.clicked.connect(self.radio_button_selected)
        self.radioButton_16.clicked.connect(self.radio_button_selected)
        self.radioButton_17.clicked.connect(self.radio_button_selected)
        self.radioButton_18.clicked.connect(self.radio_button_selected)
        self.radioButton_19.clicked.connect(self.radio_button_selected)
        self.radioButton_20.clicked.connect(self.radio_button_selected)

        #self.tabWidget.currentChanged(int).connect(self.tab_selected(int))
        #QtCore.QObject.connect(self.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.textBrowser.clear)

        #self.connect(self.tabWidget, QtCore.SIGNAL("currentChanged(int)"), self.tab_selected());
        self.connect(self.tab_2, QtCore.SIGNAL("mousePressEvent()"), self.tab_selected());
        
    def cm_tail_alert_log(self):
        filename = '/var/log/syslog'
        f = subprocess.Popen(['tail','-F',filename], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        p = select.poll()
        p.register(f.stdout)

        while True:
            if p.poll(1):
                self.textBrowser_ALERTLOG.insertPlainText(f.stdout.readline())
#                print f.stdout.readline()
            time.sleep(1)

    def tab_selected(self):
        print self.tabWidget.currentIndex()

    def radio_button_selected(self):
        self.textBrowser.clear()
        print "radio_button_selected: tab->", self.tabWidget.currentIndex()
        if self.tabWidget.currentIndex() == 0:
            if self.radioButton_NONSYSTEMDATA.isChecked(): # Loss of a non-system datafile
                self.textBrowser.insertPlainText("In this scenario you are going to lose one datafile of a non-system tablespace. "
                                                 + "You don't need to recover the entire database or all datafiles of the tablespace. "
                                                 + "You need to recover only the lost datafile.")
            elif self.radioButton_TEMPORARYDATA.isChecked(): # Loss of a temporary datafile
                self.textBrowser.insertPlainText("In this scenario you are going to lose one locally-managed tempfile of a temporary tablespace.")
            elif self.radioButton_SYSTEMDATA.isChecked(): # Loss of a system datafile
                self.textBrowser.insertPlainText("In this scenario you are going to lose one datafile of a system tablespace.")
            elif self.radioButton_UNDODATA.isChecked(): # Loss of an UNDO datafile
                self.textBrowser.insertPlainText("In this scenario you are going to lose one datafile of an UNDO tablespace.")
            elif self.radioButton_ALLDATA.isChecked(): # Loss of all datafiles
                self.textBrowser.insertPlainText("In this scenario you are going to lose some or all datafiles of a non-system tablespace.  "
                                                 + "You don't need to recover the entire database, but you need to recover all datafiles of the affected tablespace.")
            elif self.radioButton_READONLYTBS.isChecked(): # Loss of a Read-Only tablespace
                self.textBrowser.insertPlainText("In this scenario you are going to lose a READ ONLY tablespace.")
            elif self.radioButton_10.isChecked(): # Loss of a Index tablespace
                self.textBrowser.insertPlainText("In this scenario you are going to lose a Index tablespace.")
            elif self.radioButton_21.isChecked(): # Loss of all indexes in USERS tablespace
                self.textBrowser.insertPlainText("In this scenario you are going to lose all indexes in USERS tablespace.")
            elif self.radioButton_NONSYSTEMTBS.isChecked(): # Loss of a non-system tablespace
                self.textBrowser.insertPlainText("In this scenario you are going to lose a non-system tablespace.")
            elif self.radioButton_TEMPORARYTBS.isChecked(): # Loss of a temporary tablespace
                self.textBrowser.insertPlainText("In this scenario you are going to lose a temporary tablespace.")
            elif self.radioButton_SYSTEMTBS.isChecked(): # Loss of a SYSTEM tablespace
                self.textBrowser.insertPlainText("In this scenario you are going to lose a SYSTEM tablespace.")
            elif self.radioButton_UNDOTBS.isChecked(): # Loss of the UNDO tablespace
                self.textBrowser.insertPlainText("In this scenario you are going to lose the UNDO tablespace.")
            elif self.radioButton_SPFILE.isChecked(): # Loss of the spfile
                self.textBrowser.insertPlainText("In this scenario you are going to lose your server parameter file.")
            self.deselect_radioButton_tab1(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab2(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab3(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab4(self.tabWidget.currentIndex())
        elif self.tabWidget.currentIndex() == 1:
            if self.radioButton_24.isChecked(): 
                self.textBrowser.insertPlainText("")
            self.deselect_radioButton_tab0(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab2(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab3(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab4(self.tabWidget.currentIndex())
        elif self.tabWidget.currentIndex() == 2:
            if self.radioButton_37.isChecked(): 
                self.textBrowser.insertPlainText("")
            self.deselect_radioButton_tab0(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab1(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab3(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab4(self.tabWidget.currentIndex())
        elif self.tabWidget.currentIndex() == 3:
            self.deselect_radioButton_tab0(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab1(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab2(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab4(self.tabWidget.currentIndex())
        elif self.tabWidget.currentIndex() == 4:
            self.deselect_radioButton_tab0(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab1(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab2(self.tabWidget.currentIndex())
            self.deselect_radioButton_tab3(self.tabWidget.currentIndex())

    def deselect_radioButton_tab0(self, index):
            # Set to False
            self.radioButton_NONSYSTEMDATA.setCheckable(False)
            self.radioButton_TEMPORARYDATA.setCheckable(False)
            self.radioButton_SYSTEMDATA.setCheckable(False)
            self.radioButton_UNDODATA.setCheckable(False)
            self.radioButton_ALLDATA.setCheckable(False)
            self.radioButton_READONLYTBS.setCheckable(False)
            self.radioButton_10.setCheckable(False)
            self.radioButton_21.setCheckable(False)
            self.radioButton_NONSYSTEMTBS.setCheckable(False)
            self.radioButton_TEMPORARYTBS.setCheckable(False)
            self.radioButton_SYSTEMTBS.setCheckable(False)
            self.radioButton_UNDOTBS.setCheckable(False)
            self.radioButton_SPFILE.setCheckable(False)
            # Set to True
            self.radioButton_NONSYSTEMDATA.setCheckable(True)
            self.radioButton_TEMPORARYDATA.setCheckable(True)
            self.radioButton_SYSTEMDATA.setCheckable(True)
            self.radioButton_UNDODATA.setCheckable(True)
            self.radioButton_ALLDATA.setCheckable(True)
            self.radioButton_READONLYTBS.setCheckable(True)
            self.radioButton_10.setCheckable(True)
            self.radioButton_21.setCheckable(True)
            self.radioButton_NONSYSTEMTBS.setCheckable(True)
            self.radioButton_TEMPORARYTBS.setCheckable(True)
            self.radioButton_SYSTEMTBS.setCheckable(True)
            self.radioButton_UNDOTBS.setCheckable(True)
            self.radioButton_SPFILE.setCheckable(True)

    def deselect_radioButton_tab1(self, index):
            # Set to False
            self.radioButton_22.setCheckable(False)
            self.radioButton_23.setCheckable(False)
            self.radioButton_24.setCheckable(False)
            self.radioButton_25.setCheckable(False)
            self.radioButton_26.setCheckable(False)
            self.radioButton_27.setCheckable(False)
            self.radioButton_28.setCheckable(False)
            self.radioButton_29.setCheckable(False)
            self.radioButton_30.setCheckable(False)
            self.radioButton_31.setCheckable(False)
            self.radioButton_32.setCheckable(False)
            self.radioButton_33.setCheckable(False)
            self.radioButton_34.setCheckable(False)
            # Set to True
            self.radioButton_22.setCheckable(True)
            self.radioButton_23.setCheckable(True)
            self.radioButton_24.setCheckable(True)
            self.radioButton_25.setCheckable(True)
            self.radioButton_26.setCheckable(True)
            self.radioButton_27.setCheckable(True)
            self.radioButton_28.setCheckable(True)
            self.radioButton_29.setCheckable(True)
            self.radioButton_30.setCheckable(True)
            self.radioButton_31.setCheckable(True)
            self.radioButton_32.setCheckable(True)
            self.radioButton_33.setCheckable(True)
            self.radioButton_34.setCheckable(True)
 
    def deselect_radioButton_tab2(self, index):
            # Set to False
            self.radioButton_35.setCheckable(False)
            self.radioButton_36.setCheckable(False)
            self.radioButton_37.setCheckable(False)
            self.radioButton_38.setCheckable(False)
            self.radioButton_39.setCheckable(False)
            self.radioButton_40.setCheckable(False)
            self.radioButton_41.setCheckable(False)
            self.radioButton_42.setCheckable(False)
            self.radioButton_43.setCheckable(False)
            self.radioButton_44.setCheckable(False)
            self.radioButton_45.setCheckable(False)
            self.radioButton_46.setCheckable(False)
            self.radioButton_47.setCheckable(False)
            # Set to True
            self.radioButton_35.setCheckable(True)
            self.radioButton_36.setCheckable(True)
            self.radioButton_37.setCheckable(True)
            self.radioButton_38.setCheckable(True)
            self.radioButton_39.setCheckable(True)
            self.radioButton_40.setCheckable(True)
            self.radioButton_41.setCheckable(True)
            self.radioButton_42.setCheckable(True)
            self.radioButton_43.setCheckable(True)
            self.radioButton_44.setCheckable(True)
            self.radioButton_45.setCheckable(True)
            self.radioButton_46.setCheckable(True)
            self.radioButton_47.setCheckable(True)
 
    def deselect_radioButton_tab3(self, index):
            # Set to False
            self.radioButton_7.setCheckable(False)
            self.radioButton_8.setCheckable(False)
            # Set to True
            self.radioButton_7.setCheckable(True)
            self.radioButton_8.setCheckable(True)

    def deselect_radioButton_tab4(self, index):
            # Set to False
            self.radioButton_15.setCheckable(False)
            self.radioButton_16.setCheckable(False)
            self.radioButton_17.setCheckable(False)
            self.radioButton_18.setCheckable(False)
            self.radioButton_19.setCheckable(False)
            self.radioButton_20.setCheckable(False)
            # Set to True
            self.radioButton_15.setCheckable(True)
            self.radioButton_16.setCheckable(True)
            self.radioButton_17.setCheckable(True)
            self.radioButton_18.setCheckable(True)
            self.radioButton_19.setCheckable(True)
            self.radioButton_20.setCheckable(True)

    def deselect_radioButton(self, index):
        """
        Replaced with deselect_radioButton_tab0..tab4
        """
        """
        It deselects all radioButtons not connected to the current tab 
        I don't want that a previous selected radioButton is checked when
        the user, switching between tabs, has selected another radioButton.
        """
        #print "deselect_radioButton: index->", index
        if index == 0:
            self.radioButton_37.setCheckable(False)
            self.radioButton_37.setCheckable(True)
            #self.radioButton_37.setChecked(False)
        elif index == 1:
            # Set to False
            self.radioButton_NONSYSTEMDATA.setCheckable(False)
            # Set to True
            self.radioButton_NONSYSTEMDATA.setCheckable(True)

            self.radioButton_37.setCheckable(False)
            self.radioButton_37.setCheckable(True)
        elif index == 2:
            # Set to False
            self.radioButton_SPFILE.setCheckable(False)
            # Set to True
            self.radioButton_SPFILE.setCheckable(True)
            
            self.radioButton_24.setCheckable(False)
            self.radioButton_24.setCheckable(True)
        elif index == 3:
             # Set to False
            self.radioButton_NONSYSTEMDATA.setCheckable(False)
            # Set to True
            self.radioButton_NONSYSTEMDATA.setCheckable(True)

    def get_data(self, data):
        print "get_data...."
        self.data = data
        self.textBrowser_ALERTLOG.insertPlainText(self.data)

#    def paintEvent(self, event):
#        print "event", event
#        self.textBrowser_ALERTLOG.insertPlainText(self.data)

    def push_button_clicked(self):
        self.textBrowser_ALERTLOG.insertPlainText(self.data)
        """ Old code from MyThread
        if self.thread.isRunning():
            self.thread.exiting=True
            #self.batchbutton.setEnabled(False)
            while self.thread.isRunning():
                time.sleep(0.01)
                continue
            #self.batchbutton.setText('Start batch')
            #self.batchbutton.setEnabled(True)
        else:
            self.thread.exiting=False
            self.thread.start()
            #self.batchbutton.setEnabled(False)
            while not self.thread.isRunning():
                time.sleep(0.01)
                continue
            #self.batchbutton.setText('Stop batch')
            #self.batchbutton.setEnabled(True)
        """

        """
        print self.tabWidget.currentIndex()
        print self.radioButton_NONSYSTEMDATA.isChecked()
        if self.tabWidget.currentIndex() == 0:
            #print 'user on first tab', self.tabWidget.currentIndex()
            if self.radioButton_NONSYSTEMDATA.isChecked(): 
                self.menu_id_05()
            elif self.radioButton_TEMPORARYDATA.isChecked():
                self.menu_id_06()
            elif self.radioButton_SYSTEMDATA.isChecked():
                self.menu_id_07()
            elif self.radioButton_UNDODATA.isChecked():
                self.menu_id_08()
            elif self.radioButton_ALLDATA.isChecked():
                self.menu_id_17()
            elif self.radioButton_READONLYTBS.isChecked():
                self.menu_id_09()
            elif self.radioButton_10.isChecked():
                self.menu_id_05()
            elif self.radioButton_21.isChecked():
                self.menu_id_05()
            elif self.radioButton_NONSYSTEMTBS.isChecked():
                self.menu_id_12()
            elif self.radioButton_TEMPORARYTBS.isChecked():
                self.menu_id_13()
            elif self.radioButton_SYSTEMTBS.isChecked():
                self.menu_id_14()
            elif self.radioButton_UNDOTBS.isChecked():
                self.menu_id_15()
            elif self.radioButton_SPFILE.isChecked():
                self.menu_id_16()
        elif self.tabWidget.currentIndex() == 1:
            print 'user on second tab', self.tabWidget.currentIndex()
        elif self.tabWidget.currentIndex() == 2:
            print 'user on third tab', self.tabWidget.currentIndex()
        elif self.tabWidget.currentIndex() == 3:
            print 'user on fourth tab', self.tabWidget.currentIndex()
        """

    def greetings(self):
        print ("Hello %s" % self.label.setText("nuova descrizione"))
    
    def cm_set_sql_stmt(self, operation):
        global sql_stmt

        if operation == "CONTROLFILES":
            sql_stmt = "select name from v\$controlfile"
        elif operation == "NONSYSTEMDATA" or operation == "NONSYSTEMTBS":
            sql_stmt = "select FILE_NAME from dba_data_files where TABLESPACE_NAME='USERS' order by FILE_ID"
        elif operation == "TEMPORARYDATA" or operation == "TEMPORARYTBS":
            sql_stmt = "select file_name \
                        from dba_users, dba_temp_files \
                        where tablespace_name = temporary_tablespace \
                        and username = 'SYS'"
        elif operation == "SYSTEMDATA" or operation == "SYSTEMTBS":
            sql_stmt = "select FILE_NAME from dba_data_files where TABLESPACE_NAME='SYSTEM' order by FILE_ID"
        elif operation == "UNDODATA" or operation == "UNDOTBS":
            sql_stmt = "select FILE_NAME \
                        from dba_data_files a, dba_tablespaces b \
                        where b.STATUS = 'ONLINE' \
                        and b.CONTENTS = 'UNDO' \
                        and a.TABLESPACE_NAME = b.TABLESPACE_NAME \
                        order by FILE_ID"
        elif operation == "READONLYTBS":
            sql_stmt = "select file_name \
                        from dba_data_files a, dba_tablespaces b \
                        where b.STATUS = 'READ ONLY' \
                        and b.TABLESPACE_NAME = a.TABLESPACE_NAME \
                        order by FILE_ID"
        elif operation == "SPFILE":
            sql_stmt = "ls -gGl /home/oracle/app/oracle/product/11.2.0/dbhome_2/dbs/*ora |awk '{print $7}' > /tmp/spfile.tmp"
        elif operation == "ALLDATA":
            sql_stmt = "select FILE_NAME from dba_data_files order by FILE_ID"
        elif operation == "REDOMEMBER":
            sql_stmt = "select member \
                        from  v\$log a, v\$logfile b \
                        where a.group# = b.group# \
                        and a.status = 'CURRENT'"
        elif operation == "INACTIVEGROUP":
            sql_stmt = "select member \
                        from  v\$log a, v\$logfile b \
                        where a.group# = b.group# \
                        and a.status = 'INACTIVE' \
                        order by b.group#, member"
        elif operation == "ACTIVEGROUP":
            #execute immediate 'alter system switch logfile';
            sql_stmt = "select member  \
                        from  v\$log a, v\$logfile b \
                        where a.group# = b.group# \
                        and a.status = 'ACTIVE' \
                        order by b.group#, member"
        elif operation == "CURRENTGROUP":
            sql_stmt = "select member  \
                        from  v\$log a, v\$logfile b \
                        where a.group# = b.group# \
                        and a.status = 'CURRENT' \
                        order by b.group#, member"
        else:
            sql_stmt = ""

    def cm_spool_query_to_tmp(self, tmp_file_name):
        global sql_stmt

        if sql_stmt == "":
            return -1
        return 0

        #os.putenv('ORACLE_HOME','...')
        #os.putenv('LD_LIBRARY_PATH', '...')

        out_file=open(tmp_file_name,"w");
        writer = csv.writer(out_file, delimiter='\t', quotechar='\'', quoting=csv.QUOTE_ALL)

        connection = cx_Oracle.connect('/', mode = cx_Oracle.SYSDBA)

        cursor = connection.cursor()
        cursor.execute(SQL)
        for row in cursor:
            #print row # ('/app/oracle/oradata/CDB001/system01.dbf', 1, 'SYSTEM')
            writer.writerow(row)
        cursor.close()
        connection.close()
        out_file.close()

        return 0
        
    def cm_count_files(self, file_name):
        num_lines = 0
        if os.path.isfile(file_name):
            if 'ORA-' in open(file_name).read():
                return ORA_ERROR_FOUND
            else:
                num_lines = sum(1 for line in open(file_name))
        print "-------------", num_lines
        return num_lines

    def cm_read_files(self, fname):
        return [line.rstrip('\n')[1:-1] for line in open(fname)]

    # Menu 5 selected: LOSS OF A NON-SYSTEM DATAFILE
    def menu_id_05(self):
        global sql_stmt
      
        # Read from database the non-system datafile's location
        # redirecting the output to a tmp file
        self.cm_set_sql_stmt("NONSYSTEMDATA")

        tmp_file_name = "/tmp/non_system_datafile.tmp"
        return_val = self.cm_spool_query_to_tmp(tmp_file_name)
        print sql_stmt
   
        if return_val == -1:
            ERRMSG="Can not proceed. Sql statement is not set"
            self.textBrowser.append("\n" + ERRMSG)
            return SUCCESS

        # Counting the number of non-system datafiles found
        # Possible returning values: 0 ===============> temporary file empty
        #                            1 ===============> One datafile found
        #                            ORA_ERROR_FOUND => ORA-% found into the temporary file
        #                            > 1 =============> more datafiles found
        return_val = self.cm_count_files(tmp_file_name)
        if return_val == 0:
                ERRMSG="Can not proceed. Temporary file is empty."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        elif return_val == 1:
                ERRMSG="Can not proceed. Your database has just one non-system datafile. "
                self.textBrowser.append("\n" + ERRMSG)
                ERRMSG="Check the 'Loss of a non-system tablespace' radio button if you want to perform a loss of all non-system datafiles of USERS tablespace."
                self.textBrowser.append(ERRMSG)
                return SUCCESS
        elif return_val == ORA_ERROR_FOUND:
                ERRMSG="Not able to find information on your non-system datafile. Be sure your database is up and running."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        else:
                self.textBrowser.append("testing...\n")
                """
                # Read all lines of the file
                lines_read = self.cm_read_files(tmp_file_name)
                
                # Processing just the first file found into the tmp_file_name
                file_renamed = lines_read[0] + ".bck" # Renaming just the first file name
                try:
                    shutil.copyfile(lines_read[0], file_renamed)
                    os.unlink(lines_read[0]) 
                except IOError as why:
                    self.textBrowser.append("\n" + str(why))
                """
        """ 
        cm_kill_instance
        """
    # Menu 6 selected: LOSS OF A TEMPORARY DATAFILE
    def menu_id_06(self):
        global sql_stmt
      
        # Read from database the non-system datafile's location
        # redirecting the output to a tmp file
        self.cm_set_sql_stmt("TEMPORARYDATA")

        tmp_file_name = "/tmp/temporary_datafile.tmp"
        return_val = self.cm_spool_query_to_tmp(tmp_file_name)
        print sql_stmt
   
        if return_val == -1:
            ERRMSG="Can not proceed. Sql statement is not set"
            self.textBrowser.append("\n" + ERRMSG)
            return SUCCESS

        # Counting the number of non-system datafiles found
        # Possible returning values: 0 ===============> temporary file empty
        #                            1 ===============> One datafile found
        #                            ORA_ERROR_FOUND => ORA-% found into the temporary file
        #                            > 1 =============> more datafiles found
        return_val = self.cm_count_files(tmp_file_name)
        if return_val == 0:
                ERRMSG="Can not proceed. Temporary file is empty."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        elif return_val == 1:
                ERRMSG="Can not proceed. Your database has just one temporary datafile. "
                self.textBrowser.append("\n" + ERRMSG)
                ERRMSG="Check the 'Loss of a temporary tablespace' radio button if you want to perform a loss of all temporary datafiles of the temporary tablespace."
                self.textBrowser.append(ERRMSG)
                return SUCCESS
        elif return_val == ORA_ERROR_FOUND:
                ERRMSG="Not able to find information on your temporary datafile. Be sure your database is up and running."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        else:
                # Read all lines of the file
                lines_read = self.cm_read_files(tmp_file_name)
                
                # Processing just the first file found into the tmp_file_name
                file_renamed = lines_read[0] + ".bck" # Renaming just the first file name
                try:
                    shutil.copyfile(lines_read[0], file_renamed)
                    os.unlink(lines_read[0]) 
                except IOError as why:
                    self.textBrowser.append("\n" + str(why))
        """ 
        cm_kill_instance
        """

    # Menu 7 selected: LOSS OF A SYSTEM DATAFILE
    def menu_id_07(self):
        global sql_stmt
      
        # Read from database the system datafile's location
        # redirecting the output to a tmp file
        self.cm_set_sql_stmt("SYSTEMDATA")

        tmp_file_name = "/tmp/system_datafile.tmp"
        return_val = self.cm_spool_query_to_tmp(tmp_file_name)
        print sql_stmt
   
        if return_val == -1:
            ERRMSG="Can not proceed. Sql statement is not set"
            self.textBrowser.append("\n" + ERRMSG)
            return SUCCESS

        # Counting the number of system datafiles found
        # Possible returning values: 0 ===============> temporary file empty
        #                            1 ===============> One datafile found
        #                            ORA_ERROR_FOUND => ORA-% found into the temporary file
        #                            > 1 =============> more datafiles found
        return_val = self.cm_count_files(tmp_file_name)
        if return_val == 0:
                ERRMSG="Can not proceed. Temporary file is empty."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        elif return_val == 1:
                ERRMSG="Can not proceed. Your database has just one system datafile. "
                self.textBrowser.append("\n" + ERRMSG)
                ERRMSG="Check the 'Loss of the SYSTEM tablespace' radio button if you want to perform a loss of all datafiles of the SYSTEM tablespace."
                self.textBrowser.append(ERRMSG)
                return SUCCESS
        elif return_val == ORA_ERROR_FOUND:
                ERRMSG="Not able to find information on your system datafile. Be sure your database is up and running."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        else:
                # Read all lines of the file
                lines_read = self.cm_read_files(tmp_file_name)
                
                # Processing just the first file found into the tmp_file_name
                file_renamed = lines_read[0] + ".bck" # Renaming just the first file name
                try:
                    shutil.copyfile(lines_read[0], file_renamed)
                    os.unlink(lines_read[0]) 
                except IOError as why:
                    self.textBrowser.append("\n" + str(why))
        """ 
        cm_kill_instance
        """

    # Menu 8 selected: LOSS OF A UNDO DATAFILE
    def menu_id_08(self):
        global sql_stmt
      
        # Read from database the undo datafile's location
        # redirecting the output to a tmp file
        self.cm_set_sql_stmt("UNDODATA")

        tmp_file_name = "/tmp/undo_datafile.tmp"
        return_val = self.cm_spool_query_to_tmp(tmp_file_name)
        print sql_stmt
   
        if return_val == -1:
            ERRMSG="Can not proceed. Sql statement is not set"
            self.textBrowser.append("\n" + ERRMSG)
            return SUCCESS

        # Counting the number of undo datafiles found
        # Possible returning values: 0 ===============> temporary file empty
        #                            1 ===============> One datafile found
        #                            ORA_ERROR_FOUND => ORA-% found into the temporary file
        #                            > 1 =============> more datafiles found
        return_val = self.cm_count_files(tmp_file_name)
        if return_val == 0:
                ERRMSG="Can not proceed. Temporary file is empty."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        elif return_val == 1:
                ERRMSG="Can not proceed. Your database has just one undo datafile. "
                self.textBrowser.append("\n" + ERRMSG)
                ERRMSG="Check the 'Loss of the UNDO tablespace' radio button if you want to perform a loss of all datafiles of the UNDO tablespace."
                self.textBrowser.append(ERRMSG)
                return SUCCESS
        elif return_val == ORA_ERROR_FOUND:
                ERRMSG="Not able to find information on your undo datafile. Be sure your database is up and running."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        else:
                # Read all lines of the file
                lines_read = self.cm_read_files(tmp_file_name)
                
                # Processing just the first file found into the tmp_file_name
                file_renamed = lines_read[0] + ".bck" # Renaming just the first file name
                try:
                    shutil.copyfile(lines_read[0], file_renamed)
                    os.unlink(lines_read[0]) 
                except IOError as why:
                    self.textBrowser.append("\n" + str(why))
        """ 
        cm_kill_instance
        """

    # Menu 9 selected: LOSS OF A READ-ONLY TABLESPACE
    def menu_id_09(self):
        global sql_stmt
      
        # Read from database the read-only datafile's location
        # redirecting the output to a tmp file
        self.cm_set_sql_stmt("READONLYTBS")

        tmp_file_name = "/tmp/readonly_tablespace.tmp"
        return_val = self.cm_spool_query_to_tmp(tmp_file_name)
        print sql_stmt
   
        if return_val == -1:
            ERRMSG="Can not proceed. Sql statement is not set"
            self.textBrowser.append("\n" + ERRMSG)
            return SUCCESS

        # Counting the number of read-only datafiles found
        # Possible returning values: 0 ===============> temporary file empty
        #                            1 ===============> One datafile found
        #                            ORA_ERROR_FOUND => ORA-% found into the temporary file
        #                            > 1 =============> more datafiles found
        return_val = self.cm_count_files(tmp_file_name)
        if return_val == 0:
                ERRMSG="Can not proceed. Temporary file is empty."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        elif return_val == ORA_ERROR_FOUND:
                ERRMSG="Not able to find information on your read-only tablespace. Be sure your database is up and running."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        else:
                # Read all lines of the file
                lines_read = self.cm_read_files(tmp_file_name)
                
                # Processing all files found into the tmp_file_name
                for line in lines_read:
                    file_renamed = line + ".bck" # Renaming the current file
                    try:
                        shutil.copyfile(line, file_renamed)
                        os.unlink(line) 
                    except IOError as why:
                        self.textBrowser.append("\n" + str(why))
        """ 
        cm_kill_instance
        """

    # Menu 12 selected: LOSS OF A NON-SYSTEM TABLESPACE
    def menu_id_12(self):
        global sql_stmt
      
        # Read from database the non-system datafile's location
        # redirecting the output to a tmp file
        self.cm_set_sql_stmt("NONSYSTEMTBS")

        tmp_file_name = "/tmp/non_system_tablespace.tmp"
        return_val = self.cm_spool_query_to_tmp(tmp_file_name)
        print sql_stmt
   
        if return_val == -1:
            ERRMSG="Can not proceed. Sql statement is not set"
            self.textBrowser.append("\n" + ERRMSG)
            return SUCCESS

        # Counting the number of temporary datafiles found
        # Possible returning values: 0 ===============> temporary file empty
        #                            1 ===============> One datafile found
        #                            ORA_ERROR_FOUND => ORA-% found into the temporary file
        #                            > 1 =============> more datafiles found
        return_val = self.cm_count_files(tmp_file_name)
        if return_val == 0:
                ERRMSG="Can not proceed. Temporary file is empty."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        elif return_val == ORA_ERROR_FOUND:
                ERRMSG="Not able to find information on your non-system tablespace. Be sure your database is up and running."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        else:
                # Read all lines of the file
                lines_read = self.cm_read_files(tmp_file_name)
                
                # Processing all files found into the tmp_file_name
                for line in lines_read:
                    file_renamed = line + ".bck" # Renaming the current file
                    try:
                        shutil.copyfile(line, file_renamed)
                        os.unlink(line) 
                    except IOError as why:
                        self.textBrowser.append("\n" + str(why))
        """ 
        cm_kill_instance
        """
    # Menu 13 selected: LOSS OF A TEMPORARY TABLESPACE
    def menu_id_13(self):
        global sql_stmt
      
        # Read from database the non-system datafile's location
        # redirecting the output to a tmp file
        self.cm_set_sql_stmt("TEMPORARYTBS")

        tmp_file_name = "/tmp/temporary_tablespace.tmp"
        return_val = self.cm_spool_query_to_tmp(tmp_file_name)
        print sql_stmt
   
        if return_val == -1:
            ERRMSG="Can not proceed. Sql statement is not set"
            self.textBrowser.append("\n" + ERRMSG)
            return SUCCESS

        # Counting the number of temporary datafiles found
        # Possible returning values: 0 ===============> temporary file empty
        #                            1 ===============> One datafile found
        #                            ORA_ERROR_FOUND => ORA-% found into the temporary file
        #                            > 1 =============> more datafiles found
        return_val = self.cm_count_files(tmp_file_name)
        if return_val == 0:
                ERRMSG="Can not proceed. Temporary file is empty."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        elif return_val == ORA_ERROR_FOUND:
                ERRMSG="Not able to find information on your temporary tablespace. Be sure your database is up and running."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        else:
                # Read all lines of the file
                lines_read = self.cm_read_files(tmp_file_name)
                
                # Processing all files found into the tmp_file_name
                for line in lines_read:
                    file_renamed = line + ".bck" # Renaming the current file
                    try:
                        shutil.copyfile(line, file_renamed)
                        os.unlink(line) 
                    except IOError as why:
                        self.textBrowser.append("\n" + str(why))
        """ 
        cm_kill_instance
        """

    # Menu 14 selected: LOSS OF THE SYSTEM TABLESPACE
    def menu_id_14(self):
        global sql_stmt
      
        # Read from database the system datafile's location
        # redirecting the output to a tmp file
        self.cm_set_sql_stmt("SYSTEMTBS")

        tmp_file_name = "/tmp/system_tablespace.tmp"
        return_val = self.cm_spool_query_to_tmp(tmp_file_name)
        print sql_stmt
   
        if return_val == -1:
            ERRMSG="Can not proceed. Sql statement is not set"
            self.textBrowser.append("\n" + ERRMSG)
            return SUCCESS

        # Counting the number of system datafiles found
        # Possible returning values: 0 ===============> temporary file empty
        #                            1 ===============> One datafile found
        #                            ORA_ERROR_FOUND => ORA-% found into the temporary file
        #                            > 1 =============> more datafiles found
        return_val = self.cm_count_files(tmp_file_name)
        if return_val == 0:
                ERRMSG="Can not proceed. Temporary file is empty."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        elif return_val == ORA_ERROR_FOUND:
                ERRMSG="Not able to find information on your system tablespace. Be sure your database is up and running."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        else:
                # Read all lines of the file
                lines_read = self.cm_read_files(tmp_file_name)
                
                # Processing all files found into the tmp_file_name
                for line in lines_read:
                    file_renamed = line + ".bck" # Renaming the current file
                    try:
                        shutil.copyfile(line, file_renamed)
                        os.unlink(line) 
                    except IOError as why:
                        self.textBrowser.append("\n" + str(why))
        """
        cm_kill_instance
        """

    # Menu 15 selected: LOSS OF THE UNDO TABLESPACE
    def menu_id_15(self):
        global sql_stmt
      
        # Read from database the undo datafile's location
        # redirecting the output to a tmp file
        self.cm_set_sql_stmt("UNDOTBS")

        tmp_file_name = "/tmp/undo_tablespace.tmp"
        return_val = self.cm_spool_query_to_tmp(tmp_file_name)
        print sql_stmt
   
        if return_val == -1:
            ERRMSG="Can not proceed. Sql statement is not set"
            self.textBrowser.append("\n" + ERRMSG)
            return SUCCESS

        # Counting the number of undo datafiles found
        # Possible returning values: 0 ===============> temporary file empty
        #                            1 ===============> One datafile found
        #                            ORA_ERROR_FOUND => ORA-% found into the temporary file
        #                            > 1 =============> more datafiles found
        return_val = self.cm_count_files(tmp_file_name)
        if return_val == 0:
                ERRMSG="Can not proceed. Temporary file is empty."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        elif return_val == ORA_ERROR_FOUND:
                ERRMSG="Not able to find information on your undo tablespace. Be sure your database is up and running."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        else:
                # Read all lines of the file
                lines_read = self.cm_read_files(tmp_file_name)
                
                # Processing all files found into the tmp_file_name
                for line in lines_read:
                    file_renamed = line + ".bck" # Renaming the current file
                    try:
                        shutil.copyfile(line, file_renamed)
                        os.unlink(line) 
                    except IOError as why:
                        self.textBrowser.append("\n" + str(why))
        """ 
        cm_kill_instance
        """

    # Menu 17 selected: LOSS OF ALL DATAFILES
    def menu_id_17(self):
        global sql_stmt
      
        # Read from database datafile's location
        # redirecting the output to a tmp file
        self.cm_set_sql_stmt("ALLDATA")

        tmp_file_name = "/tmp/all_datafiles.tmp"
        return_val = self.cm_spool_query_to_tmp(tmp_file_name)
        print sql_stmt
   
        if return_val == -1:
            ERRMSG="Can not proceed. Sql statement is not set"
            self.textBrowser.append("\n" + ERRMSG)
            return SUCCESS

        # Counting the number of datafiles found
        # Possible returning values: 0 ===============> temporary file empty
        #                            1 ===============> One datafile found
        #                            ORA_ERROR_FOUND => ORA-% found into the temporary file
        #                            > 1 =============> more datafiles found
        return_val = self.cm_count_files(tmp_file_name)
        if return_val == 0:
                ERRMSG="Can not proceed. Temporary file is empty."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        elif return_val == ORA_ERROR_FOUND:
                ERRMSG="Not able to find information on your datafiles. Be sure your database is up and running."
                self.textBrowser.append("\n" + ERRMSG)
                return SUCCESS
        else:
                # Read all lines of the file
                lines_read = self.cm_read_files(tmp_file_name)
                
                # Processing all files found into the tmp_file_name
                for line in lines_read:
                    file_renamed = line + ".bck" # Renaming the current file
                    try:
                        shutil.copyfile(line, file_renamed)
                        os.unlink(line) 
                    except IOError as why:
                        self.textBrowser.append("\n" + str(why))
        """ 
        cm_kill_instance
        """


if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    crashmanager_1 = crashmanager()
    crashmanager_1.main()
    sys.exit(app.exec_())

