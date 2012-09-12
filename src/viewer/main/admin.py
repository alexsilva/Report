# -*- coding: UTF-8 -*-
from django.contrib import admin
from django import forms

from models import Project, MonthlyPlan, HoursAdd, YearlyPlan
import w_monthYear
########################################################################

period_object = HoursAdd._meta.get_field_by_name("period")[0]
class HoursAddForm(forms.ModelForm):
    period = forms.DateField(
        label = period_object.verbose_name, help_text = period_object.help_text, 
        widget = w_monthYear.MonthYearWidget
    )
    
starts_object = MonthlyPlan._meta.get_field_by_name("starts")[0]
finished_object = MonthlyPlan._meta.get_field_by_name("finished")[0]
class MonthlyPlanForm(forms.ModelForm):
    starts = forms.DateField(
        label = starts_object.verbose_name, help_text = starts_object.help_text, 
        widget = w_monthYear.MonthYearWidget
    )
    finished = forms.DateField(
        label = finished_object.verbose_name, help_text = finished_object.help_text, 
        widget = w_monthYear.MonthYearWidget,
        required = False
    )    
    #class Meta:
        #exclude = ("finished", )
        
########################################################################
class HoursAddInline(admin.TabularInline):
    form = HoursAddForm
    model = HoursAdd
    
class MonthlyPlanInline(admin.TabularInline):
    form = MonthlyPlanForm
    model = MonthlyPlan
    
########################################################################
class YearlyPlanAdmin(admin.ModelAdmin):
    inlines = (MonthlyPlanInline, HoursAddInline)
    
########################################################################
class HoursAddAdmin(admin.ModelAdmin):
    form = HoursAddForm

########################################################################
admin.site.register(Project)
admin.site.register(YearlyPlan, YearlyPlanAdmin)
## admin.site.register(MonthlyPlan, MonthlyPlanAdmin)
#admin.site.register(HoursAdd, HoursAddAdmin)