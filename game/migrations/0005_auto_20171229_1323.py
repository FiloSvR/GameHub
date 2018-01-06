# Generated by Django 2.0 on 2017-12-29 13:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_merge_20171229_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='price',
            field=models.DecimalField(decimal_places=2, default=20.5, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='game',
            name='name',
            field=models.TextField(max_length=300),
        ),
    ]
