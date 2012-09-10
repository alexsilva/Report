# -*- coding: utf-8 -*-
from django.db import models
import datetime

########################################################################
class Project( models.Model ):
	## CharField cannot have a "max_length" greater than 255 when using "unique=True".
	key = models.CharField("Indentificador", max_length=255, unique=True) # 
	name = models.CharField("Nome", max_length=300)
	
	class Meta:
		verbose_name = "Projeto"
		verbose_name_plural = "Projetos"
		
	def __unicode__(self):
		return (self.name or self.key)
	
########################################################################
class YearlyPlan(models.Model):
	project = models.ForeignKey(Project, verbose_name=Project._meta.verbose_name)
	created_at = models.DateField("Apartir de", help_text=u"O plano torna-se válido, apartir da data.")
	active = models.BooleanField("Ativo", help_text=u"O plano deve ser considerado válido?", default=True)
	active_text = {True:"Ativo", False:"Inativo"} # indica apartir do texto
	hours = models.FloatField("Horas")
	
	class Meta:
		verbose_name = "Plano anual"
		verbose_name_plural = "Planos anuais"
		
	def __unicode__(self):
		active = self.active_text[ self.active ]
		return u"%s - %s hora(s)(%s)"%(
		    self.project, self.hours, active,
		)
	
	@property
	def remaingDays(self):
		""" informa o número de dias restantes para esse plano """
		expire_date = datetime.date(
		    self.created_at.year+1, self.created_at.month, 
		    self.created_at.day)
		now = datetime.datetime.now()
		now_date = now.date()
		delta = expire_date - now_date
		return delta.days # dias restantes
	
	@property
	def expired(self):
		""" avalia se o plano expirou, com base no números de dias restantes """
		return (not self.remaingDays > 0)
	
	@property
	def _is_active(self):
		""" ativo se não expirado e for um plano válido """
		return (not self.expired and self.active)
	
	def getStartDate(self):
		""" retorna a data em que o plano começou """
		return self.created_at
	
########################################################################
class MonthlyPlan( models.Model ):
	yearlyplan = models.ForeignKey(YearlyPlan, verbose_name=YearlyPlan._meta.verbose_name)
	
	hours = models.FloatField("Plano mensal")
	starts = models.DateField("Apartir de", help_text=u"O plano será válido, apartir desse mês.")
	finished = models.DateField("Terminou em", blank=True, null=True)
	
	class Meta:
		verbose_name = "Plano mensal"
		verbose_name_plural = "Planos mensais"
		
	def __unicode__(self):
		projeto = "Plano anual: %s"%self.yearlyplan
		
		from_month = u"De: " + self.starts.strftime("%m/%Y")
		to_month = u"Até: "
		
		try: to_month += self.finished.strftime("%m/%Y")
		except: to_month += u"Indefinido"
		
		horas_mensais = u"Horas mensais: %.2fh (%s - %s)"%(self.hours, from_month, to_month)
		return u"%s - %s"%(projeto, horas_mensais)
	
########################################################################
class HoursAdd( models.Model ):
	monthlyPlan = models.ForeignKey(MonthlyPlan, verbose_name = MonthlyPlan._meta.verbose_name)
	hours = models.FloatField("Horas adicionais", blank=True, null=True)
	period = models.DateField(u"No mês", help_text=u"Mês, dentro do qual, a hora adicional terá validade.")
	
	class Meta:
		verbose_name = "Hora adicional"
		verbose_name_plural = "Horas adicionais"
		
	def __unicode__(self):
		return u"%.2fh (%s)" %((self.hours or 0.0), u"Para o mês: "+self.period.strftime("%m/%Y"))