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

Tasks for next week
. Drawing a rough template of database and creating appropriate models needed to distinguish between all the user types

Week beginning 25/11/24

Monday: Drew rough template of database structure in a UML Diagram
Tuesday: Created User model of CustomUser class
Wednesday: Met with supervisor and showed her my UML Diagram (she suggested changes)
Thursday: Created Referee model of CustomUser class
Friday: Created Ex-Referee model of CustomUser class


Tasks for next week:
. Establish Admin actions and define them in a class
. Login and Registration Forms


Week beginning 02/12/24

Monday: Created Registration form for referees using attributes from the Referee model in my database
Tuesday: Created Registration form for users using attributes from the User model in my database
Wednesday: Created Registration form for Ex-referees using attributes from the Ex-Referee model in my database
Thursday: HTML pages for User and Referee registration pages
Friday: Began Admin configuration

Tasks for next week: 
. Admin configuration
. Work on user homepage

Week beginning 09/12/24:

Monday: Finished off admin configuration (gave admins actions like approve the accounts of referees)
Tuesday: User dashboard, firstly drew sketches of how I want it to look with all its features
Wednesday: Continued with live chat implementation (features like audio recordings)
Thursday: Live chat; JavaScript functions
Friday: Tweaking front-end of live chat; HTML
Saturday: Testing live chat features to ensure it works as expected

Tasks for next week:
. Start implementing Voting poll system for users
. Import videos from YouTube for users to vote on

Week beginning 16/12/24:

Monday: Created the Vote model within the database
Tuesday: Created a function for Vote that submits POST requests to the server whenever users vote and the choice is saved to Vote Model
Wednesday: JavaScript code for handling vote submissions and updating vote percentages 
Thursday: Same as Wednesday
Friday: HTML frontend code for the Voting poll system with Youtube videos converted to MP4S attached

Tasks for next week:
. Test that the voting poll system works as expected, check for any issue with videos (Play, Pause, Rewind, Playback Speed, video quality etc)
. Work on creating a sample Referee table
. Research into API

Week beginning 23/12/24:

Monday: Tested for any issues with the Poll System (video quality issues and ensured vote percentages are updated)
Tuesday: Generated mock statistical data for referees and stored them in the database under each of their names
Wednesday: Began HTML code that displays the mock statistics from my database
Thursday: Began HTML code that displays the mock statistics from my database
Friday: Detailed research into the different football APIs I could use, narrowed them down to three options

Tasks for next week:
. Choose API and identify the features I want it to show
. Work on connecting API to application

Week beginning 30/12/24:

Monday: Determined what I want my API to be able to do and show (its use in my system)
Tuesday: More research, which eventually led to deciding which API I wanted to use (API-SPORTS)
Wednesday: Configured API connection in settings
Thursday: Worked on displaying live Premier League Table 
Friday: Continued to work on live Premier League Table

Tasks for next week: 
.  Explore different API endpoints and test the scope of API-SPORTS. (i.e. How much data does it cover? How detailed is the data, etc.)
. Continue working on the rest of API features that I wish to implement

Week beginning 06/01/25:

Monday: Searched a variety of API endpoints and the data that they returned in JSON format
Tuesday: Began working on the view function that fetches the Premier League table from the API for all user types
Wednesday: Same as Tuesday
Thursday: Continued working on Premier League table implementation
Friday: Premier League fixture list and result list implementation also fetched from the API

Tasks for next week:
. HTML code for actually displaying the league table that's fetched from the API
. JavaScript functions that shows match details whenever I click on the result of a match

Week beginning 13/01/2025:

Monday: HTML code that displays the live Premier League table on the homepage
Tuesday: HTML code that displays the list of fixtures and results on the homepage
Wednesday: View function that fetches match details for a specific match from the API 
Thursday: Same as Wednesday
Friday: JavaScript that shows the match details pop-up when a user clicks on a specific match 

Tasks for next week: 
. Begin Ex-Referee implementation, more specifically, rating referees


Week beginning 20/01/25:

Monday: Creation of RefereePerformanceRating model that stores all rating values given by any ex-referee in my database
Tuesday: Began implementing the rate referee function
Wednesday: Discussed rate referee functionality with supervisor, she suggested a feedback section as well for ex-referees to provide further insight
Thursday: Added 'feedback' attribute to my RefereePerformanceRating model 
Friday: JavaScript for user interaction to handle ex-referee submission

Tasks for next week:
. Ex-Referee dashboard page
. Build actual Referee table based off Ex-referee ratings- visible to both Referees and Ex-referees

Week beginning 27/01/25:

Monday: Began implementing a page that shows a list of all the matches an ex-referee has rated
Tuesday: Same as Monday
Wednesday: Began real referee table implementation - worked on creating a summary table - backend
Thursday: Continued on with referee summary table - backend
Friday: Continued to work on the referee summary table - frontend

Tasks for next week: 
. Work on the referee leaderboard table, showing more enhanced metrics from the summary table

Week beginning 03/02/25:

Monday: Referee leaderboard table implementation - Backend
Tuesday: Referee leaderboard table implementation - Backend 
Wednesday: Discussion with supervisor on next steps after implementing the referee table
Thursday: Referee leaderboard table implementation - Backend
Friday: Referee leaderboard table implementation - Frontend

Tasks for next week: 
. Create a dashboard card for referees to be able to view the most recent match that they played in

Week beginning 10/02/25:

