import pymysql

conn = pymysql.connect(
    host="localhost",
    user="root",
    password="changed",
    database="db10",
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


with conn.cursor() as cur:
    for q in tables_sql:
        cur.execute(q)

conn.close()
print("All tables created successfully.")
