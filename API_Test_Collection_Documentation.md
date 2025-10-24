# API Test Collection – Postman Documentation

This documentation describes the API endpoints, methods, and associated Postman test scripts for the `API_Test_Collection`.

---

## **Base URL**
```
{{baseUrl}}
```

All endpoints in this collection are relative to the `{{baseUrl}}` environment variable.

---

## **1. System Requests**

### **1.1 Initialize App**
**Method:** `POST`  
**Endpoint:** `{{baseUrl}}/system/init`

**Description:**  
Initializes the application or server system before authentication requests.

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest("Admin Login");
```

---

## **2. Authentication Requests**

### **2.1 Admin Login**
**Method:** `POST`  
**Endpoint:** `{{baseUrl}}/admin/login`

**Body (JSON):**
```json
{
    "username": "admin1",
    "password": "adminpass1"
}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest("List Staff");
```

---

### **2.2 Admin Logout**
**Method:** `POST`  
**Endpoint:** `{{baseUrl}}/admin/logout`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest("Staff Login");
```

---

### **2.3 Staff Login**
**Method:** `POST`  
**Endpoint:** `{{baseUrl}}/staff/login`

**Body (JSON):**
```json
{
    "username": "bob",
    "password": "bobpass"
}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest("View Profile");
```

---

### **2.4 Staff Logout**
**Method:** `POST`  
**Endpoint:** `{{baseUrl}}/staff/logout`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest(null);
```

---

## **3. Admin Requests**

### **3.1 List Staff**
**Method:** `GET`  
**Endpoint:** `{{baseUrl}}/admin/staff`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest("Add Staff");
```

---

### **3.2 Add Staff**
**Method:** `POST`  
**Endpoint:** `{{baseUrl}}/admin/staff`

**Body (JSON):**
```json
{
    "username": "{{$randomUserName}}",
    "email": "{{$randomEmail}}",
    "password": "{{$randomPassword}}",
    "role": "{{$randomJobTitle}}",
    "type": "staff"
}
```

**Tests:**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

postman.setNextRequest("Delete Staff");
```

---

### **3.3 Delete Staff**
**Method:** `DELETE`  
**Endpoint:** `{{baseUrl}}/admin/staff/:staff_id`

**Path Variable:**
```
staff_id = 8
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest("Schedule Shift");
```

---

### **3.4 Schedule Shift**
**Method:** `POST`  
**Endpoint:** `{{baseUrl}}/admin/shifts`

**Body (JSON):**
```json
{
    "staffId": 4,
    "start": "2025-03-31T08:00",
    "end": "2025-03-31T14:00"
}
```

**Tests:**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

postman.setNextRequest("List Shifts");
```

---

### **3.5 List Shifts**
**Method:** `GET`  
**Endpoint:** `{{baseUrl}}/admin/shifts`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest("Generate Report");
```

---

### **3.6 Generate Report**
**Method:** `POST`  
**Endpoint:** `{{baseUrl}}/admin/roster/:roster_id/report`

**Path Variable:**
```
roster_id = 1
```

**Tests:**
```javascript
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

postman.setNextRequest("Admin Logout");
```

---

## **4. Staff Requests**

### **4.1 View Profile**
**Method:** `GET`  
**Endpoint:** `{{baseUrl}}/staff/profile`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest("View Roster");
```

---

### **4.2 View Roster**
**Method:** `GET`  
**Endpoint:** `{{baseUrl}}/staff/roster`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest("My Shifts");
```

---

### **4.3 My Shifts**
**Method:** `GET`  
**Endpoint:** `{{baseUrl}}/staff/my-shifts`

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest("Time In");
```

---

### **4.4 Time In**
**Method:** `POST`  
**Endpoint:** `{{baseUrl}}/staff/shifts/:shift_id/time-in`

**Path Variable:**
```
shift_id = 20
```

**Body (JSON):**
```json
{
    "timestamp": "2025-10-04T11:15:00"
}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest("Time Out");
```

---

### **4.5 Time Out**
**Method:** `POST`  
**Endpoint:** `{{baseUrl}}/staff/shifts/:shift_id/time-out`

**Path Variable:**
```
shift_id = 20
```

**Body (JSON):**
```json
{
    "timestamp": "2025-10-04T18:45:00"
}
```

**Tests:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

postman.setNextRequest("Staff Logout");
```

---

## **Collection Variables**
| Variable | Example Value |
|-----------|----------------|
| `baseUrl` | *to be defined in environment* |

---

## **Execution Flow Summary**
This collection is designed to run as a chain of requests using `postman.setNextRequest()`:

1. Initialize App →  
2. Admin Login →  
3. List Staff →  
4. Add Staff →  
5. Delete Staff →  
6. Schedule Shift →  
7. List Shifts →  
8. Generate Report →  
9. Admin Logout →  
10. Staff Login →  
11. View Profile →  
12. View Roster →  
13. My Shifts →  
14. Time In →  
15. Time Out →  
16. Staff Logout → End.

---

**End of Documentation**
