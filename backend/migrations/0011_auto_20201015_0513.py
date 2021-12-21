# Generated by Django 3.1.1 on 2020-10-15 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0010_auto_20201013_1813'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('created_date',)},
        ),
        migrations.AlterModelOptions(
            name='orderitem',
            options={'ordering': ('created_date',)},
        ),
        migrations.AddField(
            model_name='orderitem',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
