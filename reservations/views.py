from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import User, House, Order
from .forms import SignUpForm,UserInfoForm,LoginForm, HouseForm, OrderForm, RoleChangeRequestForm

def home(request):
    houses = House.objects.all()
    return render(request, 'reservations/home.html', {'houses': houses})

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 3  
            user.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'ثبت نام با موفقیت انجام شد.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'reservations/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'reservations/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def user_info(request):
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserInfoForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'اطلاعات کاربری شما با موفقیت تغییر یافت.')
                return redirect('user_info')
        elif 'request_role_change' in request.POST:
            request.user.role_change_requested = True
            request.user.save()
            messages.success(request, 'درخواست میزبانی شما با موفقیت ارسال گردید.')
            return redirect('user_info')
    else:
        user_form = UserInfoForm(instance=request.user)
    
    return render(request, 'reservations/user_info.html', {
        'user_form': user_form,
    })


class HouseListView(ListView):
    model = House
    template_name = 'reservations/house_list.html'

class HouseDetailView(DetailView):
    model = House
    template_name = 'reservations/house_detail.html'

class HouseCreateView(LoginRequiredMixin, CreateView):
    model = House
    form_class = HouseForm
    template_name = 'reservations/house_form.html'
    success_url = reverse_lazy('house_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

def house_create(request):
    if request.method == 'POST':
        form = HouseForm(request.POST, request.FILES)
        if form.is_valid():
            house = form.save(commit=False)
            house.user = request.user
            house.save()
            return redirect('host_houses')
    else:
        form = HouseForm()
    return render(request, 'reservations/house_form.html', {'form': form})

class HouseUpdateView(LoginRequiredMixin, UpdateView):
    model = House
    form_class = HouseForm
    template_name = 'reservations/house_form.html'
    success_url = reverse_lazy('house_list')

    def get_queryset(self):
        return House.objects.filter(user=self.request.user)

class HouseDeleteView(LoginRequiredMixin, DeleteView):
    model = House
    template_name = 'reservations/house_confirm_delete.html'
    success_url = reverse_lazy('house_list')

    def get_queryset(self):
        return House.objects.filter(user=self.request.user)

@login_required
def order_house(request, pk):
    house = get_object_or_404(House, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.house = house
            
            existing_orders = Order.objects.filter(
                house=house,
                exit_date__gte=order.arrive_date,
                arrive_date__lte=order.exit_date
            )
            
            if existing_orders.exists():
                messages.error(request, 'در این تاریخ رزرو دیگری انجام شده است.')
                return redirect('house_detail', pk=pk)
            
            order.total_price = house.price_per_day * (order.exit_date - order.arrive_date).days
            order.save()
            messages.success(request, 'رزرو خانه با موفقیت انجام شد.')
            return redirect('house_detail', pk=pk)  # Redirect to house detail after successful order creation
    else:
        form = OrderForm()
    return render(request, 'reservations/order_form.html', {'form': form, 'house': house})

@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    houses = House.objects.all()
    if request.method == 'POST':
        order.delete()
        return redirect('user_orders')
    return render(request, 'reservations/confirm_cancel_order.html', {'order': order,'houses': houses})

def search(request):
    query = request.GET.get('q')
    if query:
        houses = House.objects.filter(name__icontains=query)
    else:
        houses = House.objects.all()
    return render(request, 'reservations/search_results.html', {'houses': houses, 'query': query})

@user_passes_test(lambda u: u.role == 1)  
def manage_role_requests(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, id=user_id)
        if action == 'approve':
            user.role = 2
        user.role_change_requested = False
        user.save()
        return redirect('manage_role_requests')

    users_requesting_role_change = User.objects.filter(role_change_requested=True)
    return render(request, 'reservations/manage_role_requests.html', {'users': users_requesting_role_change})


def host_houses(request):
    if request.user.is_authenticated and request.user.role == 2:
        host_houses = House.objects.filter(user=request.user)
        return render(request, 'reservations/host_houses.html', {'host_houses': host_houses})
    else:
        return render(request, 'reservations/access_denied.html')  
    
@login_required
def user_orders(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'reservations/user_orders.html', {'orders': orders})


@login_required
def host_reservations(request):
    if request.user.role != 2: 
        return redirect('home')
    houses = House.objects.filter(user=request.user)
    reservations = Order.objects.filter(house__in=houses)
    return render(request, 'reservations/host_reservations.html', {'reservations': reservations})

