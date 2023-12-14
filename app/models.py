from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver


class UserProfile(models.Model):
    # Establishes a one-to-one relationship with Django's built-in User model.
    # This means each User will have exactly one associated UserProfile.
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # A Boolean field to indicate whether the user's profile is approved or not.
    # Defaults to False, meaning approval is required.
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        # String representation of the model, returning the username.
        return self.user.username



class Receipt(models.Model):
    # ForeignKey relationship with the User model.
    # This links each receipt to a specific user and supports multiple receipts per user.
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Unique purchase number for each receipt.
    purchase_number = models.CharField(max_length=255, unique=True, blank=True)

    # Additional fields to store the details of each purchase.
    store_name = models.CharField(max_length=100)
    date_of_purchase = models.DateField()
    item_list = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        # String representation of the model, returning store name and date of purchase.
        return f"{self.store_name} - {self.date_of_purchase}"


@receiver(pre_save, sender=Receipt)
def set_purchase_number(sender, instance, **kwargs):
    # This function is triggered just before a Receipt object is saved.
    if not instance.purchase_number:
        # If purchase_number is not set, generate a new unique value.
        latest_receipt = Receipt.objects.order_by('-id').first()
        latest_number = int(latest_receipt.purchase_number.split(' ')[-1]) if latest_receipt else 0
        instance.purchase_number = f"Receipt {latest_number + 1}"

    



#rm db.sqlite3
#python manage.py makemigrations 
# python manage.py migrate
#python manage.py migrate
