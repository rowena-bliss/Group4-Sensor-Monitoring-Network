==============================================================================
 UNIVERSITY COURSE REGISTRATION SYSTEM
 Group 4 - Object-Oriented Programming Project (Python)
==============================================================================

GROUP MEMBERS
-------------
  Nankunda Rowena     S25B38/009
  Namugga Daniella    M25B38/007
  Keji Flora          S25B38/039
  Jjumba Julius       M25B38/016
  Asio Dementria      M25B38/039
  Ezechiel Baraka     M25B38/041


1. OVERVIEW
-----------
A console (text-menu) application that manages student enrolment at a
university ("Uganda Technology University" by default). The Registrar can:

  - add students and courses,
  - enrol students in courses and drop them,
  - search, list and report on students, courses and programmes,
  - calculate fees (in UGX) and weekly study workload for each course.

The system enforces real-world business rules (credit limits, course
capacity, programme restrictions, duplicate checks) and reports problems
with clear, specific error messages instead of crashing.

All data is held in memory only. Nothing is saved when the program exits.


2. REQUIREMENTS
---------------
  - Python 3.6 or newer (uses f-strings and numeric underscores such as
    50_000).
  - No third-party packages. Only the standard library is used:
    re, abc, datetime.


3. HOW TO RUN
-------------
  1. Save the source file (e.g. course_registration.py).
  2. Open a terminal in the same folder.
  3. Run:

         python course_registration.py

  On start-up the system automatically loads 5 programmes and their
  courses (see section 7). Student records are NOT preloaded; use menu
  option 12 to load demo students.


4. MENU GUIDE
-------------
  Option  Action
  ------  ------------------------------------------------------------
   1      Add new student - pick a programme, then enter name and email.
          The system assigns an ID automatically (STU-0001, STU-0002...).
   2      Add new course - pick a programme and category (Theory,
          Practical or Project), then enter code, title, credit units,
          capacity and any category-specific fees/hours.
   3      Enrol student in course - enter the Student ID, then choose
          from the courses of that student's own programme.
   4      Drop a course - enter the Student ID, then choose from the
          courses the student is currently taking.
   5      Courses of a student - lists active courses with charge and
          workload, plus total credits, total charges and total weekly
          workload.
   6      Students in a course - choose a course to see who is enrolled.
   7      Search students - by ID, name, programme name or programme code.
   8      Search courses - by code, title, category or programme.
   9      List all courses.
  10      List all students.
  11      Summary report - totals, per-programme and per-course figures,
          expected fee income and the most popular course.
  12      Load sample data - adds 3 demo students and 4 registrations.
  13      Programmes and their courses.
   0      Exit.

  Notes:
  - Courses and programmes are picked by NUMBER from a displayed list.
  - Student IDs are typed in (e.g. STU-0001); upper/lower case is ignored.
  - Invalid menu choices or numbers simply re-prompt or show a message.


5. BUSINESS RULES ENFORCED
--------------------------
  - A student can only take courses from their OWN programme.
  - A student cannot register for the same course twice.
  - Maximum 24 active credit units per student (Student.MAX_CREDITS).
  - A course cannot exceed its capacity.
  - Student emails must be unique and must end in @gmail.com.
  - Student names: at least 2 characters; letters, spaces and . ' -
    only. The first letter of each word is capitalised.
  - Programme code: 2-5 letters (e.g. BCS). Programme name: 3+ chars.
  - Course code: 2-4 letters followed by 3-4 digits (e.g. CSC2101).
  - Course title: 3+ characters. Credit units: whole number 1-6.
    Capacity: whole number >= 1.
  - A course's credit units cannot change once students are enrolled,
    and its capacity cannot be lowered below the current enrolment.
  - A student cannot change programme while holding active registrations.
  - Dropped registrations are kept as history (status DROPPED with a
    drop date) but no longer count toward credits, capacity or fees.
  - All checks run BEFORE any change is made, so a failed registration
    never leaves partial data behind.


6. FEES AND WORKLOAD
--------------------
Base fee: UGX 50,000 per credit unit. Each course category calculates its
own charge and workload (polymorphism):

  Category    Charge (UGX)                          Weekly workload (hours)
  ---------   -----------------------------------   -----------------------
  Theory      credits x 50,000                      credits x 3
  Practical   credits x 50,000 + lab fee            credits x 2 + lab hours
              (default lab fee 80,000, 3 lab hrs)
  Project     credits x 50,000 + supervision fee    credits x 5 + 1
              (default supervision fee 150,000)

Example: a 4-credit Practical course with a 90,000 lab fee and 3 lab hours
costs 4 x 50,000 + 90,000 = UGX 290,000 and needs 4 x 2 + 3 = 11 h/week.


