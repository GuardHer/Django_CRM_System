# Generated by Django 3.2.9 on 2023-06-14 18:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tuser',
            name='createDate',
            field=models.DateTimeField(db_column='create_date', default=datetime.datetime(2023, 6, 14, 18, 38, 20, 656605)),
        ),
    ]