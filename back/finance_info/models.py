from django.db import models

class FinanceInfo(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class MetalPrice(models.Model):
    METAL_CHOICES = (
        ('gold', '금'),
        ('silver', '은'),
    )
    
    metal_type = models.CharField(max_length=10, choices=METAL_CHOICES)
    date = models.DateField()
    price = models.FloatField()
    
    class Meta:
        unique_together = ('metal_type', 'date')
        ordering = ['date']
    
    def __str__(self):
        return f"{self.get_metal_type_display()} - {self.date}: ${self.price}"