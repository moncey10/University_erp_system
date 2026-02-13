def cap(text):
    return text.strip().title()

class Professor:
    def __init__(self, course_service):
        self.course_service = course_service

    def assign_professor_to_course(self, prof_name, course_name):
        return self.course_service.assign_professor_to_course(cap(prof_name), cap(course_name))

    def assign_student_to_course(self, student_name, course_name):
        return self.course_service.enroll_student(cap(student_name), cap(course_name))

    def view_assigned_courses(self, prof_name):
        result = self.course_service.view_professor_courses(cap(prof_name))
        return [r[0] for r in result] if result else []

    def view_enrolled_students(self, course_name):
        result = self.course_service.view_enrolled_students(cap(course_name))
        return [r[0] for r in result] if result else []

    def upload_grades(self, student_name, course_name, grade):
        return self.course_service.upload_student_grades(cap(student_name), cap(course_name), grade)

    def view_grades(self, student_name, course_name):
        return self.course_service.view_student_grades(cap(student_name), cap(course_name))