7. PRELOADED PROGRAMMES AND COURSES
-----------------------------------
  BCS  BSc Computer Science
       CSC2101 Data Structures (Theory), CSC2102 Networking Lab (Practical),
       CSC2103 Operating Systems (Theory), CSC3100 Final Year Project
  BSE  BSc Software Engineering
       SWE2101 Software Design, SWE2102 Web Development Lab,
       CSC2201 Database Systems Lab, SWE3200 Software Eng. Project
  BIT  BSc Information Technology
       ITE2101 Systems Analysis, ITE2102 Network Administration Lab,
       ITE3100 IT Capstone Project
  BDS  BSc Data Science
       DSC2101 Data Science, DSC2102 Statistics,
       DSC2201 Machine Learning Lab, DSC3100 Data Science Project
  BBA  Bachelor of Business Admin
       BUS1101 Principles of Management, BUS1102 Accounting,
       BUS2101 Marketing, BUS3100 Business Research Project

Sample data (option 12) adds:
  STU-0001 Alice Mukasa (BCS) -> CSC2101, CSC2102
  STU-0002 Brian Okello (BIT) -> ITE3100
  STU-0003 Grace Namuli (BSE) -> SWE2101


8. PROGRAM STRUCTURE (OOP DESIGN)
---------------------------------
The file is organised in four sections:

  1. EXCEPTIONS
       RegistrationError (base class) with specific subclasses:
       DuplicateRecordError, RecordNotFoundError,
       DuplicateRegistrationError, CourseFullError, CreditLimitError,
       WrongProgrammeError.

  2. MODELS
       Registration      Association class linking ONE student to ONE
                         course; stores registration date, drop date and
                         status (ACTIVE / DROPPED).
       Programme         A degree programme that owns a set of courses.
       Student           Holds personal data and the student's
                         registrations; computes credits, charges and
                         workload.
       Course (abstract) Base class for all courses; declares the abstract
                         methods calculate_course_charge() and
                         calculate_workload().
       TheoryCourse, PracticalCourse, ProjectCourse
                         Concrete subclasses that override the abstract
                         methods and extra_details().

  3. REGISTRAR
       The controller class. It stores all programmes, students, courses
       and registrations, creates Registration objects, performs lookups,
       searches and the summary report.

  4. MENU (user interface)
       Input helpers (ask, ask_int), menu action functions and main().
       All printing/input lives here; the model classes never print.

OOP concepts demonstrated:
  - Encapsulation   Private lists (double underscore, e.g.
                    __registrations) and protected attributes, accessed
                    through properties with validating setters. Read-only
                    properties return tuples/copies, so outside code
                    cannot change internal lists directly.
  - Abstraction     Course is an abstract base class (ABC) and cannot be
                    instantiated.
  - Inheritance     Theory/Practical/Project courses extend Course.
  - Polymorphism    Charges and workloads are computed by calling the same
                    method on different course types.
  - Association     Registration links Student and Course.
  - Aggregation     Registrar holds programmes, students and courses that
                    exist independently of it.
  - Custom exceptions for each kind of rule violation.

Error handling: main() wraps every menu action in a try/except for
RegistrationError and ValueError and prints "Rejected: <reason>", so the
program keeps running after invalid input.


9. SAMPLE SESSION
-----------------
  Choose an option: 12
    Sample data loaded (3 students and 4 registrations).
  Choose an option: 5
  Student ID: stu-0001

  Courses for Alice Mukasa (STU-0001):
    CSC2101  Data Structures  Theory      UGX   200,000  12 h/wk
    CSC2102  Networking Lab   Practical   UGX   230,000  9 h/wk
    Total credits: 7/24 | Total charges: UGX 430,000 | Weekly workload: 21 h


10. KNOWN LIMITATIONS AND POSSIBLE IMPROVEMENTS
-----------------------------------------------
  - No data persistence (no file or database storage). Everything is lost
    on exit. Saving to JSON/CSV or SQLite would be a natural extension.
  - Option 12 assumes the first three student IDs are free (STU-0001 to
    STU-0003) and that the demo emails are unused. Run it on a fresh
    session, once only; using it after adding students manually, or twice,
    will raise errors (duplicate email or wrong-programme rejections).
  - Only @gmail.com email addresses are accepted. Change the regular
    expression in Student.email to allow other domains.
  - In option 2 (add course), if a later input is invalid (e.g. a lab hours
    value of 0), the whole entry is rejected and must be re-typed.
  - CSC2201 "Database Systems Lab" sits in the BSE programme although its
    code prefix is CSC (cosmetic only).
  - No login or role separation; anyone running the program acts as the
    Registrar.
  - Possible additions: grades/results, prerequisites, semesters,
    timetable clash detection, fee payment tracking, and a GUI or web
    front end.

==============================================================================
