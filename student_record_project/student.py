    
import sqlite3
import json
import random
from datetime import datetime, timedelta
import pyinputplus as pyip
import os
import re

CONFIG_FILE = 'config.json'


def create():
    db = Database()
    all_courses = [
        [112, "Java", 80],
        [113, "Machine Learning", 70],
        [114, "C++", 90],
        [115, "Data Science", 60],
        [116, "Web Development", 110],
        [117, "Database Management", 85],
        [118, "Network Security", 75],
        [119, "Artificial Intelligence", 65],
        [120, "Mobile App Development", 95],
        [121, "Cloud Computing", 100]
    ]

    # Iterate over the courses and call db.add_course() for each course
    for course_info in all_courses:
        db.add_course(*course_info)
    
        

def create_tables():
    
    database = Database()
    database.create_communication_table()
    database.create_student_tables()
    database.create_course_tables()
    database.create_users_table("student_table")
    database.create_users_table("instructor_table")
    database.create_users_table("admin_table")
    database.create_instructor_tables()
    database.close()
    create()
    


        
def check_and_create_tables():
    
    # Check if the database file exists
    if not os.path.exists("database.db"):
        print("Database file does not exist. Creating database...")
            # Create a connection to the database (this will create the file)
        conn = sqlite3.connect("database.db")
        conn.close()
    # Check if the config file exists
    if not os.path.exists(CONFIG_FILE):
            
        
            # Write initial configuration to the file
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'tables_created': False}, f)
        
        
        # Read the config file
        
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
        f.close()
        # Check if tables have been created
        if not config.get('tables_created', False):
            print("hello")
            create_tables()
                # Update the config to indicate tables are created
            config['tables_created'] = True
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f)


class Student():
    def __init__(self, student_id  ,name=None,  database=None) :
        
        self.student_id = student_id
        self.db=Database()
        if name==None:
            
            self.name = self.db.get_user_data("student",self.student_id)[1]
        else:
            self.name=name
        
        self.type="student"
        self.table_name="student_info_table"
    
    def enroll_course(self, course_id):
        if self.db.course_exist(course_id):
            if not self.db.course_student_exist(course_id,self.student_id):
                if self.db.course_space_exist(course_id):
                    print(f"You succesfuly enrolled course with id: {course_id}")
                    
                    self.db.add_student_to_course(course_id , self.student_id)
                else:
                    print("Your enrollment to the course was not successful due to insufficient capacity.")
            else:
                print("You are already enrolled in this course")
        else:
            print("Given course do not exists")
    
    
      
    def drop_course(self, course_id):
        print(f"Do you want to drop course id with {course_id}?")
        
        
        
        response = pyip.inputMenu(["Yes", "No"], numbered=True)
        
        if response =="Yes":
            print("You did sucessfully drop the course")
            self.db.remove_student(course_id,self.student_id)
        elif response=="No":
            return
        

    def current_courses(self):
        result = self.db.enrolled_courses(self.student_id)
        return result
    
    #student add function
    def add_student(self, name , student_id , email="-" , phone_numer="-"):
        self.db.add_student(name, student_id )
     
    
    
    
    
    
    def update_contact_info(self, email="-" , phone_number="-"):
        print("Contact info sucessfuly updated")
        self.db.update_user_info("student_table" ,self.student_id, new_email=email , new_phone_number=phone_number)
        
    
    
        
            
    
    def delete_account(self):
        print("User is sucessfuly deleted")
        self.db.delete_user(self.student_id ,self.table_name)
        
    
    def info(self):
        
        result =self.db.get_user_data("student", self.student_id)    
        return f"Student id: {result[0]}\nStudent name: {result[1]}\nStudent email: {result[2]}\nStudent phone number: {result[3]}"
        
           
    def add_comments(self,course_id, comment):
        self.db.add_comments(course_id ,"Student", self.name ,comment)
        print("Your comment has been added")
        
        
    def look_comments(self,course_id):
        result=self.db.look_comments(course_id)
        print("Last 6 comments\n")
        for elements in result:
            print(f"{elements}")
            






