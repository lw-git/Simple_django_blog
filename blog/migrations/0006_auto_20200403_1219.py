# Generated by Django 2.1 on 2020-04-03 07:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20200402_1942'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ['title']},
        ),
    ]
