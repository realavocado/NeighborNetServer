# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Block(models.Model):
    bid = models.AutoField(primary_key=True)
    block_name = models.CharField(max_length=100, blank=True, null=True)
    hid = models.ForeignKey('Hood', models.DO_NOTHING, db_column='hid', blank=True, null=True)
    center_latitude = models.FloatField(blank=True, null=True)
    center_longitude = models.FloatField(blank=True, null=True)
    radius = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'block'


class BlockUserStatusChange(models.Model):
    auto_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey('UsersCustomuser', models.DO_NOTHING, db_column='uid', blank=True, null=True)
    bid = models.ForeignKey(Block, models.DO_NOTHING, db_column='bid', blank=True, null=True)
    status = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'block_user_status_change'


class Blockjoinapprove(models.Model):
    auto_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey('UsersCustomuser', models.DO_NOTHING, db_column='uid', related_name='uid', blank=True, null=True)
    bid = models.ForeignKey(Block, models.DO_NOTHING, db_column='bid', blank=True, null=True)
    approve_uid = models.ForeignKey('UsersCustomuser', models.DO_NOTHING, db_column='approve_uid', related_name='approve_uid',blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'blockjoinapprove'


class Hood(models.Model):
    hid = models.AutoField(primary_key=True)
    hood_name = models.CharField(max_length=100, blank=True, null=True)
    center_latitude = models.FloatField(blank=True, null=True)
    center_longitude = models.FloatField(blank=True, null=True)
    radius = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hood'



class UserFollowBlock(models.Model):
    auto_id = models.AutoField(primary_key=True)
    bid = models.ForeignKey(Block, models.DO_NOTHING, db_column='bid', blank=True, null=True)
    uid = models.ForeignKey('UsersCustomuser', models.DO_NOTHING, db_column='uid', blank=True, null=True)
    date_followed = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_follow_block'


class UserInBlock(models.Model):
    auto_id = models.AutoField(primary_key=True)
    bid = models.ForeignKey(Block, models.DO_NOTHING, db_column='bid', blank=True, null=True)
    uid = models.ForeignKey('UsersCustomuser', models.DO_NOTHING, db_column='uid', blank=True, null=True)
    date_joined = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'user_in_block'


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
