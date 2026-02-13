
class Course:
    def __init__(self):
        self.course = []  
        self.name = []  
        self.assignment = {}  
        self.student_assignment = {}  
        self.grades = {} 

    
    def add_course(self, new_course):
        if new_course not in self.course:
            self.course.append(new_course)
            return True
        return False  

    def delete_course(self, name):
        for i in self.course:
            if i.lower() == name.lower():
                self.course.remove(i)
                self.assignment.pop(i, None)
                self.student_assignment.pop(i, None)
                return True
        return False  

    def register_student_with_course(self, student_name, course_name):
        if course_name not in self.course:
            return False, f"Course '{course_name}' does not exist."
        
        if student_name not in self.name:
            self.name.append(student_name)

        if course_name not in self.student_assignment:
            self.student_assignment[course_name] = []

        if student_name not in self.student_assignment[course_name]:
            self.student_assignment[course_name].append(student_name)
            return True, f"Student '{student_name}' registered and assigned to '{course_name}'."
        else:
            return False, f"Student '{student_name}' is already enrolled in '{course_name}'."

    def remove_student(self, sname):
        removed = False
        for student in self.name:
            if student.lower() == sname.lower():
                self.name.remove(student)
                removed = True
                break
        if not removed:
            return False  

        for course, students in self.student_assignment.items():
            if sname in students:
                students.remove(sname)
        keys_to_remove = [key for key in self.grades if key[0].lower() == sname.lower()]
        for key in keys_to_remove:
            self.grades.pop(key)

        return True

   
    def course_assigned(self, prof_name, course_name):
     if course_name not in self.course:
        self.course.append(course_name)
    
     self.assignment[course_name] = prof_name
     return True

    
    def course_assigned_student(self, student_name, course_name):
        if course_name not in self.course:
            self.course.append(course_name)
        if course_name not in self.student_assignment:
            self.student_assignment[course_name] = []
        if student_name not in self.student_assignment[course_name]:
            self.student_assignment[course_name].append(student_name)
        return self.student_assignment
    
    

    def show_details(self):
        return self.course

    def view_professor_courses(self, prof_name):
        return [course for course, prof in self.assignment.items() if prof == prof_name]

    def view_student_courses(self, student_name):
        courses = []
        for course, students in self.student_assignment.items():
            if student_name in students:
                courses.append(course)
        return courses

    def view_students_in_course(self, course_name):
        return self.student_assignment.get(course_name, [])

    def upload_student_grades(self, student_name, course_name, grade):
        key = (student_name, course_name)
        self.grades[key] = grade

    def view_student_grades(self, student_name, course_name):
        key = (student_name, course_name)
        return self.grades.get(key, None)
