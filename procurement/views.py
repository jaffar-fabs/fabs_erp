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
    set_comp_code(request)
    # Get all items or filter by keyword
    if keyword:
        items = ItemMaster.objects.filter(
            Q(item_code__icontains=keyword) |
            Q(item_description__icontains=keyword) |
            Q(category__icontains=keyword),
            comp_code=COMP_CODE
        ).order_by('item_code')
    else:
        items = ItemMaster.objects.filter(comp_code=COMP_CODE).order_by('item_code')
    
    # Get all active UOMs for dropdown
    uom_data = UOMMaster.objects.filter(is_active=True).order_by('uom')
    
    # Get dropdown data for new fields
    material_type_data = CodeMaster.objects.filter(
        base_type='MATERIAL_TYPE', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    category_data = CodeMaster.objects.filter(
        base_type='ITEM_CATEGORY', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    manufacturer_data = CodeMaster.objects.filter(
        base_type='MANUFACTURER', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    country_data = CodeMaster.objects.filter(
        base_type='COUNTRY', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')

    item_description_data = CodeMaster.objects.filter(
        base_type='ITEM_DESCRIPTION', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')

    uom_data = CodeMaster.objects.filter(
        base_type='UOM', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
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
        'uom_data': uom_data,
        'material_type_data': material_type_data,
        'category_data': category_data,
        'manufacturer_data': manufacturer_data,
        'country_data': country_data,
        'item_description_data': item_description_data,
        'uom_data': uom_data,
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
                item_description=request.POST.get('item_description'),
                uom=request.POST.get('uom'),
                is_active=request.POST.get('is_active') == 'true',
                created_by=request.user.username,
                comp_code=COMP_CODE,
                # New fields
                material_type=request.POST.get('material_type'),
                category=request.POST.get('category'),
                model_no=request.POST.get('model_no'),
                capacity=request.POST.get('capacity'),
                size=request.POST.get('size'),
                thickness=request.POST.get('thickness'),
                manufacturer=request.POST.get('manufacturer'),
                country_of_origin=request.POST.get('country_of_origin'),
                specification_standard=request.POST.get('specification_standard'),
                rate=request.POST.get('rate') or 0,
                additional_information=request.POST.get('additional_information'),
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
                'is_active': item.is_active,
                # New fields
                'material_type': item.material_type,
                'category': item.category,
                'model_no': item.model_no,
                'capacity': item.capacity,
                'size': item.size,
                'thickness': item.thickness,
                'manufacturer': item.manufacturer,
                'country_of_origin': item.country_of_origin,
                'specification_standard': item.specification_standard,
                'rate': float(item.rate),
                'additional_information': item.additional_information,
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
            item.is_active = request.POST.get('is_active') == 'true'
            item.updated_by = request.user.username
            
            # Update new fields
            item.material_type = request.POST.get('material_type')
            item.category = request.POST.get('category')
            item.model_no = request.POST.get('model_no')
            item.capacity = request.POST.get('capacity')
            item.size = request.POST.get('size')
            item.thickness = request.POST.get('thickness')
            item.manufacturer = request.POST.get('manufacturer')
            item.country_of_origin = request.POST.get('country_of_origin')
            item.specification_standard = request.POST.get('specification_standard')
            item.rate = Decimal(request.POST.get('rate') or 0)
            item.additional_information = request.POST.get('additional_information')
            
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
    set_comp_code(request)
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
        pos = PurchaseOrderHeader.objects.filter(comp_code = COMP_CODE).order_by('-tran_date')
    
    # Get suppliers from PartyMaster
    suppliers = PartyMaster.objects.filter(comp_code=COMP_CODE, party_type='SUPPLIER').order_by('customer_name')
    
    # Get active POs for dropdown
    pr_items_data = MaterialRequestHeader.objects.filter(comp_code=COMP_CODE, ordr_type='PR', quot_stat='ACT').order_by('-ordr_date')
    
    items = ItemMaster.objects.filter(comp_code=COMP_CODE, is_active=True)
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
        'suppliers': suppliers,
        'pr_items_data': pr_items_data,
        'items': items
    }
    
    return render(request, 'pages/procurement/purchase_order.html', context)

def purchase_order_add(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Generate PO number using fn_get_seed_no
                with connection.cursor() as cursor:
                    cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'PO'])
                    result = cursor.fetchone()
                    tran_numb = result[0] if result else None

                if not tran_numb:
                    raise ValueError("Failed to generate PO number")

                # Create PO header
                po_header = PurchaseOrderHeader(
                    comp_code=COMP_CODE,
                    tran_type='PO',
                    tran_date=datetime.strptime(request.POST.get('tran_date'), '%Y-%m-%d').date(),
                    tran_numb=tran_numb,
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
                    stat_code=request.POST.get('stat_code', 'ACT'),
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

            return JsonResponse({
                'status': 'success',
                'message': 'Purchase Order created successfully',
                'tran_numb': tran_numb
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
                # uniq_numb=pr.uniq_numb,
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
                id=mr_header.id,
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
                    id=mr_header.id,
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
            id=mr_header.id,
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
                id=mr_header.id,
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
                    tran_type='ISS',
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
                    job_code=request.POST.get('job_code'),
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
                
            return JsonResponse({
                'status': 'success',
                'message': 'Material issue deleted successfully'
            })
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
            mr = MaterialRequestHeader.objects.get(ordr_numb=ordr_numb)
            
            items = []
            mr_details = MaterialRequestDetail.objects.filter(
                # uniq_numb=mr.uniq_numb,
                comp_code=mr.comp_code,
                ordr_type=mr.ordr_type,
                ordr_date=mr.ordr_date,
                ordr_numb=mr.ordr_numb
            ).order_by('serl_numb')
            
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
            
            response_data = {
                'status': 'success',
                'items': items
            }
            return JsonResponse(response_data)
            
        except MaterialRequestHeader.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Material Request not found'
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

def service_master(request):
    # Get search keyword
    keyword = request.GET.get('keyword', '')
    set_comp_code(request)
    # Get all services or filter by keyword
    if keyword:
        services = ServiceMaster.objects.filter(
            Q(service_code__icontains=keyword) |
            Q(service_description__icontains=keyword) |
            Q(category__icontains=keyword),
            comp_code=COMP_CODE
        ).order_by('service_code')
    else:
        services = ServiceMaster.objects.filter(comp_code=COMP_CODE).order_by('service_code')
    
    # Get dropdown data for new fields
    service_type_data = CodeMaster.objects.filter(
        base_type='PRO_SERVICE_TYPE', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    category_data = CodeMaster.objects.filter(
        base_type='PRO_SERVICE_CATEGORY', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    service_description_data = CodeMaster.objects.filter(
        base_type='PRO_SERVICE_DESCRIPTION', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    unit_data = CodeMaster.objects.filter(
        base_type='PRO_SERVICE_UNIT', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    # Pagination
    paginator = Paginator(services, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add pagination info to the page object
    page_obj.start_index = (page_obj.number - 1) * paginator.per_page + 1
    page_obj.end_index = min(page_obj.start_index + paginator.per_page - 1, paginator.count)
    
    context = {
        'services': page_obj,
        'keyword': keyword,
        'current_url': request.path + '?' + '&'.join([f"{k}={v}" for k, v in request.GET.items() if k != 'page']) + '&' if request.GET else '?',
        'service_type_data': service_type_data,
        'category_data': category_data,
        'service_description_data': service_description_data,
        'unit_data': unit_data,
    }
    
    return render(request, 'pages/procurement/service_master.html', context)

def service_master_add(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            # Generate service code using fn_get_seed_no
            with connection.cursor() as cursor:
                cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'SERVICE'])
                result = cursor.fetchone()
                service_code = result[0] if result else None

            # Create new service
            service = ServiceMaster(
                service_code=service_code,
                service_type=request.POST.get('service_type'),
                category=request.POST.get('category'),
                service_description=request.POST.get('service_description'),
                size=request.POST.get('size'),
                unit=request.POST.get('unit'),
                rate=request.POST.get('rate') or 0,
                additional_information=request.POST.get('additional_information'),
                is_active=request.POST.get('is_active') == 'true',
                created_by=request.user.username,
                comp_code=COMP_CODE,
            )
            service.save()
            return redirect('service_master')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def service_master_edit(request):
    if request.method == 'GET':
        service_id = request.GET.get('service_id')
        try:
            service = get_object_or_404(ServiceMaster, id=service_id)
            data = {
                'id': service.id,
                'service_code': service.service_code,
                'service_type': service.service_type,
                'category': service.category,
                'service_description': service.service_description,
                'size': service.size,
                'unit': service.unit,
                'rate': float(service.rate),
                'additional_information': service.additional_information,
                'is_active': service.is_active,
            }
            return JsonResponse(data)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    elif request.method == 'POST':
        try:
            service_id = request.POST.get('service_id')
            service = get_object_or_404(ServiceMaster, id=service_id)
            
            # Update service fields
            service.service_code = request.POST.get('service_code')
            service.service_type = request.POST.get('service_type')
            service.category = request.POST.get('category')
            service.service_description = request.POST.get('service_description')
            service.size = request.POST.get('size')
            service.unit = request.POST.get('unit')
            service.rate = Decimal(request.POST.get('rate') or 0)
            service.additional_information = request.POST.get('additional_information')
            service.is_active = request.POST.get('is_active') == 'true'
            service.updated_by = request.user.username
            
            service.save()
            return redirect('service_master')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def service_master_delete(request):
    set_comp_code(request)
    if request.method == 'POST':
        service_id = request.POST.get('id')
        try:
            service = ServiceMaster.objects.get(id=service_id, comp_code=COMP_CODE)
            service.delete()
            return JsonResponse({'status': 'success'})
        except ServiceMaster.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Service not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# Vendor Master Views
def vendor_master(request):
    # Get search keyword
    keyword = request.GET.get('keyword', '')
    set_comp_code(request)
    
    # Get all vendors or filter by keyword
    if keyword:
        vendors = VendorMaster.objects.filter(
            Q(vendor_code__icontains=keyword) |
            Q(vendor_short_code__icontains=keyword) |
            Q(vendor_name__icontains=keyword) |
            Q(vendor_type__icontains=keyword) |
            Q(vendor_type_detailed__icontains=keyword) |
            Q(category__icontains=keyword) |
            Q(category_detailed__icontains=keyword) |
            Q(contact_person_1__icontains=keyword) |
            Q(contact_designation_1__icontains=keyword) |
            Q(contact_person_2__icontains=keyword) |
            Q(contact_designation_2__icontains=keyword) |
            Q(contact_person_3__icontains=keyword) |
            Q(contact_designation_3__icontains=keyword) |
            Q(contact_person_4__icontains=keyword) |
            Q(contact_designation_4__icontains=keyword) |
            Q(trade_license_no__icontains=keyword) |
            Q(tax_registration_number__icontains=keyword) |
            Q(vat_number__icontains=keyword) |
            Q(flag__icontains=keyword),
            comp_code=COMP_CODE
        ).order_by('vendor_code')
    else:
        vendors = VendorMaster.objects.filter(comp_code=COMP_CODE).order_by('vendor_code')
    
    # Get dropdown data for vendor fields
    vendor_type_data = CodeMaster.objects.filter(
        base_type='VENDOR_TYPE', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    vendor_type_detailed_data = CodeMaster.objects.filter(
        base_type='VENDOR_TYPE_DETAILED', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    category_data = CodeMaster.objects.filter(
        base_type='VENDOR_CATEGORY', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    category_detailed_data = CodeMaster.objects.filter(
        base_type='VENDOR_CATEGORY_DETAILED', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    status_data = CodeMaster.objects.filter(
        base_type='VENDOR_STATUS', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    rating_data = CodeMaster.objects.filter(
        base_type='VENDOR_RATING', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    flag_data = CodeMaster.objects.filter(
        base_type='VENDOR_FLAG', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    payment_terms_data = CodeMaster.objects.filter(
        base_type='PAYMENT_TERMS', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    currency_data = CodeMaster.objects.filter(
        base_type='CURRENCY', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    pq_document_data = CodeMaster.objects.filter(
        base_type='PQ_DOCUMENT_STATUS', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    iso_certified_data = CodeMaster.objects.filter(
        base_type='ISO_CERTIFIED_STATUS', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    po_value_limit_data = CodeMaster.objects.filter(
        base_type='PO_VALUE_LIMIT', 
        is_active='Y',
        comp_code=COMP_CODE
    ).order_by('sequence_id')
    
    # Pagination
    paginator = Paginator(vendors, PAGINATION_SIZE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add pagination info to the page object
    page_obj.start_index = (page_obj.number - 1) * paginator.per_page + 1
    page_obj.end_index = min(page_obj.start_index + paginator.per_page - 1, paginator.count)
    
    context = {
        'vendors': page_obj,
        'keyword': keyword,
        'current_url': request.path + '?' + '&'.join([f"{k}={v}" for k, v in request.GET.items() if k != 'page']) + '&' if request.GET else '?',
        'vendor_type_data': vendor_type_data,
        'vendor_type_detailed_data': vendor_type_detailed_data,
        'category_data': category_data,
        'category_detailed_data': category_detailed_data,
        'status_data': status_data,
        'rating_data': rating_data,
        'flag_data': flag_data,
        'payment_terms_data': payment_terms_data,
        'currency_data': currency_data,
        'pq_document_data': pq_document_data,
        'iso_certified_data': iso_certified_data,
        'po_value_limit_data': po_value_limit_data,
    }
    
    return render(request, 'pages/procurement/vendor_master.html', context)

@csrf_exempt
def vendor_master_add(request):
    set_comp_code(request)
    if request.method == 'POST':
        try:
            # Generate vendor code using fn_get_seed_no
            with connection.cursor() as cursor:
                cursor.execute("SELECT fn_get_seed_no(%s, %s, %s);", [COMP_CODE, None, 'ITEM'])
                result = cursor.fetchone()
                vendor_code = result[0] if result else None

            # Handle logo upload
            logo = request.FILES.get('logo')

            # Create new vendor
            vendor = VendorMaster(
                vendor_code=vendor_code,
                vendor_short_code=request.POST.get('vendor_short_code'),
                vendor_name=request.POST.get('vendor_name'),
                logo=logo,
                vendor_type=request.POST.get('vendor_type'),
                vendor_type_detailed=request.POST.get('vendor_type_detailed'),
                category=request.POST.get('category'),
                category_detailed=request.POST.get('category_detailed'),
                contact_person_1=request.POST.get('contact_person_1'),
                contact_designation_1=request.POST.get('contact_designation_1'),
                contact_email_1=request.POST.get('contact_email_1'),
                contact_mobile_1=request.POST.get('contact_mobile_1'),
                contact_tel_1=request.POST.get('contact_tel_1'),
                contact_person_2=request.POST.get('contact_person_2'),
                contact_designation_2=request.POST.get('contact_designation_2'),
                contact_email_2=request.POST.get('contact_email_2'),
                contact_mobile_2=request.POST.get('contact_mobile_2'),
                contact_tel_2=request.POST.get('contact_tel_2'),
                contact_person_3=request.POST.get('contact_person_3'),
                contact_designation_3=request.POST.get('contact_designation_3'),
                contact_email_3=request.POST.get('contact_email_3'),
                contact_mobile_3=request.POST.get('contact_mobile_3'),
                contact_tel_3=request.POST.get('contact_tel_3'),
                contact_person_4=request.POST.get('contact_person_4'),
                contact_designation_4=request.POST.get('contact_designation_4'),
                contact_email_4=request.POST.get('contact_email_4'),
                contact_mobile_4=request.POST.get('contact_mobile_4'),
                contact_tel_4=request.POST.get('contact_tel_4'),
                address=request.POST.get('address'),
                address_branch_office_1=request.POST.get('address_branch_office_1'),
                address_branch_office_2=request.POST.get('address_branch_office_2'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                country=request.POST.get('country'),
                postal_code=request.POST.get('postal_code'),
                trade_license_no=request.POST.get('trade_license_no'),
                trade_license_valid_until=request.POST.get('trade_license_valid_until') or None,
                establishment_year=request.POST.get('establishment_year'),
                tax_registration_number=request.POST.get('tax_registration_number'),
                vat_number=request.POST.get('vat_number'),
                valid_until=request.POST.get('valid_until') or None,
                icv_value=request.POST.get('icv_value'),
                icv_valid_until=request.POST.get('icv_valid_until') or None,
                payment_terms=request.POST.get('payment_terms'),
                credit_limit=request.POST.get('credit_limit'),
                currency=request.POST.get('currency'),
                bank_name=request.POST.get('bank_name'),
                bank_account_number=request.POST.get('bank_account_number'),
                bank_swift_code=request.POST.get('bank_swift_code'),
                bank_iban=request.POST.get('bank_iban'),
                registration_date=request.POST.get('registration_date') or None,
                expiry_date=request.POST.get('expiry_date') or None,
                status=request.POST.get('status', 'Active'),
                rating=request.POST.get('rating'),
                pq_document=request.POST.get('pq_document'),
                iso_9001_certified=request.POST.get('iso_9001_certified'),
                iso_9001_valid_until=request.POST.get('iso_9001_valid_until') or None,
                iso_14001_certified=request.POST.get('iso_14001_certified'),
                iso_14001_valid_until=request.POST.get('iso_14001_valid_until') or None,
                iso_45001_certified=request.POST.get('iso_45001_certified'),
                iso_45001_valid_until=request.POST.get('iso_45001_valid_until') or None,
                po_value_limit=request.POST.get('po_value_limit'),
                flag=request.POST.get('flag'),
                doc_type=request.POST.get('doc_type'),
                remarks=request.POST.get('remarks'),
                is_active=request.POST.get('is_active'),
                created_by=request.user.username,
                comp_code=COMP_CODE,
            )
            vendor.save()

            # Handle document uploads
            document_names = request.POST.getlist('document_name[]')
            document_files = request.FILES.getlist('document_file[]')
            
            for i, (doc_name, doc_file) in enumerate(zip(document_names, document_files)):
                if doc_name and doc_file:
                    VendorDocuments.objects.create(
                        vendor_code=vendor.vendor_code,
                        document_name=doc_name,
                        document_file=doc_file,
                        uploaded_by=request.user.username,
                        comp_code=COMP_CODE
                    )

            return redirect('vendor_master')
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def vendor_master_edit(request):
    set_comp_code(request)
    if request.method == 'GET':
        vendor_id = request.GET.get('id')
        try:
            vendor = VendorMaster.objects.get(id=vendor_id, comp_code=COMP_CODE)
            documents = VendorDocuments.objects.filter(vendor_code=vendor.vendor_code, comp_code=COMP_CODE)
            
            data = {
                'id': vendor.id,
                'vendor_code': vendor.vendor_code,
                'vendor_short_code': vendor.vendor_short_code,
                'vendor_name': vendor.vendor_name,
                'logo': vendor.logo.url if vendor.logo and vendor.logo.name else '',
                'vendor_type': vendor.vendor_type,
                'vendor_type_detailed': vendor.vendor_type_detailed,
                'category': vendor.category,
                'category_detailed': vendor.category_detailed,
                'contact_person_1': vendor.contact_person_1,
                'contact_designation_1': vendor.contact_designation_1,
                'contact_email_1': vendor.contact_email_1,
                'contact_mobile_1': vendor.contact_mobile_1,
                'contact_tel_1': vendor.contact_tel_1,
                'contact_person_2': vendor.contact_person_2,
                'contact_designation_2': vendor.contact_designation_2,
                'contact_email_2': vendor.contact_email_2,
                'contact_mobile_2': vendor.contact_mobile_2,
                'contact_tel_2': vendor.contact_tel_2,
                'contact_person_3': vendor.contact_person_3,
                'contact_designation_3': vendor.contact_designation_3,
                'contact_email_3': vendor.contact_email_3,
                'contact_mobile_3': vendor.contact_mobile_3,
                'contact_tel_3': vendor.contact_tel_3,
                'contact_person_4': vendor.contact_person_4,
                'contact_designation_4': vendor.contact_designation_4,
                'contact_email_4': vendor.contact_email_4,
                'contact_mobile_4': vendor.contact_mobile_4,
                'contact_tel_4': vendor.contact_tel_4,
                'address': vendor.address,
                'address_branch_office_1': vendor.address_branch_office_1,
                'address_branch_office_2': vendor.address_branch_office_2,
                'city': vendor.city,
                'state': vendor.state,
                'country': vendor.country,
                'postal_code': vendor.postal_code,
                'trade_license_no': vendor.trade_license_no,
                'trade_license_valid_until': vendor.trade_license_valid_until.strftime('%Y-%m-%d') if vendor.trade_license_valid_until else '',
                'establishment_year': vendor.establishment_year,
                'tax_registration_number': vendor.tax_registration_number,
                'vat_number': vendor.vat_number,
                'valid_until': vendor.valid_until.strftime('%Y-%m-%d') if vendor.valid_until else '',
                'icv_value': vendor.icv_value,
                'icv_valid_until': vendor.icv_valid_until.strftime('%Y-%m-%d') if vendor.icv_valid_until else '',
                'payment_terms': vendor.payment_terms,
                'credit_limit': vendor.credit_limit,
                'currency': vendor.currency,
                'bank_name': vendor.bank_name,
                'bank_account_number': vendor.bank_account_number,
                'bank_swift_code': vendor.bank_swift_code,
                'bank_iban': vendor.bank_iban,
                'registration_date': vendor.registration_date.strftime('%Y-%m-%d') if vendor.registration_date else '',
                'expiry_date': vendor.expiry_date.strftime('%Y-%m-%d') if vendor.expiry_date else '',
                'status': vendor.status,
                'rating': vendor.rating,
                'pq_document': vendor.pq_document,
                'iso_9001_certified': vendor.iso_9001_certified,
                'iso_9001_valid_until': vendor.iso_9001_valid_until.strftime('%Y-%m-%d') if vendor.iso_9001_valid_until else '',
                'iso_14001_certified': vendor.iso_14001_certified,
                'iso_14001_valid_until': vendor.iso_14001_valid_until.strftime('%Y-%m-%d') if vendor.iso_14001_valid_until else '',
                'iso_45001_certified': vendor.iso_45001_certified,
                'iso_45001_valid_until': vendor.iso_45001_valid_until.strftime('%Y-%m-%d') if vendor.iso_45001_valid_until else '',
                'po_value_limit': vendor.po_value_limit,
                'flag': vendor.flag,
                'doc_type': vendor.doc_type,
                'remarks': vendor.remarks,
                'is_active': vendor.is_active,
                'documents': [{'id': doc.id, 'document_name': doc.document_name, 'document_file': doc.document_file.url} for doc in documents]
            }
            return JsonResponse(data)
        except VendorMaster.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Vendor not found'})
    
    elif request.method == 'POST':
        vendor_id = request.POST.get('id')
        try:
            vendor = VendorMaster.objects.get(id=vendor_id, comp_code=COMP_CODE)
            
            # Handle logo upload
            logo = request.FILES.get('logo')
            if logo:
                vendor.logo = logo

            print(request.POST.get('is_active'))
            # Update vendor fields
            vendor.vendor_short_code = request.POST.get('vendor_short_code')
            vendor.vendor_name = request.POST.get('vendor_name')
            vendor.vendor_type = request.POST.get('vendor_type')
            vendor.vendor_type_detailed = request.POST.get('vendor_type_detailed')
            vendor.category = request.POST.get('category')
            vendor.category_detailed = request.POST.get('category_detailed')
            vendor.contact_person_1 = request.POST.get('contact_person_1')
            vendor.contact_designation_1 = request.POST.get('contact_designation_1')
            vendor.contact_email_1 = request.POST.get('contact_email_1')
            vendor.contact_mobile_1 = request.POST.get('contact_mobile_1')
            vendor.contact_tel_1 = request.POST.get('contact_tel_1')
            vendor.contact_person_2 = request.POST.get('contact_person_2')
            vendor.contact_designation_2 = request.POST.get('contact_designation_2')
            vendor.contact_email_2 = request.POST.get('contact_email_2')
            vendor.contact_mobile_2 = request.POST.get('contact_mobile_2')
            vendor.contact_tel_2 = request.POST.get('contact_tel_2')
            vendor.contact_person_3 = request.POST.get('contact_person_3')
            vendor.contact_designation_3 = request.POST.get('contact_designation_3')
            vendor.contact_email_3 = request.POST.get('contact_email_3')
            vendor.contact_mobile_3 = request.POST.get('contact_mobile_3')
            vendor.contact_tel_3 = request.POST.get('contact_tel_3')
            vendor.contact_person_4 = request.POST.get('contact_person_4')
            vendor.contact_designation_4 = request.POST.get('contact_designation_4')
            vendor.contact_email_4 = request.POST.get('contact_email_4')
            vendor.contact_mobile_4 = request.POST.get('contact_mobile_4')
            vendor.contact_tel_4 = request.POST.get('contact_tel_4')
            vendor.address = request.POST.get('address')
            vendor.address_branch_office_1 = request.POST.get('address_branch_office_1')
            vendor.address_branch_office_2 = request.POST.get('address_branch_office_2')
            vendor.city = request.POST.get('city')
            vendor.state = request.POST.get('state')
            vendor.country = request.POST.get('country')
            vendor.postal_code = request.POST.get('postal_code')
            vendor.trade_license_no = request.POST.get('trade_license_no')
            vendor.trade_license_valid_until = request.POST.get('trade_license_valid_until') or None
            vendor.establishment_year = request.POST.get('establishment_year')
            vendor.tax_registration_number = request.POST.get('tax_registration_number')
            vendor.vat_number = request.POST.get('vat_number')
            vendor.valid_until = request.POST.get('valid_until') or None
            vendor.icv_value = request.POST.get('icv_value')
            vendor.icv_valid_until = request.POST.get('icv_valid_until') or None
            vendor.payment_terms = request.POST.get('payment_terms')
            vendor.credit_limit = request.POST.get('credit_limit')
            vendor.currency = request.POST.get('currency')
            vendor.bank_name = request.POST.get('bank_name')
            vendor.bank_account_number = request.POST.get('bank_account_number')
            vendor.bank_swift_code = request.POST.get('bank_swift_code')
            vendor.bank_iban = request.POST.get('bank_iban')
            vendor.registration_date = request.POST.get('registration_date') or None
            vendor.expiry_date = request.POST.get('expiry_date') or None
            vendor.status = request.POST.get('status', 'Active')
            vendor.rating = request.POST.get('rating')
            vendor.pq_document = request.POST.get('pq_document')
            vendor.iso_9001_certified = request.POST.get('iso_9001_certified')
            vendor.iso_9001_valid_until = request.POST.get('iso_9001_valid_until') or None
            vendor.iso_14001_certified = request.POST.get('iso_14001_certified')
            vendor.iso_14001_valid_until = request.POST.get('iso_14001_valid_until') or None
            vendor.iso_45001_certified = request.POST.get('iso_45001_certified')
            vendor.iso_45001_valid_until = request.POST.get('iso_45001_valid_until') or None
            vendor.po_value_limit = request.POST.get('po_value_limit')
            vendor.flag = request.POST.get('flag')
            vendor.doc_type = request.POST.get('doc_type')
            vendor.remarks = request.POST.get('remarks')
            vendor.is_active = request.POST.get('is_active')
            vendor.updated_by = request.user.username
            vendor.save()

            # Handle document removals
            documents_to_remove = request.POST.get('documents_to_remove', '')
            if documents_to_remove:
                doc_ids = [int(x.strip()) for x in documents_to_remove.split(',') if x.strip()]
                VendorDocuments.objects.filter(id__in=doc_ids, vendor_code=vendor.vendor_code).delete()

            # Handle new document uploads
            document_names = request.POST.getlist('document_name[]')
            document_files = request.FILES.getlist('document_file[]')
            
            for i, (doc_name, doc_file) in enumerate(zip(document_names, document_files)):
                if doc_name and doc_file:
                    VendorDocuments.objects.create(
                        vendor_code=vendor.vendor_code,
                        document_name=doc_name,
                        document_file=doc_file,
                        uploaded_by=request.user.username,
                        comp_code=COMP_CODE
                    )

            return redirect('vendor_master')
        except VendorMaster.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Vendor not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def vendor_master_delete(request):
    set_comp_code(request)
    if request.method == 'POST':
        vendor_id = request.POST.get('id')
        try:
            vendor = VendorMaster.objects.get(id=vendor_id, comp_code=COMP_CODE)
            vendor.delete()
            return JsonResponse({'status': 'success'})
        except VendorMaster.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Vendor not found'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
