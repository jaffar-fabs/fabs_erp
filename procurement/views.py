from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from datetime import datetime
from decimal import Decimal


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
    
    # Get all active UOMs for dropdown
    uoms = UOMMaster.objects.filter(is_active=True).order_by('uom')
    
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
        'current_url': request.path + '?' + '&'.join([f"{k}={v}" for k, v in request.GET.items() if k != 'page']) + '&' if request.GET else '?',
        'uoms': uoms  # Add UOMs to context
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

# Warehouse Master Views
def warehouse_master(request):
    # Get search keyword
    keyword = request.GET.get('keyword', '')
    
    # Get all warehouses or filter by keyword
    if keyword:
        warehouses = WarehouseMaster.objects.filter(
            Q(ware_code__icontains=keyword) |
            Q(ware_name__icontains=keyword) |
            Q(ware_type__icontains=keyword)
        ).order_by('ware_code')
    else:
        warehouses = WarehouseMaster.objects.all().order_by('ware_code')
    
    # Pagination
    paginator = Paginator(warehouses, 10)  # Show 10 warehouses per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add pagination info to the page object
    page_obj.start_index = (page_obj.number - 1) * paginator.per_page + 1
    page_obj.end_index = min(page_obj.start_index + paginator.per_page - 1, paginator.count)
    
    context = {
        'warehouses': page_obj,
        'keyword': keyword,
        'current_url': request.path + '?' + '&'.join([f"{k}={v}" for k, v in request.GET.items() if k != 'page']) + '&' if request.GET else '?'
    }
    
    return render(request, 'pages/procurement/warehouse_master.html', context)

