from django.db import models

# Create your models here.
class Pick(models.Model):
    '''
    Pick parcels
    '''
    id        = models.AutoField(primary_key=True)
    mobile    = models.IntegerField()
    code      = models.IntegerField()

    def __str__(self):
        return self.id

class Drop(models.Model):
    '''
    Drop parcels
    '''
    id        = models.AutoField(primary_key=True)
    number    = models.IntegerField()
    code      = models.IntegerField()
    
    def __str__(self):
        return self.id