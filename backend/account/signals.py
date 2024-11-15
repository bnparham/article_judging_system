from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.utils.timezone import now
from django.contrib import messages  # For displaying messages
from .models import User

@receiver(user_logged_in)
def update_last_login_ip(sender, request, user, **kwargs):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    user.set_last_login_ip(ip)


@receiver(user_login_failed)
def handle_failed_login(sender, credentials, request, **kwargs):
    try:
        print('fire!')
        # Retrieve the username from the login credentials
        username = credentials.get('username', '')

        # If there's no username, don't proceed further
        if not username:
            return

        # Try to get the user with the provided username
        user = User.objects.get(username=username)

        # Increment the failed login attempts counter
        user.failed_login_attempts += 1

        # Record the last failed login attempt time
        user.last_failed_login = now()

        # Optionally, check if the user has exceeded the maximum failed attempts
        # You can set your own threshold, like 5 attempts in this example
        if user.failed_login_attempts >= 5:
            user.is_locked = True  # Lock the account after 5 failed attempts
            user.save()

            # Send a message that the account is locked
            messages.error(request, 'حساب شما به دلیل تلاش های زیاد برای ورود ناموفق قفل شده است.')

        else:
            user.save()

        # Save the updated user data
        user.save()
    except User.DoesNotExist:
        # Handle invalid username scenario - display an error message
        messages.error(request, 'نام کاربری یا رمز عبور نامعتبر است. لطفا دوباره امتحان کنید.')
