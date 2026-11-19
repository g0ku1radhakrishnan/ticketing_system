from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from.models import*
from django.http import JsonResponse
from datetime import datetime

# Create your views here.

def login(request):
    if request.method == 'POST':
        uname = request.POST.get('uname')
        password = request.POST.get('pswd')
        try:
            log = Login.objects.get(username=uname, password=password)
            request.session['login_id'] = log.pk

            # Admin Login
            if log.usertype == 'admin':
                return HttpResponse("<script>alert('Login success');window.location='/admin_home';</script>")

            # Cutter Login
            elif log.usertype == 'cutter':
                cut = cutter.objects.get(login_id=log)
                request.session['cutter_id'] = cut.cutter_id
                return HttpResponse("<script>alert('Login success');window.location='/cutter_tailorapp/cutter_home';</script>")

            # Tailor Login (added for completeness)
            elif log.usertype == 'tailor':
                tl = Tailor.objects.get(login_id=log)
                request.session['tailor_id'] = tl.tailor_id
                return HttpResponse("<script>alert('Login success');window.location='/cutter_tailorapp/tailor_home';</script>")

            else:
                return HttpResponse("<script>alert('Invalid role assigned');window.location='/';</script>")

        except Login.DoesNotExist:
            return HttpResponse("<script>alert('Invalid username or password');window.location='/';</script>")
        except Exception:
            return HttpResponse("<script>alert('Profile not found or login failed');window.location='/';</script>")

    return render(request, 'login.html')





# ********ADMIN*********


def admin_home(request):

    # 1. Base Query: Only count jobs that are actively being worked on
    # (Adjust 'delivered' and 'cancelled' if you use different words in your database)
    active_orders = Ticket.objects.filter(status__in=['pending', 'in_progress'])
    
    # 2. Top-Level Statistics
    total_active_count = active_orders.count()

    completed_orders = Ticket.objects.filter(status__in=['completed', 'delivered'])
    completed_count = completed_orders.count()
    total_count = Ticket.objects.all().count()
    
    # Check for 'urgent' (make sure this matches your priority field exactly)
    urgent_tickets = active_orders.filter(priority='urgent').order_by('expected_delivery_date')
    urgent_count = urgent_tickets.count()
    
    # Unassigned: missing a cutter OR missing a tailor
    unassigned_count = active_orders.filter(Q(cutter_id__isnull=True) | Q(tailor_id__isnull=True)).count()
    
    # 3. Department Tracking (USING EXACT DATABASE SPELLING: 'in_progress')
    cutting_pending = active_orders.filter(cutting_status='pending').count()
    cutting_progress = active_orders.filter(cutting_status='in_progress').count() # Fixed underscore
    
    tailoring_pending = active_orders.filter(tailoring_status='pending').count()
    tailoring_progress = active_orders.filter(tailoring_status='in_progress').count() # Fixed underscore
    
    # If you have an alteration_status field:
    # alterations_count = active_orders.filter(alteration_status='in_progress').count()
    
    # 4. Watchlist: The 5 active tickets closest to their delivery date
    watchlist = active_orders.order_by('expected_delivery_date')[:5]

    # 5. Send exact numbers to the template
    context = {
        'total_active_count': total_active_count,
        'urgent_count': urgent_count,
        'urgent_tickets': urgent_tickets,
        'unassigned_count': unassigned_count,
        'completed_count': completed_count,
        'total_count': total_count,
        'cutting_pending': cutting_pending,
        'cutting_progress': cutting_progress,
        'tailoring_pending': tailoring_pending,
        'tailoring_progress': tailoring_progress,
        
        # 'alterations_count': alterations_count,
        'watchlist': watchlist,
    }
    return render(request,'admin_home.html',context)

# 1. Total Orders (Everything in the database)
def admin_total_orders(request):
    tickets = Ticket.objects.all().order_by('-order_date')
    return render(request, 'admin_order_list.html', {
        'tickets': tickets, 
        'page_title': 'Total Orders'
    })

