# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'YearlyPlan.project'
        db.add_column('main_yearlyplan', 'project',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['main.Project']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'YearlyPlan.project'
        db.delete_column('main_yearlyplan', 'project_id')


    models = {
        'main.hoursadd': {
            'Meta': {'object_name': 'HoursAdd'},
            'hours': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monthlyPlan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.MonthlyPlan']"}),
            'period': ('django.db.models.fields.DateField', [], {})
        },
        'main.monthlyplan': {
            'Meta': {'object_name': 'MonthlyPlan'},
            'finished': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'hours': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'starts': ('django.db.models.fields.DateField', [], {}),
            'yearlyplan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.YearlyPlan']"})
        },
        'main.project': {
            'Meta': {'object_name': 'Project'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        'main.yearlyplan': {
            'Meta': {'object_name': 'YearlyPlan'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created_at': ('django.db.models.fields.DateField', [], {}),
            'hours': ('django.db.models.fields.FloatField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Project']"})
        }
    }

    complete_apps = ['main']