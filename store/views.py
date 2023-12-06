from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from carts.models import CartItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q

from carts.views import _cart_id



# Create your views here.
def store(request, category_slug=None):
    categories = None
    products = None
    #6 Display Products by Category
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products= Product.objects.filter(category=categories, is_availeble=True)
        # paginator display
        paginator = Paginator(products, 6)
        Page = request.GET.get('page')
        Paged_Products = paginator.get_page(Page)
        #
        product_count = products.count()

    else:
        # Display Products weth no if 
        products = Product.objects.all().filter(is_availeble=True).order_by('id')
        # paginator display
        paginator = Paginator(products, 3)
        Page = request.GET.get('page')
        Paged_Products = paginator.get_page(Page)
        #
        product_count = products.count()

    context = {
        'products': Paged_Products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try: 
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
           raise e
    context = {
        'single_product': single_product,
        'in_cart'       : in_cart,
        }
    return render(request, 'store/product_detail.html', context)

def search(request):
    products = None
    product_count = 0
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-create_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    
    context = {
        'products': products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', context)
