# Generated by Django 3.2.6 on 2021-09-20 01:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0010_alter_journalissue_published'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='journalissue',
            options={'ordering': ('-volume', '-number')},
        ),
    ]
