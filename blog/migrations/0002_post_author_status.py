# Generated by Django 2.1 on 2020-03-30 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='author_status',
            field=models.CharField(default='anonymous', max_length=30),
        ),
    ]
