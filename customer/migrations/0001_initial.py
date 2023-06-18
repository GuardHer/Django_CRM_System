# Generated by Django 3.2.9 on 2023-06-12 15:24

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('khno', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=20)),
                ('area', models.CharField(max_length=20)),
                ('cusManager', models.CharField(db_column='cus_manager', max_length=30)),
                ('level', models.CharField(max_length=30)),
                ('myd', models.CharField(max_length=30)),
                ('xyd', models.CharField(max_length=30)),
                ('address', models.CharField(max_length=100)),
                ('postCode', models.CharField(db_column='post_code', max_length=10)),
                ('phone', models.CharField(max_length=18)),
                ('fax', models.CharField(max_length=20)),
                ('website', models.CharField(db_column='web_site', max_length=50)),
                ('yyzzzch', models.CharField(max_length=50)),
                ('fr', models.CharField(max_length=20)),
                ('zczj', models.CharField(max_length=20)),
                ('nyye', models.CharField(max_length=20)),
                ('khyh', models.CharField(max_length=20)),
                ('khzh', models.CharField(max_length=20)),
                ('dsdjh', models.CharField(max_length=20)),
                ('gsdjh', models.CharField(max_length=20)),
                ('state', models.IntegerField(default=0)),
                ('isValid', models.IntegerField(db_column='is_valid', default=1)),
                ('createDate', models.DateTimeField(auto_now_add=True, db_column='create_date')),
                ('updateDate', models.DateTimeField(auto_now_add=True, db_column='update_date')),
            ],
            options={
                'db_table': 't_customer',
            },
            managers=[
                ('all', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='CustomerLoss',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cusNo', models.CharField(db_column='cus_no', max_length=40)),
                ('cusName', models.CharField(db_column='cus_name', max_length=20)),
                ('cusManager', models.CharField(db_column='cus_manager', max_length=20)),
                ('lastOrderTime', models.DateTimeField(db_column='last_order_time')),
                ('confirmLossTime', models.DateTimeField(db_column='confirm_loss_time')),
                ('state', models.IntegerField()),
                ('lossReason', models.CharField(db_column='loss_reason', max_length=1000)),
                ('isValid', models.IntegerField(db_column='is_valid', default=1)),
                ('createDate', models.DateTimeField(auto_now_add=True, db_column='create_date')),
                ('updateDate', models.DateTimeField(auto_now_add=True, db_column='update_date')),
            ],
            options={
                'db_table': 't_customer_loss',
            },
        ),
        migrations.CreateModel(
            name='CustomerOrders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('orderNo', models.DateTimeField(db_column='order_no')),
                ('orderDate', models.DateTimeField(auto_now_add=True, db_column='order_date')),
                ('address', models.CharField(db_column='address', max_length=120)),
                ('totalPrice', models.FloatField(db_column='total_price')),
                ('state', models.IntegerField(choices=[(0, '未回款'), (1, '已回款')])),
                ('isValid', models.IntegerField(db_column='is_valid')),
                ('createDate', models.DateTimeField(auto_now_add=True, db_column='create_date')),
                ('updateDate', models.DateTimeField(auto_now_add=True, db_column='update_date')),
                ('customer', models.ForeignKey(db_column='cus_id', on_delete=django.db.models.deletion.DO_NOTHING, to='customer.customer')),
            ],
            options={
                'db_table': 't_customer_order',
            },
        ),
        migrations.CreateModel(
            name='LinkMan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cusId', models.IntegerField(db_column='cus_id')),
                ('linkName', models.CharField(db_column='link_name', max_length=20)),
                ('sex', models.CharField(max_length=4)),
                ('zhiwei', models.CharField(db_column='zhiwei', max_length=20)),
                ('officePhone', models.CharField(db_column='office_phone', max_length=20)),
                ('phone', models.CharField(db_column='phone', max_length=20)),
                ('isValid', models.IntegerField(db_column='is_valid', default=1)),
                ('createDate', models.DateTimeField(auto_now_add=True, db_column='create_date')),
                ('updateDate', models.DateTimeField(auto_now_add=True, db_column='update_date')),
            ],
            options={
                'db_table': 't_customer_linkman',
            },
        ),
        migrations.CreateModel(
            name='OrdersDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('goodsName', models.CharField(db_column='goods_name', max_length=100)),
                ('goodsNum', models.IntegerField(db_column='goods_num')),
                ('unit', models.CharField(db_column='unit', max_length=10)),
                ('price', models.FloatField(db_column='price')),
                ('sum', models.FloatField(db_column='sum')),
                ('isValid', models.IntegerField(db_column='is_valid')),
                ('createDate', models.DateTimeField(auto_now_add=True, db_column='create_date')),
                ('updateDate', models.DateTimeField(auto_now_add=True, db_column='update_date')),
                ('order', models.ForeignKey(db_column='order_id', on_delete=django.db.models.deletion.DO_NOTHING, to='customer.customerorders')),
            ],
            options={
                'db_table': 't_order_details',
            },
        ),
        migrations.CreateModel(
            name='CustomerReprieve',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measure', models.CharField(db_column='measure', max_length=1000)),
                ('isValid', models.IntegerField(db_column='is_valid', default=1)),
                ('createDate', models.DateTimeField(auto_now_add=True, db_column='create_date')),
                ('updateDate', models.DateTimeField(auto_now_add=True, db_column='update_date')),
                ('customerLoss', models.ForeignKey(db_column='loss_id', db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='customer.customerloss')),
            ],
            options={
                'db_table': 't_customer_reprieve',
            },
        ),
    ]
