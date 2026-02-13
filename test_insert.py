from init_db_newschema import DB

db = DB()
ok = db.run("INSERT INTO courses(name) VALUES(%s)", ("Computer Science",))
print("Insert OK?", ok)

rows = db.run("SELECT id, name, professor_name FROM courses", fetch=True)
print("Rows:", rows)
