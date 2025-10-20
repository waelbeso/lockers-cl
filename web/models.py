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
        """Return a readable representation that works before the object is saved."""

        return f"{self.cell} ({self.code})"
