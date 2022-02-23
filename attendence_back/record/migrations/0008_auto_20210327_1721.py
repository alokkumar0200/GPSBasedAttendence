# Generated by Django 3.1.7 on 2021-03-27 11:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('record', '0007_employee_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='is_admin',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='organisation',
            name='logo',
            field=models.ImageField(default='defaultLogo.jpg', upload_to='logos'),
        ),
    ]
