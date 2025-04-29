from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from .models import *
from payroll.models import *
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, connection
from datetime import datetime
from decimal import Decimal

# Define pagination size constant
PAGINATION_SIZE = 6

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
    paginator = Paginator(items, PAGINATION_SIZE)
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
            # Generate item code using fn_get_seed_no
            with connection.cursor() as cursor:
                cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'ITEM'])
                result = cursor.fetchone()
                item_code = result[0] if result else None

            # Create new item
            item = ItemMaster(
                item_code=item_code,
                item_description=request.POST.get('item_description').upper(),
                uom=request.POST.get('uom'),
                remarks=request.POST.get('remarks'),
                category=request.POST.get('category'),
                sub_category=request.POST.get('sub_category'),
                item_rate=request.POST.get('item_rate') or 0,
                stock_qty=request.POST.get('stock_qty') or 0,
                open_qty=request.POST.get('open_qty') or 0,
                reorder_qty=request.POST.get('reorder_qty') or 0,
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
                'category': item.category,
                'sub_category': item.sub_category,
                'item_rate': float(item.item_rate),
                'stock_qty': float(item.stock_qty),
                'open_qty': float(item.open_qty),
                'reorder_qty': float(item.reorder_qty),
                'is_active': item.is_active,
                'remarks': item.remarks
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
            item.category = request.POST.get('category')
            item.sub_category = request.POST.get('sub_category')
            item.item_rate = Decimal(request.POST.get('item_rate') or 0)
            item.stock_qty = Decimal(request.POST.get('stock_qty') or 0)
            item.open_qty = Decimal(request.POST.get('open_qty') or 0)
            item.reorder_qty = Decimal(request.POST.get('reorder_qty') or 0)
            item.is_active = request.POST.get('is_active') == 'true'
            item.remarks = request.POST.get('remarks')
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
    paginator = Paginator(uoms, PAGINATION_SIZE)
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
    paginator = Paginator(warehouses, PAGINATION_SIZE)
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

@csrf_exempt
def warehouse_master_add(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Generate warehouse code using fn_get_seed_no
                with connection.cursor() as cursor:
                    cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'WARE'])
                    result = cursor.fetchone()
                    ware_code = result[0] if result else None

                # Create new warehouse
                warehouse = WarehouseMaster(
                    comp_code=COMP_CODE,
                    ware_code=ware_code,
                    ware_name=request.POST.get('ware_name'),
                    ware_type=request.POST.get('ware_type'),
                    stat_code=request.POST.get('stat_code'),
                    created_by=request.user.username
                )
                warehouse.save()
                return redirect('warehouse_master')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def warehouse_master_edit(request):
    set_comp_code(request)
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
            with transaction.atomic():
                warehouse_id = request.POST.get('warehouse_id')
                warehouse = get_object_or_404(WarehouseMaster, id=warehouse_id)
                
                # Update warehouse fields
                warehouse.ware_code = request.POST.get('ware_code')
                warehouse.ware_name = request.POST.get('ware_name')
                warehouse.ware_type = request.POST.get('ware_type')
                warehouse.stat_code = request.POST.get('stat_code')
                warehouse.updated_by = request.user.username
                warehouse.save()
                
                return redirect('warehouse_master')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def warehouse_master_delete(request, warehouse_id):
    set_comp_code(request)
    if request.method == 'DELETE':
        try:
            with transaction.atomic():
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
    paginator = Paginator(pos, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add pagination info to the page object
    page_obj.start_index = (page_obj.number - 1) * paginator.per_page + 1
    page_obj.end_index = min(page_obj.start_index + paginator.per_page - 1, paginator.count)
    
    context = {
        'pos': page_obj,
        'keyword': keyword,
        'current_url': request.path + '?' + '&'.join([f"{k}={v}" for k, v in request.GET.items() if k != 'page']) + '&' if request.GET else '?',
        
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
    set_comp_code(request)
    if request.method == 'GET':
        po_id = request.GET.get('po_id')
        if not po_id:
            return JsonResponse({'status': 'error', 'message': 'PO ID is required'})
            
        try:
            po_header = get_object_or_404(PurchaseOrderHeader, id=po_id)
            po_details = PurchaseOrderDetail.objects.filter(
                tran_numb=po_header.tran_numb,
                tran_type='PO'
            ).order_by('tran_srno')
            
            # Get PR data for dropdown
            pr_items_data = MaterialRequestHeader.objects.filter(comp_code=COMP_CODE, ordr_type='PR').order_by('-ordr_date')
            
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
                    'totl_amnt': float(po_header.totl_amnt),
                    'disc_prct': float(po_header.disc_prct),
                    'disc_amnt': float(po_header.disc_amnt),
                    'taxx_prct': float(po_header.taxx_prct),
                    'taxx_amnt': float(po_header.taxx_amnt),
                    'lpoo_amnt': float(po_header.lpoo_amnt),
                    'stat_code': po_header.stat_code
                },
                'details': [{
                    'id': detail.id,
                    'item_code': detail.item_code,
                    'item_desc': detail.item_desc,
                    'item_unit': detail.item_unit,
                    'item_qnty': float(detail.item_qnty),
                    'item_rate': float(detail.item_rate),
                    'item_disc': float(detail.item_disc),
                    'item_amnt': float(detail.item_amnt),
                    'item_taxx': float(detail.item_taxx)
                } for detail in po_details],
                'pr_items_data': [{
                    'id': pr.id,
                    'ordr_numb': pr.ordr_numb,
                    'uniq_numb': pr.uniq_numb
                } for pr in pr_items_data]
            }
            return JsonResponse(data)
        except PurchaseOrderHeader.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Purchase Order not found'})
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

