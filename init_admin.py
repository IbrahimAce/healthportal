import os
import django

# Set the production settings so it connects to your live database
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
django.setup()

from accounts.models import User

email = "karanjaibrahim141@gmail.com"

# Only create the user if it doesn't already exist
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password="adminpassword123",  # You can change this later in the admin panel
        first_name="Ibrahim",
        last_name="Karanja"
    )
    print("Live superuser created successfully!")
else:
    print("Superuser already exists.")
