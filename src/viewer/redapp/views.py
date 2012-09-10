# -*- coding: UTF-8 -*-
#from django.shortcuts import render_to_response
#from django.http import HttpResponse
from viewer.main.models import Project
from viewer.main import shared
import viewer.main.views
import redclient

# -------------------------------------------------
def report_load(request):
    param = viewer.main.views.get_params( request )
    params = {
        "title": redclient.Redmine.name,
        "statistic_data": [],
        "statistic": {}
    }
    if param.project_id:
        # relatório anual ativa os 12 meses.
        if param.yearly_report: month_start, month_end = 1, 12
        else: month_start = month_end = param.period_month # só ativa o mês em questão.
        
        params["statistic"] = statistic = shared.Statistic(
            param.project_id, param.period_year, 
            param.period_month)
        
        if statistic.hasYearlyPlan and statistic.yearlyplan.is_active:
            for month in xrange(month_start, month_end+1):
                if not statistic.isValidMonthYear(month, param.period_year):
                    continue
                
                statistic.update(param.period_year, month)
                
                redmine = redclient.Redmine(
                    project_id = param.project_id,
                    month = month, year = param.period_year,
                    statistic = statistic
                )
                data = redmine.get_statistc_data( param.detail_view )
                if type(data) is list:
                    params["statistic_data"].extend( data )
                else:
                    params["statistic_data"].append( data )
    return viewer.main.views.get_response(request, param, **params)
