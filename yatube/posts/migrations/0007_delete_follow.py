# Generated by Django 2.2.16 on 2022-02-16 17:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_follow'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Follow',
        ),
    ]
