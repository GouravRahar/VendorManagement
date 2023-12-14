from rest_framework import serializers

from .models import Vendor, PurchaseOrder


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ('name', 'contact_details', 'address')


class IdSerializer(serializers.Serializer):
    id = serializers.UUIDField(allow_null=False)


class POSerializer(serializers.ModelSerializer):
    vendor = serializers.UUIDField()
    # delivery_date = serializers.DateField(allow_null=True)

    class Meta:
        model = PurchaseOrder
        exclude = ('issue_date', 'po_number', 'order_date')
