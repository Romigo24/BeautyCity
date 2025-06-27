from django.http import JsonResponse
from .models import Salon, Master, Service, Appointment
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def api_salons(request):
    master_id = request.GET.get('master')
    service_id = request.GET.get('service')
    date = request.GET.get('date')
    qs = Salon.objects.all()
    if master_id:
        qs = qs.filter(masters__id=master_id)
    if service_id:
        qs = qs.filter(masters__services__id=service_id)
    if date:
        qs = qs.filter(salon_appointments__date=date)
    data = [{
        'id': s.id,
        'name': s.name,
        'address': s.address
    } for s in qs.distinct()]
    return JsonResponse(data, safe=False)

@csrf_exempt
def api_masters(request):
    salon_id = request.GET.get('salon')
    service_id = request.GET.get('service')
    date = request.GET.get('date')
    qs = Master.objects.all()
    if salon_id:
        qs = qs.filter(salons__id=salon_id)
    if service_id:
        qs = qs.filter(services__id=service_id)
    if date:
        qs = qs.filter(appointments__date=date)
    data = [{
        'id': m.id,
        'name': m.name
    } for m in qs.distinct()]
    return JsonResponse(data, safe=False)

@csrf_exempt
def api_services(request):
    salon_id = request.GET.get('salon')
    master_id = request.GET.get('master')
    date = request.GET.get('date')
    qs = Service.objects.all()
    if salon_id:
        qs = qs.filter(masters__salons__id=salon_id)
    if master_id:
        qs = qs.filter(masters__id=master_id)
    if date:
        qs = qs.filter(service_appointments__date=date)
    data = [{
        'id': s.id,
        'name': s.name,
        'price': str(s.price) if s.price else None
    } for s in qs.distinct()]
    return JsonResponse(data, safe=False)

@csrf_exempt
def api_timeslots(request):
    salon_id = request.GET.get('salon')
    master_id = request.GET.get('master')
    service_id = request.GET.get('service')
    date = request.GET.get('date')
    all_slots = dict(Appointment.APPOINTMENT_TIME).keys()
    
    # Фильтруем записи, исключая отмененные и консультации
    qs = Appointment.objects.exclude(status__in=['canceled', 'call'])
    
    if salon_id:
        qs = qs.filter(salon_id=salon_id)
    if master_id:
        qs = qs.filter(master_id=master_id)
    if service_id:
        qs = qs.filter(service_id=service_id)
    if date:
        qs = qs.filter(date=date)
    
    # Получаем занятые слоты
    busy_slots = set(qs.values_list('time', flat=True))
    free_slots = [slot for slot in all_slots if slot not in busy_slots]
    
    return JsonResponse({'free_slots': free_slots})

@csrf_exempt
def api_dates(request):
    salon_id = request.GET.get('salon')
    master_id = request.GET.get('master')
    days_ahead = 14
    today = datetime.today().date()
    available_dates = []
    
    for i in range(days_ahead):
        d = today + timedelta(days=i)
        # Фильтруем записи, исключая отмененные и консультации
        qs = Appointment.objects.exclude(status__in=['canceled', 'call'])
        
        if salon_id:
            qs = qs.filter(salon_id=salon_id)
        if master_id:
            qs = qs.filter(master_id=master_id)
        
        busy_slots = set(qs.filter(date=d).values_list('time', flat=True))
        all_slots = set(dict(Appointment.APPOINTMENT_TIME).keys())
        
        if len(busy_slots) < len(all_slots):
            available_dates.append(str(d))
    
    return JsonResponse({'available_dates': available_dates}) 