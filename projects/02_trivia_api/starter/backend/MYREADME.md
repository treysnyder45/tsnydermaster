Getting Started

    Pre-requisites and Local Development
        Developers using this project should already have Python3, pip and node installed on their local machines.

        Backend
            From the backend folder run 'pip install requirements.txt'. All of the requirements will be in the requirements.txt file
            
            To run the application run the following commands on the command line
                'export FLASK_APP=flaskr'
                'export FLASK_DEBUG=true'
                'flask run'

            These commands put the application in development and directs our application to use the '__init__.py' file in our flaskr folder. Using the debug mode, set it to true so it restarts the server whever changes are saved. If running locally on Windows, looks for the commands in the Flask documentation given to you. 
            http://flask.pocoo.org/docs/1.0/tutorial/factory/

            The application is run on 'http://127.0.0.1:5000/' by default and is a proxy in the frontend configuration.

        Frontend
            From the frontend folder, run the following commands to start the client:
                'npm install' // only once to install dependencies
                'npm start'
            By default, the frontend will run on localhost:3000.

        Tests
            In order to run tests navigate to the backend folder and run the following commands:
                'dropdb trivia_test'
                'createdb trivia_test'
                'psql trivia_test < questions.psql'
                'python test_flaskr.py'
            
            The first time you run the test, omit the dropdb command.

            All tests are kept in that file and should be maintained as updates are made to app functionality.

API Reference

    Getting Started
        Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, 'http://127.0.0.1:5000/', which is set as a proxy in the frontend configuration.

        Authenication: This version of the application does not require authentication or API keys.

    Error Handling
        Errors are returned as JSON objects in the following format:
            {
                "success": False,
                "error": 400,
                "message": "bad request"
            }
        
        The API will return three error types when requests fail:
            400: Bad Request
            404: Resource Not Found
            422: Not Processable

Endpoints
    GET  /questions
        General:
            Returns a list of question objects, success value, and total number of questions.

            Results are paginated in groups of 10. Include a request argument to choose page number, started from 1.

            Sample: 'curl http://127.0.0.1:5000/questions'
                "questions": [
                    {
                    "answer":"Tom Cruise",
                    "category":5,
                    "difficulty":4,
                    "id":4,
                    "question":"What actor did author Anne Rice first denounce, then praise in the role of her beloved Lestat?"
                    },
                    {
                    "answer":"Edward Scissorhands",
                    "category":5,
                    "difficulty":3,
                    "id":5,     
                    "question":"What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?"
                    },
                    {
                    "answer":"Brazil",
                    "category":6,
                    "difficulty":3,
                    "id":6,
                    "question":"Which is the only team to play in every soccer World Cup tournament?"
                    },
                    {
                    "answer":"Uruguay",
                    "category":6,
                    "difficulty":4,
                    "id":7,
                    "question":"Which country won the first ever soccer World Cup in 1930?"
                    },
                    {          
                    "answer":"George Washington Carver",
                    "category":4,
                    "difficulty":2,
                    "id":8,
                    "question":"Who invented Peanut Butter?"
                    },
                    {
                    "answer":"Lake Victoria",
                    "category":3,    
                    "difficulty":2,
                    "id":9,
                    "question":"What is the largest lake in Africa?"
                    },
                    {
                    "answer":"The Palace of Versailles",
                    "category":3,
                    "difficulty":3,
                    "id":10,
                    "question":"In which royal palace would you find the Hall of Mirrors?"
                    },
                    { 
                    "answer":"Agra",
                    "category":3,
                    "difficulty":2,
                    "id":11,
                    "question":"The Taj Mahal is located in which Indian city?"
                    },
                    {
                    "answer":"Escher", "category":2,
                    "difficulty":1,
                    "id":12,
                    "question":"Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"
                    },
                    {
                    "answer":"Mona Lisa","category":2,
                    "difficulty":3,
                    "id":13,
                    "question":"La Giaconda is better known as what?"
                    }
                ],
                "success":true,
                "totalQuestions":22
                }

    POST /questions
        General:
            Creates a new book using the submitted question, answer, difficulty, and category. Returns the id of the created back, success value, total questions, and question list based on current page number to update the frontend

        curl http://127.0.0.1:5000/questions?page=1 -X POST -H "Content-Type: application/json" -d {"question":"How are you", "answer":"Good", "difficulty":[1], "category":[1]}

            {
                "questions": [
                    {
                        "question": "How are You",
                        "id": 23,
                        "answer": "Good",
                        "difficulty": 1,
                        "category": 1
                    }
                ],
                "created": 23,
                "success": true,
                "total_question": 23
            }            

    DELETE /questions/<int:question_id>/
        General:
            Deletes the question of the given ID if it exists. All it returns is the value of success.

        curl -X DELETE http://127.0.0.1:5000/<int:question_id>/1?page=1
            {
                "success": true
            }

Deployment N/A

Authors
    Trey Snyder

Acknowledgements
    