from django.db import models

# Create your models here.

class Invoices(models.Model):
    
    InvoiceId = models.AutoField(primary_key=True)
    