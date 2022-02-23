from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.gis.db.models.functions import Distance
from django.http import JsonResponse
from django.contrib.gis.geos import Point
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.decorators import permission_classes#,api_view
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import *
from datetime import date, datetime
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError


def validate_loc(x,y):
	retval = True
	try:
		if x != None and x.strip() !='' and float(x) and y != None and y.strip() !='' and float(y):
			pass
		else:
			retval = False
	except:
		retval = False
	return retval


def validate_time(tm):
	retval = False
	try:
		t1 = tm.split(':')
		if t1[0] != None and t1[0].strip() !='' and t1[1] != None and t1[1].strip() !='' and int(t1[0])>=0 and int(t1[1])>=0:
			retval=True
	except:
		retval=False
	return True


class checkLogin(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		user = request.user
		return JsonResponse({'detail':user.username})


class loginAPI(APIView):
	permission_classes = (AllowAny,)
	# @csrf_exempt
	def post(self, request):
		context={}
		username = request.data.get("username")
		password = request.data.get("password")
		if username is None or password is None:
			return Response({'data': 'Please provide both username and password','status':'failure'},
		                status=HTTP_400_BAD_REQUEST)
		user = authenticate(username=username, password=password)
		context['status'] = 'true'
		if not user:
			context['data']= 'Invalid Credentials'
			context['status'] = 'failure'
			return JsonResponse(context, status=401)
		token, _ = Token.objects.get_or_create(user=user)
		context['data']=token.key
		return JsonResponse(context)


class checkStatus(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		user = request.user
		message=''
		currDate = str(date.today().year)+'-'+str(date.today().month)+'-'+str(date.today().day)
		if employee.objects.filter(user=user).exists():
			empO = employee.objects.get(user=user)
			empOrg = empO.for_org
			if attendence.objects.filter(for_emp=empO, date=currDate, for_org=empOrg).exists():
				attO = attendence.objects.get(for_emp=empO, date=currDate, for_org=empOrg)
				if attO.loginTime != 'null' and attO.logoutTime=='null':
					message = 'true'
				else:
					message='false'
			else:
				message='false'
		else:
			message='false'
		return JsonResponse({'message':message})


class get_message(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self,request):
		context={}
		# print(loc_x,loc_y)
		l=[]
		if employee.objects.filter(user=request.user).exists():
			emp = employee.objects.get(user=request.user)
			personalMsgO = personalMsg.objects.filter(for_emp=emp)
			for x in personalMsgO:
				l.append({'message':x.message, 'date':x.date})
			context['data']=l
			return JsonResponse(context, status=200)
		else:
			context['message']='error'
			return JsonResponse(context, status=401)


class update_loc(APIView):
	permission_classes = (IsAuthenticated,)

	def post(self,request):
		loc_x = request.data.get('x')
		loc_y = request.data.get('y')
		imeiR = request.data.get('imei')
		context = {}
		print(loc_x,loc_y)
		if employee.objects.filter(user=request.user).exists():
			emp = employee.objects.get(user=request.user)
			if validate_loc(loc_x, loc_y) and imeiR != '' and imeiR != None:
				empLoc = Point(float(loc_y), float(loc_x))
				user = request.user
				emp.loc = empLoc
				emp.save()
				context['message']='done'
				return JsonResponse(context, status=200)
			else:
				return JsonResponse({'message':'error'}, status=401)
		else:
			context['message']='error'
			return JsonResponse(context, status=401)
		


class mark_attendence(APIView):
	permission_classes = (IsAuthenticated,)

	def post(self,request):
		loc_x = request.data.get('x')
		loc_y = request.data.get('y')
		imeiR = request.data.get('imei')
		message = ''
		print(loc_x,loc_y)
		if validate_loc(loc_x, loc_y) and imeiR != '' and imeiR != None:
			empLoc = Point(float(loc_y), float(loc_x))
			user = request.user
			if employee.objects.filter(user=user).exists():
				empO = employee.objects.get(user=user)
				empOrg = empO.for_org
				imei = empO.imei

				cT = datetime.now().time()
				halfDayTime = datetime.strptime(empOrg.half_day,'%H:%M').time()
				leaveTime = datetime.strptime(empOrg.leave,'%H:%M').time()
				punchOutTime = datetime.strptime(empOrg.punchOutTime,'%H:%M').time()

				currDate = str(date.today().year)+'-'+str(date.today().month)+'-'+str(date.today().day)
				currTime = str(cT.hour)+':'+str(cT.minute)

				attO,_ = attendence.objects.get_or_create(for_emp=empO, date=currDate, for_org=empOrg)
				# print(empOrg.loc.distance(empLoc))
				# print(empOrg.distanceReq)
				if imei==imeiR or imei=='x':
					if imei == 'x':
						empO.imei = imeiR
						empO.save()
					if attO.loginTime == 'null' and empOrg.loc.distance(empLoc)*100000 <= empOrg.distanceReq:
						
						attO.loginTime = currTime
						attO.date = currDate

						if cT>halfDayTime and cT<leaveTime:
							attO.status='halfday'
						elif cT > leaveTime and cT > halfDayTime:
							attO.status = 'leave'
						else:
							attO.status = 'present'

						attO.save()
						message = 'ok'
					elif attO.logoutTime == 'null' and empOrg.loc.distance(empLoc)*100000 <= empOrg.distanceReq:
						attO.logoutTime = currTime
						if punchOutTime > cT and attO.status!='leave':
							attO.status = 'halfday'
						
						attO.save()
						message = 'ok'
					else:
						message = 'errors'
				else:
					message='imei'
			else:
				message='error1'
		else:
			message = 'error1'
		return JsonResponse({'message':message})


class reqAttendenceChange(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		message = ''
		user = request.user
		if employee.objects.filter(user=user).exists():
			empO = employee.objects.get(user=user)
			empOrg = empO.for_org
			currDate = str(date.today().year)+'-'+str(date.today().month)+'-'+str(date.today().day)
			if attendence.objects.filter(for_emp=empO, date=currDate, for_org=empOrg).exists():
				print(9)
				attO = attendence.objects.get(for_emp=empO, date=currDate, for_org=empOrg)
				if attO.status != 'present':# and attendenceReq.objects.filter(for_att=attO).exists():
					reqO,_ = attendenceReq.objects.get_or_create(for_org=empOrg, for_att=attO)
					reqO.stat=True
					reqO.save()
					message = 'done'
				else:
					message='error'
			else:
				message='error'
		else:
			message='error'
		return JsonResponse({'message':message})


class checkRequest(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		message = ''
		user = request.user
		if employee.objects.filter(user=user).exists():
			empO = employee.objects.get(user=user)
			empOrg = empO.for_org
			currDate = str(date.today().year)+'-'+str(date.today().month)+'-'+str(date.today().day)
			if attendence.objects.filter(for_emp=empO, date=currDate, for_org=empOrg).exists():
				attO = attendence.objects.get(for_emp=empO, date=currDate, for_org=empOrg)
				if attendenceReq.objects.filter(for_att=attO).exists():
					req = attendenceReq.objects.get(for_att=attO)
					if req.stat == True:
						message = 'requested'
					else:
						message = 'not'
				else:
					message='error'
			else:
				message='not'
		else:
			message='not'
		# attO.delete()
		return JsonResponse({'message':message})


class getTodayAttendence(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		message = ''
		user = request.user
		if employee.objects.filter(user=user).exists():
			empO = employee.objects.get(user=user)
			empOrg = empO.for_org
			currDate = str(date.today().year)+'-'+str(date.today().month)+'-'+str(date.today().day)
			if attendence.objects.filter(for_emp=empO, date=currDate, for_org=empOrg).exists():
				attO = attendence.objects.get(for_emp=empO, date=currDate, for_org=empOrg)
				message = attO.status
			else:
				message='error'
		else:
			message='error'

		return JsonResponse({'message':message})


class getProfile(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		present=0
		halfday=0
		leave=0
		user = request.user
		if employee.objects.filter(user=user).exists():
			empO = employee.objects.get(user=user)
			empOrg = empO.for_org
			currMnth = date.today().month
			if attendence.objects.filter(for_emp=empO, for_org=empOrg, date__month=currMnth).exists():
				attO=attendence.objects.filter(for_emp=empO, for_org=empOrg, date__month=currMnth)
				for x in attO:
					if x.status == 'present':
						present+=1
					elif x.status == 'halfday':
						halfday += 1
					elif x.status == 'leave':
						leave +=1
			return JsonResponse({'username':user.username, 'present':present,
				'halfday':halfday, 'leave':leave, 'photo':empO.photo.url})
		else:
			return JsonResponse({'message':'error'},status=404)


class getAttendenceOfMonth(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		user = request.user
		if employee.objects.filter(user=user).exists():
			empO = employee.objects.get(user=user)
			empOrg = empO.for_org
			currMnth = date.today().month
			l1 = []
			if attendence.objects.filter(for_emp=empO, for_org=empOrg, date__month=currMnth).exists():
				attO = attendence.objects.filter(for_emp=empO, for_org=empOrg, date__month=currMnth)
				for x in attO:
					l1.append({'date':x.date,'status':x.status})
			return JsonResponse({'data':l1})
		else:
			return JsonResponse({'data':'error'}, status=404)


class getAnnouncementOfMonth(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		user = request.user
		if employee.objects.filter(user=user).exists():
			empO = employee.objects.get(user=user)
			empOrg = empO.for_org
			currMnth = date.today().month
			l1=[]
			if announcement.objects.filter(for_org=empOrg, date__month=currMnth).exists():
				annO = announcement.objects.filter(for_org=empOrg, date__month=currMnth)
				for x in annO:
					l1.append({'date': x.date, 'txt':x.txt})
			return JsonResponse({'data':l1})
		else:
			return JsonResponse({'data':'error'},status=404)


class getAnnouncementOfToday(APIView):
	permission_classes = (IsAuthenticated,)

	def get(self, request):
		user = request.user
		if employee.objects.filter(user=user).exists():
			empO = employee.objects.get(user=user)
			empOrg = empO.for_org
			currDate = str(date.today().year)+'-'+str(date.today().month)+'-'+str(date.today().day)
			l1=[]
			if announcement.objects.filter(for_org=empOrg, date=currDate).exists():
				annO = announcement.objects.filter(for_org=empOrg, date=currDate)
				for x in annO:
					l1.append({'date': x.date, 'txt':x.txt})
			return JsonResponse({'data':l1})
		else:
			return JsonResponse({'data':'error'},status=404)


#######################################################################
#		API ENDS HERE
#######################################################################


def validateInputStr(inputList):
	retVal=True
	for x in inputList:
		if x==None or x.strip()=='':
			retVal = False
			break
	return retVal


def logoutWeb(request):
	logout(request)
	return redirect('/')


def checkUserFromActiveOrg(user):
	retVal=True
	if employee.objects.filter(user=user).exists():
		empO = employee.objects.get(user=user)
		if empO.for_org.status != True:
			retVal = False
	else:
		retVal = False
	return retVal


def not_found(request):
	return render(request, 'record/404.html', {})



def checkAdminUser(user):
	retVal = False
	org = None
	if employee.objects.filter(user=user, is_admin=True).exists():
		retVal = True
		# empO = employee.objects.get(user=user, is_admin=True)
		# org = empO.for_org
	return retVal


@login_required(login_url='/')
def approveF(request):
	context={}
	user = request.user
	# currMnth = date.today().month
	if request.method == 'POST' and checkAdminUser(user) and checkUserFromActiveOrg(user):
		empO = employee.objects.get(user=user)
		approve = request.POST.get('approve')
		if validateInputStr([approve,]) and attendence.objects.filter(pk=approve, for_org=empO.for_org).exists():
			attO = attendence.objects.get(pk=approve)
			if attendenceReq.objects.filter(for_att=attO, stat=True).exists():
				attReq = attendenceReq.objects.get(for_att=attO, stat=True)
				attO.status='present'
				attReq.stat = False
				attO.save()
				attReq.save()
				
	return redirect('/')


@login_required(login_url='/')
def rejectF(request):
	context={}
	user = request.user
	# currMnth = date.today().month
	if request.method == 'POST' and checkAdminUser(user) and checkUserFromActiveOrg(user):
		empO = employee.objects.get(user=user)
		approve = request.POST.get('rejectF')
		if validateInputStr([approve,]) and attendence.objects.filter(pk=approve, for_org=empO.for_org).exists():
			attO = attendence.objects.get(pk=approve)
			if attendenceReq.objects.filter(for_att=attO, stat=True).exists():
				attReq = attendenceReq.objects.get(for_att=attO, stat=True)
				# attO.status='present'
				attReq.stat = False
				# attO.save()
				attReq.save()
				
	return redirect('/')



@login_required(login_url='/')
def addemp(request):
	context={}
	user = request.user
	currMnth = date.today().month
	try:
		if checkAdminUser(user) and checkUserFromActiveOrg(user):
			empO = employee.objects.get(user=user)
			if empO.for_org.totalEmp<= employee.objects.filter(for_org=empO.for_org).count():
				return redirect('/')
			attChng=[]
			numberRequest=0
			for x in attendenceReq.objects.filter(for_org=empO.for_org, stat=True):
					attChng.append(x)
					numberRequest +=1
			context['numberRequest'] = numberRequest
			context['requests'] = attChng
			context['org'] = empO.for_org.orgName
			if request.method=='POST':
				email = request.POST.get('email')
				password = request.POST.get('password')
				photo = request.FILES['photo']
				name = request.POST.get('name')
				position = request.POST.get('designation')
				contact = request.POST.get('contact')
				print(email, password, photo, name, position, contact)
				if validateInputStr([email, password, name, position, contact]):
					userN = User.objects.create_user(username=email, email=email, password=password)
					userN.save()
					emp = employee.objects.create(user=userN, for_org=empO.for_org, empName=name, photo=photo, contact=contact, designation=position, loc=Point(float(0.0),float(0.0)))
					emp.save()
					context['message'] = 'Employee added Successfully'
				else:
					context['message']='Invalid data Supplied'
		else:
			logout(request)
			return redirect('/')
	except IntegrityError:
		context['message'] = 'Employee with that detail already exists'
		
	return render(request, 'record/addEmp.html', context)


@login_required(login_url='/')
def listemployee(request, page=1):
	context={}
	user = request.user
	currMnth = date.today().month
	if checkAdminUser(user) and checkUserFromActiveOrg(user):
		empO = employee.objects.get(user=user)
		attChng=[]
		numberRequest=0
		for x in attendenceReq.objects.filter(for_org=empO.for_org, stat=True):
				attChng.append(x)
				numberRequest +=1
		context['numberRequest'] = numberRequest
		context['requests'] = attChng
		context['org'] = empO.for_org.orgName
		if request.method == 'POST':
			query = request.POST.get('query')
			if query!='' and query != None and employee.objects.filter(Q(empName__contains=query) | Q(contact__contains=query), Q(for_org=empO.for_org)).exists():
				emp = employee.objects.filter(Q(empName__contains=query) | Q(contact__contains=query), Q(for_org=empO.for_org))

				paginator = Paginator(emp.order_by('empName'),2)
				try:
					atO = paginator.page(page)
				except PageNotAnInteger:
					atO = paginator.page(1)
				except EmptyPage:
					atO = paginator.page(paginator.num_pages)

				context['attO'] = atO
		else:
			emp = employee.objects.filter(for_org=empO.for_org)
			paginator = Paginator(emp.order_by('empName'),2)
			try:
				atO = paginator.page(page)
			except PageNotAnInteger:
				atO = paginator.page(1)
			except EmptyPage:
				atO = paginator.page(paginator.num_pages)

			context['attO'] = atO
	else:
		logout(request)
		return redirect('/')
	return render(request, 'record/listemployee.html', context)


@login_required(login_url='/')
def deleteemployee(request, pk):
	context={}
	user = request.user
	# currMnth = date.today().month
	if request.method=='POST' and employee.objects.filter(pk=pk).exists() and checkAdminUser(user) and checkUserFromActiveOrg(user) and pk != None and pk.strip()!='':
		empO = employee.objects.get(pk=pk)
		empO.delete()
	
	return redirect('/listemployee')


@login_required(login_url='/')
def listmessageMonth(request, pk):
	context={}
	user = request.user
	currMnth = date.today().month
	if pk!=None and pk != '' and checkAdminUser(user) and checkUserFromActiveOrg(user) and employee.objects.filter(pk=pk).exists():
		empO = employee.objects.get(user=user)
		attChng=[]
		numberRequest=0
		for x in attendenceReq.objects.filter(for_org=empO.for_org, stat=True):
				attChng.append(x)
				numberRequest +=1
		context['numberRequest'] = numberRequest
		context['requests'] = attChng
		context['org'] = empO.for_org.orgName
		emp = employee.objects.get(pk=pk)
		announcementO = personalMsg.objects.filter(for_emp=emp, date__month=currMnth)
		context['data']=announcementO
		context['emp']=emp
	else:
		logout(request)
		return redirect('/')
	return render(request, 'record/listmessageMonth.html', context)

@login_required(login_url='/')
def listannouncementMonth(request):
	context={}
	user = request.user
	currMnth = date.today().month
	if checkAdminUser(user) and checkUserFromActiveOrg(user):
		empO = employee.objects.get(user=user)
		attChng=[]
		numberRequest=0
		for x in attendenceReq.objects.filter(for_org=empO.for_org, stat=True):
				attChng.append(x)
				numberRequest +=1
		context['numberRequest'] = numberRequest
		context['requests'] = attChng
		context['org'] = empO.for_org.orgName
		announcementO = announcement.objects.filter(for_org=empO.for_org, date__month=currMnth)
		context['data']=announcementO
	else:
		logout(request)
		return redirect('/')
	return render(request, 'record/listannouncementMonth.html', context)


@login_required(login_url='/')
def searchemployee(request, page=1):
	context={}
	user = request.user
	currMnth = date.today().month
	if checkAdminUser(user) and checkUserFromActiveOrg(user):
		empO = employee.objects.get(user=user)
		attChng=[]
		numberRequest=0
		for x in attendenceReq.objects.filter(for_org=empO.for_org, stat=True):
				attChng.append(x)
				numberRequest +=1
		context['numberRequest'] = numberRequest
		context['requests'] = attChng
		context['org'] = empO.for_org.orgName
		if request.method == 'POST':
			query = request.POST.get('query')
			if query!='' and query != None and employee.objects.filter(Q(empName__contains=query) | Q(contact__contains=query), Q(for_org=empO.for_org)).exists():
				emp = employee.objects.filter(Q(empName__contains=query) | Q(contact__contains=query), Q(for_org=empO.for_org))

				paginator = Paginator(emp.order_by('empName'),2)
				try:
					atO = paginator.page(page)
				except PageNotAnInteger:
					atO = paginator.page(1)
				except EmptyPage:
					atO = paginator.page(paginator.num_pages)

				context['attO'] = atO
		else:
			emp = employee.objects.filter(for_org=empO.for_org)
			paginator = Paginator(emp.order_by('empName'),2)
			try:
				atO = paginator.page(page)
			except PageNotAnInteger:
				atO = paginator.page(1)
			except EmptyPage:
				atO = paginator.page(paginator.num_pages)

			context['attO'] = atO
	else:
		logout(request)
		return redirect('/')
	return render(request, 'record/searchemployee.html', context)


@login_required(login_url='/')
def getAttendenceOfdayWeb(request,page=1):
	context={}
	user = request.user
	currDate = str(date.today().year)+'-'+str(date.today().month)+'-'+str(date.today().day)
	# page = request.GET.get('page',1)
	# print(page)
	if checkAdminUser(user) and checkUserFromActiveOrg(user):
		empO = employee.objects.get(user=user)
		attChng=[]
		numberRequest=0
		for x in attendenceReq.objects.filter(for_org=empO.for_org, stat=True):
				attChng.append(x)
				numberRequest +=1
		context['numberRequest'] = numberRequest
		context['requests'] = attChng
		context['org'] = empO.for_org.orgName
		if request.method == 'POST':
			tmp=''
			# tmp1=
			q = request.POST.get('query','aaa')
			if q!='' and q!=None and employee.objects.filter(Q(empName__contains=q) | Q(contact__contains=q), Q(for_org=empO.for_org)).exists():
				empL = employee.objects.filter(Q(empName__contains=q) | Q(contact__contains=q), Q(for_org=empO.for_org))
				first=0
				for x in empL:
					if first==0:
						tmp=attendence.objects.filter(for_emp=x,date=currDate)
						first=1
					else:
						tmp = tmp | attendence.objects.filter(for_emp=x,date=currDate)

				paginator = Paginator(tmp.order_by('-date'),2)
				try:
					atO = paginator.page(page)
				except PageNotAnInteger:
					atO = paginator.page(1)
				except EmptyPage:
					atO = paginator.page(paginator.num_pages)

				context['attO'] = atO


		else:
			
			l1 = []
			if attendence.objects.filter(for_org=empO.for_org, date=currDate).exists():
				attO = attendence.objects.filter(for_org=empO.for_org, date=currDate)
				paginator = Paginator(attO.order_by('-date'),2)
				try:
					atO = paginator.page(page)
				except PageNotAnInteger:
					atO = paginator.page(1)
				except EmptyPage:
					atO = paginator.page(paginator.num_pages)
				# for x in attO.order_by('-date'):
				# 	l1.append(x)
				context['attO'] = atO

	else:
		logout(request)
		return redirect('/')			

	return render(request, 'record/tableMonth.html', context)


@login_required(login_url='/')
def getAttendenceOfMonthWeb(request,page=1):
	context={}
	user = request.user
	currMnth = date.today().month
	# page = request.GET.get('page',1)
	# print(page)
	if checkAdminUser(user) and checkUserFromActiveOrg(user):
		empO = employee.objects.get(user=user)
		attChng=[]
		numberRequest=0
		for x in attendenceReq.objects.filter(for_org=empO.for_org, stat=True):
				attChng.append(x)
				numberRequest +=1
		context['numberRequest'] = numberRequest
		context['requests'] = attChng
		context['org'] = empO.for_org.orgName
		if request.method == 'POST':
			tmp=''
			# tmp1=
			q = request.POST.get('query','aaa')
			if q!='' and q!=None and employee.objects.filter(Q(empName__contains=q) | Q(contact__contains=q), Q(for_org=empO.for_org)).exists():
				empL = employee.objects.filter(Q(empName__contains=q) | Q(contact__contains=q), Q(for_org=empO.for_org))
				first=0
				for x in empL:
					if first==0:
						tmp=attendence.objects.filter(for_emp=x,date__month=currMnth)
						first=1
					else:
						tmp = tmp | attendence.objects.filter(for_emp=x,date__month=currMnth)

				paginator = Paginator(tmp.order_by('-date'),2)
				try:
					atO = paginator.page(page)
				except PageNotAnInteger:
					atO = paginator.page(1)
				except EmptyPage:
					atO = paginator.page(paginator.num_pages)

				context['attO'] = atO


		else:
			
			l1 = []
			if attendence.objects.filter(for_org=empO.for_org, date__month=currMnth).exists():
				attO = attendence.objects.filter(for_org=empO.for_org, date__month=currMnth)
				paginator = Paginator(attO.order_by('-date'),2)
				try:
					atO = paginator.page(page)
				except PageNotAnInteger:
					atO = paginator.page(1)
				except EmptyPage:
					atO = paginator.page(paginator.num_pages)
				# for x in attO.order_by('-date'):
				# 	l1.append(x)
				context['attO'] = atO

	else:
		logout(request)
		return redirect('/')			

	return render(request, 'record/tableMonth.html', context)



@login_required(login_url='/')
def getAttendenceOfYearWeb(request,page=1):
	context={}
	user = request.user
	currMnth = date.today().year
	# page = request.GET.get('page',1)
	# print(page)
	if checkAdminUser(user) and checkUserFromActiveOrg(user):
		empO = employee.objects.get(user=user)
		attChng=[]
		numberRequest=0
		for x in attendenceReq.objects.filter(for_org=empO.for_org, stat=True):
				attChng.append(x)
				numberRequest +=1
		context['numberRequest'] = numberRequest
		context['requests'] = attChng
		context['org'] = empO.for_org.orgName
		if request.method == 'POST':
			tmp=''
			# tmp1=
			q = request.POST.get('query','aaa')
			if employee.objects.filter(Q(empName__contains=q) | Q(contact__contains=q), Q(for_org=empO.for_org)).exists():
				empL = employee.objects.filter(Q(empName__contains=q) | Q(contact__contains=q), Q(for_org=empO.for_org))
				first=0
				for x in empL:
					if first==0:
						tmp=attendence.objects.filter(for_emp=x,date__year=currMnth)
						first=1
					else:
						tmp = tmp | attendence.objects.filter(for_emp=x,date__year=currMnth)

				paginator = Paginator(tmp.order_by('-date'),2)
				try:
					atO = paginator.page(page)
				except PageNotAnInteger:
					atO = paginator.page(1)
				except EmptyPage:
					atO = paginator.page(paginator.num_pages)

				context['attO'] = atO


		else:
			
			l1 = []
			if attendence.objects.filter(for_org=empO.for_org, date__year=currMnth).exists():
				attO = attendence.objects.filter(for_org=empO.for_org, date__year=currMnth)
				paginator = Paginator(attO.order_by('-date'),2)
				try:
					atO = paginator.page(page)
				except PageNotAnInteger:
					atO = paginator.page(1)
				except EmptyPage:
					atO = paginator.page(paginator.num_pages)
				# for x in attO.order_by('-date'):
				# 	l1.append(x)
				context['attO'] = atO

	else:
		logout(request)
		return redirect('/')			

	return render(request, 'record/tableYear.html', context)


@login_required(login_url='/')
def profileEmp(request,pk=1):
	context={}
	user = request.user
	if checkAdminUser(user) and checkUserFromActiveOrg(user):
		empO = employee.objects.get(user=user)
		if employee.objects.filter(for_org=empO.for_org, pk=pk).exists():
			emp = employee.objects.get(for_org=empO.for_org, pk=pk)
			if request.method == 'POST':
				checkVal = request.POST.get('checkVal')
				if checkVal!='' and checkVal != None:
					if checkVal == 'pr':
						name = request.POST.get('name')
						contact = request.POST.get('contact')
						position = request.POST.get('designation')
						imei = request.POST.get('imei')
						if validateInputStr([name, contact, position, imei]):
							emp.empName = name
							emp.contact = contact
							emp.designation = position
							emp.imei = imei
							emp.save()
							context['message'] = 'Saved Successfully'
						else:
							context['message'] = 'Invalid data Supplied'
					elif checkVal == 'msg':
						msg = request.POST.get('message')
						if validateInputStr([msg,]) and len(msg)<=5000:
							personalMsgO = personalMsg.objects.create(for_emp=emp, message=msg)
							personalMsgO.save()
							context['message'] = 'Sent'
						else:
							context['message'] = 'Invalid data Supplied'
					else:
						context['message'] = 'Invalid data Supplied'
				else:
					context['message'] = 'Invalid data Supplied'
			# else:
				#get method
			currMnth = date.today().month
			# emp = employee.objects.get(for_org=empO.for_org, pk=pk)
			ontime = 0
			halfday=0
			leave=0
			numberRequest = 0
			attChng = []
			present=0
			attO = attendence.objects.filter(for_org=emp.for_org, for_emp=emp, date__month=currMnth)
			if attO.count() >0:
				for x in attO:
					if x.status == 'present':
						present +=1
						ontime +=1
					elif x.status == 'halfday':
						halfday +=1
						present +=1
					elif x.status == 'leave':
						leave +=1
				context['empOnTime']=(ontime/attO.count())*100
				context['empOnHalf'] = (halfday/attO.count())*100
				context['empOnLeave']=(leave/attO.count())*100
				context['present']=(present/attO.count())*100
			else:
				context['empOnTime']=0
				context['empOnHalf'] = 0
				context['empOnLeave']=0
				context['present']=0

			for x in attendenceReq.objects.filter(for_org=empO.for_org, stat=True):
				attChng.append(x)
				numberRequest +=1

			context['emp'] = emp
			
			context['logo'] = empO.for_org.logo.url
			context['org'] = empO.for_org.orgName
			context['numberRequest'] = numberRequest
			context['requests'] = attChng
		else:
			print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
			return redirect('/')
	else:
		logout(request)
		return redirect('/')
	return render(request, 'record/profileEmp.html', context)


@login_required(login_url='/')
def profileAdmin(request):
	context={}
	user = request.user

	if checkAdminUser(user) and checkUserFromActiveOrg(user):
		if request.method == 'POST':
			checkVal =  request.POST.get('checkVal')
			if checkVal=='pr':
				contact = request.POST.get('contact')
				halfday = request.POST.get('halfday')
				punchout = request.POST.get('punchout')
				leave = request.POST.get('leave')
				
				if validateInputStr([contact, halfday, punchout, leave]) and validate_time(halfday) and validate_time(punchout) and validate_time(leave) and contact != '' and contact != None:
					# print(contact, halfday, punchout, leave)
					empO = employee.objects.get(user=user)
					org = empO.for_org
					org.orgContact = contact
					org.half_day = halfday
					org.leave = leave
					org.punchOutTime = punchout
					org.save()
					# print(org)
					return redirect('/profileAdmin', message='Saved Successfully!')
				else:
					return redirect('/profileAdmin', message='Invalid Input Supplied')
			elif checkVal == 'ln':
				rad = request.POST.get('rad')
				lon = request.POST.get('lat')
				lat = request.POST.get('lon')
				if validate_loc(lat, lon) and rad.isdigit():
					empO = employee.objects.get(user=user)
					org = empO.for_org
					org.loc = Point(float(lat), float(lon))
					org.distanceReq = int(rad)
					org.save()
					context['message']='Saved Successfully!'
					return redirect('/profileAdmin', message='Saved Successfully!')
				else:
					return redirect('/profileAdmin', message='Invalid Input Supplied')
			elif checkVal =='an':
				message = request.POST.get('message')
				if message != '' and message != None:
					empO = employee.objects.get(user=user)
					annO = announcement.objects.create(for_org=empO.for_org, txt=message)
					annO.save()
					return redirect('/profileAdmin', message='Saved Successfully!')
				else:
					return redirect('/profileAdmin', message='Invalid Input Supplied')
			else:
				return redirect('/profileAdmin', message='Invalid Input Supplied')
		# else:
		empO = employee.objects.get(user=user)
		currDate = str(date.today().year)+'-'+str(date.today().month)+'-'+str(date.today().day)
		numberRequest = 0
		attChng = []
		ontime = 0
		halfday = 0
		leave = 0
		present = 0
		currMnth = date.today().month

		attO = attendence.objects.filter(for_org=empO.for_org, date__month=currMnth)
		if attO.count() >0:
			for x in attO:
				if x.status == 'present':
					present +=1
					ontime +=1
				elif x.status == 'halfday':
					halfday +=1
					present +=1
				elif x.status == 'leave':
					leave +=1
			context['empOnTime']=(ontime/attO.count())*100
			context['empOnHalf'] = (halfday/attO.count())*100
			context['empOnLeave']=(leave/attO.count())*100
			context['present']=(present/attO.count())*100
		else:
			context['empOnTime']=0
			context['empOnHalf'] = 0
			context['empOnLeave']=0
			context['present']=0


		for x in attendenceReq.objects.filter(for_org=empO.for_org, stat=True):
			attChng.append(x)
			numberRequest +=1

		context['halfday'] = empO.for_org.half_day
		context['punchout'] = empO.for_org.punchOutTime
		context['leave'] = empO.for_org.leave
		context['cont'] = empO.for_org.orgContact
		context['rad'] = empO.for_org.distanceReq
		context['lon'] = empO.for_org.loc.x
		context['lat'] = empO.for_org.loc.y
		context['logo'] = empO.for_org.logo.url
		context['org'] = empO.for_org.orgName
		context['numberRequest'] = numberRequest
			

	else:
		logout(request)
		return redirect('/')
	return render(request, 'record/profile.html', context)


@login_required(login_url='/')
def home(request):
	context={}
	user = request.user

	if checkAdminUser(user) and checkUserFromActiveOrg(user):
		empO = employee.objects.get(user=user)
		currDate = str(date.today().year)+'-'+str(date.today().month)+'-'+str(date.today().day)

		total_emp = employee.objects.filter(for_org=empO.for_org).count()
		attO = attendence.objects.filter(for_org=empO.for_org, date=currDate)
		attChng = []

		present_emp = 0
		absent_emp = 0
		late_emp = 0
		numberRequest = 0
		

		for x in attO:
			if x.status == 'present':
				present_emp += 1
			elif x.status == 'halfday':
				late_emp += 1
				present_emp +=1
			elif x.status == 'leave':
				absent_emp +=1


		for x in attendenceReq.objects.filter(for_org=empO.for_org, stat=True):
			attChng.append(x)
			numberRequest +=1


		context['org'] = empO.for_org.orgName
		context['total_emp'] = total_emp
		context['present_emp'] = present_emp
		context['absent_emp'] = absent_emp
		context['late_emp'] = late_emp
		context['numberRequest'] = numberRequest
		context['requests'] = attChng
	else:
		logout(request)
		return redirect('/')
	return render(request, 'record/index.html',context)


def loginWeb(request):
	if request.user.is_authenticated:
		return redirect('home')
	context={}
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		currDate = str(date.today().year)+'-'+str(date.today().month)+'-'+str(date.today().day)
		if validateInputStr([username, password]):
			user = authenticate(username=username, password=password)
			
			if user != None and user.is_active and employee.objects.filter(user=user, is_admin=True).exists():
				login(request, user)
				# print(user)
				empO = employee.objects.get(user=user)
				if empO.for_org.expiration < date.today():
					org=empO.for_org
					org.status=False
					org.save()
				emp = employee.objects.filter(for_org=empO.for_org)
				for x in emp:
					if attendence.objects.filter(for_emp=x, date=currDate).exists()==False:
						attO = attendence.objects.create(for_org=empO.for_org, for_emp=x, date=currDate,status='leave')
						attO.save()
				return redirect('home')
			else:
				logout(request)
		else:
			context[message] = 'Invalid Credentials.'

	return render(request, 'record/login.html',context)
