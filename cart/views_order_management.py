from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from user.models import Order

@staff_member_required
def order_list_view(request):
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'order_management/order_list.html', {'orders': orders})

@staff_member_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_management/order_detail.html', {'order': order})