# 2. Active Orders (Everything NOT finished/cancelled)
def admin_active_orders(request):
    # Adjust the words in the list to match your exact database statuses
    tickets = Ticket.objects.filter(status__in=['pending', 'in_progress']).order_by('-order_date')
    return render(request, 'admin_order_list.html', {
        'tickets': tickets, 
        'page_title': 'Active Orders'
    })

# 3. Completed Orders
def admin_completed_orders(request):
    # Adjust this to match how you mark a job fully done
    tickets = Ticket.objects.filter(status__in=['completed', 'delivered']).order_by('-order_date')
    return render(request, 'admin_order_list.html', {
        'tickets': tickets, 
        'page_title': 'Completed Orders'
    })


def admin_urgent_orders(request):
    # Fetch only tickets with 'urgent' priority, ignoring delivered/cancelled if needed
    tickets = Ticket.objects.filter(
        priority='urgent'
    ).exclude(
        status__in=['delivered', 'cancelled','completed']
    ).order_by('-expected_delivery_date')

    return render(request, 'admin_order_list.html', {
        'tickets': tickets, 
        'page_title': 'Urgent Orders'
    })



def admin_search(request):
    # Grab the search term from the URL (e.g., ?q=1234)
    query = request.GET.get('q', '')
    
    if query:
        # Search for matches in Ticket Number, Customer Name, or Customer Phone
        # Adjust 'customer_id__name' and 'customer_id__phone' if your Customer model fields are named differently
        tickets = Ticket.objects.filter(
            Q(ticket_number__icontains=query) | 
            Q(customer_id__name__icontains=query) | 
            Q(customer_id__phone__icontains=query)
        ).order_by('-order_date')
        
        page_title = f"Search Results for '{query}'"
    else:
        tickets = Ticket.objects.none()
        page_title = "Please enter a search term"

    # We reuse your existing admin_order_list.html!
    return render(request, 'admin_order_list.html', {
        'tickets': tickets,
        'page_title': page_title
    })


def admin_manage_tailor(request):
    if request.method == 'POST':
        name     = request.POST.get('name')
        phone    = request.POST.get('phone')
        email    = request.POST.get('email')
        place    = request.POST.get('place')
        age      = request.POST.get('age')
        gender   = request.POST.get('gender')
        username = request.POST.get('uname')
        password = request.POST.get('pswd')


        if len(password) < 6:
            return HttpResponse("<script>alert('Password must be at least 6 characters long.');window.history.back();</script>")


        if Login.objects.filter(username=username).exists():
            return HttpResponse("<script>alert('Username already exists. Please choose another username.');window.history.back();</script>")

        x = Login.objects.create(
            username=username,
            password=password,
            usertype='tailor'
        )

        Tailor.objects.create(
            login_id=x,
            name=name,
            phone=phone,
            email=email,
            place=place,
            age=age,
            gender=gender
        )
        return HttpResponse("<script>alert('Tailor added successfully');window.location='/admin_manage_tailor';</script>")

    tailors = Tailor.objects.all()
    return render(request, 'admin_manage_tailor.html', {'tailors': tailors})

# 1. This view ONLY displays the list of tailors
# def admin_manage_tailor(request):
#     tailors = Tailor.objects.all()
#     return render(request, 'admin_manage_tailor.html', {'tailors': tailors})

# # 2. This view handles the Add form and the database saving
# def admin_add_tailor(request):
#     if request.method == 'POST':
#         name     = request.POST.get('name')
#         phone    = request.POST.get('phone')
#         email    = request.POST.get('email')
#         place    = request.POST.get('place')
#         age      = request.POST.get('age')
#         gender   = request.POST.get('gender')
#         username = request.POST.get('uname')
#         password = request.POST.get('pswd')

