import sqlite3


def run_sql():
    conn = sqlite3.connect('Database/badminton_member.db')

    c = conn.cursor()


    c.execute("""CREATE TABLE registered_member (
              discord_id integer,
              discord_name text,
              first_name text,
              last_name text,
              email text,
              pronoun text,
              is_RIT text,
              is_Eboard text,
              is_Former_Eboard text
    )""")
    
#    c.execute("DROP TABLE registered_member")

    conn.commit()

    conn.close()


if __name__ == '__main__':
    run_sql()