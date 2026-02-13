import pymysql

# Test database connection and operations


conn = pymysql.connect(
        host="localhost",
        user="root",
        password="changed",
        database="db7"
    )
    
cursor = conn.cursor()
    
    # Test insert
cursor.execute("INSERT INTO courses(name) VALUES(%s)", ("Python 101",))
conn.commit()
print("✓ Inserted course 'Python 101'")

    # Test select
cursor.execute("SELECT * FROM courses")
results = cursor.fetchall()
