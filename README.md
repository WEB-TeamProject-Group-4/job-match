# Job-match
Back-end, web application designed for job matching, enabling companies to create job listings while allowing professionals to craft resumes and connect each other for the perfect match.

**Swagger documentation:** [Link](https://job-match-c1sd.onrender.com/docs) (First opening will take a while to load.)

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


## Features:
- Public part - accessible without authentication;
- Login endpoints (for both employers and professionals) - access the private endpoints of the application. Login requires username and password;
- Register endpoints (for both employers and professionals) - requires username, first name, last name, and password (professionals) and  username, company name and password (companies);
  
- Features, related to companies:
  * Create company;
  * View all approved companies;
  * Update company information;
  * Searching company by ID;
  * Remove company - removes also created user, related to this company;
  * Create company information;
  * Update company information;
  * Upload company logo - implemented check for explicit content;
  * View company logo;
  * View company information;
  * Delete company information;
  * Search for matches - for each ad, a company can check for possible resume matches;
  * Approving potential matches - company can decide to approve the match;
  * View all matches;
    
- Features, related to professionals:
  * Create professional;
  * View all approved professionals;
  * View professional information;
  * Create/Update professional information;
  * Upload professional image - implemented check for explicit content;
  * View professional image;
  * Edit professional summary;
  * Change professional status;
  * Set main resume;
  * Delete professional profile - removes also created user, related to this professional;
  * Search for matches - for each resume, a professional can check for possible ad matches;
  * Approving potential matches - professional can decide to approve the match;
  * View all matches;
 
- Features, related to ads / resumes:
  * Create ad (for companies) / resume (for professionals);
  * View all resumes - this feature can be used by companies;
  * View all job ads - this feature can be used by professionals;
  * Update job ads - restricted for professional;
  * Update resumes - restricted for companies;
  * View ad / resume by ID;
  * Delete ad / resume;
  * Create skill;
  * View all skills;
  * Update skill;
  * Delete skill;
  * Add skill to ad / resume;
  * Remove skill from ad / resume;
 
 
## Database

![db screen](https://github.com/WEB-TeamProject-Group-4/job-match/assets/138625993/05f7e648-2a0d-4d51-a3e8-76a4cf7fb901)


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


## License
This project is licensed under the terms of MIT license.
