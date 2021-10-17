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

@login_required(login_url='login')
def apanel(request):
    if request.user.is_staff:
        if request.user.is_superuser:
            role = "Superusuario"
            products = Product.objects.all()
        else:
            role = Client.objects.get(user=User.objects.get(pk=request.user.id)).publisher
            products = Product.objects.filter(publisher=role)
        context = {
            'role':role,
            'products':products,
        }
        return render(request,'apanel.html',context)
    else:
        return redirect('home')

@login_required(login_url='login')
def add_product(request):
    if request.method == 'POST':
        form = addProductForm(request.POST or None)
        image = request.FILES.get('image')
        if form.is_valid():
            if request.user.is_superuser:
                publisher = request.POST['publisher']
            else:
                publisher = Client.objects.get(user=User.objects.get(pk=request.user.id)).publisher

            p = Product.objects.create(
                name = request.POST['name'],
                author = request.POST['author'],
                publisher = publisher,
                price = request.POST['price'],
                description = request.POST['description'],
                quantity = request.POST['quantity'],
                image = image,
                genre = request.POST['genre']
            )
        else:
            if request.user.is_superuser:
                role = "Superusuario"
                products = Product.objects.all()
            else:
                role = Client.objects.get(user=User.objects.get(pk=request.user.id)).publisher
                products = Product.objects.filter(publisher=role)
            name = request.POST['name']
            author = request.POST['author']
            publisher = request.POST['publisher']
            price = request.POST['price']
            description = request.POST['description']
            quantity = request.POST['quantity']
            genre = request.POST['genre']
            messages.success(request,"Ocurrió un error; Por favor, intenta de nuevo...")
            return render(request,'apanel.html',{
                'name':name,
                'author':author,
                'publisher':publisher,
                'price':price,
                'description':description,
                'quantity':quantity,
                'image':image,
                'genre':genre,
                'role': role,
                'products':products,
            })
    messages.success(request,f"Libro {request.POST['name']} agregado correctamente")
    return redirect('home')

def product_page(request,pk):
    product = Product.objects.get(pk=int(request.path.split('/')[2]))
    sug = Product.objects.filter(genre=product.genre).exclude(pk=pk)
    context = {
        'product':product,
        'sug':sug,
        'flag':len(sug)
    }
    return render(request,'product.html',context)

@login_required(login_url='login')
def del_product(request,pk):
    Product.objects.filter(pk=pk).delete()
    return redirect('apanel')

@login_required(login_url='login')
def my_orders(request,pk):
    print(list(Order.objects.filter(client=request.user)))
    orders = Order.objects.filter(client=request.user)
    return render(request,'myorders.html',{
        'orders':orders,
    })

@login_required(login_url='login')
def checkout(request,pk):
    product = Product.objects.get(pk=int(request.path.split('/')[2]))
    context = {
        'product':product,
    }
    return render(request,'checkout.html',context)

@login_required(login_url='login')
def thanks(request):
    return render(request,'thanks.html',{})

@login_required(login_url='login')
def payment(request):
    if request.method == 'POST':
        form = OrderForm(request.POST or None)
        product = Product.objects.get(pk=request.POST['item'])
        if form.is_valid():
            if int(request.POST['quantity']) > int(product.quantity):
                first_order = int(product.quantity)
                second_order = int(request.POST['quantity']) - int(product.quantity)
                if request.POST['shiping'] == "DHL":
                    first_order_total = first_order * product.price + 150
                    second_order_total = second_order * product.price + 150
                else:
                    first_order_total = first_order * product.price + 500
                    second_order_total = second_order * product.price + 500
                product.quantity = 0
                product.selled = int(product.selled) + int(request.POST['quantity'])
                product.save()
                Order.objects.create(
                    client = request.user,
                    item = product,
                    status = "En proceso",
                    shiping = request.POST['shiping'],
                    paying = request.POST['paying'],
                    address = request.POST['address'],
                    total = first_order_total,
                    quantity = first_order,
                )
                Order.objects.create(
                    client = request.user,
                    item = product,
                    status = "Pendiente",
                    shiping = request.POST['shiping'],
                    paying = request.POST['paying'],
                    address = request.POST['address'],
                    total = second_order_total,
                    quantity = second_order,
                )
            else:
                if request.POST['shiping'] == "DHL":
                    total = int(product.price) * int(request.POST['quantity']) + 150
                else:
                    total = int(product.price) * int(request.POST['quantity']) + 500
                product.quantity = int(product.quantity) - int(request.POST['quantity'])
                product.selled = int(product.selled) + int(request.POST['quantity'])
                product.save()
                Order.objects.create(
                    client = request.user,
                    item = product,
                    status = "En proceso",
                    shiping = request.POST['shiping'],
                    paying = request.POST['paying'],
                    address = request.POST['address'],
                    total = total,
                    quantity = request.POST['quantity'],
                )
        else:
            item = product,
            shiping = request.POST['shiping']
            paying = request.POST['paying']
            address = request.POST['address']
            quantity = request.POST['quantity']
            messages.success(request,"Ocurrió un error; Por favor, intenta de nuevo...")
            return render(request,'checkout.html',{
                'item':item,
                'shiping':shiping,
                'paying':paying,
                'address':address,
                'quantity':quantity,
                'product':product,
            })
    return redirect('thanks')