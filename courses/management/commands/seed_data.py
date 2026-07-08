from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from courses.models import Course, Module, Question


class Command(BaseCommand):
    help = (
        "Seed the database with sample course data (2 courses, 9 modules, 36 questions)"
    )

    def handle(self, *args, **options):
        self.stdout.write("Seeding database with sample data...")

        # Create test user
        user, created = User.objects.get_or_create(
            username="testuser",
            defaults={
                "email": "test@example.com",
                "is_active": True,
            },
        )
        if created:
            user.set_password("testpass123")
            user.save()
            self.stdout.write(
                self.style.SUCCESS("Created test user: testuser / testpass123")
            )
        else:
            self.stdout.write(self.style.WARNING("Test user already exists"))

        courses_data = [
            {
                "title": "Python Programming Fundamentals",
                "description": "Master Python programming from basics to advanced concepts. Learn variables, data types, control flow, functions, and object-oriented programming.",
                "image_url": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800",
            },
            {
                "title": "Database Management Systems",
                "description": "Learn relational databases, SQL queries, normalization, transactions, and data integrity concepts.",
                "image_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=800",
            },
            {
                "title": "Computer Networks Fundamentals",
                "description": "Understand network architectures, protocols, topologies, and the essentials of internet communication.",
                "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
            },
            {
                "title": "Web Technologies for BCA",
                "description": "Explore HTML, CSS, JavaScript, and modern web development concepts tailored for BCA students.",
                "image_url": "https://images.unsplash.com/photo-1517430816045-df4b7de14d12?w=800",
            },
            {
                "title": "Software Engineering Principles",
                "description": "Study software development life cycle, project planning, testing, and quality assurance for reliable systems.",
                "image_url": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=800",
            },
        ]

        courses = []
        for course_data in courses_data:
            course_item, created = Course.objects.get_or_create(
                title=course_data["title"],
                defaults=course_data,
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created course: {course_item.title}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f'Course "{course_item.title}" already exists')
                )
            courses.append(course_item)

        python_course = courses[0]
        dbms_course = courses[1]
        networks_course = courses[2]
        web_course = courses[3]
        software_course = courses[4]

        python_modules_data = [
            {
                "title": "Introduction to Python",
                "description": "Learn the basics of Python programming, including installation, variables, and basic operations.",
                "difficulty_level": "beginner",
                "order": 1,
                "estimated_minutes": 30,
            },
            {
                "title": "Data Types and Variables",
                "description": "Understand Python data types: strings, integers, floats, lists, dictionaries, and more.",
                "difficulty_level": "beginner",
                "order": 2,
                "estimated_minutes": 45,
            },
            {
                "title": "Control Flow",
                "description": "Master if statements, loops (for, while), and logical operators in Python.",
                "difficulty_level": "intermediate",
                "order": 1,
                "estimated_minutes": 60,
            },
            {
                "title": "Functions and Modules",
                "description": "Learn to create reusable functions, understand scope, and work with Python modules.",
                "difficulty_level": "intermediate",
                "order": 2,
                "estimated_minutes": 50,
            },
            {
                "title": "Object-Oriented Programming",
                "description": "Dive into OOP concepts: classes, objects, inheritance, and polymorphism in Python.",
                "difficulty_level": "advanced",
                "order": 1,
                "estimated_minutes": 90,
            },
        ]

        dbms_modules_data = [
            {
                "title": "Introduction to DBMS",
                "description": "Learn relational databases, tables, keys, and SQL basics in a BCA context.",
                "difficulty_level": "beginner",
                "order": 1,
                "estimated_minutes": 60,
            },
        ]

        networks_modules_data = [
            {
                "title": "Networking Basics",
                "description": "Understand network types, protocols, and the fundamentals of how computers communicate.",
                "difficulty_level": "intermediate",
                "order": 1,
                "estimated_minutes": 65,
            },
        ]

        web_modules_data = [
            {
                "title": "Web Technologies Overview",
                "description": "Explore HTML, CSS, JavaScript, and the building blocks of web applications.",
                "difficulty_level": "intermediate",
                "order": 1,
                "estimated_minutes": 70,
            },
        ]

        software_modules_data = [
            {
                "title": "Software Engineering Overview",
                "description": "Learn the software development life cycle, planning, testing, and quality assurance.",
                "difficulty_level": "advanced",
                "order": 1,
                "estimated_minutes": 80,
            },
        ]

        python_modules = []
        for module_data in python_modules_data:
            module, created = Module.objects.get_or_create(
                course=python_course, title=module_data["title"], defaults=module_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  Created module: {module.title}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  Module "{module.title}" already exists')
                )
            python_modules.append(module)

        dbms_modules = []
        for module_data in dbms_modules_data:
            module, created = Module.objects.get_or_create(
                course=dbms_course, title=module_data["title"], defaults=module_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  Created module: {module.title}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  Module "{module.title}" already exists')
                )
            dbms_modules.append(module)

        networks_modules = []
        for module_data in networks_modules_data:
            module, created = Module.objects.get_or_create(
                course=networks_course, title=module_data["title"], defaults=module_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  Created module: {module.title}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  Module "{module.title}" already exists')
                )
            networks_modules.append(module)

        web_modules = []
        for module_data in web_modules_data:
            module, created = Module.objects.get_or_create(
                course=web_course, title=module_data["title"], defaults=module_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  Created module: {module.title}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  Module "{module.title}" already exists')
                )
            web_modules.append(module)

        software_modules = []
        for module_data in software_modules_data:
            module, created = Module.objects.get_or_create(
                course=software_course, title=module_data["title"], defaults=module_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  Created module: {module.title}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  Module "{module.title}" already exists')
                )
            software_modules.append(module)

        modules = python_modules + dbms_modules + web_modules + networks_modules + software_modules

        # Set prerequisite for Module 3 (Control Flow) to Module 2
        python_modules[2].prerequisite_module = python_modules[1]
        python_modules[2].save()

        # No prerequisites needed across separate BCA courses

        # Create Questions
        questions_data = [
            # Module 1: Introduction to Python (4 questions)
            {
                "module": modules[0],
                "question_text": "What is the correct way to create a variable in Python?",
                "option_a": "var x = 5",
                "option_b": "x = 5",
                "option_c": "int x = 5",
                "option_d": "declare x = 5",
                "correct_answer": "B",
                "difficulty_score": 20,
                "explanation": "In Python, variables are created simply by assigning a value: x = 5",
                "tags": "variables, basics, syntax",
                "order": 1,
            },
            {
                "module": modules[0],
                "question_text": "Which keyword is used to output text in Python?",
                "option_a": "echo",
                "option_b": "print",
                "option_c": "console.log",
                "option_d": "write",
                "correct_answer": "B",
                "difficulty_score": 15,
                "explanation": "The print() function is used to output text in Python.",
                "tags": "output, functions, basics",
                "order": 2,
            },
            {
                "module": modules[0],
                "question_text": "How do you write a comment in Python?",
                "option_a": "// This is a comment",
                "option_b": "/* This is a comment */",
                "option_c": "# This is a comment",
                "option_d": "-- This is a comment",
                "correct_answer": "C",
                "difficulty_score": 10,
                "explanation": "Python uses the # symbol for single-line comments.",
                "tags": "comments, syntax, basics",
                "order": 3,
            },
            {
                "module": modules[0],
                "question_text": "What is the correct file extension for Python files?",
                "option_a": ".python",
                "option_b": ".py",
                "option_c": ".pt",
                "option_d": ".pyt",
                "correct_answer": "B",
                "difficulty_score": 10,
                "explanation": "Python files use the .py extension.",
                "tags": "files, basics",
                "order": 4,
            },
            # Module 2: Data Types and Variables (5 questions)
            {
                "module": modules[1],
                "question_text": "Which data type is mutable in Python?",
                "option_a": "Tuple",
                "option_b": "String",
                "option_c": "List",
                "option_d": "Integer",
                "correct_answer": "C",
                "difficulty_score": 40,
                "explanation": "Lists are mutable in Python, meaning they can be modified after creation.",
                "tags": "lists, data types, mutability",
                "order": 1,
            },
            {
                "module": modules[1],
                "question_text": "What is the result of type([1, 2, 3])?",
                "option_a": "<class 'tuple'>",
                "option_b": "<class 'list'>",
                "option_c": "<class 'array'>",
                "option_d": "<class 'set'>",
                "correct_answer": "B",
                "difficulty_score": 35,
                "explanation": "The type() function returns <class 'list'> for lists.",
                "tags": "lists, data types, functions",
                "order": 2,
            },
            {
                "module": modules[1],
                "question_text": "How do you create a dictionary in Python?",
                "option_a": "dict = {1, 2, 3}",
                "option_b": 'dict = [1: "a", 2: "b"]',
                "option_c": 'dict = {"key": "value"}',
                "option_d": "dict = (1, 2, 3)",
                "correct_answer": "C",
                "difficulty_score": 45,
                "explanation": 'Dictionaries are created using key-value pairs in curly braces: {"key": "value"}',
                "tags": "dictionaries, data types, syntax",
                "order": 3,
            },
            {
                "module": modules[1],
                "question_text": "Which of the following is NOT a valid Python data type?",
                "option_a": "str",
                "option_b": "int",
                "option_c": "char",
                "option_d": "float",
                "correct_answer": "C",
                "difficulty_score": 30,
                "explanation": "Python does not have a char type; single characters are strings.",
                "tags": "data types, strings",
                "order": 4,
            },
            {
                "module": modules[1],
                "question_text": 'What is the output of len("Hello")?',
                "option_a": "4",
                "option_b": "5",
                "option_c": "6",
                "option_d": "Hello",
                "correct_answer": "B",
                "difficulty_score": 25,
                "explanation": "The len() function returns the number of characters: 5.",
                "tags": "strings, functions, length",
                "order": 5,
            },
            # Module 3: Control Flow (4 questions)
            {
                "module": modules[2],
                "question_text": "What is the correct syntax for a for loop in Python?",
                "option_a": "for (i = 0; i < 5; i++)",
                "option_b": "for i in range(5):",
                "option_c": "for each i in range(5):",
                "option_d": "loop i from 0 to 5:",
                "correct_answer": "B",
                "difficulty_score": 50,
                "explanation": 'Python uses "for i in range(5):" for loops.',
                "tags": "loops, for loop, control flow",
                "order": 1,
            },
            {
                "module": modules[2],
                "question_text": 'Which operator is used for "not equal" in Python?',
                "option_a": "!=",
                "option_b": "!==",
                "option_c": "<>",
                "option_d": "not =",
                "correct_answer": "A",
                "difficulty_score": 45,
                "explanation": 'Python uses != for "not equal" comparisons.',
                "tags": "operators, comparison, control flow",
                "order": 2,
            },
            {
                "module": modules[2],
                "question_text": "What keyword is used to exit a loop early in Python?",
                "option_a": "stop",
                "option_b": "exit",
                "option_c": "break",
                "option_d": "return",
                "correct_answer": "C",
                "difficulty_score": 55,
                "explanation": "The break keyword is used to exit a loop early.",
                "tags": "loops, break, control flow",
                "order": 3,
            },
            {
                "module": modules[2],
                "question_text": "What does the continue keyword do in a loop?",
                "option_a": "Stops the loop",
                "option_b": "Skips to the next iteration",
                "option_c": "Exits the program",
                "option_d": "Pauses the loop",
                "correct_answer": "B",
                "difficulty_score": 60,
                "explanation": "The continue keyword skips the rest of the current iteration and moves to the next.",
                "tags": "loops, continue, control flow",
                "order": 4,
            },
            # Module 4: Functions and Modules (4 questions)
            {
                "module": modules[3],
                "question_text": "How do you define a function in Python?",
                "option_a": "function myFunc():",
                "option_b": "def myFunc():",
                "option_c": "create myFunc():",
                "option_d": "func myFunc():",
                "correct_answer": "B",
                "difficulty_score": 50,
                "explanation": "Functions are defined using the def keyword: def myFunc():",
                "tags": "functions, definition, syntax",
                "order": 1,
            },
            {
                "module": modules[3],
                "question_text": "What keyword is used to return a value from a function?",
                "option_a": "return",
                "option_b": "yield",
                "option_c": "output",
                "option_d": "give",
                "correct_answer": "A",
                "difficulty_score": 45,
                "explanation": "The return keyword is used to return values from functions.",
                "tags": "functions, return, values",
                "order": 2,
            },
            {
                "module": modules[3],
                "question_text": "How do you import a module in Python?",
                "option_a": "include module",
                "option_b": "import module",
                "option_c": "using module",
                "option_d": "require module",
                "correct_answer": "B",
                "difficulty_score": 40,
                "explanation": "Python uses the import keyword: import module",
                "tags": "modules, import, syntax",
                "order": 3,
            },
            {
                "module": modules[3],
                "question_text": "What is a lambda function in Python?",
                "option_a": "A recursive function",
                "option_b": "An anonymous function",
                "option_c": "A built-in function",
                "option_d": "A class method",
                "correct_answer": "B",
                "difficulty_score": 70,
                "explanation": "Lambda functions are anonymous, single-line functions in Python.",
                "tags": "functions, lambda, advanced",
                "order": 4,
            },
            # Module 5: Object-Oriented Programming (3 questions)
            {
                "module": modules[4],
                "question_text": "What keyword is used to create a class in Python?",
                "option_a": "class",
                "option_b": "Class",
                "option_c": "object",
                "option_d": "create",
                "correct_answer": "A",
                "difficulty_score": 55,
                "explanation": "The class keyword is used to create classes: class MyClass:",
                "tags": "classes, oop, syntax",
                "order": 1,
            },
            {
                "module": modules[4],
                "question_text": "What is the __init__ method in Python?",
                "option_a": "A destructor",
                "option_b": "A constructor",
                "option_c": "A static method",
                "option_d": "A class variable",
                "correct_answer": "B",
                "difficulty_score": 65,
                "explanation": "__init__ is the constructor method that initializes object instances.",
                "tags": "classes, init, oop, methods",
                "order": 2,
            },
            {
                "module": modules[4],
                "question_text": "How do you inherit from a class in Python?",
                "option_a": "class Child extends Parent:",
                "option_b": "class Child(Parent):",
                "option_c": "class Child inherits Parent:",
                "option_d": "class Child from Parent:",
                "correct_answer": "B",
                "difficulty_score": 75,
                "explanation": "Python inheritance uses: class Child(Parent):",
                "tags": "inheritance, classes, oop",
                "order": 3,
            },
            {
                "module": modules[5],
                "question_text": "Which command is used to retrieve data from a relational database?",
                "option_a": "SELECT",
                "option_b": "UPDATE",
                "option_c": "DELETE",
                "option_d": "INSERT",
                "correct_answer": "A",
                "difficulty_score": 45,
                "explanation": "SELECT is used to fetch data from a database table.",
                "tags": "sql, database, dms",
                "order": 1,
            },
            {
                "module": modules[5],
                "question_text": "What is normalization used for in DBMS?",
                "option_a": "Improve query performance",
                "option_b": "Remove redundancy and ensure data integrity",
                "option_c": "Create backups",
                "option_d": "Encrypt database content",
                "correct_answer": "B",
                "difficulty_score": 55,
                "explanation": "Normalization reduces redundancy and improves data integrity.",
                "tags": "normalization, database, dms",
                "order": 2,
            },
            {
                "module": modules[5],
                "question_text": "Which SQL clause filters rows returned by a query?",
                "option_a": "GROUP BY",
                "option_b": "ORDER BY",
                "option_c": "WHERE",
                "option_d": "HAVING",
                "correct_answer": "C",
                "difficulty_score": 50,
                "explanation": "WHERE filters rows based on a condition.",
                "tags": "sql, where clause, database",
                "order": 3,
            },
            {
                "module": modules[5],
                "question_text": "What does ACID stand for in databases?",
                "option_a": "Atomicity, Consistency, Isolation, Durability",
                "option_b": "Accuracy, Consistency, Integrity, Durability",
                "option_c": "Availability, Consistency, Isolation, Durability",
                "option_d": "Atomicity, Compatibility, Integrity, Durability",
                "correct_answer": "A",
                "difficulty_score": 60,
                "explanation": "ACID stands for Atomicity, Consistency, Isolation, Durability.",
                "tags": "acid, database, transactions",
                "order": 4,
            },
            {
                "module": modules[6],
                "question_text": "Which language is used to structure content on the web?",
                "option_a": "CSS",
                "option_b": "HTML",
                "option_c": "Python",
                "option_d": "SQL",
                "correct_answer": "B",
                "difficulty_score": 40,
                "explanation": "HTML is used to structure web content.",
                "tags": "html, web, frontend",
                "order": 1,
            },
            {
                "module": modules[6],
                "question_text": "Which CSS property changes the text color?",
                "option_a": "font-color",
                "option_b": "text-color",
                "option_c": "color",
                "option_d": "font-style",
                "correct_answer": "C",
                "difficulty_score": 45,
                "explanation": "The color property changes the text color in CSS.",
                "tags": "css, web, styles",
                "order": 2,
            },
            {
                "module": modules[6],
                "question_text": "What does JavaScript primarily add to web pages?",
                "option_a": "Structure",
                "option_b": "Style",
                "option_c": "Interactivity",
                "option_d": "Persistence",
                "correct_answer": "C",
                "difficulty_score": 55,
                "explanation": "JavaScript adds interactivity and dynamic behavior to web pages.",
                "tags": "javascript, web, frontend",
                "order": 3,
            },
            {
                "module": modules[6],
                "question_text": "Which tag is used to create a hyperlink in HTML?",
                "option_a": "<link>",
                "option_b": "<url>",
                "option_c": "<a>",
                "option_d": "<href>",
                "correct_answer": "C",
                "difficulty_score": 50,
                "explanation": "The <a> tag creates hyperlinks in HTML.",
                "tags": "html, hyperlinks, web",
                "order": 4,
            },
            {
                "module": modules[7],
                "question_text": "What does LAN stand for?",
                "option_a": "Local Area Network",
                "option_b": "Large Area Network",
                "option_c": "Long Area Network",
                "option_d": "Linked Area Network",
                "correct_answer": "A",
                "difficulty_score": 45,
                "explanation": "LAN stands for Local Area Network.",
                "tags": "networks, lan, fundamentals",
                "order": 1,
            },
            {
                "module": modules[7],
                "question_text": "Which protocol is used to send email over the internet?",
                "option_a": "HTTP",
                "option_b": "SMTP",
                "option_c": "FTP",
                "option_d": "DNS",
                "correct_answer": "B",
                "difficulty_score": 55,
                "explanation": "SMTP is the protocol commonly used to send email.",
                "tags": "smtp, email, network protocols",
                "order": 2,
            },
            {
                "module": modules[7],
                "question_text": "What is the main purpose of a router?",
                "option_a": "Store data",
                "option_b": "Connect networks and route traffic",
                "option_c": "Encrypt messages",
                "option_d": "Display web pages",
                "correct_answer": "B",
                "difficulty_score": 50,
                "explanation": "A router connects networks and forwards data between them.",
                "tags": "routing, networks, hardware",
                "order": 3,
            },
            {
                "module": modules[7],
                "question_text": "Which layer of the OSI model is responsible for end-to-end communication?",
                "option_a": "Network",
                "option_b": "Transport",
                "option_c": "Session",
                "option_d": "Data Link",
                "correct_answer": "B",
                "difficulty_score": 60,
                "explanation": "The transport layer handles end-to-end communication and reliability.",
                "tags": "osi model, transport, network",
                "order": 4,
            },
            {
                "module": modules[8],
                "question_text": "What is the first phase of the software development life cycle?",
                "option_a": "Testing",
                "option_b": "Planning",
                "option_c": "Deployment",
                "option_d": "Design",
                "correct_answer": "B",
                "difficulty_score": 50,
                "explanation": "Planning is typically the first phase of the SDLC.",
                "tags": "sdlc, planning, software engineering",
                "order": 1,
            },
            {
                "module": modules[8],
                "question_text": "Which model emphasizes iterative development and constant feedback?",
                "option_a": "Waterfall",
                "option_b": "V-Model",
                "option_c": "Agile",
                "option_d": "Spiral",
                "correct_answer": "C",
                "difficulty_score": 55,
                "explanation": "Agile emphasizes iterative delivery and frequent feedback.",
                "tags": "agile, sdlc, software engineering",
                "order": 2,
            },
            {
                "module": modules[8],
                "question_text": "What does unit testing validate?",
                "option_a": "The complete product",
                "option_b": "Individual components or functions",
                "option_c": "User acceptance",
                "option_d": "Deployment readiness",
                "correct_answer": "B",
                "difficulty_score": 45,
                "explanation": "Unit testing checks individual components or functions.",
                "tags": "testing, unit test, software engineering",
                "order": 3,
            },
            {
                "module": modules[8],
                "question_text": "What is a software requirement specification (SRS)?",
                "option_a": "A deployment guide",
                "option_b": "A test case document",
                "option_c": "A detailed description of software requirements",
                "option_d": "A code repository",
                "correct_answer": "C",
                "difficulty_score": 60,
                "explanation": "An SRS documents functional and non-functional requirements for a software system.",
                "tags": "srs, requirements, documentation",
                "order": 4,
            },
        ]

        for q_data in questions_data:
            question, created = Question.objects.get_or_create(
                module=q_data["module"],
                question_text=q_data["question_text"],
                defaults={
                    "option_a": q_data["option_a"],
                    "option_b": q_data["option_b"],
                    "option_c": q_data.get("option_c", ""),
                    "option_d": q_data.get("option_d", ""),
                    "correct_answer": q_data["correct_answer"],
                    "difficulty_score": q_data["difficulty_score"],
                    "explanation": q_data.get("explanation", ""),
                    "tags": q_data.get("tags", ""),
                    "order": q_data["order"],
                },
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"    Created question: {question.question_text[:50]}..."
                    )
                )
            else:
                self.stdout.write(self.style.WARNING(f"    Question already exists"))

        self.stdout.write(self.style.SUCCESS("\nDatabase seeding complete!"))
        self.stdout.write(
            self.style.SUCCESS("Login credentials: testuser / testpass123")
        )
        self.stdout.write(self.style.SUCCESS(f'Course: "{course.title}"'))
        self.stdout.write(self.style.SUCCESS(f"Total Modules: {len(modules)}"))
        self.stdout.write(
            self.style.SUCCESS(f"Total Questions: {Question.objects.count()}")
        )
