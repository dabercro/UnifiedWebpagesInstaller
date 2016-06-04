from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^history/', 'showlog.showlog.give_logs', name='Unified Logs'),
)
