import sqlite3
from object_classes import Discord_Member
import pandas as pd
'''
@dataclass
class Discord_Member:
        Class for recording registered discord member
    Discord_ID: int
    Discrod_Name: str
    is_RIT: str
    First_name: str
    Last_name: str
    Email: str
    is_Eboard: str
    is_Former_Eboard: str


    CREATE TABLE registered_member (
              discord_id integer,
              discord_name text,
              first_name text,
              last_name text,
              email text,
              pronoun text,
              is_RIT text,
              is_Eboard text,
              is_Former_Eboard text
'''

def test_insert_member(conn: sqlite3.Connection, member: Discord_Member, c: sqlite3.Cursor):
    c.execute("INSERT INTO registered_member VALUES(:ID, :DC_name, :is_RIT, :first, :last, :email, :pronoun, :is_Eboard, :is_Former_Eboard)", 
              {'ID': member.Discord_ID, 'DC_name': member.Discrod_Name, 'first': member.First_name, 'last': member.Last_name, 'email':member.Email, 'pronoun': member.pronoun,'is_RIT': member.is_RIT, 'is_Eboard': member.is_Eboard, 'is_Former_Eboard': member.is_Former_Eboard})
    conn.commit()

def insert_member(member: Discord_Member):
    conn = sqlite3.connect('Database/badminton_member.db')
    c = conn.cursor()
    c.execute("INSERT INTO registered_member VALUES(:ID, :DC_name, :first, :last, :email, :pronoun, :is_RIT, :is_Eboard, :is_Former_Eboard)", 
            {'ID': member.Discord_ID, 'DC_name': member.Discrod_Name, 'first': member.First_name, 'last': member.Last_name, 'email':member.Email, 'pronoun':member.pronoun,'is_RIT': member.is_RIT, 'is_Eboard': member.is_Eboard, 'is_Former_Eboard': member.is_Former_Eboard})
    conn.commit()
    conn.close()

def get_all_members():
    conn = sqlite3.connect('Database/badminton_member.db')
    members = pd.read_sql_query("SELECT * FROM registered_member", conn)
    conn.commit()
    conn.close()
    return members

def delete_member(member_id: int):
    conn = sqlite3.connect('Database/badminton_member.db')
    c = conn.cursor()
    c.execute("SELECT * FROM registered_member")
    conn.commit()
    c.execute("DELETE FROM registered_member WHERE discord_id={}".format(member_id))
    conn.commit()

def find_member(member_id: int):
    conn = sqlite3.connect('Database/badminton_member.db')
    c = conn.cursor()
    c.execute("SELECT * FROM registered_member WHERE discord_id={member_id}".format(member_id=member_id))
    conn.commit()
    result = c.fetchall()
    return result

def find_value(member_id: int, field: str):
    conn = sqlite3.connect('Database/badminton_member.db')
    c = conn.cursor()
    c.execute("SELECT {field} FROM registered_member WHERE discord_id={member_id}".format(field=field, member_id=member_id))
    conn.commit()
    result = c.fetchone()
    conn.commit()
    return result



if __name__ == '__main__':
    test_mem = Discord_Member(123, 'saf', 'yes', 'han', 'chen', 'hc', 'true', 'false', "false")

    #table name for dc members: registered_member
    #delete_member(176022438281347072)
    #insert_member(conn, test_mem, c)

    print(get_all_members())

