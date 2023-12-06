# Job-match
Back-end, web application designed for job matching, enabling companies to create job listings while allowing professionals to craft resumes and connect each other for the perfect match.

**Swagger documentation:** [Link](https://job-match-c1sd.onrender.com/docs)

## Installation
#### 1. Clone the project:
```
git clone https://github.com/WEB-TeamProject-Group-4/job-match.git
```
#### 2. Create .env file (or rename and modify .env.example) in project root and set environment variables for application

#### 3. Install the modules listed in the `requirements.txt` file (make sure that you are in the `src/` directory):
```
pip install -r requirements.txt
```
#### 4. Start the application (make sure that you are in the `src/` directory):
```
python run_server.py
```

## Testing
#### To run the tests, run the following command:
```
pytest
```
You can also write your own tests in the `tests/` directory. <br>
The test follow by the official support [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/), [pytest](https://docs.pytest.org/en/stable/), [pytest-asyncio](https://pytest-asyncio.readthedocs.io/en/latest/) for async testing application.

## Database
<img width="937" alt="Screenshot 2023-12-06 at 13 00 48" src="https://github.com/WEB-TeamProject-Group-4/job-match/assets/138571393/747e9413-2678-4cff-a73a-8854be246fb2">


## Project structure
```
├───src                   - project source.
│   ├───app               - primary app folder.
│   │   ├───api           - web related stuff.
│   │   ├───core          - application configuration.
│   │   ├───crud          - crud logic.
│   │   ├───db            - db related stuff.
│   │   ├───schemas       - pydantic models
│   │   ├───templates     - email templates
└───tests                 - project tests.
```

## Features:
- Public part - accessible without authentication;
- Login endpoints (for both employers and professionals) - access the private endpoints of the application. Login requires username and password;
- Register endpoints (for both employers and professionals) - requires username, first name, last name, and password (professionals) and  username, company name and password (companies);
- Features, related to companies:
  * Create company;
  * View all companies;
  * Update company information;
  * Searching company by ID;
  * Remove company - removes also created user, related to this company;
  * Create company information;
  * Update company information;
  * Upload company logo;
  * View company logo;
  

## License
This project is licensed under the terms of MIT license.
