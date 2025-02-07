import random
from django.core.exceptions import ValidationError
from university_adminstration.models import Teacher, FacultyEducationalGroup, TeacherFacultyEducationalGroupAssignment
from faker import Faker

fake = Faker()

# List of existing FacultyEducationalGroup objects (ensure these exist in the database)
faculty_groups_data = [
    ("MAT", "CS"),
    ("MAT", "APPMATH"),
    ("CHE", "CHEM"),
    ("CHE", "CHEMENG"),
    ("ENG", "ELEC"),
    ("ENG", "MECH")
]

# Generate FacultyEducationalGroup objects if they don't already exist
for faculty, educational_group in faculty_groups_data:
    if not FacultyEducationalGroup.objects.filter(faculty=faculty, educational_group=educational_group).exists():
        FacultyEducationalGroup.objects.create(faculty=faculty, educational_group=educational_group)

# Generate 20 sample teachers with random faculty group assignments
for _ in range(20):
    first_name = fake.first_name()
    last_name = fake.last_name()

    # Generate email with restricted domain
    email_domain = random.choice(['gmail.com', 'ymail.com'])
    email = f"{first_name.lower()}.{last_name.lower()}@{email_domain}"

    # Generate Iranian phone number (11 digits)
    phone_number = f"09{random.randint(100000000, 999999999)}"

    national_code = f"{random.randint(1, 999999999)}"
    faculty_id = f"{random.randint(1000000000000000000, 9999999999999999999)}"  # Unique faculty ID
    degree = random.choice(['MASTER', 'PHD'])  # Random degree
    # Create a teacher
    teacher = Teacher(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        national_code=national_code,
        faculty_id=faculty_id,
        degree=degree
    )

    # Perform validations
    try:
        teacher.full_clean()  # This will trigger model field validation
        teacher.save()  # Save the teacher first to avoid the unsaved related object error
        print(f"Teacher {first_name} {last_name} saved successfully!")

        # Now, randomly assign the teacher to 1 to 3 faculty groups
        number_of_groups = random.randint(1, 3)  # Randomly assign 1 to 3 groups
        assigned_groups = random.sample(list(FacultyEducationalGroup.objects.all()), number_of_groups)

        # Create TeacherFacultyEducationalGroupAssignment objects
        for group in assigned_groups:
            TeacherFacultyEducationalGroupAssignment.objects.create(
                teacher=teacher,
                faculty_educational_group=group
            )
            print(f"Assigned {teacher.name} to {group.faculty} - {group.educational_group}")

    except ValidationError as e:
        print(f"Validation Error for {first_name} {last_name}: {e}")

# exec(open('scripts/teacher_creation_script.py').read())