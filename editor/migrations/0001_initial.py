# Generated by Django 3.2.6 on 2021-09-15 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('author', '0005_alter_manuscriptauthorship_manuscript'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalIssue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('introduction', models.TextField()),
                ('date_published', models.DateTimeField(blank=True, null=True)),
                ('published', models.BooleanField(default=False)),
                ('manuscripts', models.ManyToManyField(related_name='issues', to='author.Manuscript')),
            ],
        ),
    ]
