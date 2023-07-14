#Ahnaf Ahmad
#1001835014

from flask import Flask, request
from flask_restful import Api, Resource
import sqlite3
import re
import datetime
import os

app = Flask(__name__)
api = Api(app)

#Regular expressions patterns to match name and phone numbers
name_pattern = r"(([A-Z][a-z]*(’[A-Z][a-z]*)?(-[A-Z][a-z]*)?), ([A-Z][a-z]*) [A-Z][.]\Z)|(([A-Z][a-z]*(’[A-Z][a-z]*)?(-[A-Z][a-z]*)?), (([A-Z][a-z]*) )*([A-Z][a-z]*)\Z)|(([A-Z][a-z]*)(,? ([A-Z][a-z]*(’[A-Z][a-z]*)?(-[A-Z][a-z]*)?))?\Z)"
num_pattern= r'(\+[1-9][0-9]{0,2}([ ]?))?(([0-9]{5}\Z)|(((1?[(][0-9]{3}[)])|((1-)?([0-9]{3}[-])))?([0-9]{3}-[0-9]{4}))|((1 )?[0-9]{3} [0-9]{3} [0-9]{4})|((1.)?[0-9]{3}\.[0-9]{3}\.[0-9]{4})|((45 )?[0-9]{2} [0-9]{2} [0-9]{2} [0-9]{2})|((45 )?[0-9]{4} [0-9]{4})|([0-9]{5}.[0-9]{5})|([0-9]{3} ([0-9] )?[0-9]{3} [0-9]{3} [0-9]{4})|(\([0-9]{2}\) [0-9]{3}-[0-9]{4}))'
#Create log file
log_file = open("request_log.txt", "a")


#Checking for phonebook.db in directory
if not os.path.isfile('phonebook.db'):
    #if not create a new one
    conn = sqlite3.connect('phonebook.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE phonebook
                (name VARCHAR(50), phoneNumber VARCHAR(15))''')
    conn.commit()
    conn.close()



class PhoneBook(Resource):
    #get request to get all the entries in phonebook.db
    def get(self, arg=None):
        if arg == "list":
            conn = sqlite3.connect('phonebook.db')
            c = conn.cursor()
            c.execute("SELECT * FROM PhoneBook")
            entries = c.fetchall()
            results = []
            for entry in entries:
                results.append({"name": entry[0], "phoneNumber": entry[1]})
            return results, 200
        else:
            return "Invalid Endpoint", 404
    
    #post request to add new entries
    def post(self, arg=None):
        if arg == "add":
            conn = sqlite3.connect('phonebook.db')
            c = conn.cursor()
            obj = request.json
            name = obj["name"]
            phoneNumber = obj["phoneNumber"]
            #checking for a case where both inputs are invalid
            if not re.match(name_pattern, name) and not re.match(num_pattern, phoneNumber):
                return "Invalid name and number format", 400
            #check for name input
            if not re.match(name_pattern, name):
                return "Invalid name format", 400
            #check for phone number input
            if not re.match(num_pattern, phoneNumber):
                return "Invalid number format", 400
            #if inputs are valid, add to the database
            query = "INSERT INTO phonebook VALUES (?, ?)"
            values = (name, phoneNumber)
            c.execute(query, values)
            conn.commit()
            return "Success", 200
        else:
            return "Invalid Endpoint", 404
    
    #put request to delete entries
    def put(self, arg=None):
        #deleteByName
        if arg == "deleteByName":
            conn = sqlite3.connect('phonebook.db')
            c = conn.cursor()
            obj = request.json
            name = obj["name"]
            #check for name input validation
            if not re.match(name_pattern, name):
                return "Invalid name format", 400
            query = "SELECT * FROM phonebook WHERE name=?"
            values = (name, )
            c.execute(query, values)
            #check if the entry actually exists
            if c.fetchone() is None:
                return "Name not found", 404
            
            query = "DELETE FROM phonebook WHERE name=?"
            c.execute(query, values)
            conn.commit()
            return "Success", 200
        
        #deleteByNumber
        elif arg =="deleteByNumber":
            conn = sqlite3.connect('phonebook.db')
            c = conn.cursor()
            obj = request.json
            phoneNumber = obj["phoneNumber"]
            #check for phone number input
            if not re.match(num_pattern, phoneNumber):
                return "Invalid number format", 400
            query = "SELECT * FROM phonebook WHERE phoneNumber=?"
            values = (phoneNumber,)
            c.execute(query, values)
            #check if the entry actually exists
            if c.fetchone() is None:
                return "Number not found", 404
            query = "DELETE FROM phonebook WHERE phoneNumber=?"
            values = (phoneNumber,)
            c.execute(query, values)
            conn.commit()
            return "Success", 200
        else:
            return "Invalid Endpoint", 404
        
api.add_resource(PhoneBook, "/PhoneBook", "/PhoneBook/<string:arg>")

#log before the request
@app.before_request
def log_request():
    ip_address = request.remote_addr
    request_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    request_method = request.method
    request_path = request.path
    log_file.write(f'{request_time}: {ip_address} - "{request_method} {request_path}" - ')
    
    #Get the json data in the log
    if request.method in ['POST', 'PUT']:
        json_data = request.get_json()
        if json_data:
            log_file.write(f'{json_data}\n')
        else:
            log_file.write(f'No JSON data provided\n')
    
#log after the request
@app.after_request
def log_response(response):
    response_status = response.status
    log_file.write(f'{response_status}\n')
    log_file.flush()
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("8080"),debug=False)
