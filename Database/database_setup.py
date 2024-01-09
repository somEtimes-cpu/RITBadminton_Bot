import sqlite3


def make_table():
    conn = sqlite3.connect('Database/badminton_discord_member.db')

    c = conn.cursor()

    c.execute("""CREATE TABLE registered_member (
              Discord_id integer PRIMARY KEY,
              Discord_name text,
              RIT_Username text,
              Name text,
              Pronoun text,
              Due_Paid integer DEFAULT 0
    )""")
    # 1 = True, 0 = False
    conn.commit()

    conn.close()

def drop_table():
    conn = sqlite3.connect('Database/badminton_discord_member.db')

    c = conn.cursor()

    c.execute("""DROP TABLE registered_member""")
    
    conn.commit()

    conn.close()

def print_table():
    conn = sqlite3.connect('Database/badminton_discord_member.db')

    c = conn.cursor()

    c.execute(f"""SELECT * FROM registered_member""")
    rows = c.fetchall()

    if rows:
        for row in rows:
            print("Discord ID: {}, Discord Name: {}, RIT Username: {}, Name: {}, Pronoun: {}, Due Paid: {}".format(*row))
    else:
        print("The table is empty.")
    
    conn.commit()

    conn.close()

def test(discord_id: int):
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""UPDATE registered_member SET Due_Paid = 1""")
    conn.commit()
    conn.close()

def delete_profile(discord_id: int):
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""DELETE FROM registered_member WHERE Discord_id = ?""", (discord_id,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    #make_table()
    #drop_table()
    #delete_profile(176022438281347075)
    print_table()
    #test= test(176022438231342072)