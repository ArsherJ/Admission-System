# Generated by Django 4.0.1 on 2022-01-29 05:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admissionApp', '0002_remove_applicant_appli_citizen_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicant',
            name='appli_birthday',
            field=models.CharField(max_length=100),
        ),
    ]