def get_pr_items(request):
    if request.method == "GET":
        ordr_numb = request.GET.get("ordr_numb")
        if not ordr_numb:
            return JsonResponse({"status": "error", "message": "PR Number is required"})
        
        try:
            pr = MaterialRequestHeader.objects.get(ordr_numb=ordr_numb)
            items = []
            for item in MaterialRequestDetail.objects.filter(
                uniq_numb=pr.uniq_numb,
                comp_code=pr.comp_code,
                ordr_type=pr.ordr_type,
                ordr_date=pr.ordr_date,
                ordr_numb=pr.ordr_numb
            ).order_by('serl_numb'):
                items.append({
                    "id": item.id,
                    "item_code": item.item_code,
                    "item_desc": item.item_desc,
                    "item_unit": item.item_unit,
                    "item_qnty": float(item.item_qnty),
                    "item_rate": float(item.item_rate),
                    "item_amnt": float(item.item_amnt)
                })
            return JsonResponse({
                "status": "success",
                "items": items
            })
        except MaterialRequestHeader.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Material Request not found"
            })
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": str(e)
            })
    
    return JsonResponse({"status": "error", "message": "Invalid request method"})

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
    paginator = Paginator(grns, PAGINATION_SIZE)
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

                # Create GRN details
                for i, item_id in enumerate(items, 1):
                    # Get item details from form
                    item_code = request.POST.get(f'item_code_{item_id}')
                    item_desc = request.POST.get(f'item_desc_{item_id}')
                    item_unit = request.POST.get(f'item_unit_{item_id}')
                    item_qnty = Decimal(request.POST.get(f'item_qnty_{item_id}') or 0)
                    item_in_pcs = Decimal(request.POST.get(f'item_in_pcs_{item_id}') or 0)

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

