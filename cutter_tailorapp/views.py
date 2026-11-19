from django.shortcuts import render
from ticketing_app.models import*
from django.http import HttpResponse


# Create your views here.

# ***********CUTTER*************
def cutter_home(request):   
    if 'cutter_id' not in request.session:
        return HttpResponse("<script>alert('Please login');window.location='/login';</script>")
    
    current_cutter = cutter.objects.get(cutter_id=request.session['cutter_id'])
    
    # Get quick stats for the dashboard
    available_count = Ticket.objects.filter(cutter_id__isnull=True, cutting_status='pending').count()
    my_jobs_count = Ticket.objects.filter(cutter_id=current_cutter).count()
    completed_jobs_count = Ticket.objects.filter(cutter_id=current_cutter, cutting_status='completed').count()

    return render(request, 'cutter_home.html', {
        'cutter': current_cutter,
        'available_count': available_count,
        'my_jobs_count': my_jobs_count,
        'completed_jobs_count': completed_jobs_count

    })




# 2. View Available Tickets (Job Pool)
def cutter_available_jobs(request):
    if 'cutter_id' not in request.session:
        return HttpResponse("<script>alert('Please login');window.location='/login';</script>")
    
    available_tickets = Ticket.objects.filter(cutter_id__isnull=True, cutting_status='pending').order_by('-ticket_id')
    return render(request, 'cutter_available_jobs.html', {'available_tickets': available_tickets})

# 3. View Claimed Tickets (My Jobs)
def cutter_my_jobs(request):
    if 'cutter_id' not in request.session:
        return HttpResponse("<script>alert('Please login');window.location='/login';</script>")
    
    current_cutter = cutter.objects.get(cutter_id=request.session['cutter_id'])
    my_tickets = Ticket.objects.filter(cutter_id=current_cutter).order_by('-ticket_id')
    
    return render(request, 'cutter_my_jobs.html', {'my_tickets': my_tickets})
def cutter_completed_jobs(request):
    if 'cutter_id' not in request.session:
        return HttpResponse("<script>alert('Please login');window.location='/login';</script>")
    
    # Get the logged-in cutter
    current_cutter = cutter.objects.get(cutter_id=request.session['cutter_id'])
    
    # Fetch all tickets where this cutter is assigned AND cutting_status is 'completed'
    completed_tickets = Ticket.objects.filter(
        cutter_id=current_cutter, 
        cutting_status='completed'
    ).order_by('-order_date')  # Orders by newest first

    return render(request, 'cutter_completed_jobs.html', {
        'cutter': current_cutter,
        'tickets': completed_tickets
    })

     


def claim_ticket(request, id):
    # Security check
    if 'cutter_id' not in request.session:
        return HttpResponse("<script>alert('Please login first');window.location='/login';</script>")
    
    # 1. Find the specific ticket using the ID from the URL
    ticket = Ticket.objects.get(ticket_id=id)
    
    # 2. Get the currently logged-in cutter
    current_cutter = cutter.objects.get(cutter_id=request.session['cutter_id'])
    
    # 3. Assign the cutter to the ticket and save
    ticket.cutter_id = current_cutter
    ticket.save()
    
    # 4. Redirect them to their "My Jobs" page after claiming
    # Change 'cutter_tailorapp' below to 'workers' if your main urls.py uses 'workers/'
    return HttpResponse("<script>alert('Job claimed successfully!');window.location='/cutter_tailorapp/cutter_my_jobs/';</script>")



def update_cutting_status(request, id):
    if 'cutter_id' not in request.session:
        return HttpResponse("<script>alert('Please login first');window.location='/login';</script>")
    
    if request.method == 'POST':
        new_status = request.POST.get('cutting_status')
        ticket = Ticket.objects.get(ticket_id=id)
        
        # Verify this cutter actually owns this ticket before updating
        if ticket.cutter_id.cutter_id == request.session['cutter_id']:
            ticket.cutting_status = new_status
            
            # Optional: If cutting is done, you might want to automatically set tailoring to pending
            if new_status == 'completed':
                ticket.tailoring_status = 'pending'
                
            ticket.save()
            return HttpResponse("<script>alert('Status updated successfully!');window.location='/cutter_tailorapp/cutter_my_jobs/';</script>")
        else:
            return HttpResponse("<script>alert('Unauthorized access');window.location='/cutter_tailorapp/cutter_my_jobs/';</script>")

