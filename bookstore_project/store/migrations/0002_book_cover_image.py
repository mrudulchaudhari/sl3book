# Generated by Django 5.2 on 2025-04-25 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='book_covers/'),
        ),
    ]
