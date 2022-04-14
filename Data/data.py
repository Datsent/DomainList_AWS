import sqlite3
#import Data
from Data import Utils, Collector

def add_to_table(data):
    connection = sqlite3.connect(Utils.DB_FILE)
    cursor = connection.cursor()
    cursor.execute('''INSERT INTO Domains(Domain_Name,Validity,Certificate_valid)
                            VALUES(?,?,?)''', data)
    connection.commit()
    connection.close()

def table_name(db):
    con = sqlite3.connect(db)
    cursor = con.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    a = cursor.fetchall()
    return a[0][0]

def add_list_to_db(data):
    connection = sqlite3.connect(Utils.DB_FILE)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Domains
                  (Domain_Name TEXT, Validity INT, Certificate_valid INT)''')
    for i in data:
        cursor.execute('''INSERT INTO Domains(Domain_Name,Validity,Certificate_valid)
                        VALUES(?,?,?)''', i)
    connection.commit()
    connection.close()
def create_db():
    connection = sqlite3.connect(Utils.DB_FILE)
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS Domains")
    cursor.execute('''CREATE TABLE IF NOT EXISTS Domains
                  (Domain_Name TEXT, Validity INT, Certificate_valid INT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS User
                  (username TEXT, password TEXT)''')
    connection.commit()
    connection.close()

def print_db():
    conn = sqlite3.connect(Utils.DB_FILE)
    print("Opened database for printing successfully")
    cursor = conn.execute("SELECT Domain_Name, Validity, Certificate_valid from Domains")
    for row in cursor:
        print("DOMAIN = ", row[0])
        print("Validity = ", row[1])
        print("Cert Validity = ", row[2], '\n')
    print("Operation printing done successfully")
    conn.close()

def load_db_into_list():
    conn = sqlite3.connect(Utils.DB_FILE)
    cur = conn.cursor()
    with conn:
        cur.execute("SELECT * FROM Domains")
        a = cur.fetchall()
    conn.commit()
    conn.close()
    return a

def load_user_into_list():
    conn = sqlite3.connect(Utils.DB_FILE)
    cur = conn.cursor()
    with conn:
        cur.execute("SELECT * FROM user")
        a = cur.fetchall()
    conn.commit()
    conn.close()
    return a

def add_user(data):
    connection = sqlite3.connect(Utils.DB_FILE)
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS Domains")
    cursor.execute('''CREATE TABLE IF NOT EXISTS Domains
                  (Domain_Name TEXT, Validity INT, Certificate_valid INT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS User
                  (username TEXT, password TEXT)''')
    cursor.execute('''INSERT INTO user(username,password)
                                VALUES(?,?)''', data)
    connection.commit()
    connection.close()

def add_new_domain(domain):
    '''
    Add new domain name to file, witch contain list of domain names.
    :param domain: is str. name of new domain name.
    :return: Nothing. Add name to file.
    '''
    connection = sqlite3.connect(Utils.DB_FILE)
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Domains
                      (Domain_Name TEXT, Validity INT, Certificate_valid INT)''')
    cursor.execute("SELECT Domain_Name FROM Domains WHERE Domain_Name = ?", (domain,))
    data = cursor.fetchall()
    if len(data) == 0:
        print(f'There is no component named {data}. Adding')
        print(f'Getting data for {domain}')
        new_domain = [domain, Collector.validity_date(domain), Collector.ssl_expiry_datetime(domain)]
        add_to_table(new_domain)
    else:
        print(f'Domain {domain} in the list')


if __name__ == '__main__':
    create_db()