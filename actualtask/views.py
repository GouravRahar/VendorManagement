from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.decorators import action

from .helpers import UpdateMetrics, UpdatePO
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from .serializers import VendorSerializer, IdSerializer, POSerializer


# Create your views here.
class VendorProfileViewset(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):
        data = request.GET
        try:
            all_vendors = Vendor.objects.all()
            ser_data = VendorSerializer(all_vendors, many=True).data
            Resp = list()
            for data in ser_data:
                Resp.append(data)
            return Response(data=Resp, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data=f"Some Error Occurred while Fetching Data, {e}",
                            status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None, *args, **kwargs):
        vendor_id = dict(id=pk)
        ser = IdSerializer(data=vendor_id)
        if ser.is_valid():
            try:
                vendor = Vendor.objects.get(id=ser.validated_data['id'])
                return Response(data=dict(VendorID=vendor.id, Name=vendor.name), status=status.HTTP_200_OK)
            except Vendor.DoesNotExist:
                return Response(data="Please Provide a Valid ID of Vendor", status=status.HTTP_404_NOT_FOUND)
        return Response(data=f"Cannot Fetch details of this ID, {ser.errors}", status=status.HTTP_400_BAD_REQUEST)
        pass

    def create(self, request, *args, **kwargs):
        data = request.data
        ser = VendorSerializer(data=data)
        if ser.is_valid():
            name = ser.validated_data['name']
            contact_details = ser.validated_data['contact_details']
            address = ser.validated_data['address']
            try:
                vendor_data = Vendor.objects.create(name=name, contact_details=contact_details, address=address)
            except Exception as e:
                print(e)
                return Response(data=f'Some Error occurred while saving Vendor, {e}',
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(data=dict(VendorID=vendor_data.id, Name=name), status=status.HTTP_201_CREATED)
        return Response(data=f"Data Provided is Incorrect, {ser.errors}", status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        data = request.data
        ser = VendorSerializer(data=data, partial=True)
        if ser.is_valid():
            try:
                vendor = Vendor.objects.get(id=pk)
                ser_data = ser.validated_data
                for key, val in ser_data.items():
                    if key == ('name' or 'address' or 'contact_details'):
                        setattr(vendor, key, val)
                vendor.save()
                return Response(data=dict(VendorID=vendor.id, Name=vendor.name), status=status.HTTP_200_OK)
            except Vendor.DoesNotExist:
                return Response(data="Please Provide a Valid ID of Vendor", status=status.HTTP_404_NOT_FOUND)
        return Response(data="There was some error while updating the field")

    def destroy(self, request, pk=None, *args, **kwargs):
        vendor_id = pk
        ser = IdSerializer(data=vendor_id)
        if ser.is_valid():
            try:
                vendor = Vendor.objects.get(id=ser.validated_data['id'])
                vendor.delete()
                return Response(data="Vendor Deleted Successfully", status=status.HTTP_200_OK)
            except Vendor.DoesNotExist:
                return Response(data="Please Provide a Valid ID of Vendor", status=status.HTTP_404_NOT_FOUND)
        return Response(data=f"Cannot Fetch details of this ID, {ser.errors}", status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        vendor_id = dict(id=pk)
        ser = IdSerializer(data=vendor_id)
        if ser.is_valid():
            v_id = ser.validated_data['id']
            try:
                vendor = Vendor.objects.get(id=v_id)
                performance = HistoricalPerformance.objects.create(vendor=vendor, date=timezone.now(),
                                                                   on_time_delivery_rate=vendor.on_time_delivery_rate,
                                                                   quality_rating_avg=vendor.quality_rating_avg,
                                                                   average_response_time=vendor.average_response_time,
                                                                   fulfillment_rate=vendor.fulfillment_rate)
                return Response(data=dict(Vendor=vendor.name, FulFillmentRate=(100 * vendor.fulfillment_rate),
                                          OnTimeDelivery=(100 * vendor.on_time_delivery_rate),
                                          QualityRating=vendor.quality_rating_avg,
                                          ResponseTime=vendor.average_response_time), status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data="Please Provide Correct Vendor ID", status=status.HTTP_404_NOT_FOUND)
        return Response(data=f"Id format is incorrect,{ser.errors}", status=status.HTTP_400_BAD_REQUEST)


class PurchaseOrderViewset(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):
        data = request.GET
        result = list()
        vendors = PurchaseOrder.objects.all()
        if data:
            try:
                ser = IdSerializer(data=dict(id=data['vendor']))
                if ser.is_valid():
                    vid = ser.validated_data['id']
                    vendors = vendors.filter(vendor__id=vid)
                else:
                    raise ValueError("Incorrect Vendor ID")
            except Exception as e:
                return Response(data=f"Please Provide Correct Vendor ID, {e}",
                                status=status.HTTP_404_NOT_FOUND)
        for vendor in vendors:
            result.append(dict(Items=vendor.items, Quantity=vendor.quantity, OrderDate=vendor.order_date,
                               Status=vendor.status, DeliveryDate=vendor.delivery_date))
        return Response(data=result, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        order_id = pk
        ser = IdSerializer(data=dict(id=order_id))
        if ser.is_valid():
            order_id = ser.validated_data['id']
            try:
                order = PurchaseOrder.objects.get(id=order_id)
                return Response(data=dict(Items=order.items, Quantity=order.quantity, Status=order.status,
                                          OrderDate=order.order_date, DeliveryDate=order.delivery_date),
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data=f"Please provide correct order id, {e}",
                                status=status.HTTP_404_NOT_FOUND)
        return Response(data=f"Unable to fetch your order, {ser.errors}",
                        status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        data = request.data
        ser = POSerializer(data=data)
        if ser.is_valid():
            ser_data = ser.validated_data
            vendor_id = ser_data['vendor']
            items = ser_data['items']
            quantity = ser_data['quantity']
            try:
                po = PurchaseOrder(vendor_id=vendor_id, items=items, quantity=quantity)
                po.po_number = str(po.id)
                po.save()
                return Response(data=f"Order Created Successfully, Your order id is: {po.id}",
                                status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data=f"Unable to create your order due to some error, {e}",
                                status=status.HTTP_400_BAD_REQUEST)
        return Response(data=f"Unable to create your order due to some error, {ser.errors}",
                        status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None, *args, **kwargs):
        order_id = pk
        data = request.data
        order = IdSerializer(data=dict(id=order_id))
        ser = POSerializer(data=data, partial=True)
        if ser.is_valid() and order.is_valid():
            order_id = order.validated_data['id']
            ser_data = ser.validated_data
            ans, output_message = UpdatePO(po_id=order_id, update_data=ser_data).update_fields()
            if ans:
                return Response(data=output_message, status=status.HTTP_200_OK)
            else:
                return Response(data=output_message, status=status.HTTP_404_NOT_FOUND)
        return Response(data=f"Please Provide valid Update fields and Order ID, {ser.errors}",
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        order_id = dict(id=pk)
        id_ser = IdSerializer(data=order_id)
        if id_ser.is_valid():
            try:
                order = PurchaseOrder.objects.get(id=id_ser.validated_data['id'])
                if not order.acknowledge_date:
                    raise ValueError("You cannot Acknowledge a order Twice")
                UpdateMetrics(order).update_average_response_time()
                order.acknowledge_date = timezone.now()
                order.save()
                return Response(data="Order has been acknowledged, Thank You!", status=status.HTTP_200_OK)
            except Exception as e:
                return Response(data="This Order cannot be acknowledged", status=status.HTTP_404_NOT_FOUND)
        return Response(data="Please Provide valid Acknowledgement and order id", status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        order_id = dict(id=pk)
        order = IdSerializer(data=order_id)
        if order.is_valid():
            order_id = order.validated_data['id']
            try:
                order = PurchaseOrder.objects.get(id=order_id)
                order.delete()
                return Response(data="Order details have been deleted successfully", status=status.HTTP_200_OK)
            except Exception as e:
                return Response(f"Please provide correct order id, {e}", status=status.HTTP_404_NOT_FOUND)
        return Response(data=f"Unable to delete your order, {order.errors}",
                        status=status.HTTP_400_BAD_REQUEST)

# class
