# Generated by Django 3.2.6 on 2021-10-17 01:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webstore', '0019_rename_product_order_item'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='publisher',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
