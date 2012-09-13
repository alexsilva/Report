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
def get_query(request):
    class Query(object):
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
    Query.attrs(request)
    return Query

def is_searching(request):
    return request.method == "GET" and bool(len(request.GET))

def get_response(request, query, **params):
    dateInputForm.fields["period"].initial = {
        "month": query.period_month, 
        "year": query.period_year
    }
    statistic = params["statistic"]
    print request.method == "GET" and bool(len(request.GET))
    if query.detail_view:
        headers = shared.TableHeader.get_simple()
        headersItem = shared.TableHeader.get_simple_item()
    else:
        headers = shared.TableHeader.get_full()
        headersItem = shared.TableHeader.get_full_item()
        
    response = render_to_response("main.html", {
        "title": params["title"],
        "dateInputForm": dateInputForm,
        "headers": headers,
        "rlist": get_hlist_groups(params["statistic_data"], headersItem),
        "params": {
            "yearly_report": query.yearly_report,
            "detail_view": query.detail_view,
            "statistic": statistic,
            "searching": is_searching(request),
            # html params
            "project_id_selected": query.project_id,
            "year_check": query.yearly_report,          
        },
        "projects": [(q.key, q.name) for q in Project.objects.all()],
        "date_now": date_now.strftime("%d de %b de %Y"),
    })
    return response	