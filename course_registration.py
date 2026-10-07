"""University Course Registration System 
  Group 4. 
Nankunda Rowena-S25B38/009
Namugga Daniella-M25B38/007
Keji Flora-S25B38/039
Jjumba Julius-M25B38/016
Asio Dementria-M25B38/039
Ezechiel Baraka-M25B38/041
"""
import re
from abc import ABC, abstractmethod
from datetime import date



# 1. EXCEPTIONS - specific error types for clear messages


class RegistrationError(Exception):
    """Base class for all business-rule violations in the system."""


class DuplicateRecordError(RegistrationError):
    """Raised when a student/course with the same ID/code already exists."""


class RecordNotFoundError(RegistrationError):
    """Raised when a student, course or registration cannot be found."""


class DuplicateRegistrationError(RegistrationError):
    """Raised when a student is already registered for a course."""


class CourseFullError(RegistrationError):
    """Raised when a course has reached its capacity."""


class CreditLimitError(RegistrationError):
    """Raised when a registration would exceed the student's credit limit."""


class WrongProgrammeError(RegistrationError):
    """Raised when a student tries to take a course from another programme."""



# 2. MODELS - Registration, Student, Course (abstract) and subclasses
# Registration: an ASSOCIATION CLASS linking ONE student to ONE course.
# It records extra facts about the link (dates, status) that belong to
# neither Student nor Course alone.

class Registration:
    ACTIVE = "ACTIVE"
    DROPPED = "DROPPED"

    def __init__(self, student, course):
        self._student = student
        self._course = course
        self._registration_date = date.today()
        self._drop_date = None
        self._status = Registration.ACTIVE

    @property
    def student(self):
        return self._student

    @property
    def course(self):
        return self._course

    @property
    def status(self):
        return self._status

    @property
    def is_active(self):
        return self._status == Registration.ACTIVE

    @property
    def registration_date(self):
        return self._registration_date

    @property
    def drop_date(self):
        return self._drop_date

    def drop(self):
        if not self.is_active:
            raise RegistrationError("This registration has already been dropped.")
        self._status = Registration.DROPPED
        self._drop_date = date.today()

    def __str__(self):
        return (f"{self._student.student_id} -> {self._course.code} "
                f"[{self._status}] registered {self._registration_date}")



# Programme: a degree programme that offers a set of courses

class Programme:
    def __init__(self, code, name):
        self.__courses = []                    # private: only Programme may change it
        code = str(code).strip().upper()
        if not re.fullmatch(r"[A-Z]{2,5}", code):
            raise ValueError("Programme code must be 2-5 letters (e.g. BCS).")
        self._code = code                      # protected, read-only
        self.name = name

    @property
    def code(self):
        return self._code

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = str(value).strip()
        if len(value) < 3:
            raise ValueError("Programme name must have at least 3 characters.")
        self._name = value

    @property
    def courses(self):
        return tuple(self.__courses)           # read-only view

    def has_course(self, course):
        return course in self.__courses

    def add_course(self, course):
        if self.has_course(course):
            raise DuplicateRecordError(f"{course.code} is already in {self.code}.")
        course.assign_to(self)                 # a course belongs to exactly one programme
        self.__courses.append(course)

    def __str__(self):
        return f"{self.code:<5} {self.name} ({len(self.__courses)} courses)"



# Student

