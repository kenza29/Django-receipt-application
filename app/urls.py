from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path



urlpatterns =[
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('admin/', views.admin_page, name='admin_page'),
    path('accept_user/<int:user_id>/', views.accept_user, name='accept_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    #path('get_users/', views.get_users, name='get_users'),
    path('home/', views.home, name='home'),
    path('details/<str:purchase_number>/', views.receipt_details, name='receipt_details'),
    path('add_receipt/', views.add_receipt, name='add_receipt'),
    
    path('add_receipt_form/', views.add_receipt_form, name='add_receipt_form'),
    path('delete_receipt/<str:purchase_number>/', views.delete_receipt, name='delete_receipt'),
    path('load_edit_receipt_form/<str:purchase_number>/', views.load_edit_receipt_form, name='load_edit_receipt_form'),
    path('submit_edit_receipt/<str:purchase_number>/', views.submit_edit_receipt, name='submit_edit_receipt'),

    #path('edit_receipt/<str:purchase_number>/', views.edit_receipt, name='edit_receipt'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

