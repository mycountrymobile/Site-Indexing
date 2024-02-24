from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    
    
class SiteInfo(models.Model):
    url = models.URLField()
    is_indexed = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE) 
    
    def __str__(self):
        return f"{self.project}"