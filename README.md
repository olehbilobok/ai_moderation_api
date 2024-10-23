
# AI Moderator API

This API is intended to manage posts and comments with AI moderation and postponed auto-reply to comments. Implemented with Django Rest Framework. Posts and Comments Moderation is achieved due to Google API.




## Features

- User Registration
- User authentication with JWT
- API for Posts
- API for Comments
- Checking posts or comments at the time of creation for profanity and blocking such posts or comments
- The auto-reply and its time are configurable by the user
- AI maintains context for the relevance of responses to messages and comments of any nesting depth
- Analytics on the number of comments that were added to posts for a certain period, aggregated by day. Returns the number of comments created and the number of blocked comments.
- Posts and Comments Analytics are covered with the unit tests








## Preconditions

Create API KEY to work with Google AI API
 - [Create API KEY](https://ai.google.dev/)
Copy API KEY and paste it into the set_env_variables.sh file for GEMINI_API_KEY variable when the project has been cloned


## Run Locally
Clone the project
```bash
git clone https://github.com/olehbilobok/ai_moderation_api.git
```
Create virtual environment
```bash
python3.11 -m venv venv
```
Activate virtual environment (Linux, MacOS)  
```bash
source venv/bin/activate
```
Activate virtual environment (Windows)  
```bash
 ./venv/Scripts/activate
```
Set the environment variables(Linux, MacOS)  
```bash
source set_env_variables.sh
```
Set the environment variables(Windows)  
```bash
./set_env_variables.sh
```
Install dependencies 
```bash
pip install -r requirements.txt
```
Go to the project folder
```bash
cd ai_moderator
```
Create migrations and migrate
```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```
Run Server
```bash
python manage.py runserver
```



    
## Environment Variables

The following environment variables required for project settings: 
`SECRET_KEY`, `DB_NAME` and `GEMINI_API_KEY`
Located into set_env_variables.sh file

## Running Tests

To run tests, run the following command

```bash
python manage.py test
```


## API Reference
[Postman Collection](https://api.postman.com/collections/15325181-7430e0d7-0237-4f84-811e-3491cfdf0a60?access_key=PMAT-01JATV766T14ENWBPYRRWPT51D)

