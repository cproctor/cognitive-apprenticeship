# Generated by Django 3.2.6 on 2021-08-06 16:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0003_auto_20210806_1626'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reviewer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManuscriptReviewer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('manuscript', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='author.manuscript')),
                ('reviewer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
