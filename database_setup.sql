CREATE DATABASE algocracy_elections;
USE algocracy_elections;

CREATE TABLE students (
    id VARCHAR(6) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE, -- Added UNIQUE constraint to allow it to be referenced
    password VARCHAR(255),
    grade INT NOT NULL,
    class VARCHAR(50) NOT NULL,
    gender CHAR(1) NOT NULL,
    security_question VARCHAR(255),
    security_answer VARCHAR(255)
);

CREATE TABLE teachers (
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    grade INT NOT NULL,
    class VARCHAR(50) NOT NULL,
    security_question VARCHAR(255),
    security_answer VARCHAR(255)
);

CREATE TABLE positions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    scope VARCHAR(255) NOT NULL
);

CREATE TABLE candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    position_id INT NOT NULL,
    student_name VARCHAR(255) NOT NULL,
    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE, -- Added ON DELETE CASCADE
    FOREIGN KEY (student_name) REFERENCES students(name) ON DELETE CASCADE -- Added ON DELETE CASCADE
);

CREATE TABLE votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    position_id INT NOT NULL,
    voter_hash VARCHAR(255) NOT NULL,
    candidate_name VARCHAR(255) NOT NULL,
    timestamp DATETIME NOT NULL,
    FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE, -- Added ON DELETE CASCADE
    FOREIGN KEY (candidate_name) REFERENCES students(name) ON DELETE CASCADE -- Added ON DELETE CASCADE
);

CREATE TABLE metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(255) NOT NULL UNIQUE, -- Added UNIQUE constraint for 1-to-1 relationship
    academics INT,
    discipline INT,
    clubs INT,
    community_service INT,
    teacher INT,
    leadership INT,
    public_speaking INT,
    FOREIGN KEY (student_name) REFERENCES students(name) ON DELETE CASCADE -- Added ON DELETE CASCADE
);

CREATE TABLE weights (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_votes INT NOT NULL DEFAULT 30,
    academics INT NOT NULL DEFAULT 15,
    discipline INT NOT NULL DEFAULT 10,
    clubs INT NOT NULL DEFAULT 10,
    community_service INT NOT NULL DEFAULT 5,
    teacher INT NOT NULL DEFAULT 10,
    leadership INT NOT NULL DEFAULT 10,
    public_speaking INT NOT NULL DEFAULT 10
);

CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pin VARCHAR(255) NOT NULL DEFAULT '1234',
    voting_open BOOLEAN NOT NULL DEFAULT TRUE
);

-- Insert initial data
-- Note: Passwords are removed as they should be set by the user during registration, not pre-filled.
INSERT INTO students (id, name, grade, class, gender)
VALUES
    ('KJS001', 'sevenblue1', 7, 'Blue', 'F'),
    ('KJS002', 'sevenblue2', 7, 'Blue', 'M'),
    ('KJS003', 'sevenblue3', 7, 'Blue', 'F'),
    ('KJS004', 'sevenred1', 7, 'Red', 'F'),
    ('KJS005', 'sevenred2', 7, 'Red', 'M'),
    ('KJS006', 'sevenred3', 7, 'Red', 'F'),
    ('KJS007', 'sevengreen1', 7, 'Green', 'F'),
    ('KJS008', 'sevengreen2', 7, 'Green', 'M'),
    ('KJS009', 'sevengreen3', 7, 'Green', 'F');

INSERT INTO teachers (username, password, grade, class)
VALUES
    ('teacher7blue', '$2y$10$6g7K8v9r2t4y6u8i0o2p3u5q7w9x1z3a5c7e9g1i3k5m7o9q1s3u', 7, 'Blue'),
    ('teacher7red', '$2y$10$6g7K8v9r2t4y6u8i0o2p3u5q7w9x1z3a5c7e9g1i3k5m7o9q1s3u', 7, 'Red'),
    ('teacher7green', '$2y$10$6g7K8v9r2t4y6u8i0o2p3u5q7w9x1z3a5c7e9g1i3k5m7o9q1s3u', 7, 'Green');

INSERT INTO positions (name, scope)
VALUES
    ('School President', 'school'),
    ('Governor_Grade_7', 'grade_7'),
    ('Senator_Grade_7', 'grade_7'),
    ('Girl_Representative_Grade_7', 'grade_7'),
    ('MCA_Grade_7_Blue', 'grade_7_class_blue'),
    ('7_Blue_MP', 'grade_7_class_blue');

INSERT INTO candidates (position_id, student_name)
VALUES
    (1, 'sevenblue1'), (1, 'sevenred1'), (1, 'sevengreen1'),
    (2, 'sevenblue1'), (2, 'sevenred1'), (2, 'sevengreen1'),
    (3, 'sevenblue2'), (3, 'sevenred2'), (3, 'sevengreen2'),
    (4, 'sevenblue3'), (4, 'sevenred3'), (4, 'sevengreen3'),
    (5, 'sevenblue1'), (5, 'sevenblue2'), (5, 'sevenblue3'),
    (6, 'sevenblue1'), (6, 'sevenblue2'), (6, 'sevenblue3');

INSERT INTO weights (id) VALUES (1);
INSERT INTO admin (id) VALUES (1);