from django.shortcuts import render, redirect  # Added redirect import
from .models import *
from http.client import HTTPResponse
from django.contrib import messages
from amsy.form import CustomUserForm
from django.contrib.auth import authenticate, login,logout
from django.http import JsonResponse
import json

def home(request):
    products = Product.objects.filter(trending=1)
    return render(request, 'amsy/index.html', {'products': products})
def favviewpage(request):
  if request.user.is_authenticated:
    fav=Favourite.objects.filter(user=request.user)
    return render(request,"amsy/fav.html",{"fav":fav})
  else:
    return redirect("/")
def fav_page(request):
   if request.headers.get('x-requested-with')=='XMLHttpRequest':
    if request.user.is_authenticated:
      data=json.load(request)
      product_id=data['pid']
      product_status=Product.objects.get(id=product_id)
      if product_status:
         if Favourite.objects.filter(user=request.user.id,product_id=product_id):
          return JsonResponse({'status':'Product Already in Favourite'}, status=200)
         else:
          Favourite.objects.create(user=request.user,product_id=product_id)
          return JsonResponse({'status':'Product Added to Favourite'}, status=200)
    else:
      return JsonResponse({'status':'Login to Add Favourite'}, status=200)
   else:
    return JsonResponse({'status':'Invalid Access'}, status=200)
 
def remove_fav(request,fid):
  item=Favourite.objects.get(id=fid)
  item.delete()
  return redirect("/favviewpage")
def cart_page(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request,'amsy/cart.html',{'cart':cart})
    else:
        return redirect('/')
def remove_cart(request,cid):
  cartitem=Cart.objects.get(id=cid)
  cartitem.delete()
  return redirect("/cart")

def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Ensure the request is an AJAX request
        try:
            data = json.loads(request.body)
            # Use request.body instead of json.load(request) for parsing JSON data
            product_qty = data.get('product_qty')
            product_id = data.get('pid')

            if product_qty is None or product_id is None:
                return JsonResponse({'status': 'Invalid data'}, status=400)

            # Retrieve the product from the database
            try:
                product_status = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return JsonResponse({'status': 'Product does not exist'}, status=404)

            # Check if the product is already in the cart
            if Cart.objects.filter(user=request.user, product_id=product_id).exists():
                return JsonResponse({'status': 'Product already in cart'}, status=200)

            # Check if the product quantity is available
            if product_status.quantity >= product_qty:
                # Add product to the cart
                Cart.objects.create(user=request.user, product_id=product_id, product_qty=product_qty)
                return JsonResponse({'status': 'Product added to cart'}, status=200)
            else:
                return JsonResponse({'status': 'Product stock not available'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'status': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'status': 'Invalid access'}, status=400)


def login_page(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method=='POST':
             name=request.POST.get('username')
             pwd=request.POST.get('password')
             user=authenticate(request,username=name,password=pwd)
             if user is not None:
                login(request,user)
                messages.success(request,"Logged in Successfully")
                return redirect("/")
             else:
                messages.error(request,"Invalid User Name or Password")
                return redirect("/login_page")
        return render(request,"amsy/login.html")     
def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,'Logged Out Successfully')
    return redirect('/home')


def register(request):
    form = CustomUserForm()
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration success You can Login Here...!')
            return redirect('login_page')
        return render(request, "amsy/register.html", {'form': form})

    return render(request, 'amsy/register.html', {'form': form})

def category(request):
    category = Category.objects.filter(status=0)
    return render(request, 'amsy/category.html', {'category': category})

def categoriesview(request, name):
    if Category.objects.filter(name=name, status=0):
        products = Product.objects.filter(category__name=name)
        return render(request, 'amsy/products/index.html', {'products': products})
    else:
        messages.warning(request, "No such category found")
        return redirect("categories")

def product_details(request, cname, pname):
    if Category.objects.filter(name=cname, status=0):
        if Product.objects.filter(name=pname, status=0):
            products = Product.objects.filter(name=pname, status=0).first()
            return render(request, "amsy/products/product_details.html", {"products": products})
        else:
            messages.error(request, "No such product found")
            return redirect("categories")
    else:
        messages.error(request, "No such category found")
        return redirect("categories")




