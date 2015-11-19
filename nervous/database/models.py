# -*- coding: utf-8 -*-

from django.db import models

# Enums

class SortOrder:
    Ascending, Descending = xrange(2)


class SortBy:
    Time, Likes, Views = xrange(3)


class MessageCategory:
    All, ToStudent, ToAdmin = xrange(3)


class ForewarnTarget:
    ViewsTotal, LikesTotal = xrange(2)


class NotificationOption:
    Message, Email = xrange(2)

# Models

class Admin(models.Model):
    username = models.CharField(max_length=20, primary_key=True)
    description = models.CharField(max_length=100, null=True)
    password = models.CharField(max_length=32)
    email = models.CharField(max_length=254)

    def __unicode__(self):
        return "%s: %s" % (self.username, self.description)


class Student(models.Model):
    student_id = models.IntegerField(primary_key=True)
    real_name = models.CharField(max_length=20)
    dept = models.CharField(max_length=40)
    tel = models.CharField(max_length=20)
    email = models.CharField(max_length=254)

    def information_filled(self):
        return self.real_name != ""

    def __unicode__(self):
        return "%s(%s)" % (self.student_id, self.real_name)


class OfficialAccount(models.Model):
    wx_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=300)

    def unprocessed_messages_count(self):
        return self.message_set.filter(processed__exact=False).count()

    def __unicode__(self):
        return "%s(%s)" % (self.name, self.wx_id)


class AccountRecord(models.Model):
    account = models.ForeignKey(OfficialAccount)
    date = models.DateField()
    articles = models.IntegerField()
    likes = models.IntegerField()
    views = models.IntegerField()

    def __unicode__(self):
        return "%s at %s" % (self.account.name, self.date)


class Application(models.Model):
    official_account = models.OneToOneField(OfficialAccount, primary_key=True)
    user_submit = models.CharField(max_length=32)
    operator_admin = models.CharField(max_length=32)
    status = models.CharField(max_length=10)
    manager_name = models.CharField(max_length=30)
    manager_student_id = models.CharField(max_length=15)
    manager_dept = models.CharField(max_length=40)
    manager_tel = models.CharField(max_length=20)
    manager_email = models.CharField(max_length=254)
    association = models.CharField(max_length=30)

    def __unicode__(self):
        return u"Application for %s from user %s, status: %s" % (
            self.official_account,
            self.user_submit,
            self.status
        )


class Article(models.Model):
    title = models.CharField(max_length=50)
    official_account_id = models.IntegerField()
    description = models.CharField(max_length=300, default='')
    avatar_url = models.CharField(max_length=300, default='')
    url = models.CharField(max_length=300, unique=True)
    likes = models.IntegerField()
    views = models.IntegerField()
    posttime = models.DateTimeField()

    def official_account_name(self):
        return OfficialAccount.objects.get(pk=self.official_account_id).name

    def __unicode__(self):
        return self.title


class Message(models.Model):
    official_account = models.ForeignKey(OfficialAccount)
    category = models.IntegerField()  # value should come from MessageCategory
    title = models.CharField(max_length=30)
    content = models.CharField(max_length=140)
    processed = models.BooleanField()
    admin = models.ForeignKey(Admin, null=True)
    time = models.DateTimeField(auto_now_add=True)

    def from_real_name(self):
        if self.category == MessageCategory.ToAdmin:
            return self.official_account.user_submit()
        else:
            try:
                return self.admin.description
            except:
                return "unknown admin"

    def datetime(self):
        return self.time

    def __unicode__(self):
        if self.category == MessageCategory.ToAdmin:
            direction = 'from'
        else:
            direction = 'to'
        return "%s under account %s %s %s, processed = %s" % (
            self.title,
            self.official_account.name,
            direction,
            self.official_account.application.user_submit,
            self.processed
        )


class ForewarnRule(models.Model):
    account = models.ForeignKey(OfficialAccount, null=True)
    duration = models.IntegerField()
    notification = models.IntegerField()
    target = models.IntegerField()
    value = models.IntegerField()

    def account_name(self):
        if self.account:
            return self.account.name
        else:
            return u'所有公众号'

    def __unicode__(self):
        return u"[%s, %s] for %s" % (
            self.target,
            self.value,
            self.account_name()
        )


class ForewarnRecord(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    account = models.ForeignKey(OfficialAccount)
    target = models.IntegerField()
    value = models.IntegerField()

    def account_name(self):
        return self.account.name

    def __unicode__(self):
        return u'[%s, %s] by %s at %s' % (
            self.target,
            self.value,
            self.account_name(),
            self.datetime
        )


# Add delegating attributes

def add_delegate(cls, dest, key):
    def inner_delegate(self):
        return getattr(getattr(self, dest), key)

    setattr(cls, key, inner_delegate)


for attr in [
    'manager_name',
    'manager_student_id',
    'manager_dept',
    'manager_tel',
    'manager_email',
    'association',
    'user_submit',
]:
    add_delegate(OfficialAccount, 'application', attr)

for attr in ['id', 'name', 'description']:
    add_delegate(Application, 'official_account', attr)
