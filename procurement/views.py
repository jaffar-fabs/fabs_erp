from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import *
from django.views.decorators.csrf import csrf_exempt


def set_comp_code(request):
    global COMP_CODE

    COMP_CODE = request.session.get("comp_code")

def item_master(request):
    # Get search keyword
    keyword = request.GET.get('keyword', '')
    
    # Get all items or filter by keyword
    if keyword:
        items = ItemMaster.objects.filter(
            Q(item_code__icontains=keyword) |
            Q(item_description__icontains=keyword) |
            Q(category__icontains=keyword)
        ).order_by('item_code')
    else:
        items = ItemMaster.objects.all().order_by('item_code')
    
    # Pagination
    paginator = Paginator(items, 10)  # Show 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add pagination info to the page object
    page_obj.start_index = (page_obj.number - 1) * paginator.per_page + 1
    page_obj.end_index = min(page_obj.start_index + paginator.per_page - 1, paginator.count)
    
    context = {
        'items': page_obj,
        'keyword': keyword,
        'current_url': request.path + '?' + '&'.join([f"{k}={v}" for k, v in request.GET.items() if k != 'page']) + '&' if request.GET else '?'
    }
    
    return render(request, 'pages/procurement/item_master.html', context)

def item_master_add(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            # Create new item
            item = ItemMaster(
                item_code=request.POST.get('item_code'),
                item_description=request.POST.get('item_description'),
                uom=request.POST.get('uom'),
                remarks=request.POST.get('remarks'),
                category=request.POST.get('category'),
                sub_category=request.POST.get('sub_category'),
                brand=request.POST.get('brand'),
                material=request.POST.get('material'),
                size=request.POST.get('size'),
                color=request.POST.get('color'),
                style=request.POST.get('style'),
                origin=request.POST.get('origin'),
                gender=request.POST.get('gender'),
                item_rate=request.POST.get('item_rate') or 0,
                price_if_credit=request.POST.get('price_if_credit') or 0,
                stock_qty=request.POST.get('stock_qty') or 0,
                open_qty=request.POST.get('open_qty') or 0,
                is_active=request.POST.get('is_active') == 'true',
                created_by=request.user.username,
                comp_code=COMP_CODE
            )
            item.save()
            return redirect('item_master')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def item_master_edit(request):
    if request.method == 'GET':
        item_id = request.GET.get('item_id')
        try:
            item = get_object_or_404(ItemMaster, id=item_id)
            data = {
                'id': item.id,
                'item_code': item.item_code,
                'item_description': item.item_description,
                'uom': item.uom,
                'remarks': item.remarks,
                'category': item.category,
                'sub_category': item.sub_category,
                'brand': item.brand,
                'material': item.material,
                'size': item.size,
                'color': item.color,
                'style': item.style,
                'origin': item.origin,
                'gender': item.gender,
                'item_rate': item.item_rate,
                'price_if_credit': item.price_if_credit,
                'stock_qty': item.stock_qty,
                'open_qty': item.open_qty,
                'is_active': item.is_active
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    elif request.method == 'POST':
        try:
            item_id = request.POST.get('item_id')
            item = get_object_or_404(ItemMaster, id=item_id)
            
            # Update item fields
            item.item_code = request.POST.get('item_code')
            item.item_description = request.POST.get('item_description')
            item.uom = request.POST.get('uom')
            item.remarks = request.POST.get('remarks')
            item.category = request.POST.get('category')
            item.sub_category = request.POST.get('sub_category')
            item.brand = request.POST.get('brand')
            item.material = request.POST.get('material')
            item.size = request.POST.get('size')
            item.color = request.POST.get('color')
            item.style = request.POST.get('style')
            item.origin = request.POST.get('origin')
            item.gender = request.POST.get('gender')
            item.item_rate = request.POST.get('item_rate') or 0
            item.price_if_credit = request.POST.get('price_if_credit') or 0
            item.stock_qty = request.POST.get('stock_qty') or 0
            item.open_qty = request.POST.get('open_qty') or 0
            item.is_active = request.POST.get('is_active') == 'true'
            item.updated_by = request.user.username
            
            item.save()
            return redirect('item_master')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def item_master_delete(request):
    if request.method == 'POST':
        try:
            item_id = request.POST.get('item_id')
            item = get_object_or_404(ItemMaster, id=item_id)
            item.delete()
            return JsonResponse({'status': 'success', 'message': 'Item deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# UOM Master Views
def uom_master(request):
    # Get search keyword
    keyword = request.GET.get('keyword', '')
    
    # Get all UOMs or filter by keyword
    if keyword:
        uoms = UOMMaster.objects.filter(
            Q(uom__icontains=keyword) |
            Q(base_uom__icontains=keyword)
        ).order_by('uom')
    else:
        uoms = UOMMaster.objects.all().order_by('uom')
    
    # Pagination
    paginator = Paginator(uoms, 10)  # Show 10 UOMs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add pagination info to the page object
    page_obj.start_index = (page_obj.number - 1) * paginator.per_page + 1
    page_obj.end_index = min(page_obj.start_index + paginator.per_page - 1, paginator.count)
    
    context = {
        'uoms': page_obj,
        'keyword': keyword,
        'current_url': request.path + '?' + '&'.join([f"{k}={v}" for k, v in request.GET.items() if k != 'page']) + '&' if request.GET else '?'
    }
    
    return render(request, 'pages/procurement/uom_master.html', context)

def uom_master_add(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            # Create new UOM
            uom = UOMMaster(
                uom=request.POST.get('uom'),
                seq=request.POST.get('seq'),
                base_uom=request.POST.get('base_uom'),
                is_active=request.POST.get('is_active') == 'true',
                created_by=request.user.username,
                comp_code=COMP_CODE
            )
            uom.save()
            return redirect('uom_master')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def uom_master_edit(request):
    if request.method == 'GET':
        uom_id = request.GET.get('uom_id')
        try:
            uom = get_object_or_404(UOMMaster, id=uom_id)
            data = {
                'id': uom.id,
                'uom': uom.uom,
                'seq': uom.seq,
                'base_uom': uom.base_uom,
                'is_active': uom.is_active
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    elif request.method == 'POST':
        try:
            uom_id = request.POST.get('uom_id')
            uom = get_object_or_404(UOMMaster, id=uom_id)
            
            # Update UOM fields
            uom.uom = request.POST.get('uom')
            uom.seq = request.POST.get('seq')
            uom.base_uom = request.POST.get('base_uom')
            uom.is_active = request.POST.get('is_active') == 'true'
            uom.updated_by = request.user.username
            
            uom.save()
            return redirect('uom_master')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def uom_master_delete(request):
    if request.method == 'POST':
        try:
            uom_id = request.POST.get('uom_id')
            uom = get_object_or_404(UOMMaster, id=uom_id)
            uom.delete()
            return JsonResponse({'status': 'success', 'message': 'UOM deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
