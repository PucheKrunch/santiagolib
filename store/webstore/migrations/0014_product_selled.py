# Generated by Django 3.2.6 on 2021-10-16 20:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webstore', '0013_auto_20211016_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='selled',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
