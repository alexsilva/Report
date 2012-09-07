from django.conf.urls import patterns, url, include
from django.views.generic.simple import redirect_to
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^zendesk/', include('viewer.zenapp.urls')),
    url(r'^redmine/', include('viewer.redapp.urls')),
    url('^$', 'django.views.generic.simple.redirect_to', {'url': '/zendesk/'}),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
