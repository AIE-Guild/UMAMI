from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.SlugField(max_length=64, unique=True, verbose_name='name')),
                ('service',
                 models.CharField(choices=[('discord', 'Discord'), ('battle_net_us', 'Battle.net US')], max_length=64,
                                  verbose_name='service')),
                ('enabled', models.BooleanField(default=True, verbose_name='enabled')),
                ('client_id', models.CharField(max_length=191, verbose_name='client id')),
                ('client_secret', models.CharField(max_length=191, verbose_name='client secret')),
                ('scope_override', models.TextField(blank=True, default='', verbose_name='scope override')),
            ],
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('resource_id', models.CharField(blank=True, default='', max_length=64, verbose_name='resource ID')),
                ('resource_tag', models.CharField(blank=True, default='', max_length=64, verbose_name='resource tag')),
                ('token_type', models.CharField(default='bearer', max_length=64, verbose_name='token type')),
                ('access_token', models.TextField(verbose_name='access token')),
                ('refresh_token', models.TextField(blank=True, default='', verbose_name='refresh token')),
                ('expiry', models.DateTimeField(blank=True, null=True, verbose_name='expiry')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='oauth2.Client',
                                             verbose_name='client')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL,
                                           verbose_name='user')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='token',
            unique_together={('user', 'client', 'resource_id')},
        ),
    ]
