# Generated by Django 4.1.2 on 2024-03-20 09:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0003_topic_files_alter_topic_title'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='topic',
            name='files',
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='uploads/')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='rooms.topic')),
            ],
        ),
    ]
