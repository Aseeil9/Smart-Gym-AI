# Student Affairs System
For College of science Al Zulfi
Department of Computer Science and Information

**Graduation Project**

Submitted in partial fulfillment of the requirements for the award of Bachelor degree of Majmaah University

**Submitted by:**
[Your Name] - [Your ID]
[Your Colleague's Name] - [Colleague's ID]

**Under the supervision of:**
[Supervisor Name]

---

# Abstract
Managing gym facilities and ensuring the safety of athletes during workouts traditionally involves manual monitoring and lacks real-time health analysis. The current project is designed to manage and monitor gym operations using an advanced system called Smart-Gym-AI. This system integrates the Internet of Things (IoT) using ESP32 hardware to capture real-time vital signs (heart rate, calories, steps) and Artificial Intelligence (AI) models (XGBoost and Random Forest) to predict injury risks and fatigue levels. Furthermore, the system provides WebSockets-based real-time alerts to coaches in case of emergencies or high-risk situations, and offers a comprehensive management dashboard for admins to track memberships, finances, and staff. The main feature of this project is the facilitation of a smart, safe, and automated environment for athletes, coaches, and gym management.

# Acknowledgement
We would like to express our gratitude and appreciation for our supervisor for his/her invaluable help, which have contributed to the improvement of this project. The deepest and warmest thanks are expressed to all people who have helped and supported us during the process of developing the project.

---

# Table of Contents
Chapter One: Introduction
1.1 Problem Definition
1.1.1 Goals
1.1.2 Scope
1.1.3 Objectives
1.1.4 Critical success factors
1.2 General rules

Chapter Two: System Analysis and Specification
2.1 Introduction
2.2 Data Modeling
2.2.1 The Entity of Relationships Diagram (ERD) of Project
2.2.2 Use case
2.2.3 Sequence Diagram
2.2.4 UML Class Database Diagram

Chapter Three: System design
3.1 Description of procedures and functions
3.2 Relation database schema

Chapter Four: Implementation and Testing
4.1 Layouts
4.2 Conclusion

---

# Chapter One: Introduction

## 1.1 Problem Definition
Currently, most operating gyms rely on traditional management systems and physical trainers to monitor athletes. However, coaches cannot monitor all athletes simultaneously, leading to a high risk of overexertion, muscle fatigue, and injuries. Additionally, the process of generating training plans, managing memberships, and tracking financial growth consumes time and effort. This project aims to replace manual monitoring with a smart AI-powered system integrated with IoT wearables to facilitate gym management and ensure athlete safety.

### 1.1.1 Goals
The main goal of the project is to create an application that manages gym operations technically and smartly. The use of IoT devices facilitates real-time data collection, while the AI engine analyzes this data to provide instant health feedback. Another vital goal is to create a seamless communication channel between athletes and coaches for emergency interventions (SOS).

### 1.1.2 Scope
The scope of this project includes providing athletes with real-time biometric tracking and AI-generated personalized training plans. The system alerts coaches instantly via WebSockets when an athlete reaches a critical fatigue level. Furthermore, the gym management (Admin) can manage financial revenues, register new athletes, and track the active statuses of coaches and gym hardware maintenance.

### 1.1.3 Objectives
The project aims to achieve three main objectives in order to enhance the workflow of gym management: 
1. Enhancing the safety of athletes during workouts by predicting injury risks.
2. Automating administrative tasks such as memberships and class bookings.
3. Providing real-time data analytics for continuous improvement.

### 1.1.4 Critical success factors
The success of the implementation of the project depends on some critical factors such as the technical skills to integrate ESP32 hardware with a FastAPI backend, the accuracy of the Machine Learning models (XGBoost and Random Forest), and the reliability of real-time WebSocket communication.

## 1.2 General rules
This system will be developed to work on a responsive web browser and smart devices. Thus, it is assumed that users (Admins, Coaches, Athletes) will have access to a computer or a mobile phone and to the internet, and athletes are equipped with the IoT wearable sensor during workouts.

---

# Chapter Two: System Analysis and Specification

## 2.1 Introduction
This section demonstrates how the system works and represents the logical relationships of entity sets to explain the workflow of the system.

## 2.2 Data Modeling
It is the creation of types of graphics that explain the mechanism of the project or system through texts and symbols.

