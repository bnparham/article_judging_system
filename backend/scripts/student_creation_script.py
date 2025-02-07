# student_creation_script.py
import random

from university_adminstration.models import Student, FacultyEducationalGroup


from university_adminstration.models import FacultyEducationalGroup

# List of faculty groups to ensure in the database
faculty_groups_data = [
    ("MAT", "CS"),
    ("MAT", "APPMATH"),
    ("CHE", "CHEM"),
    ("CHE", "CHEMENG"),
    ("ENG", "ELEC"),
    ("ENG", "MECH")
]

# Loop through each faculty-educational group pair and check if it exists, if not, create it
for faculty, educational_group in faculty_groups_data:
    # Check if the FacultyEducationalGroup already exists
    if not FacultyEducationalGroup.objects.filter(faculty=faculty, educational_group=educational_group).exists():
        # Create the FacultyEducationalGroup if it doesn't exist
        FacultyEducationalGroup.objects.create(faculty=faculty, educational_group=educational_group)
        print(f"Created FacultyEducationalGroup: {faculty} - {educational_group}")
    else:
        print(f"FacultyEducationalGroup {faculty} - {educational_group} already exists")

# Example FacultyEducationalGroup, assuming you've already created some
faculty_groups = [
    FacultyEducationalGroup.objects.filter(faculty="MAT", educational_group="CS"),
    FacultyEducationalGroup.objects.filter(faculty="MAT", educational_group="APPMATH"),
    FacultyEducationalGroup.objects.filter(faculty="CHE", educational_group="CHEM"),
    FacultyEducationalGroup.objects.filter(faculty="CHE", educational_group="CHEMENG"),
    FacultyEducationalGroup.objects.filter(faculty="ENG", educational_group="ELEC"),
    FacultyEducationalGroup.objects.filter(faculty="ENG", educational_group="MECH")
]

# 20 sample data entries
students_data = [
    ("حامد", "آهنگی", "hamid1@gmail.com", "09123456789", "S10001", "Ph.D.", "Current", 2021, "Male", "Subject", "Day"),
    ("زهرا", "جعفری", "zahra1@gmail.com", "09123456788", "S10002", "Master", "Defended", 2020, "Female", "NotSubject", "Night"),
    ("نسیم", "مهدوی", "nasim1@gmail.com", "09123456787", "S10003", "Ph.D.", "Current", 2021, "Female", "Subject", "Campus"),
    ("مریم", "حسینی", "maryam1@gmail.com", "09123456786", "S10004", "Master", "Defended", 2020, "Female", "NotSubject", "Day"),
    ("حسین", "عبداللهی", "hossein1@gmail.com", "09123456785", "S10005", "Ph.D.", "Current", 2021, "Male", "Subject", "Night"),
    ("رضا", "خلیلی", "reza1@gmail.com", "09123456784", "S10006", "Master", "Defended", 2020, "Male", "NotSubject", "Day"),
    ("یاسمن", "سلطانی", "yasmin1@gmail.com", "09123456783", "S10007", "Ph.D.", "Current", 2021, "Female", "Subject", "Campus"),
    ("ایمان", "علیزاده", "iman1@gmail.com", "09123456782", "S10008", "Master", "Defended", 2020, "Male", "NotSubject", "Night"),
    ("فریبا", "تاجی", "fariba1@gmail.com", "09123456781", "S10009", "Master", "Defended", 2020, "Female", "Subject", "Day"),
    ("آرش", "موسوی", "arash@gmail.com", "09123456780", "S10010", "Ph.D.", "Current", 2021, "Male", "Subject", "Night"),
    ("سارا", "شاکری", "sara@gmail.com", "09123456779", "S10011", "Master", "Defended", 2020, "Female", "NotSubject", "Day"),
    ("کامران", "نیکزاد", "kamran@gmail.com", "09123456778", "S10012", "Ph.D.", "Current", 2021, "Male", "Subject", "Campus"),
    ("فاطمه", "سالمی", "fatemeh@gmail.com", "09123456777", "S10013", "Master", "Defended", 2020, "Female", "NotSubject", "Night"),
    ("امیر", "ابراهیمی", "amir@gmail.com", "09123456776", "S10014", "Ph.D.", "Current", 2021, "Male", "Subject", "Day"),
    ("مهدی", "کمالی", "mehdi@gmail.com", "09123456775", "S10015", "Master", "Defended", 2020, "Male", "NotSubject", "Night"),
    ("مهسا", "نوروزی", "mahsan@gmail.com", "09123456774", "S10016", "Ph.D.", "Current", 2021, "Female", "Subject", "Day"),
    ("بهنام", "پیرهادی", "behnam@gmail.com", "09123456773", "S10017", "Master", "Defended", 2020, "Male", "NotSubject", "Campus"),
    ("علی", "پیشوایی", "ali@gmail.com", "09123456772", "S10018", "Ph.D.", "Current", 2021, "Male", "Subject", "Night"),
    ("ندا", "موسوی", "neda@gmail.com", "09123456771", "S10019", "Master", "Defended", 2020, "Female", "NotSubject", "Day"),
    ("سینا", "باقری", "sina@gmail.com", "09123456770", "S10020", "Ph.D.", "Current", 2021, "Male", "Subject", "Campus")
]

# Loop through the student data and create Student objects
for first_name, last_name, email, phone_number, student_number, role, status, admission_year, gender, military_status, program_type in students_data:
    try:
        # Create a new Student object
        student = Student(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            student_number=student_number,
            role=role,
            status=status,
            admission_year=admission_year,
            gender=gender,
            military_status=military_status,
            program_type=program_type,
            faculty_educational_group=random.choice(faculty_groups).first()  # Assuming you've already set a FacultyEducationalGroup
        )

        # Perform validations
        student.full_clean()  # This will trigger model field validation

        # Save the student record if no validation errors
        student.save()

        print(f"Student {first_name} {last_name} saved successfully!")
    except ValidationError as e:
        print(f"Validation Error for {first_name} {last_name}: {e}")


# exec(open('scripts/student_creation_script.py').read())