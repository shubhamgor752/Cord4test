# Generated by Django 4.2.10 on 2024-07-02 08:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Register', '0005_remove_customuser_profile_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='NameChoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_choice', models.CharField(choices=[('SHUBHAM', 'shubham'), ('GOR', 'gor')], max_length=220)),
            ],
        ),
    ]
