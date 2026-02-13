def cap(text):
    return text.strip().title()

class Student:
    def __init__(self, course_service):
        self.course_service = course_service

    def view_registered_courses(self, student_name):
        result = self.course_service.view_student_courses(cap(student_name))
        return [r[0] for r in result] if result else []

    def view_my_grade(self, student_name, course_name):
        return self.course_service.view_student_grades(cap(student_name), cap(course_name))
