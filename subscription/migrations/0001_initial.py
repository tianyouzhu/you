# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Order'
        db.create_table(u'subscription_order', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='init', max_length=128)),
            ('create_time', self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00:00', auto_now_add=True, blank=True)),
            ('volume', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('duration', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('charge', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('month_price', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('day_unit_price', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('paid_time', self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00:00')),
            ('pre_validate_time', self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00:00')),
            ('validate_time', self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00:00')),
            ('pre_expire_time', self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00:00')),
            ('expire_time', self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00:00')),
            ('token', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('domain_name', self.gf('django.db.models.fields.CharField')(default='None', max_length=128)),
            ('account_name', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('invoice_flag', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('company_name', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('post_address', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('contact_name', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('contact_phone', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
        ))
        db.send_create_signal(u'subscription', ['Order'])

        # Adding model 'Operation'
        db.create_table(u'subscription_operation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['subscription.Order'])),
            ('action', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
            ('time', self.gf('django.db.models.fields.DateTimeField')(default='1970-01-01 00:00:00', auto_now_add=True, blank=True)),
            ('operator_name', self.gf('django.db.models.fields.CharField')(default='None', max_length=255)),
        ))
        db.send_create_signal(u'subscription', ['Operation'])


    def backwards(self, orm):
        # Deleting model 'Order'
        db.delete_table(u'subscription_order')

        # Deleting model 'Operation'
        db.delete_table(u'subscription_operation')


    models = {
        u'subscription.operation': {
            'Meta': {'object_name': 'Operation'},
            'action': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'operator_name': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['subscription.Order']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00:00'", 'auto_now_add': 'True', 'blank': 'True'})
        },
        u'subscription.order': {
            'Meta': {'object_name': 'Order'},
            'account_name': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'charge': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'company_name': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00:00'", 'auto_now_add': 'True', 'blank': 'True'}),
            'day_unit_price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'domain_name': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '128'}),
            'duration': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'expire_time': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00:00'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'month_price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'paid_time': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00:00'"}),
            'post_address': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'pre_expire_time': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00:00'"}),
            'pre_validate_time': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00:00'"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'init'", 'max_length': '128'}),
            'token': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'validate_time': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00:00'"}),
            'volume': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['subscription']