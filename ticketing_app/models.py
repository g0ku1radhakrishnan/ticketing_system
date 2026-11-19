
from django.db import models

# Create your models here.
class Login(models.Model):
    login_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    usertype = models.CharField(max_length=255)


class Tailor(models.Model):
    tailor_id       = models.AutoField(primary_key=True)
    login_id      = models.ForeignKey(Login, on_delete=models.CASCADE)
    name          = models.CharField(max_length=255)
    phone         = models.CharField(max_length=255)
    email         = models.CharField(max_length=255)
    place         = models.CharField(max_length=255)
    age           = models.CharField(max_length=255)
    gender        = models.CharField(max_length=255)



class cutter(models.Model):
    cutter_id       = models.AutoField(primary_key=True)
    login_id      = models.ForeignKey(Login, on_delete=models.CASCADE)
    name          = models.CharField(max_length=255)
    phone         = models.CharField(max_length=255)
    email         = models.CharField(max_length=255)
    place         = models.CharField(max_length=255)
    age           = models.CharField(max_length=255)
    gender        = models.CharField(max_length=255)

class Receptionist(models.Model):
    receptionist_id       = models.AutoField(primary_key=True)
    login_id      = models.ForeignKey(Login, on_delete=models.CASCADE)
    name          = models.CharField(max_length=255)
    phone         = models.CharField(max_length=255)
    email         = models.CharField(max_length=255)
    place         = models.CharField(max_length=255)
    age           = models.CharField(max_length=255)
    gender        = models.CharField(max_length=255)

class Customer(models.Model):
    Customer_id       = models.AutoField(primary_key=True)
    name          = models.CharField(max_length=255)
    phone         = models.CharField(max_length=255)
    email         = models.CharField(max_length=255)
    place         = models.CharField(max_length=255)
    age           = models.CharField(max_length=255)
    gender        = models.CharField(max_length=255)

class Measurement(models.Model):
    measurement_id           = models.AutoField(primary_key=True)
    customer_id       = models.ForeignKey(Customer, on_delete=models.CASCADE)
    length            = models.CharField(max_length=255, null=True, blank=True)
    wide              = models.CharField(max_length=255, null=True, blank=True)
    shoulder_back     = models.CharField(max_length=255, null=True, blank=True)
    shoulder_front    = models.CharField(max_length=255, null=True, blank=True)
    wide_back         = models.CharField(max_length=255, null=True, blank=True)
    wide_front        = models.CharField(max_length=255, null=True, blank=True)
    c                 = models.CharField(max_length=255, null=True, blank=True)
    b                 = models.CharField(max_length=255, null=True, blank=True)
    s                 = models.CharField(max_length=255, null=True, blank=True)
    tuck_to_tuck      = models.CharField(max_length=255, null=True, blank=True)
    tuck_length       = models.CharField(max_length=255, null=True, blank=True)
    t_wide            = models.CharField(max_length=255, null=True, blank=True)
    t_point           = models.CharField(max_length=255, null=True, blank=True)
    neckdepth_front   = models.CharField(max_length=255, null=True, blank=True)
    neckdepth_back    = models.CharField(max_length=255, null=True, blank=True)
    neckshape_front   = models.CharField(max_length=255, null=True, blank=True)
    neckshape_back    = models.CharField(max_length=255, null=True, blank=True)
    regal             = models.CharField(max_length=255, null=True, blank=True)
    muscle            = models.CharField(max_length=255, null=True, blank=True)
    sleeve            = models.CharField(max_length=255, null=True, blank=True)
    puff              = models.CharField(max_length=255, null=True, blank=True)
    description       = models.TextField(null=True, blank=True)
    date              = models.CharField(max_length=255, null=True, blank=True)
    
class Ticket(models.Model):
    ticket_id              = models.AutoField(primary_key=True)
    ticket_number          = models.CharField(max_length=255, unique=True, null=True, blank=True)  # <-- Added
    customer_id            = models.ForeignKey(Customer, on_delete=models.CASCADE)
    measurement_id         = models.ForeignKey(Measurement, on_delete=models.CASCADE, null=True, blank=True)
    cutter_id              = models.ForeignKey(cutter, on_delete=models.CASCADE, null=True, blank=True)
    tailor_id              = models.ForeignKey(Tailor, on_delete=models.CASCADE, null=True, blank=True)
    garment_type           = models.CharField(max_length=255)
    quantity               = models.CharField(max_length=255)
    priority               = models.CharField(max_length=255, default='normal')
    # priority: 'low', 'normal', 'high', 'urgent'
    order_date             = models.CharField(max_length=255)
    expected_delivery_date = models.CharField(max_length=255)
    status                 = models.CharField(max_length=255, default='pending')
    # status: 'pending', 'in progress', 'completed', 'delivered', 'cancelled'
    payment_status         = models.CharField(max_length=255, default='unpaid')
    # payment_status: 'unpaid', 'partial', 'paid'
    alteration_status      = models.CharField(max_length=255, default='pending')
    # alteration_status: 'pending', 'in progress', 'completed', 'not required'
    cutting_status         = models.CharField(max_length=255, default='pending')
    # cutting_status: 'pending', 'in progress', 'completed'
    tailoring_status       = models.CharField(max_length=255, default='pending')
    # tailoring_status: 'pending', 'in progress', 'completed'
    notes                  = models.TextField(null=True, blank=True)

class TicketImage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='images')
    image = models.FileField(upload_to='ticket_designs/')