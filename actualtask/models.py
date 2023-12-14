import uuid

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Manager
from django.utils.translation import gettext_lazy as _


class TimeStampedUUIDModel(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    created_at = models.TimeField(auto_now_add=True, editable=False)
    updated_at = models.TimeField(auto_now=True, editable=False)

    class Meta:
        abstract = True


class Vendor(TimeStampedUUIDModel):
    name = models.CharField('Name', max_length=50)
    contact_details = models.TextField('Contact Details')
    address = models.TextField('Address')
    on_time_delivery_rate = models.FloatField(_('On Time Delivery Rate'), null=True, blank=True, default=0)
    quality_rating_avg = models.FloatField(_('Quality Rating Average'), null=True, blank=True, default=0)
    average_response_time = models.FloatField(_('Average Response Time'), null=True, blank=True, default=0)
    fulfillment_rate = models.FloatField(_('Fulfillment Rate'), null=True, blank=True, default=0)
    objects = Manager()

    class Meta:
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'

    def __str__(self):
        return f'{self.name}'


class PurchaseOrder(TimeStampedUUIDModel):
    ACTION_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    )
    po_number = models.CharField(unique=True, max_length=50)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField(_('Order Date'), auto_now_add=True)
    delivery_date = models.DateTimeField(_('Delivery Date'), null=True, blank=True)
    items = models.JSONField(verbose_name='Items Ordered')
    quantity = models.IntegerField('Quantity', default=1, validators=[MinValueValidator(1)])
    status = models.CharField(verbose_name='Order Status', default='Pending', choices=ACTION_CHOICES, max_length=15)
    quality_rating = models.FloatField('Quality Rating', null=True, blank=True, validators=[MinValueValidator(0),
                                                                                            MaxValueValidator(10)])
    issue_date = models.DateTimeField('Date Issued', auto_now_add=True, editable=False)
    acknowledge_date = models.DateTimeField('Acknowledgement Date', null=True, blank=True)
    objects = Manager()

    class Meta:
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'


class HistoricalPerformance(TimeStampedUUIDModel):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField(_('On Time Delivery Rate'), blank=True, null=True)
    quality_rating_avg = models.FloatField(_('Quality Rating Average'), null=True, blank=True)
    average_response_time = models.FloatField(_('Average Rating Response'), null=True, blank=True)
    fulfillment_rate = models.FloatField(_('Fulfillment Rate'), null=True, blank=True)
    objects = Manager()

    class Meta:
        verbose_name = 'Historical Performance'
        verbose_name_plural = 'Historical Performances'