class Student:
    MAX_CREDITS = 24  # maximum active credit units per semester

    def __init__(self, student_id, name, programme, email):
        self._student_id = student_id          # protected, read-only (no setter)
        self.__registrations = []              # private: only Student may touch it
        self.name = name                       # goes through validating setters
        self.programme = programme
        self.email = email

    # - controlled access (properties + validation) -
    @property
    def student_id(self):
        return self._student_id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = str(value).strip()
        if len(value) < 2 or not re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", value):
            raise ValueError("Name must be at least 2 letters (letters, spaces, . ' - only).")
        # capitalise the first letter of each word but keep the rest (McDonald, O'Neil)
        self._name = " ".join(w[:1].upper() + w[1:] for w in value.split())

    @property
    def programme(self):
        return self._programme

    @programme.setter
    def programme(self, value):
        if not isinstance(value, Programme):
            raise ValueError("A student must belong to a valid programme.")
        if hasattr(self, "_programme") and value is not self._programme \
                and self.active_registrations:
            raise ValueError("Cannot change programme while registered for courses.")
        self._programme = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        value = str(value).strip()
        if not re.fullmatch(r"[^@\s]+@gmail\.com",  value):
            raise ValueError("Invalid email address.")
        self._email = value.lower()

    # - registrations (read-only views of private data) -
    @property
    def registrations(self):
        return tuple(self.__registrations)

    @property
    def active_registrations(self):
        return [r for r in self.__registrations if r.is_active]

    @property
    def total_credits(self):
        return sum(r.course.credit_units for r in self.active_registrations)

    def total_charges(self):
        # Polymorphism: each course computes its own charge
        return sum(r.course.calculate_course_charge() for r in self.active_registrations)

    def total_workload(self):
        return sum(r.course.calculate_workload() for r in self.active_registrations)

    def is_registered_for(self, course):
        return any(r.course is course for r in self.active_registrations)

    def check_can_take(self, course):
        """Validate business rules BEFORE any change is made."""
        if self.is_registered_for(course):
            raise DuplicateRegistrationError(
                f"{self.name} is already registered for {course.code}.")
        if self.total_credits + course.credit_units > Student.MAX_CREDITS:
            raise CreditLimitError(
                f"Credit limit exceeded: {self.total_credits} + {course.credit_units} "
                f"> {Student.MAX_CREDITS}.")

    def add_registration(self, registration):
        self.check_can_take(registration.course)
        self.__registrations.append(registration)

    def __str__(self):
        return (f"{self.student_id:<9} {self.name:<22} {self.programme.code:<5} "
                f"{self.email}")



# Course: ABSTRACT base class

class Course(ABC):
    FEE_PER_CREDIT = 50_000      # UGX per credit unit
    CATEGORY = "General"

    def __init__(self, code, title, credit_units, capacity):
        self.__registrations = []              # private
        self._programme = None                 # set once by Programme.add_course()
        self._code = self._validate_code(code)  # protected, read-only
        self.title = title
        self.credit_units = credit_units
        self.capacity = capacity

    @staticmethod
    def _validate_code(code):
        code = str(code).strip().upper()
        if not re.fullmatch(r"[A-Z]{2,4}\d{3,4}", code):
            raise ValueError("Course code must look like CSC2101 (2-4 letters + 3-4 digits).")
        return code

    # - controlled access -
    @property
    def code(self):
        return self._code

    @property
    def programme(self):
        return self._programme

    def assign_to(self, programme):
        if self._programme is not None:
            raise RegistrationError(f"{self.code} already belongs to {self._programme.code}.")
        self._programme = programme

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        value = str(value).strip()
        if len(value) < 3:
            raise ValueError("Course title must have at least 3 characters.")
        self._title = value

    @property
    def credit_units(self):
        return self._credit_units

    @credit_units.setter
    def credit_units(self, value):
        if not isinstance(value, int) or not 1 <= value <= 6:
            raise ValueError("Credit units must be a whole number from 1 to 6.")
        if hasattr(self, "_credit_units") and value != self._credit_units and self.enrolment > 0:
            raise ValueError("Credit units cannot change once students are enrolled.")
        self._credit_units = value

    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError("Capacity must be a positive whole number.")
        if value < len(self.active_registrations):
            raise ValueError("Capacity cannot be lower than current enrolment.")
        self._capacity = value

    @property
    def active_registrations(self):
        return [r for r in self.__registrations if r.is_active]

    @property
    def students(self):
        return [r.student for r in self.active_registrations]

    @property
    def enrolment(self):
        return len(self.active_registrations)

    @property
    def is_full(self):
        return self.enrolment >= self._capacity

    def check_can_accept(self, student):
        if student in self.students:
            raise DuplicateRegistrationError(
                f"{student.name} is already registered for {self.code}.")
        if self.is_full:
            raise CourseFullError(f"{self.code} is full ({self._capacity}/{self._capacity}).")

    def add_registration(self, registration):
        self.check_can_accept(registration.student)
        self.__registrations.append(registration)

    # - ABSTRACT methods: every subclass MUST implement these -
    @abstractmethod
    def calculate_course_charge(self):
        """Total fee (UGX) a student pays for this course."""

    @abstractmethod
    def calculate_workload(self):
        """Estimated weekly workload in hours."""

    def extra_details(self):
        """Overridden by subclasses to describe category-specific data."""
        return ""

    def __str__(self):
        extra = f" | {self.extra_details()}" if self.extra_details() else ""
        prog = self._programme.code if self._programme else "-"
        return (f"{self.code:<8} {self.title:<26} {self.CATEGORY:<10} {prog:<5} "
                f"{self.credit_units}cu  {self.enrolment}/{self.capacity}{extra}")



