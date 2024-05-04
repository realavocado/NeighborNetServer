# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Friend(models.Model):
    auto_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey('UsersCustomuser', models.DO_NOTHING, db_column='uid', related_name='friend_uid_set', blank=True, null=True)
    fid = models.ForeignKey('UsersCustomuser', models.DO_NOTHING, db_column='fid', related_name='friend_fid_set', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'friend'
        

class Friendrequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    requester = models.ForeignKey('UsersCustomuser', models.DO_NOTHING, related_name='requester', blank=True, null=True)
    receiver = models.ForeignKey('UsersCustomuser', models.DO_NOTHING, related_name='receiver', blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    request_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'friendrequest'


class Neighbor(models.Model):
    auto_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey('UsersCustomuser', models.DO_NOTHING, db_column='uid', related_name='neighbor_uid_set', blank=True, null=True)
    nid = models.ForeignKey('UsersCustomuser', models.DO_NOTHING, db_column='nid', related_name='neighbor_nid_set', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'neighbor'

class UsersCustomuser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, max_length=254, verbose_name='email address')
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    bio = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users_customuser'