#         if len(password) < 6:
#             return HttpResponse("<script>alert('Password must be at least 6 characters long.');window.history.back();</script>")

#         if Login.objects.filter(username=username).exists():
#             return HttpResponse("<script>alert('Username already exists. Please choose another username.');window.history.back();</script>")

#         x = Login.objects.create(
#             username=username,
#             password=password,
#             usertype='tailor'
#         )

#         Tailor.objects.create(
#             login_id=x,
#             name=name,
#             phone=phone,
#             email=email,
#             place=place,
#             age=age,
#             gender=gender
#         )
#         # Note: Redirects back to the list page after successfully saving
#         return HttpResponse("<script>alert('Tailor added successfully');window.location='/admin_manage_tailor';</script>")

#     # If they just clicked the button, load the empty form page
#     return render(request, 'admin_add_tailor.html')
def admin_update_tailor(request, id):
    tailor = Tailor.objects.get(tailor_id=id)

    if request.method == 'POST':
        new_username = request.POST.get('uname')
        new_password=request.POST.get('pswd')

        if len(new_password) < 6:
            return HttpResponse("<script>alert('Password must be at least 6 characters long.');window.history.back();</script>")

        # Check if another record already uses this username
        if Login.objects.filter(username=new_username).exclude(login_id=tailor.login_id.login_id).exists():
            return HttpResponse("<script>alert('Username already exists. Please choose another username.');window.history.back();</script>")
        tailor.name   = request.POST.get('name')
        tailor.phone  = request.POST.get('phone')
        tailor.email  = request.POST.get('email')
        tailor.place  = request.POST.get('place')
        tailor.age    = request.POST.get('age')
        tailor.gender = request.POST.get('gender')
        tailor.save()

        tailor.login_id.username = request.POST.get('uname')
        tailor.login_id.password = request.POST.get('pswd')
        tailor.login_id.save()

        return HttpResponse("<script>alert('Tailor updated successfully');window.location='/admin_manage_tailor';</script>")

    tailors = Tailor.objects.all()
    return render(request, 'admin_manage_tailor.html', {
        'tailors'     : tailors,
        'update_data' : tailor
    })


def admin_delete_tailor(request, id):
    tailor = Tailor.objects.get(tailor_id=id)
    tailor.login_id.delete()  # ✅ deletes login too
    return HttpResponse("<script>alert('Tailor deleted successfully');window.location='/admin_manage_tailor';</script>")




def admin_manage_cutter(request):
    if request.method == 'POST':
        name     = request.POST.get('name')
        phone    = request.POST.get('phone')
        email    = request.POST.get('email')
        place    = request.POST.get('place')
        age      = request.POST.get('age')
        gender   = request.POST.get('gender')
        username = request.POST.get('uname')
        password = request.POST.get('pswd')
        if len(password) < 6:
                    return HttpResponse("<script>alert('Password must be at least 6 characters long.');window.history.back();</script>")
        
        
        if Login.objects.filter(username=username).exists():
                    return HttpResponse("<script>alert('Username already exists. Please choose another username.');window.history.back();</script>")

        


        x = Login.objects.create(
            username=username,
            password=password,
            usertype='cutter'
        )
        

        cutter.objects.create(
            login_id=x,
            name=name,
            phone=phone,
            email=email,
            place=place,
            age=age,
            gender=gender
        )
        return HttpResponse("<script>alert('Cutter added successfully');window.location='/admin_manage_cutter';</script>")

    cutters = cutter.objects.all()
    return render(request, 'admin_manage_cutter.html', {'cutters': cutters})


