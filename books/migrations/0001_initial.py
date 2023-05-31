# Generated by Django 4.2.1 on 2023-05-30 03:06

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BeancountDirective',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meta', models.JSONField(null=True)),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('users', models.ManyToManyField(related_name='books', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to='books.book')),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='books.book')),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='currencies', to='books.book')),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('open_date', models.DateField()),
                ('close_date', models.DateField(null=True)),
                ('booking', models.CharField(choices=[('ST', 'STRICT'), ('NO', 'NONE'), ('AV', 'AVERAGE'), ('FI', 'FIFO'), ('LI', 'LIFO'), ('HI', 'HIFO')], default=None, max_length=2, null=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accounts', to='books.book')),
                ('currencies', models.ManyToManyField(to='books.currency')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('beancountdirective_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='books.beancountdirective')),
                ('flag', models.CharField(max_length=255, null=True)),
                ('payee', models.CharField(max_length=255, null=True)),
                ('narration', models.CharField(max_length=255)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='books.book')),
                ('links', models.ManyToManyField(to='books.link')),
                ('tags', models.ManyToManyField(related_name='tags', to='books.tag')),
            ],
            bases=('books.beancountdirective',),
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('beancountdirective_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='books.beancountdirective')),
                ('amount', models.CharField(max_length=255)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='books.book')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.currency')),
            ],
            bases=('books.beancountdirective',),
        ),
        migrations.CreateModel(
            name='Posting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('units', models.CharField(max_length=255)),
                ('cost', models.CharField(max_length=255, null=True)),
                ('cost_spec', models.CharField(max_length=255, null=True)),
                ('price', models.CharField(max_length=255, null=True)),
                ('flag', models.CharField(max_length=255, null=True)),
                ('meta', models.JSONField(null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.account')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='postings', to='books.book')),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='postings', to='books.transaction')),
            ],
        ),
        migrations.CreateModel(
            name='Pad',
            fields=[
                ('beancountdirective_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='books.beancountdirective')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.account')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pads', to='books.book')),
                ('source_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pad_source_account_set', to='books.account')),
            ],
            bases=('books.beancountdirective',),
        ),
        migrations.CreateModel(
            name='Open',
            fields=[
                ('beancountdirective_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='books.beancountdirective')),
                ('booking', models.CharField(choices=[('ST', 'STRICT'), ('NO', 'NONE'), ('AV', 'AVERAGE'), ('FI', 'FIFO'), ('LI', 'LIFO'), ('HI', 'HIFO')], default=None, max_length=2, null=True)),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='books.account')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='opens', to='books.book')),
                ('currencies', models.ManyToManyField(to='books.currency')),
            ],
            bases=('books.beancountdirective',),
        ),
        migrations.CreateModel(
            name='Commodity',
            fields=[
                ('beancountdirective_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='books.beancountdirective')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commodities', to='books.book')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.currency')),
            ],
            bases=('books.beancountdirective',),
        ),
        migrations.CreateModel(
            name='Close',
            fields=[
                ('beancountdirective_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='books.beancountdirective')),
                ('account', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='books.account')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='closes', to='books.book')),
            ],
            bases=('books.beancountdirective',),
        ),
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('beancountdirective_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='books.beancountdirective')),
                ('amount', models.CharField(max_length=255)),
                ('tolerance', models.FloatField(null=True)),
                ('diff_amount', models.CharField(max_length=255, null=True)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.account')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balances', to='books.book')),
            ],
            bases=('books.beancountdirective',),
        ),
    ]
