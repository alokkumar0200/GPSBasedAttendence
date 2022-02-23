# from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User
# from django.utils.crypto import get_random_string
# Create your models here.


class organisation(models.Model):
	loc = models.PointField()
	logo = models.ImageField(upload_to='logos', default='defaultLogo.jpg')
	distanceReq = models.IntegerField(default=100)
	orgAddr = models.CharField(max_length=1000, default='address')
	orgName = models.CharField(max_length=100, default='org name')
	orgContact = models.CharField(max_length=13, default='0000000000')
	expiration = models.DateField(null=True)
	status = models.BooleanField(default=True)
	half_day = models.CharField(default='10:15', max_length=5)
	leave = models.CharField(default='15:00', max_length=5)
	punchOutTime = models.CharField(default='19:00', max_length=5)
	totalEmp = models.IntegerField(default=20)
	def __str__(self):
		return self.orgName


class employee(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	for_org = models.ForeignKey(organisation, on_delete=models.CASCADE)
	empName = models.CharField(default='emp name', max_length=50)
	photo = models.ImageField(upload_to='profile', default='defaultProfile.jpg')
	contact = models.CharField(default='0000000000', max_length=13)
	designation = models.CharField(default='designation', max_length=50)
	imei = models.CharField(default='x', max_length=200)
	loc = models.PointField()
	is_admin = models.BooleanField(default=False)

	def __str__(self):
		return self.empName


class attendence(models.Model):
	for_org = models.ForeignKey(organisation, on_delete=models.CASCADE)
	for_emp = models.ForeignKey(employee, on_delete=models.CASCADE)
	date = models.DateField(null=True)
	loginTime = models.CharField(default='null', max_length=5)
	logoutTime = models.CharField(default='null', max_length=5)
	status = models.CharField(default='halfday', max_length=20)

	def __str__(self):
		return self.for_emp.empName


class announcement(models.Model):
	for_org = models.ForeignKey(organisation, on_delete=models.CASCADE)
	date = models.DateField(auto_now=True)
	txt = models.CharField(default='announcement', max_length=5000)

	def __str__(self):
		return self.txt


class attendenceReq(models.Model):
	for_org = models.ForeignKey(organisation, on_delete=models.CASCADE, null=False)
	for_att = models.ForeignKey(attendence, on_delete=models.CASCADE)
	stat= models.BooleanField(default=False)

	def ___str__(self):
		return self.for_att.for_emp.empName


class personalMsg(models.Model):
	for_emp = models.ForeignKey(employee, on_delete=models.CASCADE)
	message = models.CharField(default='', max_length=5000)
	date = models.DateField(auto_now=True)

	def __str__(self):
		return self.message