def admin_update_cutter(request, id):
    cut = cutter.objects.get(cutter_id=id)

    if request.method == 'POST':
        new_username = request.POST.get('uname')
        new_password=request.POST.get('pswd')



        
        if len(new_password) < 6:
            return HttpResponse("<script>alert('Password must be at least 6 characters long.');window.history.back();</script>")

        # Check if another record already uses this username
        if Login.objects.filter(username=new_username).exclude(login_id=tailor.login_id.login_id).exists():
            return HttpResponse("<script>alert('Username already exists. Please choose another username.');window.history.back();</script>")
        cut.name   = request.POST.get('name')
        cut.phone  = request.POST.get('phone')
        cut.email  = request.POST.get('email')
        cut.place  = request.POST.get('place')
        cut.age    = request.POST.get('age')
        cut.gender = request.POST.get('gender')
        cut.save()

        cut.login_id.username = request.POST.get('uname')
        cut.login_id.password = request.POST.get('pswd')
        cut.login_id.save()

        return HttpResponse("<script>alert('Cutter updated successfully');window.location='/admin_manage_cutter';</script>")

    cutters = cutter.objects.all()
    return render(request, 'admin_manage_cutter.html', {
        'cutters'     : cutters,
        'update_data' : cut
    })


def admin_delete_cutter(request, id):
    cut = cutter.objects.get(cutter_id=id)
    cut.login_id.delete()  # ✅ deletes login too
    return HttpResponse("<script>alert('Cutter deleted successfully');window.location='/admin_manage_cutter';</script>")






def admin_manage_customer(request):
    if request.method == 'POST':
        name     = request.POST.get('name')
        phone    = request.POST.get('phone')
        email    = request.POST.get('email')
        place    = request.POST.get('place')
        age      = request.POST.get('age')
        gender   = request.POST.get('gender')
 

        Customer.objects.create(
            # login_id=x,
            name=name,
            phone=phone,
            email=email,
            place=place,
            age=age,
            gender=gender
        )
        return HttpResponse("<script>alert('Customer added successfully');window.location='/admin_manage_customer';</script>")
    search_query = request.GET.get('search', '').strip()
    if search_query:
        # If user selected an item formatted as "Name (Phone)", extract phone/name
        cleaned_query = search_query
        if '(' in search_query and search_query.endswith(')'):
            cleaned_query = search_query.split('(')[-1].replace(')', '').strip()

        customers = Customer.objects.filter(
            Q(name__icontains=cleaned_query) | 
            Q(phone__icontains=cleaned_query) |
            Q(name__icontains=search_query)
        )
    else:
        customers = Customer.objects.all()

    return render(request, 'admin_manage_customer.html', {
        'customers': customers,
        'search_query': search_query
    })

    


def admin_update_customer(request, id):
    customer = Customer.objects.get(Customer_id=id)

    if request.method == 'POST':
        
        
        customer.name   = request.POST.get('name')
        customer.phone  = request.POST.get('phone')
        customer.email  = request.POST.get('email')
        customer.place  = request.POST.get('place')
        customer.age    = request.POST.get('age')
        customer.gender = request.POST.get('gender')
        customer.save()


        return HttpResponse("<script>alert('Customer updated successfully');window.location='/admin_manage_customer';</script>")

    customers = Customer.objects.all()
    return render(request, 'admin_manage_customer.html', {
        'customers'   : customers,
        'update_data' : customer
    })


def admin_delete_customer(request, id):
    customer = Customer.objects.get(Customer_id=id)
    customer.delete()
    return HttpResponse("<script>alert('Customer deleted successfully');window.location='/admin_manage_customer';</script>")

def customer_search_suggestions(request):
    query = request.GET.get('term', '').strip()
    results = []
    
    if query:
        customers = Customer.objects.filter(
            Q(name__icontains=query) | Q(phone__icontains=query)
        )[:10]
        
        for c in customers:
            results.append({
                'id': c.Customer_id,
                'label': f"{c.name} ({c.phone})"
            })
            
    return JsonResponse(results, safe=False)




