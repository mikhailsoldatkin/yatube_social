# Generated by Django 2.2.16 on 2022-02-16 17:03

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('posts', '0003_auto_20220216_2002'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserFollow',
            new_name='Follow',
        ),
    ]
