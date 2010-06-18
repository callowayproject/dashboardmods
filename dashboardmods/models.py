from django.db import models

class RSSDashboardModule(models.Model):
    """
    Each item is an RSS feed that will become an available Dashboard module
    """
    
    title = models.CharField(max_length=100)
    feed = models.URLField(verify_exists=False)
    limit = models.IntegerField('Number of items', default=5, help_text="The latest number of articles that should appear in the list")
    
    class Meta:
        pass

    def __unicode__(self):
        return self.feed

