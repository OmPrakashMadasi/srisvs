# Generated by Django 5.1 on 2024-08-26 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0011_rename_date_testimonial_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testimonial',
            name='customer_rating',
            field=models.PositiveSmallIntegerField(),
        ),
        migrations.AlterField(
            model_name='testimonial',
            name='customer_review',
            field=models.TextField(),
        ),
    ]
