# -*- coding: UTF-8 -*-
from django.contrib import admin
from django import forms

from models import Project, MonthlyPlan, HoursAdd, YearlyPlan
import w_monthYear

period_object = HoursAdd._meta.get_field_by_name("period")[0]
class HoursAddForm(forms.ModelForm):
    period = forms.DateField(
        label = period_object.verbose_name, help_text = period_object.help_text, 
        widget = w_monthYear.MonthYearWidget
    )
    
########################################################################
starts_object = MonthlyPlan._meta.get_field_by_name("starts")[0]
class MonthlyPlanForm(forms.ModelForm):
    starts = forms.DateField(
        label = starts_object.verbose_name, help_text = starts_object.help_text, 
        widget = w_monthYear.MonthYearWidget
    )
    class Meta:
        exclude = ("finished", )
        
########################################################################
class HoursAddInline(admin.TabularInline):
    model = HoursAdd
    form = HoursAddForm
    
########################################################################
class MonthlyPlan_Admin(admin.ModelAdmin):
    inlines = (HoursAddInline, )
    form = MonthlyPlanForm
    
    def save_model(self, request, obj, form, change):
        try:
            lastPlan = MonthlyPlan.objects.filter(project__key=obj.project.key)
            lastPlan = lastPlan.order_by("starts")
            lastPlan = lastPlan[lastPlan.count()-1]
        except:
            lastPlan = None
            
        if change: # guarda a referencia para o obj antigo.
            try: obj_before_save = MonthlyPlan.objects.get(pk=obj.pk)
            except: obj_before_save = None
            
        obj.save() # salvando o modelo prinicipal.
        
        if not change and lastPlan:
            # o ultimo plano termina no começo do plano atual.
            if obj.starts >= lastPlan.starts:
                lastPlan.finished = obj.starts
                lastPlan.save()
        else:
            # busca o plano imediatamente anterior a este.
            try:
                previousPlan = MonthlyPlan.objects.filter(
                    project__key = obj_before_save.project.key,
                    starts__lte = obj_before_save.starts, 
                    finished__gte = obj_before_save.starts,
                    pk__lt = obj.pk
                )
                previousPlan = previousPlan[previousPlan.count()-1]
            except:
                previousPlan = None
                
            # asegura que o plano anterior, sempre fecha no começo do atual.
            if previousPlan and obj.starts != previousPlan.finished:
                # impede que o plano termine anterior a quando começou.
                if obj.starts >= previousPlan.starts:
                    previousPlan.finished = obj.starts
                    previousPlan.save()
                    
########################################################################
class HoursAdd_Admin(admin.ModelAdmin):
    form = HoursAddForm

########################################################################
admin.site.register(Project)
admin.site.register(YearlyPlan)
admin.site.register(MonthlyPlan, MonthlyPlan_Admin)
admin.site.register(HoursAdd, HoursAdd_Admin)