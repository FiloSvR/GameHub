# Generated by Django 2.0 on 2018-01-18 14:46

from django.db import migrations, models
import game.models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0024_auto_20180107_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='gamethumb',
            field=models.ImageField(blank=True, null=True, upload_to=game.models.user_directory_path),
        ),
    ]