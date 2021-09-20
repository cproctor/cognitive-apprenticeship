from django.db import models

class JournalIssue(models.Model):
    title = models.CharField(max_length=200)
    volume = models.IntegerField()
    number = models.IntegerField()
    introduction = models.TextField()
    date_published = models.DateTimeField(blank=True, null=True)
    manuscripts = models.ManyToManyField('author.Manuscript', related_name='issues', blank=True)
    published = models.BooleanField(default=False, blank=True)

    def __str__(self):
        return "{} (Vol {}, Number {})".format(self.title, self.volume, self.number)

    class Meta:
        ordering = ('-volume', '-number')
