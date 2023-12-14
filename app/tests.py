from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Receipt, UserProfile

class UserTestCase(TestCase):
    """
    A base test case for creating a superuser and a regular user,
    to be used across different test cases.
    """
class UserTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='12345')
        UserProfile.objects.create(user=self.user, is_approved=True)

    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username='admin', 
            email='admin@example.com', 
            password='adminpassword'
        )
        self.regular_user = User.objects.create_user(
            username='testuser', 
            email='testuser@example.com', 
            password='12345'
        )
        UserProfile.objects.create(user=self.regular_user, is_approved=False)

 
class UserTestCase2(TestCase):
    #create a user accepted by the superuser
    def setUp(self):
        self.user = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='123456')
        UserProfile.objects.create(user=self.user, is_approved=True)


#testing signup view
class SignupViewTest(UserTestCase):
    
    def test_get_signup_view(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth.html')

    def test_post_signup_view(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'complex_password',
            'password2': 'complex_password'
        })
        self.assertEqual(User.objects.count(), 3)  # Includes superuser, regular user, and new user
        self.assertRedirects(response, reverse('signin'))

#testing signuin view

class SigninViewTest(UserTestCase2):
    
    def test_get_signin_view(self):
        response = self.client.get(reverse('signin'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'auth.html')

    def test_post_signin_view(self):
        response = self.client.post(reverse('signin'), {
            'email': 'testuser2@example.com', 
            'password': '123456'
        })
        self.assertRedirects(response, reverse('home'))


"""
    Test case for accessing the admin page.
"""

class AdminPageViewTest(UserTestCase):
    
    def test_admin_page_view(self):
     # Test the response for accessing the admin page as a superuser
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('admin_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin.html')


class AcceptUserViewTest(UserTestCase):
    """
    Test case for the user acceptance process by a superuser.
    """
    def test_accept_user_with_superuser(self):
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(reverse('accept_user', args=[self.regular_user.id]))
        self.assertEqual(response.status_code, 200)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.userprofile.is_approved)

    def test_accept_user_without_superuser(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('accept_user', args=[self.regular_user.id]))
        self.assertEqual(response.status_code, 403)  # Forbidden


class DeleteUserViewTest(UserTestCase):
    """
    Test case for the user deleting process by a superuser.
    """
    def test_delete_user_with_superuser(self):
        self.client.login(username='admin', password='adminpassword')
        response = self.client.post(reverse('delete_user', args=[self.regular_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())

    def test_delete_user_without_superuser(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('delete_user', args=[self.regular_user.id]))
        self.assertEqual(response.status_code, 403)


class AddReceiptViewTest(UserTestCase):
    """
    Test case for adding a receipt.
    """
    def test_add_receipt_with_valid_data(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('add_receipt'), {
            'store_name': 'Store 1',
            'date_of_purchase': '2021-01-01',
            'item_list': 'Item 1, Item 2',
            'total_amount': 100.00
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Receipt.objects.count(), 1)

    def test_add_receipt_with_invalid_data(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('add_receipt'), {})
        self.assertEqual(response.status_code, 400)  # Bad Request


class EditAndDeleteReceiptViewTest(UserTestCase):
    """
    Test case for editing and deleting a receipt.
    """
    def setUp(self):
        super().setUp()
        self.receipt = Receipt.objects.create(
            user=self.regular_user, 
            store_name='Store 1', 
            date_of_purchase='2021-01-01',
            item_list='Item 1, Item 2', 
            total_amount=100.00
        )

    def test_edit_receipt(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('submit_edit_receipt', args=[self.receipt.purchase_number]), {
            'store_name': 'Store 2',
            'date_of_purchase': '2021-01-02',
            'item_list': 'Item 3, Item 4',
            'total_amount': 200.00
        })
        self.assertEqual(response.status_code, 200)
        self.receipt.refresh_from_db()
        self.assertEqual(self.receipt.store_name, 'Store 2')

    def test_delete_receipt(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('delete_receipt', args=[self.receipt.purchase_number]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Receipt.objects.filter(purchase_number=self.receipt.purchase_number).exists())

