import pymysql

# ---------------------------
# CONFIG (change these)
# ---------------------------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "changed"
DB_NAME = "db10"

# ✅ You create this admin and share creds manually
ADMIN_NAME = "Company"
ADMIN_EMAIL = "admin@company.com"
ADMIN_PASSWORD = "Admin@123"  # keep simple for demo; later you can hash


conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    autocommit=True
)

tables_sql = [
"""
CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  user_name VARCHAR(100) NOT NULL,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  role ENUM('admin','professor','student') NOT NULL,
  mobile_no VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
""",
"""
CREATE TABLE IF NOT EXISTS admin (
  admin_id INT PRIMARY KEY,
  FOREIGN KEY (admin_id) REFERENCES users(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;
""",
"""
CREATE TABLE IF NOT EXISTS professor (
  professor_id INT PRIMARY KEY,
  status ENUM('waiting','approved','rejected') DEFAULT 'waiting',
  FOREIGN KEY (professor_id) REFERENCES users(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;
""",
"""
CREATE TABLE IF NOT EXISTS student (
  student_id INT PRIMARY KEY,
  FOREIGN KEY (student_id) REFERENCES users(user_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;
""",
"""
CREATE TABLE IF NOT EXISTS course (
  course_id INT AUTO_INCREMENT PRIMARY KEY,
  course_name VARCHAR(150) NOT NULL,
  course_fees DECIMAL(10,2) NOT NULL,
  course_duration VARCHAR(50) NOT NULL
) ENGINE=InnoDB;
""",
"""
CREATE TABLE IF NOT EXISTS course_professor (
  course_id INT NOT NULL,
  professor_id INT NOT NULL,
  status ENUM('active','inactive') DEFAULT 'active',
  PRIMARY KEY (course_id, professor_id),
  FOREIGN KEY (course_id) REFERENCES course(course_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (professor_id) REFERENCES professor(professor_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;
""",
"""
CREATE TABLE IF NOT EXISTS enrollment (
  course_id INT NOT NULL,
  student_id INT NOT NULL,
  status ENUM('enrolled','completed','dropped') DEFAULT 'enrolled',
  PRIMARY KEY (course_id, student_id),
  FOREIGN KEY (course_id) REFERENCES course(course_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  FOREIGN KEY (student_id) REFERENCES student(student_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB;
""",
"""
CREATE TABLE IF NOT EXISTS professor_course_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    professor_name VARCHAR(100) NOT NULL,
    course_name VARCHAR(150) NOT NULL,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_request (professor_name, course_name)
) ENGINE=InnoDB;
"""
]


def seed_single_admin(cur):
    """
    Ensures there is exactly ONE admin user + admin table row.
    If an admin exists, do nothing.
    If not, create one using ADMIN_* constants.
    """
    # 1) check if admin exists
    cur.execute("SELECT user_id, email FROM users WHERE role='admin' LIMIT 1;")
    row = cur.fetchone()
    if row:
        print(f"✅ Admin already exists: user_id={row[0]}, email={row[1]}")
        return

    # 2) create admin user
    cur.execute(
        "INSERT INTO users (user_name, password, email, role, mobile_no) VALUES (%s, %s, %s, %s, %s);",
        (ADMIN_NAME, ADMIN_PASSWORD, ADMIN_EMAIL, "admin", "0000000000")
    )
    admin_user_id = cur.lastrowid

    # 3) create admin table record
    cur.execute("INSERT INTO admin (admin_id) VALUES (%s);", (admin_user_id,))

    print("✅ Admin created successfully:")
    print("   Email:", ADMIN_EMAIL)
    print("   Password:", ADMIN_PASSWORD)


with conn.cursor() as cur:
    for q in tables_sql:
        cur.execute(q)

    seed_single_admin(cur)

conn.close()
print("All tables created successfully.")
