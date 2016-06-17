from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^showlog/', 'showlog.showlog.give_logs', name='Unified Logs'),
    url(r'^4dinfo/', '4dinfo.4dinfo.return_page', name='4D Errors'),
)
