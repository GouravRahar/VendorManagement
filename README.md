# Vendor Profile Management


## Project Setup Guide

Follow these steps to set up and run the Vendor Management System project.

### Prerequisites
Ensure you have the following installed on your system:

 - Python (version 3.6 or higher)
 - Database (SQLite or any other supported by Django)

   
### Steps to Set Up
1. Clone the Repository:

```
git clone https://github.com/GouravRahar/VendorManagement.git
cd vendor-management-system
```

2. Create and Activate Virtual Environment:


```
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

3. Install Dependencies:

```
pip install -r requirements.txt
```

4. Apply Migrations:

```
python manage.py migrate
```

5. Create Superuser:

```
python manage.py createsuperuser
```

6. Run the Development Server:

```
python manage.py runserver
```

7. Access the Admin Panel:
   
   Open your browser and go to `http://127.0.0.1:8000/admin/` Log in with the superuser credentials created in step 5.

9. Access API Endpoints:
    
   You can easily interact with the Vendor Management System API using Postman. To streamline your testing process, I've created a Postman collection that includes requests for all the API endpoints.

<br/>

   [![Postman API Collection](https://run.pstmn.io/button.svg)](https://api.postman.com/collections/12167432-eb094d03-3159-42e7-aa72-c5d47ba0c41c?access_key=PMAT-01HHKJMYYM9EHSWFDVF62EPJBR)

     Click the button above to open the collection. Copy the URL and paste that url in Postman Under Import New Collection. This collection includes requests for each API endpoint, allowing you to easily test and explore the functionality of the Vendor Management System.

<br/>


<br/>



## Model Design
### 1. Vendor Model
This model stores essential information about each vendor and their performance metrics.
  #### Fields:
  - Name:  Vendor's name.
  - Contact :   Contact information of the vendor.
  - Address:    Physical address of the vendor.
  - Delivery Rate:    Tracks the percentage of on-time deliveries.
  - Quality:    Average rating of quality based on purchase orders.
  - Response TIme:    Average time taken to acknowledge purchase orders.
  - Fulfillment:    Percentage of purchase orders fulfilled successfully.


### 2. Purchase Order Model
  This model captures the details of each purchase order and is used to calculate various performance metrics.
  #### Fields:
  - Vendor:    Link to the Vendor model.
  - Order Date:    Date when the order was placed.
  - Delivery Date:    Expected or actual delivery date of the order.
  - Items:   Details of items ordered.
  - Quantity:   Total quantity of items in the PO.
  - Order Status:   Current status of the PO (e.g., pending, completed, canceled).
  - Quality Rating:   Rating given to the vendor for this PO (nullable).
  - Issue Date:    Timestamp when the PO was issued to the vendor.
  - Acknowledgement Date:    Timestamp when the vendor acknowledged the PO.

### 3.Performance Model
  This model optionally stores historical data on vendor performance, enabling trend analysis.
  #### Fields:
  - Vendor:    Link to the Vendor model.
  - Date :   Date of the performance record.
  - Delivery Rate:    Tracks the percentage of on-time deliveries.
  - Quality:    Average rating of quality based on purchase orders.
  - Response TIme:    Average time taken to acknowledge purchase orders.
  - Fulfillment:    Percentage of purchase orders fulfilled successfully.

<br/>


## API Endpoints

#### Vendor Profile Management
 - POST /api/vendors/: Create a new vendor.
 - GET /api/vendors/: List all vendors.
 - GET /api/vendors/{vendor_id}/: Retrieve a specific vendor's details.
 - PUT /api/vendors/{vendor_id}/: Update a vendor's details.
 - DELETE /api/vendors/{vendor_id}/: Delete a vendor.

#### Purchase Order Tracking
 - POST /api/purchase_orders/: Create a purchase order.
 - GET /api/purchase_orders/: List all purchase orders with an option to filter by vendor.
 - GET /api/purchase_orders/{po_id}/: Retrieve details of a specific purchase order.
 - PUT /api/purchase_orders/{po_id}/: Update a purchase order.
 - DELETE /api/purchase_orders/{po_id}/: Delete a purchase order.
 - POST /api/purchase_orders/{po_id}/: Acknowledges the Order

#### Vendor Performance Evaluation
 - GET /api/vendors/{vendor_id}/performance/: Retrieve a vendor's performance metrics


<br/>


## Backend Logic for Performance Metrics
 #### 1. On-Time Delivery Rate:
  - Calculated each time a PO status changes to 'completed'.
  - Logic: Count the number of completed POs delivered on or before delivery_date and divide by the total number of completed POs for that vendor.

 #### 2. Quality Rating:
  - Updated upon the completion of each PO where a quality_rating is provided.
  - Logic: Calculate the average of all quality_rating values for completed POs of the vendor.

 #### 3. Response Time:
  - Calculated each time a PO is acknowledged by the vendor.
  - Logic: Compute the time difference between issue_date and acknowledgment_date for each PO, and then find the average of these times for all POs of the vendor.

 #### 4. Fulfilment Rate:
  - Calculated upon any change in PO status.
  - Logic: Divide the number of successfully fulfilled POs (status 'completed' without issues) by the total number of POs issued to the vendor.