def admin_manage_ticket(request):
    if request.method == 'POST':
        customer_id_val        = request.POST.get('customer_id')
        measurement_id_val     = request.POST.get('measurement_id')
        cutter_id_val          = request.POST.get('cutter_id')
        tailor_id_val          = request.POST.get('tailor_id')
        garment_type           = request.POST.get('garment_type')
        quantity               = request.POST.get('quantity')
        priority               = request.POST.get('priority', 'normal')
        expected_delivery_date = request.POST.get('expected_delivery_date')
        status                 = request.POST.get('status', 'pending')
        payment_status         = request.POST.get('payment_status', 'unpaid')
        alteration_status      = request.POST.get('alteration_status', 'pending')
        cutting_status         = request.POST.get('cutting_status', 'pending')
        tailoring_status       = request.POST.get('tailoring_status', 'pending')
        # design_image           = request.FILES.get('image')  # <-- Retrieve uploaded file
        notes                  = request.POST.get('notes')
        order_date             = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 1. Generate unique short ticket number
        last_ticket = Ticket.objects.exclude(ticket_number__isnull=True).exclude(ticket_number='').order_by('-ticket_id').first()
        if last_ticket and last_ticket.ticket_number and last_ticket.ticket_number.startswith('TCK-'):
            try:
                last_num = int(last_ticket.ticket_number.split('-')[-1])
                generated_ticket_no = f"TCK-{last_num + 1}"
            except ValueError:
                generated_ticket_no = f"TCK-{last_ticket.ticket_id + 1001}"
        else:
            generated_ticket_no = "TCK-1001"

        # Safe Foreign Key lookup
        customer_obj    = Customer.objects.get(Customer_id=customer_id_val)
        measurement_obj = Measurement.objects.get(measurement_id=measurement_id_val) if measurement_id_val and measurement_id_val.strip() else None
        cutter_obj      = cutter.objects.get(cutter_id=cutter_id_val) if cutter_id_val and cutter_id_val.strip() else None
        tailor_obj      = Tailor.objects.get(tailor_id=tailor_id_val) if tailor_id_val and tailor_id_val.strip() else None

        # 2. Save with ticket_number included
        new_ticket=Ticket.objects.create(
            ticket_number=generated_ticket_no,  # ✅ ADDED THIS LINE
            customer_id=customer_obj,
            measurement_id=measurement_obj,
            cutter_id=cutter_obj,
            tailor_id=tailor_obj,
            garment_type=garment_type,
            quantity=quantity,
            priority=priority,
            order_date=order_date,
            expected_delivery_date=expected_delivery_date,
            status=status,
            # image=design_image,  # <-- Save image
            payment_status=payment_status,
            alteration_status=alteration_status,
            cutting_status=cutting_status,
            tailoring_status=tailoring_status,
            notes=notes
        )
        if 'image' in request.FILES:
            for img in request.FILES.getlist('image'):
                TicketImage.objects.create(ticket=new_ticket, image=img)
        return HttpResponse(f"<script>alert('Ticket created successfully! Ticket No: {generated_ticket_no}');window.location='/admin_manage_ticket';</script>")

    search_query = request.GET.get('search', '').strip()
    if search_query:
        tickets = Ticket.objects.filter(
            Q(ticket_number__icontains=search_query) |
            Q(customer_id__name__icontains=search_query) |
            Q(customer_id__phone__icontains=search_query) |
            Q(garment_type__icontains=search_query) |
            Q(status__icontains=search_query) |
            Q(priority__icontains=search_query)
        )
    else:
        tickets = Ticket.objects.all().order_by('-ticket_id')

    customers    = Customer.objects.all()
    measurements = Measurement.objects.all()
    cutters      = cutter.objects.all()
    tailors      = Tailor.objects.all()

    return render(request, 'admin_manage_ticket.html', {
        'tickets': tickets,
        'customers': customers,
        'measurements': measurements,
        'cutters': cutters,
        'tailors': tailors,
        'search_query': search_query
    })