### 2.2.1 The Entity of Relationships Diagram (ERD) of Project
An entity-relationship diagram (ERD) explains how the connections of entity groups are gathered in a database.
#### 2.2.1.1 Description of Entities
I. **Admin:** Manages the overall gym, handles athlete subscriptions, and views financial revenue.
II. **Coach:** Monitors athletes' health metrics, manages workout classes, and receives emergency alerts.
III. **Athlete (Guest):** The athlete uses the IoT sensors, requests AI training plans, and books classes.
IV. **SensorData:** Represents the real-time vital signs (heart rate, steps, calories) sent from the hardware.
V. **AIPrediction:** The results generated by the ML engine to evaluate injury risks and fatigue levels.
VI. **WorkoutClass:** Scheduled training sessions created by coaches for athletes to join.

#### 2.2.1.2 Description of Relations
2.2.1.2.1 **Coach – WorkoutClass relationship**
This is a one-to-many relationship where one coach can manage and schedule multiple workout classes.
2.2.1.2.2 **Athlete – SensorData relationship**
This is a one-to-many relationship where one athlete generates multiple sensor data readings during their workout.
2.2.1.2.3 **SensorData – AIPrediction relationship**
This is a one-to-one relationship where each batch of sensor data readings triggers one specific AI prediction report.
2.2.1.2.4 **Athlete – WorkoutClass relationship**
This is a many-to-many relationship where an athlete can enroll in multiple classes, and a class can contain multiple athletes.
2.2.1.2.5 **Admin – Athlete relationship**
This is a one-to-many relationship where the admin manages the gym memberships and subscriptions for all athletes.

#### 2.2.1.3 Drawing ERD

*(Please insert your ERD image here)*
**Figure 1. ERD**

### 2.2.2 Use case
Use case is an important and useful requirement to explain how the system works.
In figure 2, the tasks of Admin in the app are represented below:
*(Please insert your Admin Use Case diagram here)*
**Figure 2. Use case (Admin)**

In figure 3, the tasks of Coach in the app are represented below:
*(Please insert your Coach Use Case diagram here)*
**Figure 3. Use case (Coach)**

In figure 4, the tasks of Athlete in the app are represented below:
*(Please insert your Athlete Use Case diagram here)*
**Figure 4. Use case (Athlete)**

### 2.2.3 Sequence Diagram
Sequence Diagrams are representative diagrams that explain the workflow of a system operations.

#### 2.2.3.1 Admin
I. **Log In**
At first, the admin logs in on the home page and verifies the login data by sending the data to the databases by accepting or rejecting the entry.
*(Please insert Admin Login Sequence Diagram here)*
**Figure 5. Admin Login**

II. **Story Administration**
Login then review financial statistics, manage athlete subscriptions, and verify the maintenance of hardware devices, and finally sign out.
*(Please insert Admin Administration Sequence Diagram here)*
**Figure 6. Story Administration**

#### 2.2.3.2 Coach
I. **Monitor Team and Alerts**
Login then review team analytics, check average heart rates, and receive real-time critical alerts via WebSockets, and finally sign out.
*(Please insert Coach Monitoring Sequence Diagram here)*
**Figure 7. Coach Monitoring**

#### 2.2.3.3 Athlete
I. **AI Prediction and Dashboard**
At first, log in, view the dashboard for health metrics, log exercise weights to get smart AI recommendations, and finally log out.
*(Please insert Athlete Dashboard Sequence Diagram here)*
**Figure 8. Athlete Dashboard**

II. **Trigger SOS Alarm**
Athlete presses the SOS button, sending a real-time WebSocket alert to all active coaches in the gym to provide immediate help.
*(Please insert Athlete SOS Sequence Diagram here)*
**Figure 9. Trigger SOS**

### 2.2.4 UML Class Database Diagram
The class diagram shows the building blocks of any object-orientated system.
*(Please insert your UML Class Diagram here)*
**Figure 10. UML Class Database Diagram**

---

# Chapter Three: System design

## 3.1 Description of procedures and functions
### 3.1.1 Function
**3.1.1.1 Admin**
I. Add new athlete profile and subscription.
II. View total revenue and finance charts.
III. Manage gym hardware maintenance notes.

**3.1.1.2 Coach**
I. View team average heart rate and active athletes.
II. Update AI risk thresholds.
III. Send direct instructions to athletes via chat.