# Concrete subclasses (method overriding)

class TheoryCourse(Course):
    CATEGORY = "Theory"

    def calculate_course_charge(self):
        return self.credit_units * Course.FEE_PER_CREDIT

    def calculate_workload(self):
        # 1 lecture hour + 2 self-study hours per credit unit
        return self.credit_units * 3


class PracticalCourse(Course):
    CATEGORY = "Practical"

    def __init__(self, code, title, credit_units, capacity, lab_hours=3, lab_fee=80_000):
        super().__init__(code, title, credit_units, capacity)
        if lab_hours < 1 or lab_fee < 0:
            raise ValueError("Lab hours must be >= 1 and lab fee cannot be negative.")
        self._lab_hours = lab_hours
        self._lab_fee = lab_fee

    def calculate_course_charge(self):
        return self.credit_units * Course.FEE_PER_CREDIT + self._lab_fee

    def calculate_workload(self):
        # lectures + weekly lab session + 1 self-study hour per credit unit
        return self.credit_units * 2 + self._lab_hours

    def extra_details(self):
        return f"lab {self._lab_hours}h/wk, lab fee {self._lab_fee:,}"


class ProjectCourse(Course):
    CATEGORY = "Project"

    def __init__(self, code, title, credit_units, capacity, supervision_fee=150_000):
        super().__init__(code, title, credit_units, capacity)
        if supervision_fee < 0:
            raise ValueError("Supervision fee cannot be negative.")
        self._supervision_fee = supervision_fee

    def calculate_course_charge(self):
        return self.credit_units * Course.FEE_PER_CREDIT + self._supervision_fee

    def calculate_workload(self):
        # mostly independent work: 5 hours per credit unit + 1 supervision meeting
        return self.credit_units * 5 + 1

    def extra_details(self):
        return f"supervision fee {self._supervision_fee:,}"



# 3. REGISTRAR - coordinates students, courses and registrations


