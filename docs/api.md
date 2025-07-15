# AidConnect API Documentation

This document provides detailed information about the AidConnect REST API.

## Authentication

The AidConnect API uses token-based authentication. To authenticate, you need to include an Authorization header in your requests.

```
Authorization: Token <your-token>
```

You can obtain a token by sending a POST request to the `/api-auth/login/` endpoint with your username and password.

## API Endpoints

The AidConnect API provides the following endpoints:

### Users

#### List all users

```
GET /api/users/
```

**Response**:
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "",
    "last_name": "",
    "role": "admin"
  },
  {
    "id": 2,
    "username": "manager1",
    "email": "",
    "first_name": "",
    "last_name": "",
    "role": "case_manager"
  }
]
```

#### Get a specific user

```
GET /api/users/{id}/
```

**Response**:
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "",
  "last_name": "",
  "role": "admin"
}
```

#### Create a new user

```
POST /api/users/
```

**Request**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "securepassword",
  "role": "field_officer"
}
```

**Response**:
```json
{
  "id": 4,
  "username": "newuser",
  "email": "newuser@example.com",
  "first_name": "",
  "last_name": "",
  "role": "field_officer"
}
```

### Beneficiaries

#### List all beneficiaries

```
GET /api/beneficiaries/
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "dob": "1990-01-01",
    "gender": "male",
    "address": "123 Main St, City",
    "created_at": "2023-06-01T10:00:00Z",
    "updated_at": "2023-06-01T10:00:00Z"
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "dob": "1985-05-15",
    "gender": "female",
    "address": "456 Oak Ave, Town",
    "created_at": "2023-06-02T11:30:00Z",
    "updated_at": "2023-06-02T11:30:00Z"
  }
]
```

#### Get a specific beneficiary

```
GET /api/beneficiaries/{id}/
```

**Response**:
```json
{
  "id": 1,
  "name": "John Doe",
  "dob": "1990-01-01",
  "gender": "male",
  "address": "123 Main St, City",
  "created_at": "2023-06-01T10:00:00Z",
  "updated_at": "2023-06-01T10:00:00Z"
}
```

#### Create a new beneficiary

```
POST /api/beneficiaries/
```

**Request**:
```json
{
  "name": "New Beneficiary",
  "dob": "1995-10-20",
  "gender": "female",
  "address": "789 Pine St, Village"
}
```

**Response**:
```json
{
  "id": 3,
  "name": "New Beneficiary",
  "dob": "1995-10-20",
  "gender": "female",
  "address": "789 Pine St, Village",
  "created_at": "2023-06-10T09:45:00Z",
  "updated_at": "2023-06-10T09:45:00Z"
}
```

### Cases

#### List all cases

```
GET /api/cases/
```

**Response**:
```json
[
  {
    "id": 1,
    "title": "Initial Assessment",
    "beneficiary": 1,
    "beneficiary_name": "John Doe",
    "case_manager": 2,
    "case_manager_name": "manager1",
    "status": "open",
    "description": "Initial assessment for new beneficiary",
    "opened_date": "2023-06-01T10:30:00Z",
    "closed_date": null,
    "notes": [],
    "assessments": [],
    "created_at": "2023-06-01T10:30:00Z",
    "updated_at": "2023-06-01T10:30:00Z"
  }
]
```

#### Get a specific case

```
GET /api/cases/{id}/
```

**Response**:
```json
{
  "id": 1,
  "title": "Initial Assessment",
  "beneficiary": 1,
  "beneficiary_name": "John Doe",
  "case_manager": 2,
  "case_manager_name": "manager1",
  "status": "open",
  "description": "Initial assessment for new beneficiary",
  "opened_date": "2023-06-01T10:30:00Z",
  "closed_date": null,
  "notes": [
    {
      "id": 1,
      "case": 1,
      "created_by": 2,
      "created_by_username": "manager1",
      "content": "Initial meeting with beneficiary completed",
      "created_at": "2023-06-01T11:00:00Z",
      "updated_at": "2023-06-01T11:00:00Z"
    }
  ],
  "assessments": [
    {
      "id": 1,
      "title": "Needs Assessment",
      "description": "Basic needs assessment",
      "case": 1,
      "created_by": 3,
      "created_by_username": "officer1",
      "questions": [],
      "created_at": "2023-06-02T09:00:00Z",
      "updated_at": "2023-06-02T09:00:00Z"
    }
  ],
  "created_at": "2023-06-01T10:30:00Z",
  "updated_at": "2023-06-01T10:30:00Z"
}
```

#### Create a new case

```
POST /api/cases/
```

**Request**:
```json
{
  "title": "Follow-up Assessment",
  "beneficiary": 1,
  "case_manager": 2,
  "status": "open",
  "description": "Follow-up assessment after initial intervention"
}
```

**Response**:
```json
{
  "id": 2,
  "title": "Follow-up Assessment",
  "beneficiary": 1,
  "beneficiary_name": "John Doe",
  "case_manager": 2,
  "case_manager_name": "manager1",
  "status": "open",
  "description": "Follow-up assessment after initial intervention",
  "opened_date": "2023-06-10T10:00:00Z",
  "closed_date": null,
  "notes": [],
  "assessments": [],
  "created_at": "2023-06-10T10:00:00Z",
  "updated_at": "2023-06-10T10:00:00Z"
}
```

### Case Notes

#### List all case notes

```
GET /api/case-notes/
```

**Response**:
```json
[
  {
    "id": 1,
    "case": 1,
    "created_by": 2,
    "created_by_username": "manager1",
    "content": "Initial meeting with beneficiary completed",
    "created_at": "2023-06-01T11:00:00Z",
    "updated_at": "2023-06-01T11:00:00Z"
  }
]
```

#### Get a specific case note

```
GET /api/case-notes/{id}/
```

**Response**:
```json
{
  "id": 1,
  "case": 1,
  "created_by": 2,
  "created_by_username": "manager1",
  "content": "Initial meeting with beneficiary completed",
  "created_at": "2023-06-01T11:00:00Z",
  "updated_at": "2023-06-01T11:00:00Z"
}
```

#### Create a new case note

```
POST /api/case-notes/
```

**Request**:
```json
{
  "case": 1,
  "created_by": 3,
  "content": "Conducted home visit, beneficiary's situation has improved"
}
```

**Response**:
```json
{
  "id": 2,
  "case": 1,
  "created_by": 3,
  "created_by_username": "officer1",
  "content": "Conducted home visit, beneficiary's situation has improved",
  "created_at": "2023-06-10T14:00:00Z",
  "updated_at": "2023-06-10T14:00:00Z"
}
```

### Assessments

#### List all assessments

```
GET /api/assessments/
```

**Response**:
```json
[
  {
    "id": 1,
    "title": "Needs Assessment",
    "description": "Basic needs assessment",
    "case": 1,
    "created_by": 3,
    "created_by_username": "officer1",
    "questions": [
      {
        "id": 1,
        "assessment": 1,
        "text": "What are your immediate needs?",
        "question_type": "text",
        "choices": "",
        "required": true,
        "order": 0
      }
    ],
    "created_at": "2023-06-02T09:00:00Z",
    "updated_at": "2023-06-02T09:00:00Z"
  }
]
```

#### Get a specific assessment

```
GET /api/assessments/{id}/
```

**Response**:
```json
{
  "id": 1,
  "title": "Needs Assessment",
  "description": "Basic needs assessment",
  "case": 1,
  "created_by": 3,
  "created_by_username": "officer1",
  "questions": [
    {
      "id": 1,
      "assessment": 1,
      "text": "What are your immediate needs?",
      "question_type": "text",
      "choices": "",
      "required": true,
      "order": 0
    }
  ],
  "created_at": "2023-06-02T09:00:00Z",
  "updated_at": "2023-06-02T09:00:00Z"
}
```

#### Create a new assessment

```
POST /api/assessments/
```

**Request**:
```json
{
  "title": "Health Assessment",
  "description": "Assessment of health needs",
  "case": 1,
  "created_by": 3
}
```

**Response**:
```json
{
  "id": 2,
  "title": "Health Assessment",
  "description": "Assessment of health needs",
  "case": 1,
  "created_by": 3,
  "created_by_username": "officer1",
  "questions": [],
  "created_at": "2023-06-10T15:00:00Z",
  "updated_at": "2023-06-10T15:00:00Z"
}
```

### Assessment Questions

#### List all assessment questions

```
GET /api/assessment-questions/
```

**Response**:
```json
[
  {
    "id": 1,
    "assessment": 1,
    "text": "What are your immediate needs?",
    "question_type": "text",
    "choices": "",
    "required": true,
    "order": 0
  }
]
```

#### Get a specific assessment question

```
GET /api/assessment-questions/{id}/
```

**Response**:
```json
{
  "id": 1,
  "assessment": 1,
  "text": "What are your immediate needs?",
  "question_type": "text",
  "choices": "",
  "required": true,
  "order": 0
}
```

#### Create a new assessment question

```
POST /api/assessment-questions/
```

**Request**:
```json
{
  "assessment": 2,
  "text": "Do you have any chronic health conditions?",
  "question_type": "boolean",
  "required": true,
  "order": 0
}
```

**Response**:
```json
{
  "id": 2,
  "assessment": 2,
  "text": "Do you have any chronic health conditions?",
  "question_type": "boolean",
  "choices": "",
  "required": true,
  "order": 0
}
```

### Assessment Answers

#### List all assessment answers

```
GET /api/assessment-answers/
```

**Response**:
```json
[
  {
    "id": 1,
    "question": 1,
    "answer_text": "Food, shelter, and medical care",
    "created_by": 3,
    "created_at": "2023-06-02T10:00:00Z",
    "updated_at": "2023-06-02T10:00:00Z"
  }
]
```

#### Get a specific assessment answer

```
GET /api/assessment-answers/{id}/
```

**Response**:
```json
{
  "id": 1,
  "question": 1,
  "answer_text": "Food, shelter, and medical care",
  "created_by": 3,
  "created_at": "2023-06-02T10:00:00Z",
  "updated_at": "2023-06-02T10:00:00Z"
}
```

#### Create a new assessment answer

```
POST /api/assessment-answers/
```

**Request**:
```json
{
  "question": 2,
  "answer_text": "Yes",
  "created_by": 3
}
```

**Response**:
```json
{
  "id": 2,
  "question": 2,
  "answer_text": "Yes",
  "created_by": 3,
  "created_at": "2023-06-10T16:00:00Z",
  "updated_at": "2023-06-10T16:00:00Z"
}
```

## Filtering and Searching

Most endpoints support filtering and searching. For example:

- Filter cases by status: `/api/cases/?status=open`
- Filter cases by case manager: `/api/cases/?case_manager=2`
- Filter beneficiaries by gender: `/api/beneficiaries/?gender=female`
- Search beneficiaries by name: `/api/beneficiaries/?search=John`

## Pagination

API responses are paginated by default. You can control pagination using the following query parameters:

- `page`: The page number (default: 1)
- `page_size`: The number of items per page (default: 10)

Example:
```
GET /api/beneficiaries/?page=2&page_size=20
```

## Error Handling

The API returns appropriate HTTP status codes for different types of errors:

- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a JSON object with an error message:

```json
{
  "detail": "Authentication credentials were not provided."
}
```

## Rate Limiting

The API has rate limiting to prevent abuse. If you exceed the rate limit, you will receive a `429 Too Many Requests` response.