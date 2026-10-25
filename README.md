# referee_system

## This was my final year project at university, it is an interactive system in which referees within the Premier League are ranked from best to worst based on their decision making at pivotal moments in the match. Their rankings are displayed in the form of a table, that shows several metrics. The system uses a custom metric, the Poor Decisions Per Game index, which weighs referee decisions against how Virtual Assistant Referee (VAR) would have assessed the same decision.

## This system consists of four user types: 
. Casual fans (who are able to vote on decisions within the game, but don't have an influence on the referee rankings)

. Ex-Referees (able to vote on referee performances and leave comments. Each vote of theirs contributes to referee Average Performance Ratings)

. Referees (able to view their performance ratings)

. Admins (control user onboarding, bans, etc.)

Information about this repository

. To run this project, enter python manage.py runserver in the terminal 

. To debug a file before running press F5 on your keyboard

. To terminate the running project enter Ctrl+C in the terminal

. All database schema can be viewed within shell, enter python manage.py shell to make database queries

. To create an admin account with your own details, enter python manage.py createsuperuser

. Please note that, as an ex-referee, in order to be able to rate referees' performances, you must first verify that you have watched a match by answering questions

. In order to set questions for any match, first log in as an admin through http://127.0.0.1:8000/admin/login/?next=/admin/ and click "Match Questions" under accounts

. There you will see a list of all previously set questions by admin, and if you want to add questions for a specific match,click "ADD MATCH QUESTION" at the top right of the screen

 Project structure:
├── 📁 referee_system 
│   ├── 📁 accounts 
│   │   ├── 📁 management
│   │   │   ├── 📁 commands
│   │   │   └── __init__.py
│   │   ├── 📁 __pycache__
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── fan_chat.py
│   │   ├── forms.py
│   │   ├── middleware.py
│   │   ├── models.py
│   │   ├── routing.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── 📁 migrations
│   ├── 📁 static
│   ├── 📁 templates
│   │   └── 📁 accounts
│   │       ├── base.html
│   │       ├── dashboard.html
│   │       ├── ex_referee_dashboard.html
│   │       ├── ex_referee_login.html
│   │       ├── fan_chat.html
│   │       ├── fixtures_api.html
│   │       ├── home.html
│   │       ├── login.html
│   │       ├── pending_approval.html
│   │       ├── profile.html
│   │       ├── rate_referee.html
│   │       ├── referee_detail.html
│   │       ├── referee_feedback.html
│   │       ├── referee_leaderboard.html
│   │       ├── referee_ratings_table.html
│   │       ├── register_ex_referee.html
│   │       ├── register_referee_step2.html
│   │       ├── register_referee.html
│   │       ├── register_user.html
│   │       ├── test_view.html
│   │       ├── upload_picture.html
│   │       └── verify_match_watching.html
│   └── __init__.py

├── 📁 static
├── 📁 staticfiles
├── 📁 media
├── 📁 myvirtualenv (virtual environment)
│   ├── bin/
│   ├── lib/
│   ├── include/
│   └── pyvenv.cfg

├── manage.py
├── db.sqlite3
├── .env
├── .gitignore
├── .coverage
├── 📄 README.md
├── 📄 project_log.md
├── 📄 referee_system.code-workspace
├── 📄 referee_system_accounts_erd.png
├── 📄 referee_system_updated
├── 📄 referee_system_uml.png
├── 📄 referee_system.png
├── 📄 accounts_diagram.dot
├── 📁 frontend
│   ├── node_modules/
│   ├── package.json
│   ├── package-lock.json
│   ├── webpack.config.js
│   └── .babelrc
└── 📁 da307
