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
    block_name = models.CharField(blank=True, null=True)
    hid = models.ForeignKey('Hood', models.DO_NOTHING, db_column='hid', blank=True, null=True)
    center_latitude = models.FloatField(blank=True, null=True)
    center_longitude = models.FloatField(blank=True, null=True)
    radius = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'block'


class BlockUserStatusChange(models.Model):
    auto_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid', blank=True, null=True)
    bid = models.ForeignKey(Block, models.DO_NOTHING, db_column='bid', blank=True, null=True)
    status = models.CharField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'block_user_status_change'


class BlockJoinApprove(models.Model):
    auto_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid', blank=True, null=True)
    bid = models.ForeignKey(Block, models.DO_NOTHING, db_column='bid', blank=True, null=True)
    approve_uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='approve_uid', related_name='blockjoinapprove_approve_uid_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'blockjoinapprove'


class Friend(models.Model):
    auto_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid', blank=True, null=True)
    fid = models.ForeignKey('Users', models.DO_NOTHING, db_column='fid', related_name='friend_fid_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'friend'


class FriendRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    requester = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    receiver = models.ForeignKey('Users', models.DO_NOTHING, related_name='friendrequest_receiver_set', blank=True, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    request_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'friendrequest'


class Hood(models.Model):
    hid = models.AutoField(primary_key=True)
    hood_name = models.CharField(blank=True, null=True)
    center_latitude = models.FloatField(blank=True, null=True)
    center_longitude = models.FloatField(blank=True, null=True)
    radius = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hood'


class Message(models.Model):
    mid = models.AutoField(primary_key=True)
    author = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    tid = models.ForeignKey('Thread', models.DO_NOTHING, db_column='tid', blank=True, null=True)
    reply_to_mid = models.ForeignKey('self', models.DO_NOTHING, db_column='reply_to_mid', blank=True, null=True)
    title = models.CharField(blank=True, null=True)
    text = models.CharField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'message'


class Neighbor(models.Model):
    auto_id = models.AutoField(primary_key=True)
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid', blank=True, null=True)
    nid = models.ForeignKey('Users', models.DO_NOTHING, db_column='nid', related_name='neighbor_nid_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'neighbor'


class Review(models.Model):
    auto_id = models.AutoField(primary_key=True)
    mid = models.ForeignKey(Message, models.DO_NOTHING, db_column='mid', blank=True, null=True)
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid', blank=True, null=True)
    status = models.CharField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'review'


class Thread(models.Model):
    tid = models.AutoField(primary_key=True)
    topic = models.CharField(blank=True, null=True)
    subject = models.CharField(blank=True, null=True)
    author_id = models.IntegerField(blank=True, null=True)
    visibility = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'thread'


class ThreadVisibleToBlock(models.Model):
    tid = models.OneToOneField(Thread, models.DO_NOTHING, db_column='tid', primary_key=True)
    bid = models.ForeignKey(Block, models.DO_NOTHING, db_column='bid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'threadvisibletoblock'


class ThreadVisibleToHood(models.Model):
    tid = models.OneToOneField(Thread, models.DO_NOTHING, db_column='tid', primary_key=True)
    hid = models.ForeignKey(Hood, models.DO_NOTHING, db_column='hid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'threadvisibletohood'


class ThreadVisibleToUser(models.Model):
    tid = models.OneToOneField(Thread, models.DO_NOTHING, db_column='tid', primary_key=True)
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'threadvisibletouser'


class UserFollowBlock(models.Model):
    auto_id = models.AutoField(primary_key=True)
    bid = models.ForeignKey(Block, models.DO_NOTHING, db_column='bid', blank=True, null=True)
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid', blank=True, null=True)
    date_followed = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_follow_block'


class UserInBlock(models.Model):
    auto_id = models.AutoField(primary_key=True)
    bid = models.ForeignKey(Block, models.DO_NOTHING, db_column='bid', blank=True, null=True)
    uid = models.ForeignKey('Users', models.DO_NOTHING, db_column='uid', blank=True, null=True)
    date_joined = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_in_block'


class Users(models.Model):
    uid = models.AutoField(primary_key=True)
    name = models.CharField(blank=True, null=True)
    email = models.CharField(unique=True, blank=True, null=True)
    password = models.CharField(blank=True, null=True)
    address = models.CharField(blank=True, null=True)
    image_url = models.CharField(blank=True, null=True)
    bio = models.CharField(blank=True, null=True)
    last_access_timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
