import psycopg2

conn_DB=psycopg2.connect("dbname='NOM DE TA BASE DE DONNEE' user='PSEUDO DE TA BASE DE DONNEE' host='IP DE TA BASE DE DONNEE' password='MOT DE PASSE DE TA BASE DE DONNEE'")

cur = conn_DB.cursor()

cur.execute("""SELECT id_user, nom_usuel, dernier_message_XP, experience, dernier_message_meme, position FROM users""")

rows = cur.fetchall()

for row in rows:
    print("ID = {} ".format(row[0]))
    print("NOM USUEL = {}".format(row[1]))
    print("DERNIER MESSAGE XP = {}".format(row[2]))
    print("XP = {}".format(row[3]))
    print("DERNIER MESSAGE MEME = {}".format(row[4]))
    print("POSITION = {}".format(row[5]))
    print("\n")

#input("Press enter for quit...")