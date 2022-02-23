from django.urls import path
from .views import (mark_attendence,loginAPI,checkStatus,checkLogin,reqAttendenceChange,getTodayAttendence,
checkRequest, getProfile,getAttendenceOfMonth,getAnnouncementOfMonth,
getAnnouncementOfToday,loginWeb, home,get_message, getAttendenceOfMonthWeb, searchemployee, 
logoutWeb,profileAdmin,getAttendenceOfYearWeb,not_found, addemp, 
getAttendenceOfdayWeb, listemployee, profileEmp,rejectF,approveF, 
deleteemployee,listannouncementMonth,listmessageMonth, update_loc)

from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('mark_attendence', mark_attendence.as_view()),
    path('login',loginAPI.as_view()),
    path('checkStatus', checkStatus.as_view()),
    path('checkLogin', checkLogin.as_view()),
    path('reqAttendenceChange',reqAttendenceChange.as_view()),
    path('getTodayAttendence',getTodayAttendence.as_view()),
    path('checkRequest', checkRequest.as_view()),
    path('getProfile', getProfile.as_view()),
    path('getAttendenceOfMonth', getAttendenceOfMonth.as_view()),
    path('getAnnouncementOfMonth',getAnnouncementOfMonth.as_view()),
    path('getAnnouncementOfToday', getAnnouncementOfToday.as_view()),

    path('',loginWeb),
    path('logoutWeb', logoutWeb),
    path('home', home, name='home'),
    path('profileAdmin',profileAdmin),
    path('getAttendenceOfMonthWeb',getAttendenceOfMonthWeb),
    path('getAttendenceOfMonthWeb/<int:page>',getAttendenceOfMonthWeb),
    path('getAttendenceOfYearWeb',getAttendenceOfYearWeb),
    path('getAttendenceOfYearWeb/<int:page>',getAttendenceOfYearWeb),
    path('getAttendenceOfdayWeb',getAttendenceOfdayWeb),
    path('getAttendenceOfdayWeb/<int:page>',getAttendenceOfdayWeb),
    path('not_found', not_found),
    path('searchemployee',searchemployee),
    path('searchemployee/<int:page>',searchemployee),
    path('listemployee/<int:page>',listemployee),
    path('listemployee',listemployee),
    path('profileEmp/<int:pk>',profileEmp),
    path('approveF',approveF),
    path('rejectF',rejectF),
    path('addemp',addemp),
    path('deleteemployee/<str:pk>',deleteemployee),
    path('listannouncementMonth',listannouncementMonth),
    path('listmessageMonth/<str:pk>',listmessageMonth),
    path('get_message',get_message.as_view()),
    path('update_loc',update_loc.as_view()),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)