def warehouse_master_add(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            # Create new warehouse
            warehouse = WarehouseMaster(
                comp_code=COMP_CODE,
                ware_code=request.POST.get('ware_code'),
                ware_name=request.POST.get('ware_name'),
                ware_type=request.POST.get('ware_type'),
                stat_code=request.POST.get('stat_code', 'A'),
                created_by=request.user.username
            )
            warehouse.save()
            return redirect('warehouse_master')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def warehouse_master_edit(request):
    if request.method == 'GET':
        warehouse_id = request.GET.get('warehouse_id')
        try:
            warehouse = get_object_or_404(WarehouseMaster, id=warehouse_id)
            data = {
                'id': warehouse.id,
                'ware_code': warehouse.ware_code,
                'ware_name': warehouse.ware_name,
                'ware_type': warehouse.ware_type,
                'stat_code': warehouse.stat_code
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    elif request.method == 'POST':
        try:
            warehouse_id = request.POST.get('warehouse_id')
            warehouse = get_object_or_404(WarehouseMaster, id=warehouse_id)
            
            # Update warehouse fields
            warehouse.ware_code = request.POST.get('ware_code')
            warehouse.ware_name = request.POST.get('ware_name')
            warehouse.ware_type = request.POST.get('ware_type')
            warehouse.stat_code = request.POST.get('stat_code', 'A')
            warehouse.updated_by = request.user.username
            
            warehouse.save()
            return redirect('warehouse_master')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def warehouse_master_delete(request):
    if request.method == 'POST':
        try:
            warehouse_id = request.POST.get('warehouse_id')
            warehouse = get_object_or_404(WarehouseMaster, id=warehouse_id)
            warehouse.delete()
            return JsonResponse({'status': 'success', 'message': 'Warehouse deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# Purchase Order Views
def purchase_order(request):
    # Get search keyword
    keyword = request.GET.get('keyword', '')
    
    # Get all POs or filter by keyword
    if keyword:
        pos = PurchaseOrderHeader.objects.filter(
            Q(tran_numb__icontains=keyword) |
            Q(supl_name__icontains=keyword) |
            Q(supl_code__icontains=keyword)
        ).order_by('-tran_date')
    else:
        pos = PurchaseOrderHeader.objects.all().order_by('-tran_date')
    
    # Pagination
    paginator = Paginator(pos, 10)  # Show 10 POs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add pagination info to the page object
    page_obj.start_index = (page_obj.number - 1) * paginator.per_page + 1
    page_obj.end_index = min(page_obj.start_index + paginator.per_page - 1, paginator.count)
    
    context = {
        'pos': page_obj,
        'keyword': keyword,
        'current_url': request.path + '?' + '&'.join([f"{k}={v}" for k, v in request.GET.items() if k != 'page']) + '&' if request.GET else '?'
    }
    
    return render(request, 'pages/procurement/purchase_order.html', context)

def purchase_order_add(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create PO header
                po_header = PurchaseOrderHeader(
                    comp_code=COMP_CODE,
                    tran_type='PO',
                    tran_date=datetime.strptime(request.POST.get('tran_date'), '%Y-%m-%d').date(),
                    tran_numb=request.POST.get('tran_numb'),
                    supl_code=request.POST.get('supl_code'),
                    supl_name=request.POST.get('supl_name'),
                    supl_add1=request.POST.get('supl_add1'),
                    supl_add2=request.POST.get('supl_add2'),
                    supl_add3=request.POST.get('supl_add3'),
                    cont_name=request.POST.get('cont_name'),
                    mobl_numb=request.POST.get('mobl_numb'),
                    teln_numb=request.POST.get('teln_numb'),
                    mail_addr=request.POST.get('mail_addr'),
                    refn_numb=request.POST.get('refn_numb'),
                    refn_date=datetime.strptime(request.POST.get('refn_date'), '%Y-%m-%d').date() if request.POST.get('refn_date') else None,
                    tran_remk=request.POST.get('tran_remk'),
                    totl_amnt=request.POST.get('totl_amnt') or 0,
                    disc_prct=request.POST.get('disc_prct') or 0,
                    disc_amnt=request.POST.get('disc_amnt') or 0,
                    taxx_prct=request.POST.get('taxx_prct') or 0,
                    taxx_amnt=request.POST.get('taxx_amnt') or 0,
                    lpoo_amnt=request.POST.get('lpoo_amnt') or 0,
                    created_by=request.user.username
                )
                po_header.save()

                # Create PO details
                items = request.POST.getlist('items[]')
                for i, item in enumerate(items, 1):
                    po_detail = PurchaseOrderDetail(
                        comp_code=COMP_CODE,
                        tran_type='PO',
                        tran_date=po_header.tran_date,
                        tran_numb=po_header.tran_numb,
                        tran_srno=i,
                        item_code=request.POST.get(f'item_code_{item}'),
                        item_desc=request.POST.get(f'item_desc_{item}'),
                        item_unit=request.POST.get(f'item_unit_{item}'),
                        item_qnty=request.POST.get(f'item_qnty_{item}') or 0,
                        item_rate=request.POST.get(f'item_rate_{item}') or 0,
                        item_disc=request.POST.get(f'item_disc_{item}') or 0,
                        item_amnt=request.POST.get(f'item_amnt_{item}') or 0,
                        item_taxx=request.POST.get(f'item_taxx_{item}') or 0,
                        created_by=request.user.username
                    )
                    po_detail.save()

            return JsonResponse({'status': 'success', 'message': 'Purchase Order created successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def purchase_order_edit(request):
    if request.method == 'GET':
        po_id = request.GET.get('po_id')
        try:
            po_header = get_object_or_404(PurchaseOrderHeader, id=po_id)
            po_details = PurchaseOrderDetail.objects.filter(
                tran_numb=po_header.tran_numb,
                tran_type='PO'
            ).order_by('tran_srno')
            
            data = {
                'header': {
                    'id': po_header.id,
                    'tran_date': po_header.tran_date.strftime('%Y-%m-%d'),
                    'tran_numb': po_header.tran_numb,
                    'supl_code': po_header.supl_code,
                    'supl_name': po_header.supl_name,
                    'supl_add1': po_header.supl_add1,
                    'supl_add2': po_header.supl_add2,
                    'supl_add3': po_header.supl_add3,
                    'cont_name': po_header.cont_name,
                    'mobl_numb': po_header.mobl_numb,
                    'teln_numb': po_header.teln_numb,
                    'mail_addr': po_header.mail_addr,
                    'refn_numb': po_header.refn_numb,
                    'refn_date': po_header.refn_date.strftime('%Y-%m-%d') if po_header.refn_date else None,
                    'tran_remk': po_header.tran_remk,
                    'totl_amnt': po_header.totl_amnt,
                    'disc_prct': po_header.disc_prct,
                    'disc_amnt': po_header.disc_amnt,
                    'taxx_prct': po_header.taxx_prct,
                    'taxx_amnt': po_header.taxx_amnt,
                    'lpoo_amnt': po_header.lpoo_amnt,
                    'stat_code': po_header.stat_code
                },
                'details': [{
                    'id': detail.id,
                    'item_code': detail.item_code,
                    'item_desc': detail.item_desc,
                    'item_unit': detail.item_unit,
                    'item_qnty': detail.item_qnty,
                    'item_rate': detail.item_rate,
                    'item_disc': detail.item_disc,
                    'item_amnt': detail.item_amnt,
                    'item_taxx': detail.item_taxx
                } for detail in po_details]
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                po_id = request.POST.get('po_id')
                po_header = get_object_or_404(PurchaseOrderHeader, id=po_id)
                
                # Update PO header
                po_header.tran_date = datetime.strptime(request.POST.get('tran_date'), '%Y-%m-%d').date()
                po_header.supl_code = request.POST.get('supl_code')
                po_header.supl_name = request.POST.get('supl_name')
                po_header.supl_add1 = request.POST.get('supl_add1')
                po_header.supl_add2 = request.POST.get('supl_add2')
                po_header.supl_add3 = request.POST.get('supl_add3')
                po_header.cont_name = request.POST.get('cont_name')
                po_header.mobl_numb = request.POST.get('mobl_numb')
                po_header.teln_numb = request.POST.get('teln_numb')
                po_header.mail_addr = request.POST.get('mail_addr')
                po_header.refn_numb = request.POST.get('refn_numb')
                po_header.refn_date = datetime.strptime(request.POST.get('refn_date'), '%Y-%m-%d').date() if request.POST.get('refn_date') else None
                po_header.tran_remk = request.POST.get('tran_remk')
                po_header.totl_amnt = request.POST.get('totl_amnt') or 0
                po_header.disc_prct = request.POST.get('disc_prct') or 0
                po_header.disc_amnt = request.POST.get('disc_amnt') or 0
                po_header.taxx_prct = request.POST.get('taxx_prct') or 0
                po_header.taxx_amnt = request.POST.get('taxx_amnt') or 0
                po_header.lpoo_amnt = request.POST.get('lpoo_amnt') or 0
                po_header.stat_code = request.POST.get('stat_code', 'ACT')
                po_header.updated_by = request.user.username
                po_header.save()

                # Delete existing details
                PurchaseOrderDetail.objects.filter(
                    tran_numb=po_header.tran_numb,
                    tran_type='PO'
                ).delete()

                # Create new details
                items = request.POST.getlist('items[]')
                for i, item in enumerate(items, 1):
                    po_detail = PurchaseOrderDetail(
                        comp_code=COMP_CODE,
                        tran_type='PO',
                        tran_date=po_header.tran_date,
                        tran_numb=po_header.tran_numb,
                        tran_srno=i,
                        item_code=request.POST.get(f'item_code_{item}'),
                        item_desc=request.POST.get(f'item_desc_{item}'),
                        item_unit=request.POST.get(f'item_unit_{item}'),
                        item_qnty=request.POST.get(f'item_qnty_{item}') or 0,
                        item_rate=request.POST.get(f'item_rate_{item}') or 0,
                        item_disc=request.POST.get(f'item_disc_{item}') or 0,
                        item_amnt=request.POST.get(f'item_amnt_{item}') or 0,
                        item_taxx=request.POST.get(f'item_taxx_{item}') or 0,
                        created_by=request.user.username
                    )
                    po_detail.save()

            return JsonResponse({'status': 'success', 'message': 'Purchase Order updated successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def purchase_order_delete(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                po_id = request.POST.get('po_id')
                po_header = get_object_or_404(PurchaseOrderHeader, id=po_id)
                
                # Delete details first
                PurchaseOrderDetail.objects.filter(
                    tran_numb=po_header.tran_numb,
                    tran_type='PO'
                ).delete()
                
                # Delete header
                po_header.delete()
                
            return JsonResponse({'status': 'success', 'message': 'Purchase Order deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# GRN Views
def grn(request):
    # Get search keyword
    keyword = request.GET.get('keyword', '')
    
    # Get all GRNs or filter by keyword
    if keyword:
        grns = GRNHeader.objects.filter(
            Q(tran_numb__icontains=keyword) |
            Q(supl_code__icontains=keyword) |
            Q(ware_code__icontains=keyword)
        ).order_by('-tran_date')
    else:
        grns = GRNHeader.objects.all().order_by('-tran_date')
    
    # Get warehouses and suppliers for dropdowns
    warehouses = WarehouseMaster.objects.filter(stat_code='A').order_by('ware_name')
    suppliers = PurchaseOrderHeader.objects.values('supl_code', 'supl_name').distinct().order_by('supl_name')
    
    # Get active POs for dropdown
    pos = PurchaseOrderHeader.objects.filter(stat_code='ACT').order_by('-tran_date')
    
    # Pagination
    paginator = Paginator(grns, 10)  # Show 10 GRNs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add pagination info to the page object
    page_obj.start_index = (page_obj.number - 1) * paginator.per_page + 1
    page_obj.end_index = min(page_obj.start_index + paginator.per_page - 1, paginator.count)
    
    context = {
        'grns': page_obj,
        'keyword': keyword,
        'current_url': request.path + '?' + '&'.join([f"{k}={v}" for k, v in request.GET.items() if k != 'page']) + '&' if request.GET else '?',
        'warehouses': warehouses,
        'suppliers': suppliers,
        'pos': pos  # Add POs to context
    }
    
    return render(request, 'pages/procurement/grn.html', context)

def grn_add(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create GRN header
                grn_header = GRNHeader(
                    comp_code=COMP_CODE,
                    tran_type='GRN',
                    tran_date=datetime.strptime(request.POST.get('tran_date'), '%Y-%m-%d').date(),
                    tran_numb=request.POST.get('tran_numb'),
                    ware_code=request.POST.get('ware_code'),
                    supl_code=request.POST.get('supl_code'),
                    lpoo_numb=request.POST.get('lpoo_numb'),
                    lpoo_date=datetime.strptime(request.POST.get('lpoo_date'), '%Y-%m-%d').date() if request.POST.get('lpoo_date') else None,
                    tran_remk=request.POST.get('tran_remk'),
                    stat_code=request.POST.get('stat_code', 'ACT'),
                    created_by=request.user.username
                )
                grn_header.save()

                # Get all items from the form
                items = request.POST.getlist('items[]')
                if not items:
                    raise ValueError("No items provided for GRN")

                # Create GRN details and update PO details
                for i, item in enumerate(items, 1):
                    # Get item details from form
                    item_code = request.POST.get(f'item_code_{item}')
                    item_desc = request.POST.get(f'item_desc_{item}')
                    item_unit = request.POST.get(f'item_unit_{item}')
                    item_qnty = Decimal(request.POST.get(f'item_qnty_{item}') or 0)
                    item_in_pcs = Decimal(request.POST.get(f'item_in_pcs_{item}') or 0)

                    if item_in_pcs <= 0:
                        continue  # Skip items with zero or negative in pieces

                    # Create GRN detail
                    grn_detail = GRNDetail(
                        comp_code=COMP_CODE,
                        tran_type='GRN',
                        tran_date=grn_header.tran_date,
                        tran_numb=grn_header.tran_numb,
                        tran_srno=i,
                        ware_code=grn_header.ware_code,
                        item_code=item_code,
                        item_desc=item_desc,
                        item_unit=item_unit,
                        item_qnty=item_qnty,
                        item_in_pcs=item_in_pcs,
                        created_by=request.user.username
                    )
                    grn_detail.save()

                    # Update PO detail's received quantity
                    try:
                        po_detail = PurchaseOrderDetail.objects.get(
                            comp_code=COMP_CODE,
                            tran_type='PO',
                            tran_numb=grn_header.lpoo_numb,
                            item_code=item_code
                        )
                        
                        # Update received quantity
                        current_recv_qnty = po_detail.recv_qnty or Decimal('0')
                        po_detail.recv_qnty = current_recv_qnty + item_in_pcs
                        po_detail.save()
                        
                    except PurchaseOrderDetail.DoesNotExist:
                        raise ValueError(f"PO detail not found for: {grn_header.lpoo_numb} - {item_code}")
                    except Exception as e:
                        raise ValueError(f"Error updating PO detail: {str(e)}")

            return JsonResponse({'status': 'success', 'message': 'GRN created successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def grn_delete(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                grn_id = request.POST.get('grn_id')
                grn_header = get_object_or_404(GRNHeader, id=grn_id)
                
                # Delete details first
                GRNDetail.objects.filter(
                    tran_numb=grn_header.tran_numb,
                    tran_type='GRN'
                ).delete()
                
                # Delete header
                grn_header.delete()
                
            return JsonResponse({'status': 'success', 'message': 'GRN deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def get_po_items(request):
    if request.method == 'GET':
        lpoo_numb = request.GET.get('lpoo_numb')
        try:
            # Get PO details for the given LPO number
            po_details = PurchaseOrderDetail.objects.filter(
                tran_numb=lpoo_numb,
                tran_type='PO'
            ).order_by('tran_srno')
            
            data = {
                'details': [{
                    'item_code': detail.item_code,
                    'item_desc': detail.item_desc,
                    'item_unit': detail.item_unit,
                    'item_qnty': detail.item_qnty,
                    'item_rate': detail.item_rate,
                    'item_disc': detail.item_disc,
                    'item_amnt': detail.item_amnt,
                    'item_taxx': detail.item_taxx,
                    'recv_qnty': detail.recv_qnty
                } for detail in po_details]
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
