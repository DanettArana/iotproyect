# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monitoreo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dato',
            name='raw_payload',
            field=models.TextField(blank=True, null=True),
        ),
    ]

