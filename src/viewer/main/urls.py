# coding: utf-8
from django.conf.urls import patterns, include, url

urlpatterns = patterns('viewer.main.views',
    ##url(r'', 'option_load'),
    url(r'^pdfgen/$', 'generate_pdf')
)