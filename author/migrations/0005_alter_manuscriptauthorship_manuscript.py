# Generated by Django 3.2.6 on 2021-08-30 00:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0004_auto_20210806_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manuscriptauthorship',
            name='manuscript',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authorships', to='author.manuscript'),
        ),
    ]