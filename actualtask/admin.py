from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.postgres.fields import JSONField
from prettyjson import PrettyJSONWidget

from .models import Vendor, PurchaseOrder, HistoricalPerformance


# Register your models here.

class JsonModelAdmin(BaseModelAdmin):
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_details', 'address', 'on_time_delivery_rate', 'quality_rating_avg',
                    'average_response_time', 'fulfillment_rate')
    list_filter = ('created_at', 'updated_at')


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin, JsonModelAdmin):
    list_display = ('vendor', 'items', 'quantity', 'issue_date')
    readonly_fields = ('po_number','quality_rating', 'acknowledge_date', 'status', 'delivery_date')
    list_filter = ('created_at', 'updated_at')
    raw_id_fields = ['vendor']


@admin.register(HistoricalPerformance)
class HistoricalPerformanceAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'date', 'on_time_delivery_rate', 'quality_rating_avg', 'average_response_time',
                    'fulfillment_rate')
    list_filter = ('created_at', 'updated_at')
    raw_id_fields = ['vendor']
