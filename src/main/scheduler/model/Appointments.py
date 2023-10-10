import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql


class Appointments:
    def __init__(self, id, patient, caregiver, vaccine, time):
        self.id = id
        self.patient = patient
        self.caregiver = caregiver
        self.vaccine = vaccine
        self.time = time

    # def get_username(self):
    #     return self.username

    # def get_salt(self):
    #     return self.salt

    # def get_hash(self):
    #     return self.hash

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_appointments = "INSERT INTO Appointments VALUES (%d, %s, %s, %s, %s)"
        try:
            cursor.execute(add_appointments, (self.id, self.patient, self.caregiver, self.vaccine, self.time))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()