from django.urls import re_path
from supportSystem.views import staff, login


app_name = 'supportSystem'

base64_pattern = r'(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'

urlpatterns = [
    re_path(r'^dashboard/$',
        staff.dashboard,
        name='dashboard'),

    re_path(r'^tickets/$',
        staff.ticket_list,
        name='list'),

    re_path(r'^tickets/update/$',
        staff.mass_update,
        name='mass_update'),


    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/$',
        staff.view_ticket,
        name='view'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/followup_edit/(?P<followup_id>[0-9]+)/$',
        staff.followup_edit,
        name='followup_edit'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/followup_delete/(?P<followup_id>[0-9]+)/$',
        staff.followup_delete,
        name='followup_delete'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/update/$',
        staff.update_ticket,
        name='update'),

    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/delete/$',
        staff.delete_ticket,
        name='delete'),


    re_path(r'^tickets/(?P<ticket_id>[0-9]+)/attachment_delete/(?P<attachment_id>[0-9]+)/$',
        staff.attachment_del,
        name='attachment_del'),


    re_path(r'^reports/$',
        staff.report_index,
        name='report_index'),

    re_path(r'^reports/(?P<report>\w+)/$',
        staff.run_report,
        name='run_report'),


    re_path(r'^datatables_ticket_list/(?P<query>{})$'.format(base64_pattern),
        staff.datatables_ticket_list,
        name="datatables_ticket_list"),

]

urlpatterns += [
    re_path(r'^$',
        staff.homepage,
        name='home'),
]


urlpatterns += [
    re_path(r'^login/$', login.loginPage, name='login'),
    re_path(r'^authenticate/$', login.auth, name='signin'),
    re_path(r'^callback/$', login.callback, name='callback'),
    re_path(r'^signout/$', login.signout, name='signout'),
]
