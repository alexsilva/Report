# -*- coding: UTF-8 -*-
import os, sys
import datetime, calendar
from viewer.main.models import Project
from django.utils.dates import MONTHS
from dateutil import parser
import admin

DATE_FORMAT = "%d/%m/%Y"
HOUR_FORMAT = "%H:%M:%S"

def getFormatedDate(dateString):
    p = parser.parse(dateString)
    return p.strftime("%d/%m/%Y às %H:%M:%S")

def convertToDatetime(dataString):
    return parser.parse( dataString )

class TableHeader(object):
    """ armazena os headers da representação dos dados """
    full = (
        ("Data", "created"),
        ("Hora", "created_hour"),
        ("Plano mensal", "plan_hours"),
        ("Horas Adicionais", "hours_add"),
        ("Horas Totais", "total_hours"),
        ("Horas Estimadas", "estimated"),
        ("Horas Gastas", "spent"),
        ("Horas Restantes", "remainder")
    )
    simple = (
        ("Data", "created"),
        ("Hora", "created_hour"),
        ("ID", "id"),
        ("Assunto", "subject"),
        ("Horas Estimadas", "estimated"),
        ("Horas Gastas", "spent")
    )
    @classmethod
    def get_full(cls):
        return [e[0] for e in cls.full]
    @classmethod
    def get_full_item(cls):
        return [e[-1] for e in cls.full]
    @classmethod
    def get_simple(cls):
        return [e[0] for e in cls.simple]
    @classmethod
    def get_simple_item(cls):
        return [e[-1] for e in cls.simple]
    @classmethod
    def getBaseDict(cls, full=True):
        if full: headers = cls.get_full_item()
        else: headers = cls.get_simple_item()
        return dict([(key,None) for key in headers])
    
########################################################################
class DateInputForm(admin.HoursAddForm):
    """ cria inputs(html) de dados uma data(ano,mês) """
    class Meta:
        model = admin.HoursAdd
        fields = ("period", )
        
########################################################################
class Statistic(object):
    """ gera a soma de todas as horas gastas das taferas encontradas """
    #----------------------------------------------------------------------
    def __init__(self, project_id, year=0, month=0, **params):
        self.params = params
        self.project_id = project_id
        
        self.project = project = Project.objects.get(key=project_id)
        try: self.yearlyplan = project.yearlyplan_set.get(created_at__year=year)
        except: self.yearlyplan = None
        
        self.date = self.getDateForYearMonth(year, month)
        
        # guarda as horas consumidas de todos o meses
        self.yearlySpent = 0.0
        self.yearlyExtra = 0.0
        
    def update(self, year, month):
        self.date = date = self.getDateForYearMonth(year, month)
        try:
            # procura o plano mensal do dentro do plano anual
            monthlyPlan = self.yearlyplan.monthlyplan_set.filter(
                starts__lte = date.isoformat(), 
                finished__gt = date.isoformat()
            )
            if monthlyPlan.count() > 0:
                # Plano com periodo inicial, porém final ilimitado.
                monthlyPlan = monthlyPlan[monthlyPlan.count()-1]
                plan_hours = monthlyPlan.hours
            else:
                # Plano mensal com témino ilimitado.
                monthlyPlan = self.yearlyplan.monthlyplan_set.filter(
                    starts__lte = date.isoformat(), finished = None
                )
                if monthlyPlan.count() > 0:
                    monthlyPlan = monthlyPlan[monthlyPlan.count()-1]
                    plan_hours = monthlyPlan.hours
                else:
                    plan_hours = 0.0 # o plano ainda não existe.
            try: # pesquisando as horas adicionais, atreladas ao plano mensal.
                hours_add = sum([
                    hoursadd.hours 
                    for hoursadd in self.yearlyplan.hoursadd_set.filter(
                        period__month = month, period__year = year
                    )
                ])
            except:
                hours_add = 0.0
            total_hours = plan_hours + hours_add
        except Exception as e:
            print "Search in database: %s" % e
            plan_hours = hours_add = total_hours = 0.0
        
        self.statistic = {
            "estimated": 0.0, "spent": 0.0,
            "project": self.project.name,
            "yearly_hours": self.yearly_hours,
            "created": date.strftime("%m/%Y"),
            "total_hours": total_hours,
            "plan_hours": plan_hours,
            "hours_add":  hours_add,
            "remainder": 0.0,
        }
        # soma de todas as horas, adicionais, do ano.
        self.add_yearly_extra( hours_add )
        
    def __str__(self):
        return "\n".join(["%s: %s"%(k, self.statistic[k])for k in self.statistic])
    
    @property
    def hasYearlyPlan(self):
        """ avalia se algum plano válido foi encontrado para o mês/ano"""
        return bool(self.yearlyplan)
    
    def isValidMonthYear(self, month, year):
        """ verifica se o mês e o ano são cobertos pelo plano anual """
        start_dt = self.yearlyplan.getStartDate()
        return (start_dt.month <= month and start_dt.year <= year)
    
    @property
    def checkMonthYear(self):
        date = self.get_date()
        return self.isValidMonthYear(date.month, date.year)
    
    def get(self, name, default):
        return self.statistic.get(name, default)
    
    def add_yearly_spent(self, v):
        self.yearlySpent += v
        
    def add_yearly_extra(self, v):
        self.yearlyExtra += v
    
    @property
    def yearly_spent(self):
        return self.yearlySpent
    
    @property
    def yearly_extra(self):
        return self.yearlyExtra
    
    @property
    def yearly_hours(self):
        """ plano de horas anuais. se inexistente, sempre retorna zero."""
        return getattr(self.yearlyplan,"hours",0.0)
    
    @property
    def yearly_total_hours(self):
        return (self.yearly_hours + self.yearly_extra)
    
    @property
    def yearly_remainder(self):
        return (self.yearly_total_hours - self.yearly_spent)
    
    @property
    def yearlyPlanStartDate(self):
        """ retorna a data inicial do plano anual """
        method = getattr(self.yearlyplan,"getStartDate",datetime.datetime.now)
        return method()
    
    @staticmethod
    def getDateForYearMonth(year, month):
        now = datetime.datetime.now()
        
        if not month: month = now.month
        if not year: year = now.year
        
        maxdays = calendar.monthrange(year, month)[-1]
        d = datetime.datetime(year, month, maxdays)
        return d.date()
    
    def __getitem__(self, key):
        return self.statistic[key]

    def __setitem__(self, key, value):
        self.statistic[key] = value
        
    def get_date(self):
        return self.date
    
    def get_data(self):
        return self.statistic