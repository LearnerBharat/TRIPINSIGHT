from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('app', '0011_alter_placemode_description'),
    ]

    operations = [
        # Update Profile model
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='auth.user'),
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='you_City',
            new_name='city',
        ),
        migrations.RenameField(
            model_name='profile',
            old_name='you_State',
            new_name='state',
        ),
        migrations.AddField(
            model_name='profile',
            name='trophies',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        
        # Remove ProfileModel
        migrations.DeleteModel(
            name='ProfileModel',
        ),
    ]