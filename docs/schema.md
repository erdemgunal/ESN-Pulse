# ESN Pulse Database Schema

This document describes the schema of the ESN Pulse database. The schema includes tables for organizations, activities, and statistics. 

## 1. Organisations Table

The `organisations` table stores information about each ESN organization.

| Field                  | Type       | Description                                    |
|------------------------|------------|------------------------------------------------|
| `organisation_id`       | INTEGER    | Primary Key, Unique ID for the organization    |
| `organisation_name`     | VARCHAR    | Name of the organization                      |
| `country_code`          | VARCHAR    | Country code of the organization               |
| `city`                  | VARCHAR    | City where the organization is located         |
| `country`               | VARCHAR    | Country where the organization is located      |
| `email`                 | VARCHAR    | Contact email for the organization            |
| `website`               | VARCHAR    | Website of the organization                   |
| `longitude`             | FLOAT      | Longitude of the organization’s location      |
| `university_name`       | VARCHAR    | Name of the university                        |
| `university_website`    | VARCHAR    | Website of the university                     |
| `social_media`          | JSON       | Social media links in a JSON format           |
| `activity_count`        | INTEGER    | Number of activities organized by the entity  |
| `city_count`            | INTEGER    | Number of cities the organization operates in |
| `participant_count`     | INTEGER    | Total number of participants in all activities|

## 2. Activities Table

The `activities` table stores detailed information about each event or activity organized by an ESN organization.

| Field                  | Type       | Description                                    |
|------------------------|------------|------------------------------------------------|
| `activity_id`          | INTEGER    | Primary Key, Unique ID for the activity        |
| `organisation_id`      | INTEGER    | Foreign Key to the `organisations` table       |
| `activity_title`       | VARCHAR    | Title of the activity                          |
| `activity_date`        | DATE       | Date when the activity takes place             |
| `activity_city`        | VARCHAR    | City where the activity occurs                 |
| `activity_country`     | VARCHAR    | Country where the activity occurs              |
| `participant_count`    | INTEGER    | Number of participants in the activity         |
| `activity_causes`      | JSON       | Causes associated with the activity (JSON)     |
| `activity_type`        | VARCHAR    | Type of activity (e.g., sports, cultural, etc.)|
| `activity_goal`        | TEXT       | Goal or objective of the activity              |
| `activity_description` | TEXT       | Detailed description of the activity           |
| `sdg_goals`            | JSON       | Sustainable Development Goals associated (JSON)|
| `activity_objectives`  | TEXT       | Objectives of the activity                     |
| `activity_organiser`   | VARCHAR    | Person or group responsible for organizing the activity|

## 3. Statistics Table

The `statistics` table stores statistical data related to the activities organized by each ESN organization.

| Field                             | Type     | Description                                        |
|-----------------------------------|----------|----------------------------------------------------|
| `organisation_id`                 | INTEGER  | Foreign Key to the `organisations` table           |
| `total_physical_activities`       | INTEGER  | Total number of physical activities                |
| `total_online_activities`         | INTEGER  | Total number of online activities                  |
| `local_students_participants`     | INTEGER  | Number of local students participating             |
| `international_students_participants`| INTEGER| Number of international students participating    |
| `coordinators_participants`       | INTEGER  | Number of coordinators participating               |
| `total_participants`              | INTEGER  | Total number of participants across all activities|
| `environmental_sustainability_activities` | INTEGER | Number of sustainability-related activities    |
| `social_inclusion_activities`     | INTEGER  | Number of social inclusion activities              |
| `culture_activities`              | INTEGER  | Number of cultural activities                      |
| `education_youth_activities`      | INTEGER  | Number of educational/youth activities             |
| `health_wellbeing_activities`     | INTEGER  | Number of health and wellbeing activities          |
| `skills_employability_activities` | INTEGER  | Number of skills and employability activities      |
| `physical_activity_types`         | JSON     | Types of physical activities (JSON format)         |
| `online_activity_types`           | JSON     | Types of online activities (JSON format)           |

## 4. Data Collection and Processing

Data for the above tables will be collected using a web scraping technique. Python's BeautifulSoup and Requests libraries will be used to scrape data from the ESN Activities portal. 

After collecting the data, it will be stored in a PostgreSQL database and processed for further analysis. Regular automated data collection will ensure that the statistics and activity information are always up-to-date.

