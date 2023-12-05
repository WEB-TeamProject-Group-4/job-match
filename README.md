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
