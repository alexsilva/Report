# -*- coding: UTF-8 -*-
# from django.shortcuts import render_to_response
# from django.http import HttpResponse
import viewer.main.views
from viewer.main import shared
import zenclient
# --------------------------------------------------------------------

def report_load(request):
    query = viewer.main.views.get_query( request )
    params = {
        "title": zenclient.Zendesk.name,
        "statistic_data": [],
        "statistic": {}
    }
    if query.project_id:
        # relatório anual ativas os 12 meses.
        if query.yearly_report: month_start, month_end = 1, 12
        else: month_start = month_end = query.period_month # só ativa o mês em questão.
        
        params["statistic"] = statistic = shared.Statistic(
            query.project_id, query.period_year, 
            query.period_month)
        
        if statistic.hasYearlyPlan and statistic.yearlyplan.is_active:
            for month in xrange(month_start, month_end+1):
                if not statistic.isValidMonthYear(month, query.period_year):
                    continue
                
                statistic.update(query.period_year, month)
                
                zendesk = zenclient.Zendesk(
                    project_id = query.project_id, 
                    year = query.period_year, month = month,
                    statistic = statistic
                )
                data = zendesk.get_statistc_data(query.detail_view)
                
                if type(data) is list:
                    params["statistic_data"].extend( data )
                else:
                    params["statistic_data"].append( data )
    return viewer.main.views.get_response(request, query, **params)