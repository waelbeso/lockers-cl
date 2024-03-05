from django.db import models

# Create your models here.
class Cell(models.Model):
    '''
    Cell Key
    '''
    id        = models.AutoField(primary_key=True)
    cell      = models.TextField()
    code      = models.TextField()
    used      = models.BooleanField(default=False)

    def __str__(self):
        return self.id