from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.forms import UserCreationForm
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='guest')
def home(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request,'home.html',context)

def guest(request):
    products = Product.objects.all()
    context = {'products':products}
    return render(request,'guest.html',context)

@login_required(login_url='login')
def cart(request,pk):
    if request.path.split('/')[2] == str(request.user.id):
        client = User.objects.get(pk=pk)
        context = {'client':client}
        return render(request,'cart.html',context)
    else:
        return redirect('home')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        context = {}
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username = username, password = password)
            if user is not None:
                try:
                    login(request, user)
                    return redirect('home')
                except:
                    messages.success(request,"Ha ocurrido un error, intenta de nuevo")
                    return render(request,'login.html',context)
            else:
                messages.success(request,"Usuario no registrado")
                return render(request,'login.html',context)

        return render(request,'login.html',context)

def user_logout(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        client_form = addClientForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            client_form = addClientForm(request.POST)
            if form.is_valid() and client_form.is_valid():
                user = form.save()
                client = client_form.save(commit=False)
                client.user = user
                client.save()
                username = form.cleaned_data.get('username')
                messages.success(request,"Cuenta creada para exitosamente para " + username)
                return redirect('login')

        context = {'form':form}
        return render(request,'register.html',context)

@login_required(login_url='login')
def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        products = Product.objects.filter(name__contains=searched)
        context = {
            'products':products,
            'item_searched':searched,
            'flag':len(products),
        }
        return render(request,'search.html',context)
    else:
        products = Product.objects.all()
        context = {'products':products}
        return render(request,'search.html',context)

def apanel(request):
    if request.user.is_staff:
        context = {}
        return render(request,'apanel.html',context)
    else:
        return redirect('home')

def add_product(request):
    if request.method == 'POST':
        form = addProductForm(request.POST or None)
        image = request.FILES.get('image')
        print(image)
        if form.is_valid():
            p = Product.objects.create(
                name = request.POST['name'],
                price = request.POST['price'],
                description = request.POST['description'],
                image = image,
            )
        else:
            name = request.POST['name']
            price = request.POST['price']
            description = request.POST['description']
            messages.success(request,"Ocurrió un error; Por favor, intenta de nuevo...")
            return render(request,'apanel.html',{
                'name':name,
                'price':price,
                'description':description,
                'image':image,
            })
    messages.success(request,f"Producto {request.POST['name']} agregado correctamente")
    return redirect('home')

def product_page(request,pk):
    product = Product.objects.get(pk=int(request.path.split('/')[2]))
    context = {
        'product':product,
    }
    return render(request,'product.html',context)