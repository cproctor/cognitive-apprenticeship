# Generated by Django 3.2.6 on 2021-08-07 02:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='is_teacher',
            new_name='is_editor',
        ),
    ]