class Registrar:
    def __init__(self, institution="Uganda Technology University"):
        self.institution = institution
        self._programmes = {}      # aggregation: programmes exist independently
        self._students = {}        # aggregation: students exist independently
        self._courses = {}         # aggregation: courses exist independently
        self._registrations = []   # aggregation: master list of Registration records
                                   # (Registrar creates them via register_for_course)
        self._next_id = 1

    # - registration of records -
    def add_programme(self, programme):
        if not isinstance(programme, Programme):
            raise TypeError("Only Programme objects can be added.")
        if programme.code in self._programmes:
            raise DuplicateRecordError(f"Programme {programme.code} already exists.")
        self._programmes[programme.code] = programme
        return programme

    def register_student(self, name, programme_code, email):
        programme = self.find_programme(programme_code)
        student = Student(f"STU-{self._next_id:04d}", name, programme, email)
        if any(s.email == student.email for s in self._students.values()):
            raise DuplicateRecordError(f"A student with email {student.email} already exists.")
        self._next_id += 1
        self._students[student.student_id] = student
        return student

    def add_course(self, course, programme_code):
        if not isinstance(course, Course):
            raise TypeError("Only Course objects can be added.")
        if course.code in self._courses:
            raise DuplicateRecordError(f"Course code {course.code} already exists.")
        self.find_programme(programme_code).add_course(course)
        self._courses[course.code] = course
        return course

    # - lookups -
    def find_programme(self, code):
        key = str(code).strip().upper()
        if key not in self._programmes:
            raise RecordNotFoundError(f"No programme with code '{code}'.")
        return self._programmes[key]

    def find_student(self, student_id):
        key = str(student_id).strip().upper()
        if key not in self._students:
            raise RecordNotFoundError(f"No student with ID '{student_id}'.")
        return self._students[key]

    def find_course(self, code):
        key = str(code).strip().upper()
        if key not in self._courses:
            raise RecordNotFoundError(f"No course with code '{code}'.")
        return self._courses[key]

    @property
    def programmes(self):
        return list(self._programmes.values())

    @property
    def students(self):
        return list(self._students.values())

    @property
    def courses(self):
        return list(self._courses.values())

    # - main transactions -
    def register_for_course(self, student_id, course_code):
        student = self.find_student(student_id)
        course = self.find_course(course_code)
        # validate everything first so a failure leaves no partial changes
        if course.programme is not student.programme:
            raise WrongProgrammeError(
                f"{course.code} belongs to {course.programme.code}, but {student.name} "
                f"is in {student.programme.code}.")
        student.check_can_take(course)
        course.check_can_accept(student)
        registration = Registration(student, course)
        student.add_registration(registration)
        course.add_registration(registration)
        self._registrations.append(registration)
        return registration

    def drop_course(self, student_id, course_code):
        student = self.find_student(student_id)
        course = self.find_course(course_code)
        for reg in student.active_registrations:
            if reg.course is course:
                reg.drop()
                return reg
        raise RegistrationError(f"{student.name} is not registered for {course.code}.")

    # - queries -
    def courses_of_student(self, student_id):
        return [r.course for r in self.find_student(student_id).active_registrations]

    def students_in_course(self, course_code):
        return self.find_course(course_code).students

    def search_students(self, keyword):
        k = keyword.strip().lower()
        return [s for s in self.students
                if k in s.student_id.lower() or k in s.name.lower()
                or k in s.programme.name.lower() or k in s.programme.code.lower()]

    def search_courses(self, keyword):
        k = keyword.strip().lower()
        return [c for c in self.courses
                if k in c.code.lower() or k in c.title.lower()
                or k in c.CATEGORY.lower() or k in c.programme.name.lower()
                or k in c.programme.code.lower()]

    # - report -
    def summary(self):
        active = [r for r in self._registrations if r.is_active]
        dropped = len(self._registrations) - len(active)
        by_cat = {}
        for c in self.courses:
            by_cat.setdefault(c.CATEGORY, []).append(c)
        lines = [f"===== {self.institution}: Registration Summary =====",
                 f"Students registered : {len(self._students)}",
                 f"Programmes offered  : {len(self._programmes)}",
                 f"Courses offered     : {len(self._courses)}",
                 f"Active registrations: {len(active)}   (dropped: {dropped})"]
        lines.append("\nPer programme:")
        for p in self.programmes:
            n = sum(1 for s in self.students if s.programme is p)
            lines.append(f"  {p.code:<5} {p.name:<34} {len(p.courses)} courses, {n} students")
        lines.append("\nPer course (polymorphic charge & workload):")
        for c in self.courses:
            lines.append(f"  {c.code:<8} {c.CATEGORY:<10} enrolled {c.enrolment}/{c.capacity:<3} "
                         f"charge UGX {c.calculate_course_charge():>9,}  "
                         f"workload {c.calculate_workload():>2} h/wk"
                         f"{'  [FULL]' if c.is_full else ''}")
        lines.append("\nCourses by category: " +
                     ", ".join(f"{k}={len(v)}" for k, v in by_cat.items()))
        revenue = sum(r.course.calculate_course_charge() for r in active)
        lines.append(f"Expected fee income : UGX {revenue:,}")
        if self.courses:
            top = max(self.courses, key=lambda c: c.enrolment)
            lines.append(f"Most popular course : {top.code} - {top.title} ({top.enrolment} students)")
        return "\n".join(lines)



# 4. MENU - user interface only (input/output)


# - input helpers -
def ask(prompt):
    return input(prompt).strip()


def ask_int(prompt, low=None, high=None):
    while True:
        try:
            value = int(ask(prompt))
        except ValueError:
            print("  ! Please enter a whole number.")
            continue
        if (low is not None and value < low) or (high is not None and value > high):
            if low is not None and high is not None:
                print(f"  ! Value must be between {low} and {high}.")
            elif low is not None:
                print(f"  ! Value must be at least {low}.")
            else:
                print(f"  ! Value must be at most {high}.")
            continue
        return value


