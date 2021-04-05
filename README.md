# db-project
 course project of databases spring2021
## To Start
    git clone https://github.com/Zacchaeus14/db-project.git
    cd db-project
    pip install -r requirements.txt
    export FLASK_APP=app.py
    export FLASK_ENV=development
on a windows PC, use `set` instead of `export`

Create a `dbconfig.json` under the project's root directory with content:

    {"host": "localhost", "user": "root", "password": "your_db_password", "database": "your_db_name"}
Then run the flask server with:

    flask run
    
