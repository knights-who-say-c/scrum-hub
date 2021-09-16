import mysql.connector

print("Starting Demo...")

database = mysql.connector.connect(
    host = "localhost",
    port = "3306",
    user = "armani",
    password = "jesse",
    database = "test"
    )

cursor = database.cursor()

cursor.execute("USE test")

print("Wiping table...")
cursor.execute("DROP TABLE IF EXISTS demo")

cursor.execute("CREATE TABLE demo (FirstName Char(30), LastName Char(30), Age INT, Class Char(7))")

print("Table 'demo' created...")

name = input("Enter full name: ").split()
age = int(input("Enter age: "))

cursor.execute("INSERT INTO demo (FirstName, LastName, Age, Class) VALUES(%s, %s, %s, %s)", (name[0], name[1], age, "CSE 442"))

database.commit()

cursor.execute("SELECT * FROM demo")

res = cursor.fetchall()

for x in res:
    print(res)
