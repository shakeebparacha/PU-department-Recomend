from django.db import models


class MeritData(models.Model):
    """Model to store merit program data"""
    faculty = models.CharField(max_length=255)
    program = models.CharField(max_length=255)
    merit_percentage = models.FloatField()
    campus = models.CharField(max_length=255)
    semester = models.CharField(max_length=50)
    year = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "Merit Data"
        ordering = ['faculty', 'merit_percentage']
    
    def __str__(self):
        return f"{self.program} - {self.merit_percentage}%"
