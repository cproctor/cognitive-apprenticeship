# Generated by Django 3.2.6 on 2021-08-06 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0002_manuscriptauthorship_deleted'),
    ]

    operations = [
        migrations.RenameField(
            model_name='revision',
            old_name='date_closed',
            new_name='date_decided',
        ),
        migrations.RemoveField(
            model_name='manuscriptauthorship',
            name='deleted',
        ),
        migrations.AddField(
            model_name='manuscript',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
    ]
