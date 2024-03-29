# Generated by Django 2.2.6 on 2019-10-18 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Friends',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('person_user_name', models.CharField(max_length=30)),
                ('friend_user_name', models.CharField(max_length=30)),
            ],
            options={
                'unique_together': {('person_user_name', 'friend_user_name')},
            },
        ),
    ]
