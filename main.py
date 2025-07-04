from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QGridLayout, QLineEdit, \
    QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QVBoxLayout, QLineEdit, QComboBox, QPushButton, QToolBar, \
    QStatusBar, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
import sys 
import mysql.connector

class DataBaseConnection:
    def __init__(self, host="localhost", user="root", password="Ruxicristi1", database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        connection = mysql.connector.connect(host=self.host, user=self.user, 
                                             password=self.password, database=self.database)
        return connection



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)  # Set the minimum size of the window

        file_menu_item = self.menuBar().addMenu("&File")  # Create a File menu
        help_menu_item = self.menuBar().addMenu("&Help")  # Create a File menu
        edit_menu_item = self.menuBar().addMenu("&Edit")  # Create a File menu

        add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self) # Create an action for adding a student -> subitem in the File menu
        add_student_action.triggered.connect(self.insert) #it shows the dialog for adding a student
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About", self) # Create an action for the About dialog -> subitem in the Help menu
        help_menu_item.addAction(about_action)
        #about_action.setMenuRole(QAction.MenuRole.NoRole) for MAC
        about_action.triggered.connect(self.about)

        search_action = QAction(QIcon("icons/search.png"), "Search", self) # Create an action for the Edit dialog -> subitem in the Edit menu
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search) # it shows the dialog for searching a student
        
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False) # Hide the vertical header
        self.setCentralWidget(self.table)

    #Create a toolbar and add toolbar elements

        toolbar = QToolBar()  # Create a toolbar
        toolbar.setMovable(True)  # Make the toolbar movable
        self.addToolBar(toolbar)  # Add the toolbar to the main window
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

    #Create a status bar and add status bar elements
        self.status_bar = QStatusBar() # Create a status bar
        self.setStatusBar(self.status_bar)  # Add the status bar to the main window

    #Detect a cell click in the table
        self.table.cellClicked.connect(self.cell_clicked)
    
    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton) #removes the duplicate buttons
        if children:
            for child in children:
                self.status_bar.removeWidget(child)  # Remove existing buttons from the status bar
        
        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)
    
    #load data from the database and display it in the table
    def load_data(self):
        connection = DataBaseConnection().connect()  # Connect to the database
        cursor = connection.cursor() #mysql uses cursor!!!!!
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()  
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data))) #coordinate of the cell
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()
    
    def edit(self):
        dialog = EditDialog()
        dialog.exec()
    
    def delete(self):
       dialog = DeleteDialog()
       dialog.exec()
    
    def about(self):
        dialog = AboutDialog()
        dialog.exec()

    
class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created during the course "The Python Mega Course".
        Feel free to use and modify this app.
        """

        self.setText(content)


class EditDialog(QDialog):
    def __init__(self):

        super().__init__()
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(200)

        layout = QVBoxLayout()

        #Get student name from selected row
        index = main_window.table.currentRow() 
        student_name = main_window.table.item(index, 1).text() #index 1 is for column with names

        #Get id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        #Add student name 
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Enter Student Name")
        layout.addWidget(self.student_name)

        #Add combo box
        course_name = main_window.table.item(index, 2).text()
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics" ]
        self.course_name.addItems(courses) #course_name for adding elements in combo box
        self.course_name.setCurrentText(course_name) #displays the course_name for the course that is already chosen
        layout.addWidget(self.course_name)

        #Add mobile number
        mobile = main_window.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Enter Student Mobile")
        layout.addWidget(self.mobile)

        #Add submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = %s WHERE id = %s", 
                       (self.student_name.text(), 
                        self.course_name.itemText(self.course_name.currentIndex()), 
                        self.mobile.text(), self.student_id))
        connection.commit()
        cursor.close()
        #refresh the table 
        main_window.load_data()


class DeleteDialog(QDialog): 
     def __init__(self):

        super().__init__()
        self.setWindowTitle("Delete Student Data")
        

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")
        
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)

     def delete_student(self):
         #Get selected row index and id
         index = main_window.table.currentRow()
         student_id = main_window.table.item(index, 0).text()

         connection = DataBaseConnection().connect()
         cursor = connection.cursor()
         cursor.execute("DELETE FROM students WHERE id = %s", (student_id, ))
         connection.commit()
         cursor.close()
         main_window.load_data()

         self.close()

         confirmation_widget = QMessageBox()
         confirmation_widget.setWindowTitle("Success")
         confirmation_widget.setText("The record was deleted successfully")
         confirmation_widget.exec()

        
class InsertDialog(QDialog):
    def __init__(self):

        super().__init__()
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedHeight(200)

        layout = QVBoxLayout()

        #Add student name 
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Enter Student Name")
        layout.addWidget(self.student_name)

        #Add combo box
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics" ]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        #Add mobile number
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Enter Student Mobile")
        layout.addWidget(self.mobile)

        #Add submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)
    
    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.mobile.text()
        connection = DataBaseConnection().connect()  # Connect to the database
        cursor = connection.cursor() # for inserting data
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (%s, %s, %s)",
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

class SearchDialog(QDialog):
    def __init__(self):

        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedHeight(200)

        layout = QVBoxLayout()

        #Add student name 
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Enter Student Name")
        layout.addWidget(self.student_name)

        #Add search button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = DataBaseConnection().connect()
        cursor = connection.cursor()
        #result = cursor.execute("SELECT * FROM students WHERE name LIKE ?", ('%' + name + '%',))
        cursor.execute("SELECT * FROM students WHERE name = %s", (name,))
        result = cursor.fetchall()
        row = list(result)
        print(row)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            main_window.table.item(item.row(), 1).setSelected(True)  # Select the row with the matching name
        cursor.close()
        connection.close()



app = QApplication(sys.argv) # Create an instance of QApplication

main_window = MainWindow() # Create an instance of the AgeCalculator class

main_window.show()  # Show the window

main_window.load_data()  # Load data from the database into the table

sys.exit(app.exec()) # Start the event loop and exit when done