def admin_update_ticket(request, id):
    ticket = Ticket.objects.get(ticket_id=id)

    if request.method == 'POST':
        customer_id_val    = request.POST.get('customer_id')
        measurement_id_val = request.POST.get('measurement_id')
        cutter_id_val      = request.POST.get('cutter_id')
        tailor_id_val      = request.POST.get('tailor_id')

        # Safe Foreign Key lookup
        ticket.customer_id            = Customer.objects.get(Customer_id=customer_id_val)
        ticket.measurement_id         = Measurement.objects.get(measurement_id=measurement_id_val) if measurement_id_val and measurement_id_val.strip() else None
        ticket.cutter_id              = cutter.objects.get(cutter_id=cutter_id_val) if cutter_id_val and cutter_id_val.strip() else None
        ticket.tailor_id              = Tailor.objects.get(tailor_id=tailor_id_val) if tailor_id_val and tailor_id_val.strip() else None
        ticket.garment_type           = request.POST.get('garment_type')
        ticket.quantity               = request.POST.get('quantity')
        ticket.priority               = request.POST.get('priority')
        ticket.expected_delivery_date = request.POST.get('expected_delivery_date')
        ticket.status                 = request.POST.get('status')
        ticket.payment_status         = request.POST.get('payment_status')
        ticket.alteration_status      = request.POST.get('alteration_status')
        ticket.cutting_status         = request.POST.get('cutting_status')
        ticket.tailoring_status       = request.POST.get('tailoring_status')
        ticket.notes                  = request.POST.get('notes')
# 1. SELECTIVE DELETE: Check if any "Delete" checkboxes were clicked
        images_to_delete = request.POST.getlist('delete_images')
        if images_to_delete:
            # Find those specific images by their ID
            bad_images = TicketImage.objects.filter(id__in=images_to_delete)
            for bad_img in bad_images:
                if bad_img.image:
                    bad_img.image.delete(save=False) # Delete physical file
            bad_images.delete() # Delete from database
            
        # 2. ADD NEW: Simply append any newly uploaded images
        if 'image' in request.FILES:
            for img in request.FILES.getlist('image'):
                TicketImage.objects.create(ticket=ticket, image=img)

        ticket.save()

        return HttpResponse("<script>alert('Ticket updated successfully');window.location='/admin_manage_ticket';</script>")

    tickets      = Ticket.objects.all()
    customers    = Customer.objects.all()
    measurements = Measurement.objects.all()
    cutters      = cutter.objects.all()
    tailors      = Tailor.objects.all()
    existing_images = TicketImage.objects.filter(ticket=ticket)

    return render(request, 'admin_manage_ticket.html', {
        'tickets': tickets,
        'customers': customers,
        'measurements': measurements,
        'cutters': cutters,
        'tailors': tailors,
        'update_data': ticket,
        'existing_images': existing_images,
    })


def admin_delete_ticket(request, id):
    ticket = Ticket.objects.get(ticket_id=id)
    ticket.delete()
    return HttpResponse("<script>alert('Ticket deleted successfully');window.location='/admin_manage_ticket';</script>")