# Material Request Views
def material_request(request):
    set_comp_code(request)
    # Get search keyword
    keyword = request.GET.get('keyword', '')
    
    # Get all material requests
    mrs = MaterialRequestHeader.objects.filter(comp_code=COMP_CODE).order_by('-ordr_date')
    pr_data = MaterialRequestHeader.objects.filter(comp_code=COMP_CODE, ordr_type='PR', quot_stat='ACT').order_by('-ordr_date')
    items = ItemMaster.objects.filter(comp_code=COMP_CODE, is_active=True)
    job_codes = projectMaster.objects.filter(comp_code=COMP_CODE).values('prj_code', 'prj_name').distinct()
    
    # Apply search filter if keyword exists
    if keyword:
        mrs = mrs.filter(
            Q(ordr_numb__icontains=keyword) |
            Q(job_code__icontains=keyword) |
            Q(quot_numb__icontains=keyword)
        )
    
    # Pagination
    paginator = Paginator(mrs, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    mrs = paginator.get_page(page_number)
    
    # Get current URL for pagination
    current_url = request.path + '?'
    if keyword:
        current_url += f'keyword={keyword}&'
    
    context = {
        'mrs': mrs,
        'keyword': keyword,
        'current_url': current_url,
        'pr_data': pr_data,
        'items': items,
        'job_codes': job_codes
    }
    
    return render(request, 'pages/procurement/material_request.html', context)

@csrf_exempt
def material_request_add(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                ordr_type = request.POST.get('ordr_type')
                
                # Generate order number based on type
                with connection.cursor() as cursor:
                    if ordr_type == 'MR':
                        cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'MR'])
                    elif ordr_type == 'PR':
                        cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'PR'])
                    else:
                        raise ValueError("Invalid order type. Must be 'MR' or 'PR'")
                    
                    result = cursor.fetchone()
                    ordr_numb = result[0] if result else None

                if not ordr_numb:
                    raise ValueError(f"Failed to generate order number for type {ordr_type}")

                # Create MR header
                mr_header = MaterialRequestHeader.objects.create(
                    comp_code=COMP_CODE,
                    ordr_type=ordr_type,
                    ordr_date=datetime.strptime(request.POST.get('ordr_date'), '%Y-%m-%d').date(),
                    ordr_numb=ordr_numb,
                    job_code=request.POST.get('job_code'),
                    quot_numb=request.POST.get('quot_numb'),
                    quot_date=datetime.strptime(request.POST.get('quot_date'), '%Y-%m-%d').date() if request.POST.get('quot_date') else None,
                    quot_stat='ACT',
                    created_by=request.user.username
                )

                # Create MR details
                items = request.POST.getlist('items[]')
                for index, item_id in enumerate(items, 1):
                    item_code = request.POST.get(f'item_code_{item_id}')
                    item_desc = request.POST.get(f'item_desc_{item_id}')
                    item_unit = request.POST.get(f'item_unit_{item_id}')
                    item_qnty = request.POST.get(f'item_qnty_{item_id}')

                    if not all([item_code, item_desc, item_unit, item_qnty]):
                        raise ValueError(f"Missing required fields for item {index}")

                    MaterialRequestDetail.objects.create(
                        comp_code=mr_header.comp_code,
                        ordr_type=mr_header.ordr_type,
                        ordr_date=mr_header.ordr_date,
                        ordr_numb=mr_header.ordr_numb,
                        serl_numb=index,
                        item_code=item_code,
                        item_desc=item_desc,
                        item_unit=item_unit,
                        item_qnty=item_qnty,
                        created_by=request.user.username
                    )

                return JsonResponse({
                    'status': 'success',
                    'message': f'{ordr_type} request added successfully',
                    'ordr_numb': ordr_numb
                })

        except ValueError as ve:
            return JsonResponse({
                'status': 'error',
                'message': str(ve)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Failed to create {ordr_type} request: {str(e)}'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

@csrf_exempt
def material_request_edit(request):
    if request.method == 'POST':
        try:
            mr_id = request.POST.get('mr_id')
            mr_header = MaterialRequestHeader.objects.get(id=mr_id)
            
            # Update header
            mr_header.ordr_type = request.POST.get('ordr_type')
            mr_header.ordr_date = request.POST.get('ordr_date')
            mr_header.ordr_numb = request.POST.get('ordr_numb')
            mr_header.job_code = request.POST.get('job_code')
            mr_header.quot_numb = request.POST.get('quot_numb')
            mr_header.quot_date = request.POST.get('quot_date') or None
            mr_header.updated_by = request.user.username
            mr_header.updated_date = datetime.now()
            mr_header.save()
            
            # Delete existing details
            MaterialRequestDetail.objects.filter(
                uniq_numb=mr_header.uniq_numb,
                comp_code=mr_header.comp_code,
                ordr_type=mr_header.ordr_type,
                ordr_date=mr_header.ordr_date,
                ordr_numb=mr_header.ordr_numb
            ).delete()
            
            # Create new details
            items = request.POST.getlist('items[]')
            for item_id in items:
                item_code = request.POST.get(f'item_code_{item_id}')
                item_desc = request.POST.get(f'item_desc_{item_id}')
                item_unit = request.POST.get(f'item_unit_{item_id}')
                item_qnty = request.POST.get(f'item_qnty_{item_id}')
                
                MaterialRequestDetail.objects.create(
                    uniq_numb=mr_header.uniq_numb,
                    comp_code=mr_header.comp_code,
                    ordr_type=mr_header.ordr_type,
                    ordr_date=mr_header.ordr_date,
                    ordr_numb=mr_header.ordr_numb,
                    serl_numb=len(items),
                    item_code=item_code,
                    item_desc=item_desc,
                    item_unit=item_unit,
                    item_qnty=item_qnty,
                    created_by=request.user.username
                )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Material request updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    # GET request - get MR details
    mr_id = request.GET.get('mr_id')
    try:
        mr_header = MaterialRequestHeader.objects.get(id=mr_id)
        mr_details = MaterialRequestDetail.objects.filter(
            uniq_numb=mr_header.uniq_numb,
            comp_code=mr_header.comp_code,
            ordr_type=mr_header.ordr_type,
            ordr_date=mr_header.ordr_date,
            ordr_numb=mr_header.ordr_numb
        )
        
        return JsonResponse({
            'status': 'success',
            'header': {
                'id': mr_header.id,
                'ordr_type': mr_header.ordr_type,
                'ordr_date': mr_header.ordr_date.strftime('%Y-%m-%d'),
                'ordr_numb': mr_header.ordr_numb,
                'job_code': mr_header.job_code,
                'quot_numb': mr_header.quot_numb,
                'quot_date': mr_header.quot_date.strftime('%Y-%m-%d') if mr_header.quot_date else None
            },
            'details': list(mr_details.values())
        })
        
    except MaterialRequestHeader.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Material request not found'
        })

