from db import DB

def cap(text):
    return text.strip().title()


class CourseService:
    def __init__(self):
        self.db = DB()

    # ----------------- helpers -----------------
    def _get_course_id(self, course_name):
        course_name = cap(course_name)
        row = self.db.run(
            "SELECT course_id FROM course WHERE LOWER(course_name)=%s",
            (course_name.lower(),),
            fetchone=True
        )
        return row[0] if row else None

    def _get_user_id_by_name_and_role(self, user_name, role):
        user_name = cap(user_name)
        row = self.db.run(
            "SELECT user_id FROM users WHERE LOWER(user_name)=%s AND role=%s",
            (user_name.lower(), role),
            fetchone=True
        )
        return row[0] if row else None

    def _ensure_professor(self, prof_name):
        # create user if not exists
        uid = self._get_user_id_by_name_and_role(prof_name, "professor")
        if uid is None:
            self.db.run(
                "INSERT INTO users(user_name,password,email,role,mobile_no) VALUES(%s,%s,%s,%s,%s)",
                (cap(prof_name), "pass", f"{cap(prof_name).replace(' ', '').lower()}@demo.com", "professor", "NA")
            )
            uid = self._get_user_id_by_name_and_role(prof_name, "professor")
        # ensure professor row exists
        self.db.run(
            "INSERT IGNORE INTO professor(professor_id) VALUES(%s)",
            (uid,)
        )
        return uid

    def _ensure_student(self, student_name):
        uid = self._get_user_id_by_name_and_role(student_name, "student")
        if uid is None:
            self.db.run(
                "INSERT INTO users(user_name,password,email,role,mobile_no) VALUES(%s,%s,%s,%s,%s)",
                (cap(student_name), "pass", f"{cap(student_name).replace(' ', '').lower()}@demo.com", "student", "NA")
            )
            uid = self._get_user_id_by_name_and_role(student_name, "student")
        self.db.run(
            "INSERT IGNORE INTO student(student_id) VALUES(%s)",
            (uid,)
        )
        return uid

    # ==================== COURSE OPERATIONS ====================
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

    def course_exists(self, course_name):
        return self._get_course_id(course_name) is not None

    # ==================== PROFESSOR OPERATIONS ====================
    def assign_professor_to_course(self, prof_name, course_name):
        cid = self._get_course_id(course_name)
        if not cid:
            return False

        pid = self._ensure_professor(prof_name)

        # Insert mapping, if exists update status to active
        ok = self.db.run(
            "INSERT INTO course_professor(course_id, professor_id, status) VALUES(%s,%s,'active') "
            "ON DUPLICATE KEY UPDATE status='active'",
            (cid, pid)
        )
        return ok

    def view_professor_courses(self, prof_name):
        pid = self._get_user_id_by_name_and_role(prof_name, "professor")
        if not pid:
            return []

        return self.db.run(
            "SELECT c.course_name "
            "FROM course_professor cp "
            "JOIN course c ON c.course_id = cp.course_id "
            "WHERE cp.professor_id=%s AND cp.status='active'",
            (pid,),
            fetch=True
        )

    # ==================== ENROLLMENT OPERATIONS ====================
    def enroll_student(self, student_name, course_name):
        cid = self._get_course_id(course_name)
        if not cid:
            return False

        sid = self._ensure_student(student_name)

        return self.db.run(
            "INSERT INTO enrollment(course_id, student_id, status) VALUES(%s,%s,'enrolled') "
            "ON DUPLICATE KEY UPDATE status='enrolled'",
            (cid, sid)
        )

    def view_student_courses(self, student_name):
        sid = self._get_user_id_by_name_and_role(student_name, "student")
        if not sid:
            return []

        return self.db.run(
            "SELECT c.course_name "
            "FROM enrollment e "
            "JOIN course c ON c.course_id = e.course_id "
            "WHERE e.student_id=%s AND e.status='enrolled'",
            (sid,),
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

    # ==================== GRADE OPERATIONS ====================
    def upload_student_grades(self, student_name, course_name, grade):
        cid = self._get_course_id(course_name)
        if not cid:
            return False

        sid = self._get_user_id_by_name_and_role(student_name, "student")
        if not sid:
            return False

        # ensure student is enrolled
        enrolled = self.db.run(
            "SELECT 1 FROM enrollment WHERE course_id=%s AND student_id=%s AND status='enrolled'",
            (cid, sid),
            fetchone=True
        )
        if not enrolled:
            return False

        return self.db.run(
            "INSERT INTO grades(course_id, student_id, grade) VALUES(%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE grade=%s",
            (cid, sid, grade, grade)
        )

    def view_student_grades(self, student_name, course_name):
        cid = self._get_course_id(course_name)
        if not cid:
            return None

        sid = self._get_user_id_by_name_and_role(student_name, "student")
        if not sid:
            return None

        row = self.db.run(
            "SELECT grade FROM grades WHERE course_id=%s AND student_id=%s",
            (cid, sid),
            fetchone=True
        )
        return row[0] if row else None
    
        # ==================== PROFESSOR REQUESTS (NEW) ====================

    def request_professor_course(self, professor_name, course_name):
        professor_name = cap(professor_name)
        course_name = cap(course_name)

        # Ensure course exists
        if not self.course_exists(course_name):
            return False

        # Insert request as pending (or reset to pending if previously rejected)
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

        # If accepted -> assign professor in courses table (your old schema supports 1 professor per course)
        if status == "accepted":
            # reuse your existing method if you have it, else update directly
            ok = self.assign_professor_to_course(professor_name, course_name)
            if not ok:
                return False

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