#datbase class of managment system all dataabase function is in this class
class Database():
    def __init__(self) :
        self.conn = sqlite3.connect("database.db")
        self.cursor = self.conn.cursor()
       
       
    def take_course(self,instructor, course_id):
        courses =self.get_courses()
        
        result = [x[2] for x in courses if x[0] == course_id]
        if result[0]=="-":
            print("Appointed as the instructor of the course")
            update_quary="""
                    UPDATE course_table
                    SET instructor =?
                    WHERE course_id =?
                     """
            self.cursor.execute(update_quary , (instructor , course_id))
            self.conn.commit()
        else:
            print("This course is being taught by someone")
        
       
    
       
       
    def get_all_courses(self):
        self.cursor.execute("SELECT * FROM course_table")
        result=self.cursor.fetchall()
        return result

       
    

    def add_comment_to_course(self,course_id):
        self.cursor.execute("INSERT INTO communication_table (course_id, text) VALUES (?,?)",(course_id, ""))
        self.conn.commit()
        
        
        
            
    #communication functions
    def create_communication_table(self):
        self.cursor.execute( "CREATE TABLE IF NOT EXISTS communication_table ( course_id INTEGER PRIMARY KEY, text TEXT);")
        self.conn.commit()
   
    def get_comments(self, course_id):
        self.cursor.execute(f"SELECT * FROM communication_table WHERE course_id =?",(course_id,))
        res=self.cursor.fetchone()[1]
        return self._json_to_list(res)
        
    
    def look_comments(self,course_id):
        result=self.get_comments(course_id)
        return result[-6:]
    
    
    def add_comments(self, course_id, user_type , user_name ,comment):
        result =self.get_comments(course_id)
        comment_text=f"{user_type} {user_name} [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:]\n{comment}"
        
        result.append(comment_text)
        update_quary="""
                    UPDATE communication_table
                    SET text =?
                    WHERE course_id =?
                     """
        
                     
        all_comments =self._list_to_json(result)
        self.cursor.execute(update_quary, (all_comments , course_id  ))
        self.conn.commit()
            
    
    
    
    
    
    
    
        
        
    def create_student_tables(self):
        self.cursor.execute( "CREATE TABLE IF NOT EXISTS student_info_table ( id INTEGER PRIMARY KEY,  name TEXT,  email TEXT,  phone_number TEXT);")
        self.conn.commit()
    
    
    def add_student(self, name, student_id , email="-",phone_number="-"):
        self.cursor.execute("INSERT INTO student_info_table (id,name , email,phone_number) VALUES (?,?,?,?) ", (student_id,name,email,phone_number))
        self.conn.commit()
        
    def create_instructor_tables(self):
        self.cursor.execute( """CREATE TABLE IF NOT EXISTS instructor_info_table (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                email TEXT,
                                phone_number TEXT);
                             """
        )
        self.conn.commit()
    
    
    def add_instructor(self, name, id , email="-",phone_number="-"):
        self.cursor.execute("INSERT INTO instructor_info_table (id,name , email,phone_number) VALUES (?,?,?,?) ", (id,name,email,phone_number))
        self.conn.commit()
        
    def create_admin_tables(self):
        self.cursor.execute( """CREATE TABLE IF NOT EXISTS admin_info_table (
                                id INTEGER PRIMARY KEY,
                                name TEXT,
                                email TEXT,
                                phone_number TEXT);
                             """
        )
        self.conn.commit()
    
    
    def add_admin(self, name, id , email="-",phone_number="-"):
        self.cursor.execute("INSERT INTO admin_info_table (id,name , email,phone_number) VALUES (?,?,?,?) ", (id,name,email,phone_number))
        self.conn.commit() 
    
    
    
    
    
    
    
        
        
    def get_user_data(self,user_type ,id=None):
        if user_type =="student":
            table_name="student_info_table"
        elif user_type=="instructor":
            table_name="instructor_info_table"
        else:
            table_name ="admin_info_table"
            
        if id !=None:
            self.cursor.execute(f"SELECT * FROM {table_name} WHERE id =?",(id,))
            return self.cursor.fetchone()
        else:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            return self.cursor.fetchall()
        
        
        
    def close(self):
        self.conn.close()
        
        
    def update_user_info(self,table_name , id , new_email="-",new_phone_number="-"):
        if table_name =="instructor_table":
            res = "instructor_info_table"
        elif table_name =="student_table":
            res="student_info_table"
            
        
        if new_email=="-":
            new_email = self.get_user_data(res[:-11] , id)[-2]
        if new_phone_number=="-":
            new_phone_number=self.get_user_data(res[:-11] ,id)[-1]
            
        
        update_quary=f"""
                    UPDATE {res}
                    SET email=? , phone_number=?
                    WHERE id =?
                     """
        self.cursor.execute(update_quary, (new_email ,new_phone_number, id ))
        self.conn.commit()
    
    
        
        
    #course functions 
    
    #course table creation
    
    
    #add course
    def course_exist(self, course_id):
        
        result= self.get_courses(course_id)[0]
        
        return result>0
        
    def course_student_exist(self, course_id,student_id):
        
        result= self.get_courses(course_id)[3]
        current_students = self._json_to_list(result)
        
        if int(student_id) in current_students:
            return True
        else:
            return False
        
        
        
    def course_space_exist(self, course_id):
        result = self.get_courses(course_id)
        
        capacity= result[-2]
        current_enrolled= result[-1]
        
        return capacity >current_enrolled
    
        
    def enrolled_courses(self,student_id):
        result = self.get_courses()
        current_courses=[]
        for elements in result:
            student_ids = self._json_to_list(elements[3])
            if student_id in student_ids:
                current_courses.append(elements[0])
        return current_courses
    
    
             
            
            
            
        
        
    #course creation
    def add_course(self, course_id , course_name , course_capacity,instructor="-" ):
        query="INSERT INTO course_table (course_id , course_name ,instructor, student_ids,course_capacity,current_enrolled) VALUES (?,?,?,?,?,?) "
        self.cursor.execute(query, (course_id,course_name, instructor, "", course_capacity,0))
        self.conn.commit()
        
        self.add_comment_to_course(course_id)
        
        
    
    
    #delete course function
    def delete_course(self, course_id):
        query = """
        DELETE FROM course_table
        WHERE course_id =?
                        """
                        
        self.cursor.execute(query , (course_id,))
        self.conn.commit() 
        
    #change instructor of course
    
    def update_instructor(self,course_id, new_instructor="-"):
        course = self.get_courses(course_id)
        
        
            
        update_quary="""
                    UPDATE course_table
                    SET instructor =?
                    WHERE course_id =?
                     """
        
                     
        
        self.cursor.execute(update_quary, (new_instructor , course_id  ))
        self.conn.commit()

        
    
    def search_student_by_id(self,student_id):
        self.cursor.execute("SELECT * FROM student_info_table WHERE student_id =?",(student_id,))  
        return self.cursor.fetchone()
    
    
    def get_ids(self):
        self.cursor.execute("SELECT * FROM student_info_table")
        return [x[0] for x in self.cursor.fetchall()]
        

        
    def show_instructors_courses(self , instructor_id):
        self.cursor.execute("SELECT * FROM course_table WHERE instructor =?",(instructor_id,))
        result = self.cursor.fetchall()
        
        return [x[0] for x in result]

        
        
        
        
        
    def create_course_tables(self):
        self.cursor.execute( f"""CREATE TABLE IF NOT EXISTS course_table (
                                course_id INTEGER PRIMARY KEY,
                                course_name TEXT,
                                instructor TEXT,
                                student_ids TEXT,
                                course_capacity INTEGER,
                                current_enrolled INTEGER);
                             """
        )
        self.conn.commit()
    
    def get_courses(self, course_id=None):
        if course_id !=None:
            self.cursor.execute("SELECT * FROM course_table WHERE course_id =?",(course_id,))
            return self.cursor.fetchone()
        else:
            self.cursor.execute("SELECT * FROM course_table")
            return self.cursor.fetchall()
    

    def _list_to_json(self, text):
        return json.dumps(text)
    def _json_to_list(self , serialized_text):
        if len(serialized_text)==0:
            return []
        return json.loads(serialized_text)

        
    def get_course_ids(self):
        self.cursor.execute("SELECT * FROM course_table")
        rows= self.cursor.fetchall()
        
        course_ids = [row[0] for row in rows]
        return course_ids        
        
    
    def add_student_to_course(self , course_id , student_id):
        course = self.get_courses(course_id=course_id)
        
        current_enrolled = course[-1]+1
        
        
        student_ids = self._json_to_list(course[3])
        student_ids.append(student_id)
        
        serialized_student_ids = self._list_to_json(student_ids)
        
        update_quary="""
                    UPDATE course_table
                    SET student_ids =? , current_enrolled=?
                    WHERE course_id =?
                     """
        self.cursor.execute(update_quary, (serialized_student_ids ,current_enrolled , course_id  ))
        self.conn.commit()
        
        
        
    def remove_student(self,course_id , student_id):
        
        course = self.get_courses(course_id=course_id)
        
        student_ids = self._json_to_list(course[3])
        
        student_ids.remove(student_id)
        
        serialized_student_ids = self._list_to_json(student_ids)
        
        update_quary="""
                    UPDATE course_table
                    SET student_ids =?,
                    current_enrolled =?
                    WHERE course_id =?
                     """
        self.cursor.execute(update_quary, (serialized_student_ids , course[-1]-1, course_id  ))
        self.conn.commit()
        
        
        
        
       
        
    
        
        
        
        
     
        

   
        
    
        
    
    
   
    
        
    
        
    
    
  
    
    def create_users_table(self,table_name ):
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
                                id INTEGER PRIMARY KEY,
                                username TEXT,
                                password TEXT); 
                             """)
        self.conn.commit()
    
    
    def get_users(self,table_name):
        
        quary=f""" SELECT * FROM {table_name}
              """
        self.cursor.execute(quary)
        
        result_users = self.cursor.fetchall()
    
        return result_users
    
    def add_user(self, id , username , password,table_name):
        self.cursor.execute(f"INSERT INTO {table_name} (id , username , password) VALUES (?,?,?) " , (id, username, password))
        self.conn.commit()
        
    
    def update_user(self):
        pass
    
    #delete user
    
    def delete_user(self, id, table_name):
        if table_name =="student_info_table":
            users_table = "student_table"
        elif table_name =="instructor_info_table":
            users_table="instructor_table"
        else:
            users_table="admin_table"
            
            
        delete_query = f"DELETE FROM {users_table} WHERE id = ?"    
        self.cursor.execute(delete_query , (id,))
        self.conn.commit()
        
        
        delete_query = f"DELETE FROM {table_name} WHERE id = ?"     
               
        self.cursor.execute(delete_query , (id,))
        self.conn.commit()  
        
            
  
     
    
    
    
        
        
          
#instructor class     
class Insctructor():
    def __init__(self, instructor_id , name=None , database=None ):
        
        
        self.instructor_id = instructor_id
        self.db=Database()
        if name==None:
            
            self.name = self.name = self.db.get_user_data("instructor",self.instructor_id)[1]
        else:
            self.name = name    
        
        
        
        self.db=Database()
        self.type="instructor"
        self.table_name = "instructor_info_table"
        
        
      
    def delete_account(self):
        print("User is sucessfuly deleted")
        self.db.delete_user(self.instructor_id ,self.table_name)
        
    def info(self ):
        
        result =self.db.get_user_data("instructor", self.instructor_id)    
        return f"Instructor id: {result[0]}\nInstructor name: {result[1]}\nInstructor email: {result[2]}\nInstructor phone number: {result[3]}"
            
    
    def add_instructor(self, name ,id , email="-" , phone_number="-"):
        self.db.add_instructor(name , id , email , phone_number)
        
    def take_course(self, course_id):
        self.db.take_course(self.name ,course_id )
            

        
    def update_contact_info(self,new_email="-" , new_phone_number="-"):
        print("Contact info sucessfuly updated")
        self.db.update_user_info("instructor_table" ,self.instructor_id ,  new_email=new_email , new_phone_number=new_phone_number)

    def get_dates(self , course_id):
        return self.db.get_dates(course_id)
    
    
   
    def show_courses(self):
        course_list =self.db.show_instructors_courses(self.name)
        if len(course_list)==0:
            print("You have no courses as instructor")
        else:
            if len(course_list)==1:
                word="is"
            else:
                word="are"
                
            str_course_list=  [str(x) for x in course_list]
            
            print(f"Courses you are teaching {word}: {' '.join(str_course_list)}")
            
        return course_list                                                                 
            
            
    def search_student_by_id(self, student_id):
        if student_id in self.db.get_ids():
            print("The information about student\n")
            s1= Student(student_id)
            print(s1.info())
            return s1.info()
               
           
            
        else:
            print("Given student id does not exist")
        
        
    def drop_course(self, course_id):
        result =self.db.get_courses(course_id=course_id)
        if not  result[2]==self.name:
            print("This course is not taught by you")
            return
        
        update_quary="""
                    UPDATE course_table
                    SET instructor =?
                    WHERE course_id =?
                     """
        self.db.cursor.execute(update_quary , ("-" , course_id))
        self.db.conn.commit()
            
            
            
            
        
        
        


        
        




class Main():
    def __init__(self) -> None:
        
        self.db=Database()
        self.user=None
        self.logged_in=False
        self.user_type=None
        self.back=True
        
        
    def text_print(self ,text):
        print(text)
        print("-"*len(text))
    
    
    def user_login(self,user_type):
        if user_type=="student":
            table_name = "student_table"
        elif user_type=="instructor":
            table_name="instructor_table"
        
        
        print(f"Login as a {user_type}")
        print("------------------")
        
        
            
        users_data =self.db.get_users(table_name)
        id_data = [x[0] for x in users_data]
        
        
        
        while True:
            
            id=pyip.inputInt("Enter id , 0 for back to menu ",max=999999999)
            
            if id ==0:
                break
            password=pyip.inputStr("Enter password ")
            
            username_bool = id in id_data
            
            
            if username_bool:
                password_bool =  password == users_data[id_data.index(id)][-1]
                if password_bool:
                    self.text_print("Login successfull")
                    
                    
                    
                    if user_type=="student":
                        logined_user = Student(id)
                    elif user_type=="instructor":
                        logined_user = Insctructor(id)
                        
                    
                    self.user=logined_user
                    self.user_type=self.user.type
                    self.logged_in=True
                    self.back=True
                    
                    break
                else:
                    self.text_print("Username or password is incorrect")
                
            else:
                self.text_print("Username or password is incorrect")
                
    
    
    
    
    
    def user_signup(self,user_type):
        if user_type=="student":
            table_name = "student_table"
        elif user_type=="instructor":
            table_name="instructor_table"
        else:
            table_name="admin_table"
        
        
        
        print(f"Signup as a {user_type}")
        print("-------------------")
        
        name=pyip.inputStr("Enter name ")
        password=pyip.inputInt("Enter password ")
        
        

        
        
            
            
        print("Registration successful")
            
        if user_type=="student":
                
            student_ids = [ x[0] for x in self.db.get_user_data("student") ]
            while True:
                id = random.randint(100000000,999999999)
                if id not in student_ids:
                    break
                    
            
                    
                
                
            new_user =Student(name,id,self.db)
            new_user.add_student(name , id)

                
        elif user_type=="instructor":
            student_ids = [ x[0] for x in self.db.get_user_data("instructor") ]
            while True:
                id = random.randint(100000000,999999999)
                if id not in student_ids:
                    break
                
                
            new_user =Insctructor(name,id,self.db)
            new_user.add_instructor(name ,id)
            
            
        else:
            student_ids = [ x[0] for x in self.db.get_user_data("admin") ]
            while True:
                id = random.randint(100000000,999999999)
                if id not in student_ids:
                    break
                
            new_user =Admin(name,id,self.db)
            new_user.add_admin()
            #add admin
        self.text_print(f"Your id is {id}")
        self.db.add_user(id ,name, password,table_name)   
    
    def login_signup_menu(self,usertype):
        response = pyip.inputMenu(["Login", "Signup","Back"], numbered=True) 
        if response=="Login":
            self.user_login(usertype)

        elif response=="Signup":
            self.user_signup(usertype)
        else:
            return

    

        
    def list_to_string(self,input_list):
        result_text=""
        for elements in input_list:
            result_text+=str(elements)+" "
        return result_text
        
        
    def student_actions(self):
        
        self.text_print("Welcome to student menu")
        while True:
            
            
            response = pyip.inputMenu(["Delete Account","See Course List","See Info","Add Comments","Look Comments", "Enroll Course","Current courses", "Drop Course","Update contact info","Back"], numbered=True) 
            
            if response=="Delete Account":
                self.user.delete_account()
                self.logged_in=False
                break
                
            elif response == "See Info":
                res=self.user.info()
                self.text_print(res)
            
                
            elif response=="See Course List":
                result=self.db.get_all_courses()
                
                print("Id    Name                Instructor       Capacity    Enrolled")
                for elements in result:
                    print(f"{elements[0]}     {elements[1]:<20} {elements[2]:<15} {elements[4]:<10} {elements[5]}")
                                
                            
                            
                
            elif response=="Add Comments":
                
                course_id=pyip.inputInt("Enter course id ")
                course_ids =self.db.get_course_ids()
                
                if course_id not in course_ids:
                    print("Course id do not exist")
                    continue
                if not self.db.course_student_exist(course_id , self.user.student_id):
                    print("You are not enrolled in this course")
                    continue
                    
                comment = pyip.inputStr("Enter your comment,enter nothing to go back ")
                if comment=="":
                    continue
                
                
                
                self.user.add_comments(course_id,comment)
                
                
                
            elif response=="Look Comments":  
                course_id=pyip.inputInt("Enter course id ")
                course_ids =self.db.get_course_ids()
                
                if course_id not in course_ids:
                    print("Course id do not exist")
                    continue
                if not self.db.course_student_exist(course_id , self.user.student_id):
                    print("You are not enrolled in this course ")
                    continue
                self.user.look_comments(course_id)
                
             
            elif response=="Enroll Course":
                
                course_id=pyip.inputInt("Enter course id, enter nothing to go back ")
                if response =="":
                    continue
                else:
                    self.user.enroll_course(course_id)
                    
                    
            elif response=="Current courses":
                curr_course_list= self.user.current_courses()
                courses_str = self.list_to_string(curr_course_list)
                self.text_print(f"Current enrolled courses are {courses_str}")
                
                
                
            elif response=="Drop Course":
                course_id=pyip.inputInt("Enter course id, enter 0 to go back ")
                if response ==0:
                    continue
                else:
                    if course_id not in self.user.current_courses():
                        print("You are not enrolled in this class")
                        continue
                    self.user.drop_course(course_id)
                
                
                
                
                
            elif response=="Update contact info":
                def inputEmail(prompt):
                    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    return pyip.inputStr(prompt, allowRegexes=[email_regex],default='')

                new_email = inputEmail("Enter your email, - for nonupdate, enter nothing to go back:  ")
                
                
                
                
                if new_email=="":
                    continue
                
                def inputPhone(prompt):
                    phone_regex = r'^\+?1?\d{9,15}$'
                    return pyip.inputStr(prompt, allowRegexes=[phone_regex],default='')

                new_phone = inputPhone("Enter new phone, - for nonupdate, enter nothing to go back: ")
                
                
                
                
                
                
                
                
                if new_phone=="":
                    continue
                
                self.user.update_contact_info(new_email,new_phone )   
                
                
                   
            elif response=="Back":
                self.back=False
                self.user=None
                self.logged_in=False
                self.user_type=None
                break 
    
   
        
            
    def instructor_actions(self):
        
        self.text_print("Welcome to instructor menu")
        while True:
            
            
            response = pyip.inputMenu(["See Course List","Take Course","See Info","Show Courses","Search Student", "Update contact info", "Drop Course","Back"], numbered=True) 
            
            
                
            if response=="See Info":
                res=self.user.info()  
                
                self.text_print(res)
                
            elif response=="See Course List":
                result=self.db.get_all_courses()
                
                print("Id    Name                Instructor       Capacity    Enrolled")
                for elements in result:
                    print(f"{elements[0]}     {elements[1]:<20} {elements[2]:<15} {elements[4]:<10} {elements[5]}")        
            elif response=="Drop Course":
                course_list =self.user.show_courses()
                
                
                    
                
                course_id = pyip.inputInt("Enter the course id of the lecture you want to drop, enter 0 to go back")
                
                if not course_id in course_list:
                    print("Given course is not taught by you")
                    return
                self.user.drop_course(course_id)
                
                
                
            elif response=="Show Courses":
                
                self.user.show_courses()     
            elif response=="Take Course":
                course_id = pyip.inputInt("Enter the course id of the lecture you want to teach, enter 0 to go back")
                if course_id==0:
                    continue
                
                self.user.take_course(course_id)
                
            elif response=="Update contact info":
                def inputEmail(prompt):
                    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    return pyip.inputStr(prompt, allowRegexes=[email_regex],default='')

                new_email = inputEmail("Enter your email, - for nonupdate, enter nothing to go back:  ")
                
                
                
                
                if new_email=="":
                    continue
                
                def inputPhone(prompt):
                    phone_regex = r'^\+?1?\d{9,15}$'
                    return pyip.inputStr(prompt, allowRegexes=[phone_regex],default='')

                new_phone = inputPhone("Enter new phone, - for nonupdate, enter nothing to go back: ")
                
                
                
                
                
                
                
                
                if new_phone=="":
                    continue
                
                self.user.update_contact_info(new_email,new_phone )           
            
            elif response=="Search Student":
                response =pyip.inputInt("Enter student id to search, 0 for back ")
                if response==0:
                    continue
                
                
                
                self.user.search_student_by_id(response)
                
                
            elif response=="Back":
                self.back=False
                self.user=None
                self.logged_in=False
                self.user_type=None
                break
            
            
            
    
    
            
    def main_menu(self):
        self.text_print("Welcome to system management please select user type")
        response = pyip.inputMenu(["student", "instructor"], numbered=True)       
        self.login_signup_menu(response)
    
            
    def run(self):
        while True:
            
            if self.logged_in and self.back:
                if self.user_type == "student":
                    self.student_actions()
                elif self.user_type == "instructor":
                    self.instructor_actions()
                
            else:
                self.main_menu()       
    

    
    
    







    
    