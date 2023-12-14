from django.contrib import admin
from .models import UserProfile, Receipt
# Register the UserProfile model with Django's admin site.
# This allows the model to be managed through the Django admin interface.
admin.site.register(UserProfile)

# Register the Receipt model with Django's admin site.
# This enables the admin to view, add, edit, and delete Receipt records from the admin interface.
admin.site.register(Receipt)
