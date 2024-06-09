from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    home, signup, login_view,cancel_order, logout_view, host_reservations, user_info, host_houses, house_create,user_orders,
    HouseListView, HouseDetailView, HouseCreateView, HouseUpdateView, HouseDeleteView, order_house, search, manage_role_requests
)

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('user_info/', user_info, name='user_info'),
    path('houses/', HouseListView.as_view(), name='house_list'),
    path('houses/<int:pk>/', HouseDetailView.as_view(), name='house_detail'),
    path('houses/new/', house_create, name='house_create'),
    path('houses/<int:pk>/edit/', HouseUpdateView.as_view(), name='house_update'),
    path('houses/<int:pk>/delete/', HouseDeleteView.as_view(), name='house_delete'),
    path('houses/<int:pk>/order/', order_house, name='order_house'),
    path('search/', search, name='search'),
    path('host-houses/', host_houses, name='host_houses'),
    path('manage_role_requests/', manage_role_requests, name='manage_role_requests'),
    path('user/orders/', user_orders, name='user_orders'),
    path('cancel_order/<int:pk>/', cancel_order, name='cancel_order'),
    path('host_reservations/', host_reservations, name='host_reservations'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)