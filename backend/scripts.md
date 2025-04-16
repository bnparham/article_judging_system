# 📜 How to Run a Python Script Inside `manage.py shell` in Django

Sometimes, you might want to execute a standalone Python script (e.g., for generating test data) that needs access to Django models and database context. A clean and safe way to do this is to run the script **inside Django's shell environment**.

---

## ✅ Steps

1. **Prepare your script** (e.g., `scripts/create_teachers.py`):
   
   - Do **not** include `os.environ.setdefault(...)` or `django.setup()` — the shell takes care of that.
   - Just write code that you'd normally run in `manage.py shell`.

   Example:

```python
   from your_app.models import Teacher
   from faker import Faker

   fake = Faker()

   for _ in range(10):
       Teacher.objects.create(
           name=fake.name(),
           email=fake.email()
       )

   print("✅ 10 random teachers created!")
```

## run the script using input redirection (<):
```bash
python manage.py shell < scripts/create_teachers.py
```
   