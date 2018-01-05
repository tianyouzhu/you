# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Order.charge'
        db.alter_column(u'subscription_order', 'charge', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

        # Changing field 'Order.month_price'
        db.alter_column(u'subscription_order', 'month_price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

        # Changing field 'Order.day_unit_price'
        db.alter_column(u'subscription_order', 'day_unit_price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

        # Changing field 'Order.paid_price'
        db.alter_column(u'subscription_order', 'paid_price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2))

    def backwards(self, orm):

        # Changing field 'Order.charge'
        db.alter_column(u'subscription_order', 'charge', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Order.month_price'
        db.alter_column(u'subscription_order', 'month_price', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Order.day_unit_price'
        db.alter_column(u'subscription_order', 'day_unit_price', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Order.paid_price'
        db.alter_column(u'subscription_order', 'paid_price', self.gf('django.db.models.fields.IntegerField')())

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
            'charge': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'}),
            'company_name': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00:00'", 'auto_now_add': 'True', 'blank': 'True'}),
            'day_unit_price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'}),
            'domain_name': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '128'}),
            'expire_time': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00:00'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice_flag': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'month_price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'}),
            'number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'paid_price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '10', 'decimal_places': '2'}),
            'paid_time': ('django.db.models.fields.DateTimeField', [], {'default': "'1970-01-01 00:00:00'"}),
            'pay_plan': ('django.db.models.fields.CharField', [], {'default': "'None'", 'max_length': '255'}),
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