Monday: Began implementing the most recent match feature, filtering matches in the database for any given referee to their most recent
Tuesday: Continued with the most recent match feature, filtering ex-referee ratings to gather ratings for the same match as the referee's requested most recent
Wednesday: Calculated average ratings using Django's aggregate functions
Thursday: Created JSON Dictionary, setting values to attributes within the database and completed the most recent match view function
Friday: Began JavaScript for the most recent match function


Tasks for next week: 
. Complete JavaScript code
. Begin unit testing on code

Week beginning 17/02/25

Monday: Finished with JavaScript code
Tuesday: Tested referee's most recent match function to see if it showed the right information for each referee
Wednesday: Overviewed my project in its entirety, played with each user type to verify that all their requirements have been met
Thursday: Project interview
Friday: Unit testing, created a test model file that tests the models in my database, experienced some failed test cases 
Saturday: Reviewed Study Guide

Tasks for next week:
. Finish test models, ensuring that no test cases fail
. Begin test views
. Begin dissertation


Week beginning 24/02/25:

Monday: Finished test models, with all test cases passed. Met with the supervisor to show her my test models file
Tuesday: Began writing test views file, testing that the view functions work correctly
Wednesday: Same as Tuesday
Thursday: Looked into example dissertations to gauge understanding of a well formatted dissertation and then wrote out a plan (labelling all the sections and sub-sections of my dissertation)
Friday: Read marking rubric to understand what markers are looking for when marking

Tasks for next week: 
. Complete introduction 
. Make a start on Survey of Literature Review

Week beginning 03/03/25:

Monday: Began introduction 
Tuesday: Completed introduction
Wednesday: Checked coverage report of my test file, saw that coverage was too low so wrote more test cases under test models and test views 
Thursday: Created functionality test file
Friday: Continued working on functionality test file

Tasks for next week: 
. Review introduction
. Begin working survey of literature review section of the dissertation

Week beginning 10/03/25:

Monday: Proof-read introduction
Tuesday: More test cases (adding to existing test files)
Wednesday: Same as Tuesday
Thursday: Began Survey of Literature/Information Sources section of dissertation (Research on similar existing systems)
Friday: Did Survey of Literature/Information Sources again (writing)

Tasks for next week:
. Finalise the Survey of Literature Review section
. Begin Technical Specification
. Continue testing (work on creating integrational test cases)

Week beginning 17/03/25:

Monday: Finalised and proofread Survey of Literature/Information Sources section
Tuesday: More testing (integrational test cases)
Wednesday: Same as Tuesday
Thursday: Began Technical Specification write-up 
Friday: Continued with Technical Specification write-up
Saturday: Finished and proofread the Technical Specification write-up 

Tasks for next week:
. Begin and complete System Architecture section of Dissertation
. Begin Implementation write-up
. Software testing (testing the system as a whole)

Week beginning 24/03/25:

Monday: Began writing up System Architecture section (Models, Views, Databases and Data Flow explanation)
Tuesday: System Architecture write-up finished (UML Diagram and explanation of Diagram)
Wednesday: Began implementation write-up, I gathered the tracked steps of my implementation process from my notes and decided I would use this to explain everything I did step-by-step
Thursday: Continued implementation write-up
Friday: Same as Thursday
Saturday: Same as Wednesday and Thursday
Sunday: Finished off Implementation write-up (wrote about Challenges faced while implementting) and proofread

Tasks for next week: 
. Software testing (testing the system as a whole)
. Testing section write-up

Week beginning 31/03/25:

Monday: Ran software testing of code
Tuesday: Made note of all the testing methods used within the project and then began testing write-up
Wednesday: Continued testing write-up
Thursday: Same as Wednesday
Friday: User Acceptance testing - Allowed peers to play with my code and asked them questions about how well it works and whether they think it meets its requirements, and if not, what needs to be improved
Saturday: User Acceptance Testing write-up (wrote about feedback from peers), and evaluated this feedback, also completed Testing section
Sunday: Proofread Testing Section

Tasks for next week: 
. Minor improvements to code based on feedback
. Results and Discussion write-up 

Week beginning 07/04/25:

Monday: Used feedback from peers to make some frontend changes
Tuesday: Began implementing proof of viewed match feature for ex-referees (based of feedback)
Wednesday: Finished implementing proof of viewed match feature for ex-referees
Thursday: Results and Discussion write-up
Friday: Finished Results and Discussion write-up

Tasks for next week: 
. Begin and complete Critical Appraisal section 
. Begin and complete Conclusion

Week beginning 14/04/25:

Monday: Began Critical Appraisal section - What went well and Even Better If?
Tuesday: Continued with Critical Appraisal - Social and Economic Impact
Wednesday: Finished Critical Appraisal - wrote Personal Development and proofread
Thursday: Started the Conclusion
Friday: Continued the Conclusion
Saturday: Finalised and proofread the Conclusion and began the Abstract
Sunday: Finished the Abstract

Tasks for next week: 
. Arrange References (using RefWorks Citation Manager)
. Final Review of Dissertation and Code

Week beginning 21/04/25:

Monday: References (using RefWorks Citation Manager) and arranged headings using table of contents
Tuesday: Proofread Dissertation and checked all endpoints of code
Wednesday: Continued proofreading dissertation 
Thursday: Final proofread
Friday: Submission

Tasks for next week: 
. More proofreading, checking code and final Changes
. Submission 

Week beginning: 28/04/25: 

Monday: Proofreading Dissertation
Tuesday: Checking dissertation against marking rubric
Wednesday: Checking code, adding comments where necessary
Thursday: Same as Wednesday
Friday: Submission
