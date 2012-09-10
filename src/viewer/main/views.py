# -*- coding: UTF-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from models import Project
import shared, datetime

date_now = datetime.datetime.now()
dateInputForm = shared.DateInputForm()
# --------------------------------------------------------------------
def option_load(request):
    return render_to_response("options.html")

# --------------------------------------------------------------------
def get_hlist_groups(elements, headersItem):
    """ object: {'a': 1, 'b':2} -> return: [[1, 2]]"""
    list_group = []
    elements_type = type(elements)
    if elements_type is dict:
        templist = []
        for key in headersItem:
            templist.append(elements.get(key,"..."))
        list_group.append( templist )
    elif elements_type is list:
        for element in elements:
            templist = []
            for key in headersItem:
                templist.append(element.get(key,"..."))
            list_group.append( templist )
    else: raise TypeError, "only 'dict' or 'list' suported."
    return list_group

# --------------------------------------------------------------------
def get_params(request):
    class param(object):
        __all__ = {
            "project_id": ("", str), 
            "period_month": (date_now.month, int), 
            "period_year": (date_now.year, int), 
            "yearly_report": (0, int),
            "detail_view": (0, int)
        }
        @classmethod
        def attrs(cls, request):
            for name in cls.__all__:
                d, conv = cls.__all__[name]
                v = conv(request.GET.get(name, d))
                setattr(cls, name, v)
    # atribuindo os parametros à classe
    param.attrs(request)
    return param

def get_response(request, param, **params):
    html = {
        "project_id_selected": param.project_id,
        "year_check": param.yearly_report,
        "detail_check": param.detail_view,
        "detail_view": param.detail_view
    }
    dateInputForm.fields["period"].initial = {
        "month": param.period_month, 
        "year": param.period_year
    }
    statistic = params["statistic"]
    
    if param.detail_view:
        headers = shared.ReportHeader.getSimpleHeader()
        headersItem = shared.ReportHeader.getSimpleHeaderItem()
    else:
        headers = shared.ReportHeader.getFullHeader()
        headersItem = shared.ReportHeader.getFullHeaderItem()
        
    response = render_to_response("main.html", {
        "widgetTitle": params["title"],
        "dateInputForm": dateInputForm,
        "headers": headers,
        "rlist": get_hlist_groups(params["statistic_data"], headersItem),
        "params": {
            "yearly_report": param.yearly_report,
            "detail_view": param.detail_view,
            "statistic": statistic
        },
        "projects": [(q.key, q.name) for q in Project.objects.all()],
        "date_now": date_now.strftime("%d de %b de %Y"),
        "html": html
    })
    return response	