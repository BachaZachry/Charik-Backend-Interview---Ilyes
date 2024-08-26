# Charik Backend Test API

This API provides a solution for interacting with the HubSpot API, focusing on contact and deal management.

## Setup

1. Clone repo.
2. Create a `.env` file similar to `.env.example` with your API key and id of your Hubspot account.
3. Build the docker image:

```bash
docker build -t charik-test .
```

4. Run the docker image:

```bash
    docker run -p 8000:8000 charik-test
```

5. Access the application at `http://localhost:8000`

## Endpoints

### 1. Associate Contact with Deal

- **POST** `/associate/`
- Associates an existing contact with a deal in HubSpot

### 2. Create HubSpot Contact

- **POST** `/contact/`
- Creates a new contact in HubSpot

### 3. List Contacts

- **GET** `/contact/list/`
- Retrieves a paginated list of contacts from HubSpot with their associations
- Supports pagination using the `after` query parameter

### 4. Create HubSpot Deal

- **POST** `/deal/`
- Creates a new deal in HubSpot

## Authentication

The API supports the following authentication methods:

- Cookie Authentication
- Basic Authentication

## Data Models

### Contact

Required fields:

- email

Optional fields:

- firstname
- lastname
- website
- company
- address
- city
- state

### Deal

Required fields:

- pipeline
- dealstage
- amount
- closedate

### AssociateContactWDeal

Required fields:

- deal_id
- contact_id

For more detailed information about request/response formats and additional parameters, please refer to the full API documentation available at `/api/schema/swagger-ui/`.
