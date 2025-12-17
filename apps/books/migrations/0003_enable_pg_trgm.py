# Generated migration to enable PostgreSQL extensions

from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_add_search_vector'),
    ]

    operations = [
        # Enable pg_trgm extension for trigram similarity search
        TrigramExtension(),
    ]
