A Project Log
Weekly Log

Week beginning 21/10/24

Monday: Worked on the Aims and Objectives section of my interim report
Tuesday: Drew out a low-fidelity ER Diagram of my system (basic functions)
Wednesday: Worked on requirements section of my interim report
Thursday: Met with supervisor and discussed next steps of my project
Friday: Continued to work on requirements section of my report


Tasks for next week: 

. Complete planning of project
. Understand how the architecture of my system is supposed to look and draw it out 
. Finish rest of my report


Week beginning 28/10/24

Monday: Drew out a medium-fidelity diagram of system in a UML Diagram
Tuesday: Finished Aims and Objectives section of interim report
Wednesday: Survey of Literature Review section (Research on Flask and Django frameworks)
Thursday: Survey of Literature Review (Research on most suitable database connection)
Friday: Wrote out functional requirements to get a vague idea before typing them out on Interim Report

Tasks for next week: 

. Complete functional requirements (Users, Referees, Ex-referees, Admin)
. Outline of Specification and Design - Look into the software architecture of Django in relation to my project(in other words, how my application will be structured)


Week beginning 04//11/24

Monday: Functional requirements added to interim report (Users)
Tuesday: Functional requirements added to Interim report (Referees)
Wednesday: Met with supervisor, and she clarified my confusion over software architecture of Django
Thursday: Functional Requirements added to Interim Report (Ex-Referees and Admin)
Friday: Drew Django Software Architecture diagram (on paper)
Saturday: Further research on the connection between all the layers that make up my software architecture 

Tasks for next week:

. Final template of Software Architecture diagram- add to Interim report and annotate all components
. High fidelity ER Diagram drawn and explained in report


Week beginning 11/11/24

Monday: Software Architecture drawn and Data Layer explained
Tuesday: Authentication and Role-Based User System and Core Business Logic Layer explained
Wednesday: The rest of architecture explanation complete
Thursday: High-Fidelity ER Diagram complete
Friday: Explained ER diagram

Tasks for next week: 

. Set a plan for the rest of project after interim report
. Consult with supervisor on whether any changes should be made to plan (perhaps if time frames are unrealistic etc.)
. Review Interim report and double-check for readability, spelling or grammatical errors

Week beginning 18/11/24

Monday: Rough plan of the rest of report (timescales etc.)
Tuesday: Timetable of plan (week by week) including what has already been done
Wednesday: Showed plan to supervisor and she suggested changes, also reviewed Interim Report
Thursday: Reviewed Interim Report 
Friday: Interim Report submission

Next step: Drawing a rough template of database and creating appropriate models needed to distinguish between all the user types

Week beginning 02/12/24

Monday: Drew rough template of database structure in a UML Diagram
Tuesday: Created User model of CustomUser class
Wednesday: Met with supervisor and showed her my UML Diagram (she suggested changes)
Thursday: Created Referee model of CustomUser class
Friday: Created Ex-Referee model of CustomUser class


Tasks for next week:

. Establish Admin actions and define them in a class
. Login and Registration Forms


Week beginning 09/12/24

Monday: Created Registration form for referees using attributes from the Referee model in my database
Tuesday: Created Registration form for users using attributes from the User model in my database
Wednesday: Created Registration form for Ex-referees using attributes from the Ex-Referee model in my database
Thursday: HTML pages for User and Referee registration pages
Friday: Began Admin configuration

Christmas break

Week beginning 06/01/25:

Monday: Finished off admin configuration (gave admins actions like approve the accounts of referees)
Tuesday: User dashboard, firstly drew sketches of how I want it to look with all its features
Wednesday: Continued with live chat implementation (features like audio recordings)
Thursday: Live chat; JavaScript functions
Friday: Tweaking front-end of live chat; HTML
Saturday: Testing live chat features to ensure it works as expected

Tasks for next week:

. Start implementing Voting poll system for users
. Import videos from YouTube for users to vote on

Week beginning 13/01/25:

Monday: Created the Vote model within the database
Tuesday: Created a function for Vote that submits POST requests to the server whenever users vote and the choice is saved to Vote Model
Wednesday: Spoke with supervisor to track progress, she gave me some suggestions on how I should display the voting poll with the videos on the user dashboard
Thursday: JavaScript code for handling vote submissions and updating vote percentages 
Friday: HTML frontend code for the Voting poll system with Youtube videos converted to MP4S attached

Tasks for next week:

. Test that the voting poll system works as expected, check for any issue with videos (Play, Pause, Rewind, Playback Speed, video quality etc)
. Work on creating a sample Referee table
. Research into API

Week beginning 20/01/25:

Monday: Tested for any issues with the Poll System (video quality issues and ensured vote percentages are updated)
Tuesday: Generated mock statistical data for referees and stored them in the database under each of their names
Wednesday: Began HTML code that displays the mock statistics from my database
Thursday: Began HTML code that displays the mock statistics from my database
Friday: Detailed research into the different football APIs I could use, narrowed them down to three options

Tasks for next week:
. Choose API and identify the features I want it to show
. Work on connecting API to application

Week beginning 27/01/25:

Monday: Determined what I want my API to be able to do and show (its use in my system)
Tuesday: More research, which eventually led to deciding which API I wanted to use (API-SPORTS)
Wednesday: Configured API connection in settings
Thursday: Worked on displaying live Premier League Table 
Friday: Continued to work on live Premier League Table

Tasks for next week: 
.  Explore different API endpoints and test the scope of API-SPORTS. (i.e. How much data does it cover? How detailed is the data, etc.)
. Continue working on the rest of API features that I wish to implement

Week beginning 03/02/25:

Monday: Searched a variety of API endpoints and the data that they returned in JSON format
Tuesday: Began working on the view function that fetches the Premier League table from the API for all user types
Wednesday: Showed my supervisor the API I would be using going forward, and I explained its benefits
Thursday: Continued working on Premier League table implementation
Friday: Premier League fixture list and result list implementation also fetched from the API

Tasks for next week:
. HTML code for actually displaying the league table that's fetched from the API
. JavaScript functions that shows match details whenever I click on the result of a match

Week beginning 10/02/2025:

Monday: HTML code that displays the live Premier League table on the homepage
Tuesday: HTML code that displays the list of fixtures and results on the homepage
Wednesday: View function that fetches match details for a specific match from the API 
Thursday: Same as Wednesday
Friday: JavaScript that shows the match details pop-up when a user clicks on a specific match 

Tasks for next week: 
. Begin Ex-Referee implementation, more specifically, rating referees


Week beginning 17/02/25:

Monday: Creation of RefereePerformanceRating model that stores all rating values given by any ex-referee in my database
Tuesday: Began implementing the rate referee function
Wednesday: Discussed rate referee functionality with supervisor, she suggested a feedback section as well for ex-referees to provide further insight
Thursday: Added 'feedback' attribute to my RefereePerformanceRating model 
Friday: Created Ex-Referee Dashboard displaying all the matches that the ex-referee has rated

Tasks for next week:
. Build actual Referee table based off Ex-referee ratings
