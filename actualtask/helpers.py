from datetime import datetime

from django.db.models import F, Sum
from django.utils import timezone
from .models import PurchaseOrder


class UpdatePO:
    def __init__(self, po_id, update_data):
        self.po_id = po_id
        self.data = update_data

    def update_fields(self):
        try:
            order = PurchaseOrder.objects.get(id=self.po_id)
            update_metrics = UpdateMetrics(order)
            result = list()
            for key, value in self.data.items():
                if key == 'quality_rating' and order.status == 'Completed' and not order.quality_rating:
                    update_metrics.update_quality_rating(rating=value)
                    result.append(key)
                    setattr(order, key, value)
                elif key == 'status' and order.status != value:
                    update_metrics.update_fulfillment_rate(status=value)
                    if value == 'Completed':
                        update_metrics.update_on_time_delivery_rate()
                    result.append(key)
                    setattr(order, key, value)
                elif key == 'delivery_date' and order.status != 'Complete' and value:
                    result.append(key)
                    setattr(order, key,value)
                order.save()
            return True, f"{result} Fields have been updated of order"
        except Exception as e:
            return False, f"Please provide correct order ID or correct fields,{e}"


class UpdateMetrics:
    def __init__(self, order):
        self.order = order
        self.count = PurchaseOrder.objects.filter(vendor=order.vendor).count()
        self.vendor = order.vendor

    def update_on_time_delivery_rate(self):
        complete_count = PurchaseOrder.objects.filter(vendor=self.vendor, status='Completed',
                                                      delivery_date__lt=F("issue_date")).count()
        if self.order.delivery_date > timezone.now():
            self.vendor.on_time_delivery_rate = complete_count + 1 / self.count
        else:
            self.vendor.on_time_delivery_rate = complete_count / self.count
        self.vendor.save()

    def update_quality_rating(self, rating):
        rated_orders = (PurchaseOrder.objects.filter(vendor=self.vendor, status='Completed',
                                                     quality_rating__isnull=False).
                        aggregate(avg_rating=Sum('quality_rating')))
        avg_rating = rated_orders['avg_rating'] if rated_orders['avg_rating'] is not None else 0.0
        self.vendor.quality_rating_avg = (avg_rating + rating) / self.count
        self.vendor.save()

    def update_average_response_time(self):
        time_diff = timezone.now() - self.order.issue_date
        days_diff = time_diff.days
        orders = (PurchaseOrder.objects.filter(vendor=self.vendor, acknowledge_date__isnull=False)
                  .aggregate(avg_time=Sum(F("acknowledge_date") - F("issue_date"))))
        avg_resp_time = orders['avg_time'].days if orders['avg_time'].days is not None else 0.0
        self.vendor.average_response_time = (avg_resp_time + days_diff) / self.count
        self.vendor.save()

    def update_fulfillment_rate(self, status):
        order = PurchaseOrder.objects.filter(vendor=self.vendor, status='Completed').count()
        if status != 'Completed':
            self.vendor.fulfillment_rate = order / self.count
        else:
            self.vendor.fulfillment_rate = (order + 1) / self.count
        self.vendor.save()
