# Generated by Django 3.2.6 on 2021-08-17 02:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviewer', '0002_manuscriptreviewer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='date_submitted',
            field=models.DateTimeField(null=True),
        ),
    ]