**3.1.1.3 Athlete**
I. View AI-generated training plans.
II. Log exercise maximum weights.
III. Simulate or receive live IoT sensor data.
IV. Send SOS notifications.

### 3.1.2 Operation
**3.1.2.1 Admin**
I. Manage the gym operations, users, and business growth.
**3.1.2.2 Coach**
I. Manage team safety and evaluate athlete performances.
**3.1.2.3 Athlete**
I. Manage personal health profile and training routines.

### 3.1.3 Process
**3.1.3.1 Admin**
Login then review the dashboard for total revenue, register new athletes for 3, 6, or 12 months, manage maintenance notes for broken sensors, and finally sign out.
**3.1.3.2 Coach**
Login then view the team analytics to ensure no athlete is at a critical injury risk, adjust AI parameters if needed, and communicate via direct alerts with athletes.
**3.1.3.3 Athlete**
Log in and view real-time metrics, select the number of training days to generate an AI training plan, record weightlifting progress, and log out.

## 3.2 Relation database schema
Relationships are explained such as one to one, one to many, or many to many also an Attribute and its types are clarified.

### 3.2.1 Tables and Attributes

**User (Employee / Guest)**
| Attribute | Type | Notice |
| :--- | :--- | :--- |
| id | Integer | Primary Key |
| first_name | Varchar (45) | |
| email | Varchar (45) | Unique |
| hashed_password | Varchar (32) | |
| role | Enum | (Admin, Coach, Athlete) |

**SensorData**
| Attribute | Type | Notice |
| :--- | :--- | :--- |
| id | Integer | Primary Key |
| user_id | Integer | Foreign Key from Table User |
| heart_rate | Float | |
| steps | Integer | |
| calories | Float | |
| timestamp | DateTime | |

**AIPrediction**
| Attribute | Type | Notice |
| :--- | :--- | :--- |
| id | Integer | Primary Key |
| user_id | Integer | Foreign Key from Table User |
| injury_risk | Float | |
| recommendation | Varchar (255) | |

**WorkoutClass**
| Attribute | Type | Notice |
| :--- | :--- | :--- |
| id | Integer | Primary Key |
| class_name | Varchar (45) | |
| capacity | Integer | |

### 3.2.2 Database schema
In figure 11, there are tables and their relationships, for example, one-to-one relationship, one to many relationship and many to many as well as the types of attributes such as integer, varchar, and datetime, and also the constraints on the attributes such as the primary key.
*(Please insert Database Schema diagram here)*
**Figure 11. Database Schema**

### 3.2.3 Code
The code is written to create the project database which clarify the types of attributes such as integer, varchar, and datetime. These attributes are described by constraints such as the primary key, the foreign key, and the unique key.

**3.2.3.1 User Table Model (SQLAlchemy/FastAPI)**
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.ATHLETE)
    has_injury = Column(Integer, default=0)
```

**3.2.3.2 SensorData Table Model**
```python
class SensorData(Base):
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    heart_rate = Column(Float)
    steps = Column(Integer)
    calories = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
```

---

# Chapter Four: Implementation and Testing

## 4.1 Layouts
### 4.1.1 Athlete Interfaces
*(Please insert screenshots of the Athlete Dashboard, IoT Simulator, and AI Training Plan here)*
**Figure 12. Athlete Homepage**
**Figure 13. Health Metrics & AI Prediction**

### 4.1.2 Coach Interfaces
*(Please insert screenshots of the Coach Dashboard, Team Analytics, and SOS Alerts here)*
**Figure 14. Coach Dashboard & Alerts**

### 4.1.3 Admin Interfaces
*(Please insert screenshots of the Admin Dashboard, Revenue Charts, and Member Management here)*
**Figure 15. Admin Financial Analytics**
**Figure 16. Data Management (Athletes)**

## 4.2 Conclusion
The Smart-Gym-AI system successfully achieves its goal of bridging the gap between physical fitness and advanced technology. By employing real-time IoT tracking, sophisticated Machine Learning models, and instantaneous WebSocket communication, the project provides a safe, efficient, and highly responsive environment. The system not only minimizes the risk of sports injuries but also modernizes the administrative and coaching workflows of modern gymnasiums, outperforming traditional management ways.
