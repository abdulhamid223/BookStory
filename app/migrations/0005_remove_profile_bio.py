from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_profile"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="bio",
        ),
    ]
