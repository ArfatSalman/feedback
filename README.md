# Feedback
A model of a user-feedback site with password encryption.

## Usage and Code Information
Registering an account will allow a user to submit private feedback to the site. Feedback can only be later edited or deleted by the submitting user while they are logged in. User accounts can similarly only be accessed or deleted by the user themself while they are logged in.

User logged-in status is preserved using Flask sessions to store the username - this is cleared if the user logs out, and using this stored username to compare against the tables of users and feedback prevents unauthorized access to private pages.

Users and their feedback are stored in corresponding tables in a relational database using PostgreSQL, accessed via Flask-Sqlalchemy. User entries record their username, password, email, first name, and last name. User passwords are stored securely using Flask-Bcrypt as a bcrypt-hashing utility. Feedback entries record their title, content, and an auto-incrementing ID. The two are linked via a one-to-many relationship (user-to-feedback), with users having a list of their feedback entries and feedback having the posting user's username.

The app is hosted on Heroku and is available at https://acollino-feedback.herokuapp.com.

## Previews
<img src="https://user-images.githubusercontent.com/8853721/186508124-7eddfdcf-47ee-4239-b3f7-cf73dfcaa100.png" alt="Feedback home page" style="width: 700px">

<img src="https://user-images.githubusercontent.com/8853721/186508226-8a302699-261e-4e11-8210-b1eb207f7997.png" alt="Feedback site registration form" style="width: 500px;">

<img src="https://user-images.githubusercontent.com/8853721/186508632-a6679b3e-a1e6-48b2-ab19-dfb1e4782fbb.png" alt="New feedback submission form" style="width: 500px;">

<img src="https://user-images.githubusercontent.com/8853721/186518972-71697ebc-812e-45ed-bade-f628ffcbc69e.png" alt="Feedback editing form" style="width: 500px;">



## Attributions
**Background Pattern:** [Endless Constellation vector background by SVGBackgrounds.com](https://www.svgbackgrounds.com/)