def admin_manage_measurement(request):
    if request.method == 'POST':
        customer_id_val = request.POST.get('customer_id')
        customer_obj    = Customer.objects.get(Customer_id=customer_id_val)

        Measurement.objects.create(
            customer_id=customer_obj,
            length=request.POST.get('length'),
            wide=request.POST.get('wide'),
            shoulder_back=request.POST.get('shoulder_back'),
            shoulder_front=request.POST.get('shoulder_front'),
            wide_back=request.POST.get('wide_back'),
            wide_front=request.POST.get('wide_front'),
            c=request.POST.get('c'),
            b=request.POST.get('b'),
            s=request.POST.get('s'),
            tuck_to_tuck=request.POST.get('tuck_to_tuck'),
            tuck_length=request.POST.get('tuck_length'),
            t_wide=request.POST.get('t_wide'),
            t_point=request.POST.get('t_point'),
            neckdepth_front=request.POST.get('neckdepth_front'),
            neckdepth_back=request.POST.get('neckdepth_back'),
            neckshape_front=request.POST.get('neckshape_front'),
            neckshape_back=request.POST.get('neckshape_back'),
            regal=request.POST.get('regal'),
            muscle=request.POST.get('muscle'),
            sleeve=request.POST.get('sleeve'),
            puff=request.POST.get('puff'),
            description=request.POST.get('description'),
            date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        return HttpResponse("<script>alert('Measurement added successfully');window.location='/admin_manage_measurement';</script>")

    search_query = request.GET.get('search', '').strip()
    if search_query:
        measurements = Measurement.objects.filter(
            Q(customer_id__name__icontains=search_query) |
            Q(customer_id__phone__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    else:
        measurements = Measurement.objects.all()

    customers = Customer.objects.all()
    return render(request, 'admin_manage_measurement.html', {
        'measurements': measurements,
        'customers': customers,
        'search_query': search_query
    })


def admin_update_measurement(request, id):
    measurement = Measurement.objects.get(measurement_id=id)

    if request.method == 'POST':
        customer_id_val = request.POST.get('customer_id')
        measurement.customer_id     = Customer.objects.get(Customer_id=customer_id_val)
        measurement.length          = request.POST.get('length')
        measurement.wide            = request.POST.get('wide')
        measurement.shoulder_back   = request.POST.get('shoulder_back')
        measurement.shoulder_front  = request.POST.get('shoulder_front')
        measurement.wide_back       = request.POST.get('wide_back')
        measurement.wide_front      = request.POST.get('wide_front')
        measurement.c               = request.POST.get('c')
        measurement.b               = request.POST.get('b')
        measurement.s               = request.POST.get('s')
        measurement.tuck_to_tuck    = request.POST.get('tuck_to_tuck')
        measurement.tuck_length     = request.POST.get('tuck_length')
        measurement.t_wide          = request.POST.get('t_wide')
        measurement.t_point         = request.POST.get('t_point')
        measurement.neckdepth_front = request.POST.get('neckdepth_front')
        measurement.neckdepth_back  = request.POST.get('neckdepth_back')
        measurement.neckshape_front = request.POST.get('neckshape_front')
        measurement.neckshape_back  = request.POST.get('neckshape_back')
        measurement.regal           = request.POST.get('regal')
        measurement.muscle          = request.POST.get('muscle')
        measurement.sleeve          = request.POST.get('sleeve')
        measurement.puff            = request.POST.get('puff')
        measurement.description     = request.POST.get('description')
        measurement.save()

        return HttpResponse("<script>alert('Measurement updated successfully');window.location='/admin_manage_measurement';</script>")

    measurements = Measurement.objects.all()
    customers    = Customer.objects.all()
    return render(request, 'admin_manage_measurement.html', {
        'measurements': measurements,
        'customers': customers,
        'update_data': measurement
    })


def admin_delete_measurement(request, id):
    measurement = Measurement.objects.get(measurement_id=id)
    measurement.delete()
    return HttpResponse("<script>alert('Measurement deleted successfully');window.location='/admin_manage_measurement';</script>")



def get_customer_measurements(request):
    customer_id = request.GET.get('customer_id')
    measurements_data = []

    if customer_id and customer_id.strip():
        measurements = Measurement.objects.filter(customer_id_id=customer_id)
        for m in measurements:
            details = []
            if m.length: details.append(f"Len: {m.length}")
            if m.c: details.append(f"C: {m.c}")
            if m.b: details.append(f"B: {m.b}")
            if m.sleeve: details.append(f"Slv: {m.sleeve}")
            
            detail_str = f" ({', '.join(details)})" if details else ""
            label = f"Measurement #{m.measurement_id} - {m.date or ''}{detail_str}"

            measurements_data.append({
                'measurement_id': m.measurement_id,
                'label': label
            })

    return JsonResponse(measurements_data, safe=False)

































