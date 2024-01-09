import sqlite3

async def new_registered_member(discord_id: int, discord_name: str):
    if (await check_existence(discord_id=discord_id)):
        return
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO registered_member(Discord_id, Discord_name)
              VALUES(?,?)""", (discord_id, discord_name))    
    conn.commit()
    conn.close()

async def update_verified_username(discord_id: int, discord_name: str, RIT_username: str):
    if not (await check_existence(discord_id=discord_id)):
        await new_registered_member(discord_id=discord_id, discord_name=discord_name)
    RIT_username_toString = f"{RIT_username}" 
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""UPDATE registered_member SET RIT_Username = ? 
              WHERE Discord_id = ?""", (RIT_username_toString, discord_id))
    conn.commit()
    conn.close()

async def update_name(discord_id: int, discord_name: str, name: str):
    if not (await check_existence(discord_id=discord_id)):
        await new_registered_member(discord_id=discord_id, discord_name=discord_name) 
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""UPDATE registered_member SET Name = ? 
              WHERE Discord_id = ?""", (name, discord_id))
    conn.commit()
    conn.close()

async def update_paid_status(discord_id: int, discord_name: str, is_due_paid: int):
    if not (await check_existence(discord_id=discord_id)):
        await new_registered_member(discord_id=discord_id, discord_name=discord_name)
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""UPDATE registered_member SET Due_Paid = ? 
              WHERE Discord_id = ?""", (is_due_paid, discord_id))
    conn.commit()
    conn.close()

async def update_pronoun(discord_id: int, discord_name: str, pronoun: str):
    if not (await check_existence(discord_id=discord_id)):
        await new_registered_member(discord_id=discord_id, discord_name=discord_name)
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""UPDATE registered_member SET Pronoun = ? 
              WHERE Discord_id = ?""", (pronoun, discord_id))
    conn.commit()
    conn.close()

async def check_paid(discord_id: int) -> bool:
    respond = False
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""SELECT 1 FROM registered_member WHERE Due_Paid = 1 AND Discord_id = ?""", (discord_id,))
    result = c.fetchone()
    if result:
        respond = True
    conn.close()
    return respond

async def check_existence(discord_id: int) ->  bool:
    respond = False
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""SELECT 1 FROM registered_member WHERE Discord_id = ?""", (discord_id,))
    result = c.fetchone()
    if result:
        respond = True
    conn.close()
    return respond

async def is_Username_registered(RIT_Username: str, discord_id: int) -> bool:
    respond = False
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""SELECT 1 FROM registered_member WHERE RIT_Username = ? AND Discord_id != ?""", (RIT_Username, discord_id))
    result = c.fetchone()
    if result:
        respond = True
    conn.close()
    return respond

async def get_RIT_Username(discord_id: int):
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""SELECT RIT_Username FROM registered_member WHERE Discord_id = ?""", (discord_id,))
    result = c.fetchone()
    conn.close()
    return result

async def get_Name(discord_id: int):
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""SELECT Name FROM registered_member WHERE Discord_id = ?""", (discord_id,))
    result = c.fetchone()
    conn.close()
    return result

async def get_Pronoun(discord_id: int):
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""SELECT Pronoun FROM registered_member WHERE Discord_id = ?""", (discord_id,))
    result = c.fetchone()
    conn.close()
    return result

async def get_paid_status(discord_id: int):
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""SELECT Due_Paid FROM registered_member WHERE Discord_id = ?""", (discord_id,))
    result = c.fetchone()
    conn.close()
    return result

async def delete_RIT_info(discord_id: int, discord_name: str):
    await update_paid_status(discord_id=discord_id, discord_name=discord_name, is_due_paid=0)
    await update_verified_username(discord_id=discord_id, discord_name=discord_name, RIT_username=None)
    await update_name(discord_id=discord_id, discord_name=discord_name, name=None)

async def delete_profile(discord_id: int):
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""DELETE FROM registered_member WHERE Discord_id = ?""", (discord_id,))
    conn.commit()
    conn.close()

async def get_all_verified_RIT_member():
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""SELECT Discord_id FROM registered_member WHERE RIT_Username != ?""", ("None",))
    result = c.fetchall()
    conn.close()
    return result

async def get_all_verified_RIT_member_name():
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""SELECT Name FROM registered_member WHERE Name != ?""", ("None",))
    result = c.fetchall()
    names = []
    for name in result:
        names.append(name[0])
    conn.close()
    return names

async def set_all_paid_0():
    conn = sqlite3.connect('Database/badminton_discord_member.db')
    c = conn.cursor()
    c.execute("""UPDATE registered_member SET Due_Paid = 0""")
    conn.commit()
    conn.close()


"""
CREATE TABLE registered_member (
              Discord_id integer PRIMARY KEY,
              Discord_name text,
              RIT_Username text,
              Pronoun text,
              Due_Paid integer DEFAULT 0   
    """