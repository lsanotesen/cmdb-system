import json
import os
import uuid
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import OfficePart

# ==================== 办公机配件管理 ====================

@login_required
def office_parts_list(request):
    """办公机配件列表页面"""
    parts = OfficePart.objects.all().order_by('-created_at')
    
    # 搜索和筛选
    search_keyword = request.GET.get('keyword', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    health_filter = request.GET.get('health', '')
    
    if search_keyword:
        parts = parts.filter(
            Q(name__icontains=search_keyword) |
            Q(brand__icontains=search_keyword) |
            Q(model__icontains=search_keyword) |
            Q(serial_number__icontains=search_keyword) |
            Q(source_computer__icontains=search_keyword)
        )
    
    if category_filter:
        parts = parts.filter(category=category_filter)
    
    if status_filter:
        parts = parts.filter(status=status_filter)
    
    if health_filter:
        parts = parts.filter(health_status=health_filter)
    
    context = {
        'parts': parts,
        'search_keyword': search_keyword,
        'category_filter': category_filter,
        'status_filter': status_filter,
        'health_filter': health_filter,
        'categories': OfficePart.CATEGORY_CHOICES,
        'statuses': OfficePart.STATUS_CHOICES,
        'health_statuses': OfficePart.HEALTH_CHOICES,
    }
    return render(request, 'cmdb/office_parts/list.html', context)


@login_required
def office_part_add(request):
    """添加办公机配件"""
    if request.method == 'POST':
        try:
            part = OfficePart()
            part.name = request.POST.get('name')
            part.category = request.POST.get('category', 'other')
            part.brand = request.POST.get('brand', '')
            part.model = request.POST.get('model', '')
            part.serial_number = request.POST.get('serial_number') or None
            part.source_computer = request.POST.get('source_computer', '')
            part.status = request.POST.get('status', 'in_stock')
            part.health_status = request.POST.get('health_status', 'not_tested')
            part.health_percentage = request.POST.get('health_percentage') or None
            part.smart_remark = request.POST.get('smart_remark', '')
            part.power_on_hours = request.POST.get('power_on_hours') or None
            part.bad_sector_remark = request.POST.get('bad_sector_remark', '')
            part.location = request.POST.get('location', '')
            part.purchase_date = request.POST.get('purchase_date') or None
            part.remark = request.POST.get('remark', '')
            
            # 处理图片上传 - 按年月日创建目录
            if request.FILES.getlist('images'):
                images = request.FILES.getlist('images')
                image_paths = []
                import datetime
                date_dir = datetime.datetime.now().strftime('%Y%m%d')
                for img in images:
                    filename = f"{uuid.uuid4()}_{img.name}"
                    filepath = os.path.join(settings.MEDIA_ROOT, 'spareparts', date_dir, filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    with open(filepath, 'wb+') as destination:
                        for chunk in img.chunks():
                            destination.write(chunk)
                    image_paths.append(f"/media/spareparts/{date_dir}/{filename}")
                
                # 更新图片字段
                if image_paths:
                    part.images = json.dumps(image_paths)
            
            part.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': '只支持POST请求'})


@login_required
def office_part_edit(request, part_id):
    """编辑办公机配件"""
    if request.method == 'GET':
        try:
            part = OfficePart.objects.get(id=part_id)
            return JsonResponse({
                'success': True,
                'data': {
                    'id': part.id,
                    'name': part.name,
                    'category': part.category,
                    'brand': part.brand,
                    'model': part.model,
                    'serial_number': part.serial_number or '',
                    'source_computer': part.source_computer,
                    'status': part.status,
                    'health_status': part.health_status,
                    'health_percentage': part.health_percentage,
                    'smart_remark': part.smart_remark,
                    'power_on_hours': part.power_on_hours,
                    'bad_sector_remark': part.bad_sector_remark,
                    'location': part.location,
                    'purchase_date': part.purchase_date.strftime('%Y-%m-%d') if part.purchase_date else '',
                    'remark': part.remark,
                }
            })
        except OfficePart.DoesNotExist:
            return JsonResponse({'success': False, 'error': '配件不存在'})
    elif request.method == 'POST':
        try:
            part = OfficePart.objects.get(id=part_id)
            part.name = request.POST.get('name')
            part.category = request.POST.get('category', 'other')
            part.brand = request.POST.get('brand', '')
            part.model = request.POST.get('model', '')
            part.serial_number = request.POST.get('serial_number') or None
            part.source_computer = request.POST.get('source_computer', '')
            part.status = request.POST.get('status', 'in_stock')
            part.health_status = request.POST.get('health_status', 'not_tested')
            part.health_percentage = request.POST.get('health_percentage') or None
            part.smart_remark = request.POST.get('smart_remark', '')
            part.power_on_hours = request.POST.get('power_on_hours') or None
            part.bad_sector_remark = request.POST.get('bad_sector_remark', '')
            part.location = request.POST.get('location', '')
            part.purchase_date = request.POST.get('purchase_date') or None
            part.remark = request.POST.get('remark', '')
            
            # 处理图片上传 - 按年月日创建目录
            # 获取剩余的现有图片路径
            remaining_images = []
            if request.POST.get('remaining_images'):
                try:
                    remaining_images = json.loads(request.POST.get('remaining_images'))
                except:
                    pass
            
            # 处理新上传的图片
            new_image_paths = []
            if request.FILES.getlist('images'):
                images = request.FILES.getlist('images')
                import datetime
                date_dir = datetime.datetime.now().strftime('%Y%m%d')
                for img in images:
                    filename = f"{uuid.uuid4()}_{img.name}"
                    filepath = os.path.join(settings.MEDIA_ROOT, 'spareparts', date_dir, filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    with open(filepath, 'wb+') as destination:
                        for chunk in img.chunks():
                            destination.write(chunk)
                    new_image_paths.append(f"/media/spareparts/{date_dir}/{filename}")
            
            # 合并剩余图片和新上传的图片
            all_images = remaining_images + new_image_paths
            if all_images:
                part.images = json.dumps(all_images)
            else:
                part.images = ''
            
            part.save()
            return JsonResponse({'success': True})
        except OfficePart.DoesNotExist:
            return JsonResponse({'success': False, 'error': '配件不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': '只支持GET和POST请求'})


@login_required
def office_part_delete(request, part_id):
    """删除办公机配件"""
    if request.method == 'POST':
        try:
            part = OfficePart.objects.get(id=part_id)
            part.delete()
            return JsonResponse({'success': True})
        except OfficePart.DoesNotExist:
            return JsonResponse({'success': False, 'error': '配件不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': '只支持POST请求'})


@login_required
def office_part_update_status(request):
    """更新配件状态"""
    if request.method == 'POST':
        try:
            part_id = request.POST.get('part_id')
            new_status = request.POST.get('status')
            
            part = OfficePart.objects.get(id=part_id)
            part.status = new_status
            part.save()
            return JsonResponse({'success': True})
        except OfficePart.DoesNotExist:
            return JsonResponse({'success': False, 'error': '配件不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': '只支持POST请求'})