# ***********Tailor***************



#  Dashboard
def tailor_home(request):
    if 'tailor_id' not in request.session:

        return HttpResponse("<script>alert('Please login as tailor');window.location='/login';</script>")
    
    current_tailor = Tailor.objects.get(tailor_id=request.session['tailor_id'])
    
    # Available = Cutting is finished, but no tailor assigned yet
    available_count = Ticket.objects.filter(
        tailor_id__isnull=True, 
        cutting_status='completed',
        tailoring_status='pending'
    ).count()
    
    my_jobs_count = Ticket.objects.filter(tailor_id=current_tailor).count()
    
    # NEW: Completed jobs count
    completed_jobs_count = Ticket.objects.filter(
        tailor_id=current_tailor, 
        tailoring_status='completed'
    ).count()

    return render(request, 'tailor_home.html', {
        'tailor': current_tailor,
        'available_count': available_count,
        'my_jobs_count': my_jobs_count,
        'completed_jobs_count': completed_jobs_count # Passed to dashboard
    })

def tailor_completed_jobs(request):
    if 'tailor_id' not in request.session:
        return HttpResponse("<script>alert('Please login as tailor');window.location='/login';</script>")
    
    # Get the logged-in tailor
    current_tailor = Tailor.objects.get(tailor_id=request.session['tailor_id'])
    
    # Fetch all tickets where this tailor is assigned AND tailoring_status is 'completed'
    completed_tickets = Ticket.objects.filter(
        tailor_id=current_tailor, 
        tailoring_status='completed'
        ).order_by('-order_date')  # Orders by newest first

    return render(request, 'tailor_completed_jobs.html', {
        'tailor': current_tailor,
        'tickets': completed_tickets
    })
# 2. View Available Tickets
def tailor_available_jobs(request):
    if 'tailor_id' not in request.session:
        return HttpResponse("<script>alert('Please login as tailor');window.location='/login';</script>")
    
    available_tickets = Ticket.objects.filter(
        tailor_id__isnull=True, 
        cutting_status='completed', 
        tailoring_status='pending'
    ).order_by('-ticket_id')
    
    return render(request, 'tailor_available_jobs.html', {'available_tickets': available_tickets})

# 3. View Claimed Tickets
def tailor_my_jobs(request):
    if 'tailor_id' not in request.session:
        return HttpResponse("<script>alert('Please login');window.location='/login';</script>")
    
    current_tailor = Tailor.objects.get(tailor_id=request.session['tailor_id'])
    my_tickets = Ticket.objects.filter(tailor_id=current_tailor).order_by('-ticket_id')
    
    return render(request, 'tailor_my_jobs.html', {'my_tickets': my_tickets})

# 4. Claim a Ticket
def tailor_claim_ticket(request, id):
    if 'tailor_id' not in request.session:
        return HttpResponse("<script>alert('Please login');window.location='/login';</script>")
    
    ticket = Ticket.objects.get(ticket_id=id)
    current_tailor = Tailor.objects.get(tailor_id=request.session['tailor_id'])
    
    ticket.tailor_id = current_tailor
    ticket.save()
    
    return HttpResponse("<script>alert('Job claimed successfully!');window.location='/cutter_tailorapp/tailor_my_jobs/';</script>")

# 5. Update Status
def update_tailoring_status(request, id):
    if 'tailor_id' not in request.session:
        return HttpResponse("<script>alert('Please login');window.location='/login';</script>")
    
    if request.method == 'POST':
        new_status = request.POST.get('tailoring_status')
        ticket = Ticket.objects.get(ticket_id=id)
        
        if ticket.tailor_id.tailor_id == request.session['tailor_id']:
            ticket.tailoring_status = new_status
            
            # AUTOMATIC STATUS SYNC LOGIC
            if new_status == 'completed':
                # Once the tailor is done, the entire garment is finished!
                ticket.status = 'completed' 
                
            ticket.save()
            return HttpResponse("<script>alert('Status updated!');window.location='/cutter_tailorapp/tailor_home/';</script>")

