CREATE DATABASE college_db;
USE college_db;

CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(50)
);

INSERT INTO admins (username, password) VALUES ('admin', '1234');

CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    marks FLOAT,
    category VARCHAR(10)
);

CREATE TABLE courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(50),
    total_seats INT,
    available_seats INT,
    min_marks FLOAT
);

CREATE TABLE preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    course_id INT,
    preference_order INT
);

CREATE TABLE allocations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    course_id INT,
    round_no INT
);

select * from students;

select * from courses;

select * from preferences;
select * from allocations;