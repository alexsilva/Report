# -*- coding: UTF-8 -*-
# from django.shortcuts import render_to_response
# from django.http import HttpResponse
import viewer.main.views
from viewer.main import shared
import zenclient
# --------------------------------------------------------------------

def report_load(request):
    param = viewer.main.views.get_params( request )
    params = {
        "title": zenclient.Zendesk.name,
        "statistic_data": [],
        "statistic": {}
    }
    if param.project_id:
        # relatório anual ativas os 12 meses.
        if param.yearly_report: month_start, month_end = 1, 12
        else: month_start = month_end = param.period_month # só ativa o mês em questão.
        
        params["statistic"] = statistic = shared.Statistic(
            param.project_id, param.period_year, 
            param.period_month)
        
        for month in xrange(month_start, month_end+1):
            statistic.update(param.period_year, month)
            
            zendesk = zenclient.Zendesk(
                project_id = param.project_id, 
                year = param.period_year, month = month,
                statistic = statistic
            )
            data = zendesk.get_statistc_data(param.detail_view)
            
            if type(data) is list:
                params["statistic_data"].extend( data )
            else:
                params["statistic_data"].append( data )
            
    return viewer.main.views.get_response(request, param, **params)