def load_defaults(reg):
    """Preset programmes, each with its own courses: loaded at start-up."""
    catalogue = {
        ("BCS", "BSc Computer Science"): [
            TheoryCourse("CSC2101", "Data Structures", 4, 40),
            PracticalCourse("CSC2102", "Networking Lab", 3, 20, 3, 80_000),
            TheoryCourse("CSC2103", "Operating Systems", 3, 40),
            ProjectCourse("CSC3100", "Final Year Project", 6, 10, 150_000)],
        ("BSE", "BSc Software Engineering"): [
            TheoryCourse("SWE2101", "Software Design", 3, 40),
            PracticalCourse("SWE2102", "Web Development Lab", 3, 25, 3, 80_000),
            PracticalCourse("CSC2201", "Database Systems Lab", 4, 25, 3, 90_000),
            ProjectCourse("SWE3200", "Software Eng. Project", 5, 15, 120_000)],
        ("BIT", "BSc Information Technology"): [
            TheoryCourse("ITE2101", "Systems Analysis", 3, 40),
            PracticalCourse("ITE2102", "Network Administration Lab", 3, 20, 3, 80_000),
            ProjectCourse("ITE3100", "IT Capstone Project", 5, 15, 120_000)],
        ("BDS", "BSc Data Science"): [
            TheoryCourse("DSC2101", "Data Science", 4, 40),
            TheoryCourse("DSC2102", "Statistics", 3, 40),
            PracticalCourse("DSC2201", "Machine Learning Lab", 4, 20, 3, 90_000),
            ProjectCourse("DSC3100", "Data Science Project", 5, 15, 120_000)],
        ("BBA", "Bachelor of Business Admin"): [
            TheoryCourse("BUS1101", "Principles of Management", 3, 60),
            TheoryCourse("BUS1102", "Accounting", 3, 60),
            TheoryCourse("BUS2101", "Marketing", 3, 50),
            ProjectCourse("BUS3100", "Business Research Project", 5, 20, 100_000)],
    }
    for (code, name), courses in catalogue.items():
        reg.add_programme(Programme(code, name))
        for course in courses:
            reg.add_course(course, code)


def pick_programme(reg):
    """Show a numbered list of programmes and let the user choose by number."""
    programmes = reg.programmes
    if not programmes:
        raise RegistrationError("There are no programmes to choose from.")
    print("\nProgrammes:")
    for i, p in enumerate(programmes, 1):
        print(f"  {i:>2}. {p}")
    return programmes[ask_int("Choose programme number: ", 1, len(programmes)) - 1]


def pick_course(reg, courses=None):
    """Show a numbered list and let the user choose by number."""
    courses = reg.courses if courses is None else courses
    if not courses:
        raise RegistrationError("There are no courses to choose from.")
    print("\nAvailable courses:")
    for i, c in enumerate(courses, 1):
        print(f"  {i:>2}. {c}")
    return courses[ask_int("Choose course number: ", 1, len(courses)) - 1]


# - menu actions -
def register_student(reg):
    programme = pick_programme(reg)
    s = reg.register_student(ask("Full name: "), programme.code, ask("Email: "))
    print(f"  ✓ Student registered with ID {s.student_id}")


def add_course(reg):
    programme = pick_programme(reg)
    print("Category: 1) Theory  2) Practical  3) Project")
    choice = ask_int("Choose: ", 1, 3)
    code, title = ask("Course code (e.g. CSC2101): "), ask("Title: ")
    credits, cap = ask_int("Credit units (1-6): ", 1, 6), ask_int("Capacity: ", 1)
    if choice == 1:
        course = TheoryCourse(code, title, credits, cap)
    elif choice == 2:
        course = PracticalCourse(code, title, credits, cap,
                                 ask_int("Lab hours per week: "), ask_int("Lab fee (UGX): "))
    else:
        course = ProjectCourse(code, title, credits, cap, ask_int("Supervision fee (UGX): "))
    reg.add_course(course, programme.code)
    print(f"  ✓ Course {course.code} added to {programme.code}. Charge: UGX {course.calculate_course_charge():,}")


