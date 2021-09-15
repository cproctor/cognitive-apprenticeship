from django.db import models

class JournalIssue(models.Model):
    title = models.TextField()
    volume = models.IntegerField()
    number = models.IntegerField()
    introduction = models.TextField()
    date_published = models.DateTimeField(blank=True, null=True)
    manuscripts = models.ManyToManyField('author.Manuscript', related_name='issues', blank=True)
    published = models.BooleanField(default=False)
