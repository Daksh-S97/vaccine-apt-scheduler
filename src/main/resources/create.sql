CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities(
    Time date,
    Username varchar(255) REFERENCES Caregivers(Username),
    Booked INT, -- 1 means booked 
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines(
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients(
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Appointments(
    id VARCHAR(500),
    patient VARCHAR(255) REFERENCES Patients(Username),
    caregiver VARCHAR(255) REFERENCES Caregivers(Username),
    vaccine VARCHAR(255) REFERENCES Vaccines(Name),
    appointment_time date,
    PRIMARY KEY(id)
);

