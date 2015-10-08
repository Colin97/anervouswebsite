from django.db import models

class Admin(models.Model):
    username = models.CharField(max_length=20, primary_key=True)
    password = models.CharField(max_length=32)
    def __unicode__(self):
        return self.username


class OfficialAccount(models.Model):
    name = models.CharField(max_length=40)
    def __unicode__(self):
        return self.name


class Application(models.Model):
    official_account = models.OneToOneField(OfficialAccount, primary_key=True)
    user_submit = models.CharField(max_length=32)
    operator_admin = models.CharField(max_length=32)
    status = models.CharField(max_length=10)
    manager_name = models.CharField(max_length=30)
    manager_student_id = models.IntegerField
    manager_dept = models.CharField(max_length=40)
    manager_tel = models.CharField(max_length=20)
    manager_email = models.CharField(max_length=254)
    def __unicode__(self):
        return "Application for %s from user %s, status: %s" % (
            self.official_account,
            self.user_submit,
            self.status
        )