@csrf_exempt
def material_request_delete(request):
    if request.method == 'POST':
        try:
            mr_id = request.POST.get('mr_id')
            mr_header = MaterialRequestHeader.objects.get(id=mr_id)
            
            # Delete details first
            MaterialRequestDetail.objects.filter(
                uniq_numb=mr_header.uniq_numb,
                comp_code=mr_header.comp_code,
                ordr_type=mr_header.ordr_type,
                ordr_date=mr_header.ordr_date,
                ordr_numb=mr_header.ordr_numb
            ).delete()
            
            # Delete header
            mr_header.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Material request deleted successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

# Warehouse Opening Stock Views
def warehouse_opening_stock(request):
    # Get search keyword
    keyword = request.GET.get('keyword', '')
    
    # Get all details or filter by keyword
    if keyword:
        details = WarehouseDetail.objects.filter(
            Q(ware_code__icontains=keyword) |
            Q(item_code__icontains=keyword)
        ).filter(tran_type='OPN').order_by('-tran_date', 'ware_code', 'item_code')
    else:
        details = WarehouseDetail.objects.filter(tran_type='OPN').order_by('-tran_date', 'ware_code', 'item_code')
    
    # Get warehouses and items for dropdowns
    warehouses = WarehouseMaster.objects.filter(stat_code='A').order_by('ware_code')
    items = ItemMaster.objects.filter(is_active=True).order_by('item_code')
    
    # Get item descriptions
    item_descriptions = {}
    for item in ItemMaster.objects.all():
        if item.item_code not in item_descriptions:
            item_descriptions[item.item_code] = item.item_description
    
    # Add item descriptions to details
    for detail in details:
        detail.item_desc = item_descriptions.get(detail.item_code, '')
    
    # Pagination
    paginator = Paginator(details, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add pagination info to the page object
    page_obj.start_index = (page_obj.number - 1) * paginator.per_page + 1
    page_obj.end_index = min(page_obj.start_index + paginator.per_page - 1, paginator.count)
    
    context = {
        'details': page_obj,
        'keyword': keyword,
        'current_url': request.path + '?' + '&'.join([f"{k}={v}" for k, v in request.GET.items() if k != 'page']) + '&' if request.GET else '?',
        'warehouses': warehouses,
        'items': items
    }
    
    return render(request, 'pages/procurement/warehouse_opening_stock.html', context)

def warehouse_opening_stock_add(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get items from form data
                items = []
                for key in request.POST:
                    if key.startswith('items[') and key.endswith('][item_code]'):
                        index = key.split('[')[1].split(']')[0]
                        item_code = request.POST.get(f'items[{index}][item_code]')
                        quantity = request.POST.get(f'items[{index}][quantity]')
                        if item_code and quantity:
                            items.append({
                                'item_code': item_code,
                                'quantity': quantity
                            })
                
                if not items:
                    return JsonResponse({'status': 'error', 'message': 'No items provided'})
                
                # Create warehouse details for each item
                for item in items:
                    detail = WarehouseDetail(
                        comp_code=COMP_CODE,
                        tran_type='OPN',
                        tran_date=datetime.strptime(request.POST.get('tran_date'), '%Y-%m-%d').date(),
                        tran_numb=f"OPN{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        tran_srno=1,
                        ware_code=request.POST.get('ware_code'),
                        item_code=item['item_code'],
                        item_tran='OPN',
                        tran_qnty=item['quantity'],
                        item_luom=request.POST.get('item_luom'),
                        crte_user=request.user.username
                    )
                    detail.save()

                return JsonResponse({'status': 'success', 'message': 'Opening stock created successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def warehouse_opening_stock_edit(request):
    if request.method == 'GET':
        stock_id = request.GET.get('id_number')
        try:
            detail = get_object_or_404(WarehouseDetail, id_number=stock_id, tran_type='OPN')
            # Get item description from ItemMaster
            item = ItemMaster.objects.filter(item_code=detail.item_code).first()
            data = {
                'status': 'success',
                'data': {
                    'id_number': detail.id_number,
                    'tran_date': detail.tran_date.strftime('%Y-%m-%d'),
                    'ware_code': detail.ware_code,
                    'item_code': detail.item_code,
                    'item_desc': item.item_description if item else '',
                    'tran_qnty': float(detail.tran_qnty),
                    'item_luom': detail.item_luom
                }
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                stock_id = request.POST.get('stock_id')
                detail = get_object_or_404(WarehouseDetail, id_number=stock_id, tran_type='OPN')
                
                # Update detail
                detail.tran_date = datetime.strptime(request.POST.get('tran_date'), '%Y-%m-%d').date()
                detail.ware_code = request.POST.get('ware_code')
                detail.item_code = request.POST.get('item_code')
                detail.tran_qnty = request.POST.get('open_qnty') or 0
                detail.item_luom = request.POST.get('item_luom')
                detail.updt_user = request.user.username
                detail.save()

            return JsonResponse({'status': 'success', 'message': 'Opening stock updated successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def warehouse_opening_stock_delete(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                stock_id = request.POST.get('stock_id')
                detail = get_object_or_404(WarehouseDetail, id_number=stock_id, tran_type='OPN')
                
                # Delete detail
                detail.delete()
                
            return JsonResponse({'status': 'success', 'message': 'Opening stock deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def get_item_details(request):
    if request.method == 'GET':
        item_code = request.GET.get('item_code')
        try:
            item = get_object_or_404(ItemMaster, item_code=item_code)
            return JsonResponse({
                'status': 'success',
                'uom': item.uom
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# Material Issue Views
def material_issue(request):
    # Get search keyword
    keyword = request.GET.get('keyword', '')
    
    # Get all issues or filter by keyword
    if keyword:
        issues = WarehouseDetail.objects.filter(
            Q(tran_type='MI') &
            (Q(tran_numb__icontains=keyword) |
            Q(refn_numb__icontains=keyword) |
            Q(cust_code__icontains=keyword))
        ).order_by('-tran_date')
    else:
        issues = WarehouseDetail.objects.filter(tran_type='MI').order_by('-tran_date')
    
    # Get material requests and warehouses for dropdowns
    material_requests = MaterialRequestHeader.objects.filter(ordr_type='MR').order_by('-ordr_date')
    warehouses = WarehouseMaster.objects.filter(stat_code='A').order_by('ware_code')
    
    # Pagination
    paginator = Paginator(issues, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add pagination info to the page object
    page_obj.start_index = (page_obj.number - 1) * paginator.per_page + 1
    page_obj.end_index = min(page_obj.start_index + paginator.per_page - 1, paginator.count)
    
    context = {
        'issues': page_obj,
        'keyword': keyword,
        'current_url': request.path + '?' + '&'.join([f"{k}={v}" for k, v in request.GET.items() if k != 'page']) + '&' if request.GET else '?',
        'material_requests': material_requests,
        'warehouses': warehouses
    }
    
    return render(request, 'pages/procurement/material_issue.html', context)

def material_issue_add(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Create material issue header
                issue = WarehouseDetail(
                    comp_code=COMP_CODE,
                    tran_type='MI',
                    tran_date=datetime.strptime(request.POST.get('tran_date'), '%Y-%m-%d').date(),
                    tran_numb=f"MI{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    tran_srno=1,
                    ware_code=request.POST.get('ware_code'),
                    item_code=request.POST.get('item_code'),
                    item_tran='OUT',
                    tran_qnty=request.POST.get('tran_qnty') or 0,
                    refn_type='MR',
                    refn_date=datetime.strptime(request.POST.get('refn_date'), '%Y-%m-%d').date(),
                    refn_numb=request.POST.get('refn_numb'),
                    refn_srno=1,
                    cust_code=request.POST.get('cust_code'),
                    item_luom=request.POST.get('item_luom'),
                    crte_user=request.user.username
                )
                issue.save()

                # Update warehouse stock
                stock = WarehouseHeader.objects.get(
                    comp_code=COMP_CODE,
                    ware_code=issue.ware_code,
                    item_code=issue.item_code
                )
                stock.issu_qnty += issue.tran_qnty
                stock.baln_qnty = stock.open_qnty + stock.recv_qnty - stock.issu_qnty
                stock.updt_user = request.user.username
                stock.save()

            return JsonResponse({'status': 'success', 'message': 'Material issue created successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def material_issue_edit(request):
    if request.method == 'GET':
        issue_id = request.GET.get('issue_id')
        try:
            issue = get_object_or_404(WarehouseDetail, id_number=issue_id)
            data = {
                'id_number': issue.id_number,
                'tran_date': issue.tran_date.strftime('%Y-%m-%d'),
                'refn_numb': issue.refn_numb,
                'refn_date': issue.refn_date.strftime('%Y-%m-%d'),
                'cust_code': issue.cust_code,
                'ware_code': issue.ware_code,
                'items': [{
                    'item_code': issue.item_code,
                    'item_desc': issue.item_desc,
                    'item_unit': issue.item_luom,
                    'mr_qty': float(issue.tran_qnty),
                    'issued_qty': float(issue.tran_qnty),
                    'balance': float(issue.tran_qnty),
                    'stock_qty': float(WarehouseHeader.objects.get(
                        comp_code=issue.comp_code,
                        ware_code=issue.ware_code,
                        item_code=issue.item_code
                    ).baln_qnty),
                    'issue_qty': float(issue.tran_qnty)
                }]
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                issue_id = request.POST.get('issue_id')
                issue = get_object_or_404(WarehouseDetail, id_number=issue_id)
                
                # Update issue
                old_qnty = issue.tran_qnty
                new_qnty = Decimal(request.POST.get('tran_qnty') or 0)
                
                issue.tran_date = datetime.strptime(request.POST.get('tran_date'), '%Y-%m-%d').date()
                issue.ware_code = request.POST.get('ware_code')
                issue.item_code = request.POST.get('item_code')
                issue.tran_qnty = new_qnty
                issue.refn_date = datetime.strptime(request.POST.get('refn_date'), '%Y-%m-%d').date()
                issue.refn_numb = request.POST.get('refn_numb')
                issue.cust_code = request.POST.get('cust_code')
                issue.item_luom = request.POST.get('item_luom')
                issue.updt_user = request.user.username
                issue.save()

                # Update warehouse stock
                stock = WarehouseHeader.objects.get(
                    comp_code=issue.comp_code,
                    ware_code=issue.ware_code,
                    item_code=issue.item_code
                )
                stock.issu_qnty = stock.issu_qnty - old_qnty + new_qnty
                stock.baln_qnty = stock.open_qnty + stock.recv_qnty - stock.issu_qnty
                stock.updt_user = request.user.username
                stock.save()

            return JsonResponse({'status': 'success', 'message': 'Material issue updated successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def material_issue_delete(request):
    if request.method == 'POST':
        try:
            with transaction.atomic():
                issue_id = request.POST.get('issue_id')
                issue = get_object_or_404(WarehouseDetail, id_number=issue_id)
                
                # Update warehouse stock
                stock = WarehouseHeader.objects.get(
                    comp_code=issue.comp_code,
                    ware_code=issue.ware_code,
                    item_code=issue.item_code
                )
                stock.issu_qnty -= issue.tran_qnty
                stock.baln_qnty = stock.open_qnty + stock.recv_qnty - stock.issu_qnty
                stock.updt_user = request.user.username
                stock.save()
                
                # Delete issue
                issue.delete()
                
            return JsonResponse({'status': 'success', 'message': 'Material issue deleted successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def get_mr_items(request):
    if request.method == 'GET':
        ordr_numb = request.GET.get('ordr_numb')
        if not ordr_numb:
            return JsonResponse({
                'status': 'error',
                'message': 'MR Number is required'
            })
        
        try:
            # Debug print
            print(f"Fetching MR items for order number: {ordr_numb}")
            
            mr = MaterialRequestHeader.objects.get(ordr_numb=ordr_numb)
            print(f"Found MR header: {mr.__dict__}")
            
            items = []
            mr_details = MaterialRequestDetail.objects.filter(
                uniq_numb=mr.uniq_numb,
                comp_code=mr.comp_code,
                ordr_type=mr.ordr_type,
                ordr_date=mr.ordr_date,
                ordr_numb=mr.ordr_numb
            ).order_by('serl_numb')
            
            print(f"Found {mr_details.count()} MR details")
            
            for item in mr_details:
                # Get issued quantity
                issued_qty = WarehouseDetail.objects.filter(
                    refn_numb=ordr_numb,
                    item_code=item.item_code,
                    tran_type='MI'
                ).aggregate(total=Sum('tran_qnty'))['total'] or 0
                
                item_data = {
                    'item_code': item.item_code,
                    'item_desc': item.item_desc,
                    'item_unit': item.item_unit,
                    'item_qnty': float(item.item_qnty),
                    'issued_qty': float(issued_qty),
                    'balance': float(item.item_qnty - issued_qty)
                }
                items.append(item_data)
                print(f"Processed item: {item_data}")
            
            response_data = {
                'status': 'success',
                'items': items
            }
            print(f"Sending response: {response_data}")
            return JsonResponse(response_data)
            
        except MaterialRequestHeader.DoesNotExist:
            print(f"MR not found for order number: {ordr_numb}")
            return JsonResponse({
                'status': 'error',
                'message': 'Material Request not found'
            })
        except Exception as e:
            print(f"Error processing MR items: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def get_warehouse_stock(request):
    set_comp_code(request)
    if request.method == 'GET':
        warehouse_code = request.GET.get('ware_code')
        item_codes = request.GET.get('item_codes', '').split(',')
        
        if not warehouse_code:
            return JsonResponse({
                'status': 'error',
                'message': 'Warehouse code is required'
            })
        
        try:
            # Get stock quantities for all items in the warehouse
            stocks = []
            for item_code in item_codes:
                if not item_code:
                    continue
                    
                try:
                    stock = WarehouseHeader.objects.get(
                        comp_code=COMP_CODE,
                        ware_code=warehouse_code,
                        item_code=item_code
                    )
                    stocks.append({
                        'item_code': stock.item_code,
                        'baln_qnty': float(stock.baln_qnty)
                    })
                except WarehouseHeader.DoesNotExist:
                    # If no stock record exists, add with zero quantity
                    stocks.append({
                        'item_code': item_code,
                        'baln_qnty': 0
                    })
            
            return JsonResponse({
                'status': 'success',
                'stocks': stocks
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def check_uom_exists(request):
    if request.method == 'GET':
        uom = request.GET.get('uom')
        try:
            exists = UOMMaster.objects.filter(uom=uom).exists()
            return JsonResponse({'exists': exists})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