def register_for_course(reg):
    student = reg.find_student(ask("Student ID: "))      # fail early if no such student
    print(f"Enrolling {student.name} ({student.programme.name}; "
          f"{student.total_credits}/{student.MAX_CREDITS} credits used)")
    course = pick_course(reg, list(student.programme.courses))   # only own programme
    r = reg.register_for_course(student.student_id, course.code)
    print(f"  ✓ {r.student.name} registered for {r.course.code} "
          f"(UGX {r.course.calculate_course_charge():,})")


def drop_course(reg):
    student = reg.find_student(ask("Student ID: "))
    course = pick_course(reg, reg.courses_of_student(student.student_id))
    r = reg.drop_course(student.student_id, course.code)
    print(f"  ✓ {r.student.name} dropped {r.course.code}")


def student_courses(reg):
    sid = ask("Student ID: ")
    student = reg.find_student(sid)
    courses = reg.courses_of_student(sid)
    print(f"\nCourses for {student.name} ({student.student_id}):")
    if not courses:
        print("  (none)")
    for c in courses:
        print(f"  {c.code:<8} {c.title:<26} {c.CATEGORY:<10} "
              f"UGX {c.calculate_course_charge():>9,}  {c.calculate_workload()} h/wk")
    print(f"  Total credits: {student.total_credits}/{student.MAX_CREDITS} | "
          f"Total charges: UGX {student.total_charges():,} | "
          f"Weekly workload: {student.total_workload()} h")


def course_students(reg):
    course = pick_course(reg)
    code = course.code
    print(f"\nStudents in {course.code} - {course.title} ({course.enrolment}/{course.capacity}):")
    students = reg.students_in_course(code)
    for s in students:
        print("  ", s)
    if not students:
        print("  (none)")


def show(items, label):
    print(f"\n{label}:" if items else "\n  (nothing to display yet)")
    for i in items:
        print("  ", i)


def show_programmes(reg):
    for p in reg.programmes:
        print(f"\n{p.code} - {p.name}")
        for c in p.courses:
            print("   ", c)


def search_students(reg):
    show(reg.search_students(ask("Search (ID/name/programme): ")), "Matching students")


def search_courses(reg):
    show(reg.search_courses(ask("Search (code/title/category): ")), "Matching courses")


def load_sample_data(reg):
    """Demo students/registrations (programmes and courses are already preloaded)."""
    for n, p, e in [("Alice Mukasa", "BCS", "alice@gmail.com"),
                    ("Brian Okello", "BIT", "brian@gmail.com"),
                    ("Grace Namuli", "BSE", "grace@gmail.com")]:
        reg.register_student(n, p, e)
    reg.register_for_course("STU-0001", "CSC2101")
    reg.register_for_course("STU-0001", "CSC2102")
    reg.register_for_course("STU-0002", "ITE3100")
    reg.register_for_course("STU-0003", "SWE2101")
    print("  ✓ Sample data loaded (3 students and 4 registrations).")


MENU = """
================ COURSE REGISTRATION SYSTEM ================
 1. Add new student             8. Search courses
 2. Add new course              9. List all courses
 3. Enrol student in course    10. List all students
 4. Drop a course              11. Summary report
 5. Courses of a student       12. Load sample data
 6. Students in a course       13. Programmes and their courses
 7. Search students
 0. Exit
"""


def main():
    reg = Registrar()
    load_defaults(reg)
    actions = {"1": register_student, "2": add_course, "3": register_for_course,
               "4": drop_course, "5": student_courses, "6": course_students,
               "7": search_students, "8": search_courses,
               "9": lambda r: show(r.courses, "All courses"),
               "10": lambda r: show(r.students, "All students"),
               "11": lambda r: print("\n" + r.summary()),
               "12": load_sample_data, "13": show_programmes}
    while True:
        print(MENU)
        choice = ask("Choose an option: ")
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action is None:
            print("  ! Invalid option.")
            continue
        try:
            action(reg)
        except (RegistrationError, ValueError) as err:   # clear messages for invalid operations
            print(f"  ✗ Rejected: {err}")


if __name__ == "__main__":
    main()