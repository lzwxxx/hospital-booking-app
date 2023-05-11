# Setting up

## 1. Run WampServer

1.  Ensure both PHP and MySQL is running
    
2.  Login to phpmyadmin and import following SQL files in order (located in the sql folder):
    

	1.  setup.sql - creates a new SQL user `is213`
    
	2.  doctor.sql
    
	3.  patient.sql
    
	4.  appointment.sql
    
	5.  analytics.sql
    

3.  Run Docker containers:
    

	1.  Go to terminal and run following commands in order:

	2.  Run application service containers: `docker compose up --build -d`
    
	3.  Run Apache Airflow Init first (container need to exit(0) to finish setup): `docker compose -f docker-compose-airflow.yml up airflow-init --build -d`
	
	4.  Run rest of Apache Airflow containers: `docker compose -f  docker-compose-airflow.yml up --build -d`
   
	5.  To tear down and delete all volumes: `docker compose -f docker-compose-airflow.yml -f docker-compose.yml down -v`

    

# Application URLs

## Appointment Booking UI

1.  Access Booking UI via: [http://localhost:3001/](http://localhost:3001/)
    
2.  To book an appointment via Singpass:
	1.  Click on “Retrieve with Singpass MyInfo” to retrieve user’s information
	2.  Select a user & click “Login”
    3.  Fill in the necessary details & proceed to “Book Appointment” once done.
     4.  A confirmation email has been sent to the email address that you have input.
    
## Admin Dashboard UI

1.  Access Booking UI via: [http://localhost:3002/](http://localhost:3001/)
2.  Login Credentials:
    -   Username: `admin`
    -   Password: `admin`
3.  Logout once done (top right corner button)
    
## Apache Airflow

1.  Access Apache Airflow via: [http://localhost:8081/](http://localhost:3001/)
-   Username: `airflow`
-   Password: `airflow`

