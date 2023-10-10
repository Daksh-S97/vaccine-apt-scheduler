from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Appointments import Appointments
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def check_pswd(pswd):
    # length >=8
    if len(pswd) < 8:
        return False
    # lowercase and uppercase
    if pswd.upper() == pswd or pswd.lower() == pswd:
        return False
    # contains digit
    if not any(char.isdigit() for char in pswd):
        return False
    # contains [?,!,@,#] 
    lis = ['!', '?', '@', '#']
    if not any(spchar in pswd for spchar in lis):
        return False
    return True    

def create_patient(tokens):
    """
    TODO: Part 1
    """
    #create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    #check 3: strong password    
    if not check_pswd(password):
        print('Please enter a strong password!')
        print ('A strong password must be at least 8 characters long and contain:')
        print ('- A mixture of both lowercase and uppercase letters')
        print('- A mixture of letters and numbers')
        print('- At least one special character, from “!”, “@”, “#”, “?”')
        return    

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save the patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    #check 3: strong password    
    if not check_pswd(password):
        print('Please enter a strong password!')
        print ('A strong password must be at least 8 characters long and contain:')
        print ('- A mixture of both lowercase and uppercase letters')
        print('- A mixture of letters and numbers')
        print('- At least one special character, from “!”, “@”, “#”, “?”')
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    """
    TODO: Part 1
    """
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient
    pass


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2
    
    """
    cm = ConnectionManager()
    conn = cm.create_connection()
    if not current_caregiver and not current_patient:
        print("Please login first!")
        return
    if len(tokens) != 2:
        print('Please try again!!')
        return 
    date = tokens[1]
    caregivers = "SELECT a.Username AS Caregiver, v.Name as Vaccine, v.Doses as Doses FROM Availabilities as a, Vaccines as v WHERE \
                    a.Time = %s AND a.Booked = 0 ORDER BY Caregiver"

    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(caregivers, (date))
        #print([row for row in  cursor])
        if cursor.rowcount == 0:
            print('No caregivers available!')
            return   
        for row in cursor:
            print(str(row["Caregiver"]) + " " + str(row["Vaccine"]) + " " + str(row['Doses']))
                
    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()                  

    


def reserve(tokens):
    """
    TODO: Part 2

    """
    cm = ConnectionManager()
    conn = cm.create_connection()
    if not current_caregiver and not current_patient:
        print("Please login first!")
        return
    if not current_patient:
        print('Please login as a patient!')
    if len(tokens)!=3:
        print('Invalid input')
    date = tokens[1]
    vaccine = tokens[2] 
    vax_ava = "SELECT * FROM Vaccines WHERE Vaccines.Name = %s"
    caregivers = "SELECT a.Username AS Caregiver, v.Name as Vax, v.Doses as Doses FROM Availabilities as a, Vaccines as v\
                    WHERE a.Time = %s AND a.Booked = 0 AND v.Name = %s AND Doses > 0\
                     ORDER BY Caregiver"   
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(vax_ava, vaccine)
        if cursor.rowcount == 0:
            print('No vaccine of this brand. Check your input!')
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            if row['Doses'] <= 0:
                print('No Doses available for this vaccine!')
                return
            else:
                cursor2 = conn.cursor(as_dict=True)
                cursor2.execute(caregivers, (date, vaccine))
                if cursor2.rowcount == 0:
                    print('No Caregivers available')
                else:
                    for row2 in cursor2:
                        caregiver = row2['Caregiver']
                        doses = row2['Doses']
                        patient = current_patient.get_username()
                        date_tokens = date.split("-")
                        month = int(date_tokens[0])
                        day = int(date_tokens[1])
                        year = int(date_tokens[2])
                        d = datetime.datetime(year, month, day)
                        cur_id = str(month) + str(day) + str(year) + caregiver
                        apt = Appointments(cur_id, patient, caregiver, vaccine, d) 
                        #print(cur_id, patient, caregiver, vaccine, d)
                        booked = 'UPDATE Availabilities SET Booked=1 WHERE Time = %s AND Username = %s'
                        cursor3 = conn.cursor(as_dict=True)
                        try:
                            apt.save_to_db()
                            vax = Vaccine(vaccine, doses).get()
                            vax.decrease_available_doses(1)
                            cursor3.execute(booked, (date, caregiver))
                            conn.commit()
                            print('SUCCESS')
                            print('Appointment ID: {id}, Caregiver username: {name}'.format(id = cur_id, name = caregiver))

            

                        except pymssql.Error as e:
                            print("Please try again!")
                            print("Db-Error:", e)
                            quit()
                        except Exception as e:
                            print("Please try again!")
                            print("Error:", e)
                        
                break            

        


    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("PLease try again!")
        print("Error:", e)
    finally:
        cm.close_connection()            




def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    pass


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")



def get_patients(name):
    cm = ConnectionManager()
    conn = cm.create_connection()
    get_apt_details = "SELECT id, vaccine, appointment_time, patient FROM Appointments WHERE caregiver = %s  ORDER BY id"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(get_apt_details, (name))
        if cursor.rowcount==0:
            print("No appointments found for caregiver: {n}".format(n=name))
            return
        else:
            for row in cursor:
                print(str(row['id']) + " " + str(row['vaccine']) + " " + str(row['appointment_time']) + " " + str(row['patient']))    

    except pymssql.Error as e:
        raise e
    finally:
        cm.close_connection()
    return None


def get_caregivers(name):
    cm = ConnectionManager()
    conn = cm.create_connection()  
    get_apt_details = "SELECT id, vaccine, appointment_time, caregiver FROM Appointments WHERE patient = %s  ORDER BY id"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(get_apt_details, name)
        if cursor.rowcount==0:
            print("No appointments found for patient: {n}".format(n=name))
            return
        else:
            for row in cursor:
                print(str(row['id']) + " " + str(row['vaccine']) + " " + str(row['appointment_time']) + " " + str(row['caregiver']))    
    except pymssql.Error as e:
        raise e
    finally:
        cm.close_connection()
    return None


def show_appointments(tokens):
    '''
    TODO: Part 2
    '''
    global current_caregiver
    global current_patient
    if not current_caregiver and not current_patient:
        print('Please login first!')
        return
    if len(tokens)!=1:
        print('Invalid input')
    if current_patient is not None:
        get_caregivers(current_patient.get_username())
    elif current_caregiver is not None:
        #print(current_caregiver.get_username())
        get_patients(current_caregiver.get_username())     
    


def logout(tokens):
    """
    TODO: Part 2
    """
    global current_patient
    global current_caregiver
    if not current_caregiver and not current_patient:
        print('Please login first!')
        return
    if len(tokens)!=1:
        print('Invalid input')
        return
    if current_caregiver is not None:
        current_caregiver = None
        print('Successfully logged out')
    elif current_patient is not None:
        current_patient = None
        print('Successfully logged out!')                    


def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
        print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
        print("> upload_availability <date>")
        print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
        print("> logout")  # // TODO: implement logout (Part 2)
        print("> Quit")
        print()
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break
        tokens = response.split(" ")
        #response = response.lower()
        # only password should be case sensitive
        if len(tokens) > 1:
            tokens[1] = tokens[1].lower()
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0].lower()
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == cancel:
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
