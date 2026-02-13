from db import DB

def cap(text: str) -> str:
    return (text or "").strip().title()


class CourseService:
    def __init__(self):
        self.db = DB()

    # ----------------- helpers -----------------
    def _get_course_id(self, course_name: str):
        course_name = cap(course_name)
        row = self.db.run(
            "SELECT course_id FROM course WHERE LOWER(course_name)=LOWER(%s)",
            (course_name,),
            fetchone=True
        )
        return row[0] if row else None

    def _get_user_by_email(self, email: str):
        email = (email or "").strip().lower()
        return self.db.run(
            "SELECT user_id, user_name, password, role, email, mobile_no "
            "FROM users WHERE LOWER(email)=LOWER(%s)",
            (email,),
            fetchone=True
        )

    def _validate_mobile(self, mobile_no: str, required: bool = False):
        mobile_no = (mobile_no or "").strip()

        if required and not mobile_no:
            return False, "Mobile number is required."

        if not mobile_no:
            return True, ""

        if not mobile_no.isdigit():
            return False, "Mobile number must contain digits only."
        if len(mobile_no) != 10:
            return False, "Mobile number must be exactly 10 digits."

        return True, ""

    # ----------------- dropdown data -----------------
    def get_users_by_role(self, role: str, only_approved_professors: bool = True):
        """
        Returns list[(user_id, user_name, email)]
        """
        role = (role or "").strip().lower()

        if role == "professor" and only_approved_professors:
            rows = self.db.run(
                "SELECT u.user_id, u.user_name, u.email "
                "FROM users u "
                "JOIN professor p ON p.professor_id = u.user_id "
                "WHERE u.role='professor' AND p.status='approved' "
                "ORDER BY u.user_name",
                fetch=True
            )
            return rows or []

        rows = self.db.run(
            "SELECT user_id, user_name, email "
            "FROM users WHERE role=%s "
            "ORDER BY user_name",
            (role,),
            fetch=True
        )
        return rows or []

    # ----------------- AUTH -----------------
    def register_user(self, user_name, email, password, role, mobile_no=""):
        user_name = cap(user_name)
        email = (email or "").strip().lower()
        password = (password or "").strip()

        if role not in ("admin", "professor", "student"):
            return False, "Invalid role."

        if not user_name or not email or not password:
            return False, "Name, email and password are required."

        ok_m, msg = self._validate_mobile(mobile_no, required=False)
        if not ok_m:
            return False, msg

        mobile_no = (mobile_no or "").strip()

        if self._get_user_by_email(email):
            return False, "Email already registered."

        ok = self.db.run(
            "INSERT INTO users(user_name,password,email,role,mobile_no) VALUES(%s,%s,%s,%s,%s)",
            (user_name, password, email, role, mobile_no)
        )
        if not ok:
            return False, "DB error while creating user."

        user = self._get_user_by_email(email)
        if not user:
            return False, "User created but cannot read back."

        user_id = user[0]

        if role == "admin":
            self.db.run("INSERT IGNORE INTO admin(admin_id) VALUES(%s)", (user_id,))
        elif role == "student":
            self.db.run("INSERT IGNORE INTO student(student_id) VALUES(%s)", (user_id,))
        elif role == "professor":
            self.db.run(
                "INSERT IGNORE INTO professor(professor_id, status) VALUES(%s,'waiting')",
                (user_id,)
            )

        return True, {"user_id": user_id, "user_name": user_name, "email": email, "role": role}

    def login_user(self, email, password, role):
        email = (email or "").strip().lower()
        password = (password or "").strip()

        row = self._get_user_by_email(email)
        if not row:
            return False, "No account found for this email."

        user_id, user_name, db_pass, db_role, db_email, db_mobile = row

        if db_role != role:
            return False, f"This email is registered as '{db_role}', not '{role}'."

        if db_pass != password:
            return False, "Wrong password."

        if role == "professor":
            pr = self.db.run(
                "SELECT status FROM professor WHERE professor_id=%s",
                (user_id,),
                fetchone=True
            )
            status = pr[0] if pr else "waiting"
            if status != "approved":
                return False, f"Professor account is '{status}'. Ask admin to approve."

        return True, {"user_id": user_id, "user_name": user_name, "email": db_email, "role": db_role}

    # ----------------- Admin: professor approvals -----------------
    def get_professors_by_status(self, status="waiting"):
        rows = self.db.run(
            "SELECT u.user_id, u.user_name, u.email, p.status "
            "FROM professor p JOIN users u ON u.user_id=p.professor_id "
            "WHERE p.status=%s ORDER BY u.user_name",
            (status,),
            fetch=True
        )
        return rows or []

    def set_professor_account_status(self, professor_id, status):
        if status not in ("approved", "rejected", "waiting"):
            return False
        return self.db.run(
            "UPDATE professor SET status=%s WHERE professor_id=%s",
            (status, professor_id)
        )

    # ==================== COURSE OPS ====================
    def add_course(self, name):
        name = cap(name)
        return self.db.run(
            "INSERT INTO course(course_name, course_fees, course_duration) VALUES(%s, %s, %s)",
            (name, 0.00, "NA")
        )

    def delete_course(self, name):
        cid = self._get_course_id(name)
        if not cid:
            return False
        return self.db.run("DELETE FROM course WHERE course_id=%s", (cid,))

    def show_courses(self):
        return self.db.run("SELECT course_name FROM course", fetch=True)

    # ==================== PROFESSOR OPS ====================
    def assign_professor_to_course_by_id(self, professor_id, course_name):
        cid = self._get_course_id(course_name)
        if not cid:
            return False

        self.db.run("INSERT IGNORE INTO professor(professor_id) VALUES(%s)", (professor_id,))

        return self.db.run(
            "INSERT INTO course_professor(course_id, professor_id, status) VALUES(%s,%s,'active') "
            "ON DUPLICATE KEY UPDATE status='active'",
            (cid, professor_id)
        )

    def view_professor_courses_by_id(self, professor_id):
        return self.db.run(
            "SELECT c.course_name "
            "FROM course_professor cp "
            "JOIN course c ON c.course_id = cp.course_id "
            "WHERE cp.professor_id=%s AND cp.status='active'",
            (professor_id,),
            fetch=True
        )

    # ==================== ENROLLMENT OPS ====================
    def enroll_student_by_id(self, student_id, course_name):
        cid = self._get_course_id(course_name)
        if not cid:
            return False

        self.db.run("INSERT IGNORE INTO student(student_id) VALUES(%s)", (student_id,))

        return self.db.run(
            "INSERT INTO enrollment(course_id, student_id, status) VALUES(%s,%s,'enrolled') "
            "ON DUPLICATE KEY UPDATE status='enrolled'",
            (cid, student_id)
        )

    def view_student_courses_by_id(self, student_id):
        return self.db.run(
            "SELECT c.course_name "
            "FROM enrollment e "
            "JOIN course c ON c.course_id = e.course_id "
            "WHERE e.student_id=%s AND e.status='enrolled'",
            (student_id,),
            fetch=True
        )

    def view_enrolled_students(self, course_name):
        cid = self._get_course_id(course_name)
        if not cid:
            return []
        return self.db.run(
            "SELECT u.user_name "
            "FROM enrollment e "
            "JOIN users u ON u.user_id = e.student_id "
            "WHERE e.course_id=%s AND e.status='enrolled'",
            (cid,),
            fetch=True
        )

    # ==================== GRADES OPS ====================
    def upload_student_grades_by_id(self, student_id, course_name, grade):
        cid = self._get_course_id(course_name)
        if not cid:
            return False

        enrolled = self.db.run(
            "SELECT 1 FROM enrollment WHERE course_id=%s AND student_id=%s AND status='enrolled'",
            (cid, student_id),
            fetchone=True
        )
        if not enrolled:
            return False

        return self.db.run(
            "INSERT INTO grades(course_id, student_id, grade) VALUES(%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE grade=%s",
            (cid, student_id, grade, grade)
        )

    def view_student_grades_by_id(self, student_id, course_name):
        cid = self._get_course_id(course_name)
        if not cid:
            return None

        row = self.db.run(
            "SELECT grade FROM grades WHERE course_id=%s AND student_id=%s",
            (cid, student_id),
            fetchone=True
        )
        return row[0] if row else None

    # ==================== PROFESSOR COURSE REQUESTS (old feature) ====================
    def request_professor_course(self, professor_name, course_name):
        professor_name = cap(professor_name)
        course_name = cap(course_name)

        if self._get_course_id(course_name) is None:
            return False

        return self.db.run(
            "INSERT INTO professor_course_requests (professor_name, course_name, status) "
            "VALUES (%s, %s, 'pending') "
            "ON DUPLICATE KEY UPDATE status='pending'",
            (professor_name, course_name)
        )

    def get_pending_professor_requests(self):
        rows = self.db.run(
            "SELECT professor_name, course_name, status "
            "FROM professor_course_requests "
            "WHERE status='pending' "
            "ORDER BY requested_at DESC",
            fetch=True
        )
        return rows or []

    def set_professor_request_status(self, professor_name, course_name, status):
        professor_name = cap(professor_name)
        course_name = cap(course_name)

        if status not in ("accepted", "rejected"):
            return False

        if status == "accepted":
            # NOTE: this accepts by name; fine if you keep your old requests system
            # If you want name->id mapping, tell me and I’ll convert it.
            pass

        return self.db.run(
            "UPDATE professor_course_requests SET status=%s "
            "WHERE professor_name=%s AND course_name=%s",
            (status, professor_name, course_name)
        )

    def get_professor_requests(self, professor_name):
        professor_name = cap(professor_name)
        rows = self.db.run(
            "SELECT course_name, status "
            "FROM professor_course_requests "
            "WHERE professor_name=%s "
            "ORDER BY requested_at DESC",
            (professor_name,),
            fetch=True
        )
        return rows or []
