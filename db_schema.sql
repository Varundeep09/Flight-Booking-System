-- Flight Booking Simulator Database Schema
-- Complete SQL schema with constraints, indexes, and sample data

-- Create database
CREATE DATABASE IF NOT EXISTS flight_booking_db;
USE flight_booking_db;

-- Airlines table
CREATE TABLE airlines (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(3) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_airline_code (code)
);

-- Airports table  
CREATE TABLE airports (
    id INT PRIMARY KEY AUTO_INCREMENT,
    iata_code VARCHAR(3) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    country VARCHAR(100) NOT NULL DEFAULT 'India',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_iata_code (iata_code),
    INDEX idx_city (city)
);

-- Flights table
CREATE TABLE flights (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flight_no VARCHAR(10) UNIQUE NOT NULL,
    airline_id INT NOT NULL,
    origin_id INT NOT NULL,
    destination_id INT NOT NULL,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    base_fare DECIMAL(10,2) NOT NULL,
    total_seats INT NOT NULL DEFAULT 180,
    seats_available INT NOT NULL,
    aircraft_type VARCHAR(50) DEFAULT 'Boeing 737',
    status ENUM('SCHEDULED', 'DELAYED', 'CANCELLED') DEFAULT 'SCHEDULED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (airline_id) REFERENCES airlines(id) ON DELETE CASCADE,
    FOREIGN KEY (origin_id) REFERENCES airports(id) ON DELETE CASCADE,
    FOREIGN KEY (destination_id) REFERENCES airports(id) ON DELETE CASCADE,
    
    CHECK (seats_available >= 0),
    CHECK (seats_available <= total_seats),
    CHECK (departure_time < arrival_time),
    CHECK (base_fare > 0),
    
    INDEX idx_flight_no (flight_no),
    INDEX idx_route (origin_id, destination_id),
    INDEX idx_departure (departure_time),
    INDEX idx_airline (airline_id)
);

-- Bookings table
CREATE TABLE bookings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    pnr VARCHAR(10) UNIQUE NOT NULL,
    flight_id INT NOT NULL,
    passenger_name VARCHAR(200) NOT NULL,
    passenger_age INT NOT NULL,
    passenger_phone VARCHAR(15) NOT NULL,
    passenger_email VARCHAR(100),
    seat_number VARCHAR(5) NOT NULL,
    booking_status ENUM('CONFIRMED', 'CANCELLED', 'PENDING') DEFAULT 'PENDING',
    final_fare DECIMAL(10,2) NOT NULL,
    booking_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_status ENUM('SUCCESS', 'FAILED', 'PENDING') DEFAULT 'PENDING',
    
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE CASCADE,
    
    CHECK (passenger_age > 0 AND passenger_age < 120),
    CHECK (final_fare > 0),
    
    INDEX idx_pnr (pnr),
    INDEX idx_flight_booking (flight_id),
    INDEX idx_booking_time (booking_time),
    INDEX idx_passenger_phone (passenger_phone)
);

-- Fare history table for analytics
CREATE TABLE fare_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flight_id INT NOT NULL,
    calculated_fare DECIMAL(10,2) NOT NULL,
    seats_remaining INT NOT NULL,
    demand_level ENUM('LOW', 'MEDIUM', 'HIGH') NOT NULL,
    time_to_departure INT NOT NULL, -- hours
    seat_factor DECIMAL(3,2) NOT NULL,
    time_factor DECIMAL(3,2) NOT NULL,
    demand_factor DECIMAL(3,2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (flight_id) REFERENCES flights(id) ON DELETE CASCADE,
    
    INDEX idx_flight_fare (flight_id),
    INDEX idx_recorded_time (recorded_at)
);

-- Insert sample airlines
INSERT INTO airlines (name, code) VALUES
('Air India', 'AI'),
('IndiGo', '6E'),
('SpiceJet', 'SG'),
('Vistara', 'UK'),
('GoAir', 'G8');

-- Insert sample airports
INSERT INTO airports (iata_code, name, city, country) VALUES
('DEL', 'Indira Gandhi International Airport', 'Delhi', 'India'),
('BOM', 'Chhatrapati Shivaji International Airport', 'Mumbai', 'India'),
('BLR', 'Kempegowda International Airport', 'Bangalore', 'India'),
('MAA', 'Chennai International Airport', 'Chennai', 'India'),
('CCU', 'Netaji Subhas Chandra Bose International Airport', 'Kolkata', 'India'),
('HYD', 'Rajiv Gandhi International Airport', 'Hyderabad', 'India'),
('AMD', 'Sardar Vallabhbhai Patel International Airport', 'Ahmedabad', 'India'),
('GOI', 'Goa International Airport', 'Goa', 'India');

-- Insert sample flights (next 7 days)
INSERT INTO flights (flight_no, airline_id, origin_id, destination_id, departure_time, arrival_time, base_fare, total_seats, seats_available, aircraft_type) VALUES
-- Delhi to Mumbai flights
('AI101', 1, 1, 2, '2024-01-15 06:00:00', '2024-01-15 08:30:00', 5500.00, 180, 120, 'Boeing 737'),
('6E201', 2, 1, 2, '2024-01-15 08:15:00', '2024-01-15 10:45:00', 4800.00, 180, 95, 'Airbus A320'),
('SG301', 3, 1, 2, '2024-01-15 14:30:00', '2024-01-15 17:00:00', 4200.00, 180, 150, 'Boeing 737'),
('UK401', 4, 1, 2, '2024-01-15 19:45:00', '2024-01-15 22:15:00', 6200.00, 180, 75, 'Airbus A321'),

-- Mumbai to Bangalore flights  
('AI102', 1, 2, 3, '2024-01-15 07:30:00', '2024-01-15 09:00:00', 4500.00, 180, 110, 'Boeing 737'),
('6E202', 2, 2, 3, '2024-01-15 12:00:00', '2024-01-15 13:30:00', 3800.00, 180, 140, 'Airbus A320'),
('SG302', 3, 2, 3, '2024-01-15 16:15:00', '2024-01-15 17:45:00', 3500.00, 180, 165, 'Boeing 737'),

-- Bangalore to Chennai flights
('AI103', 1, 3, 4, '2024-01-15 09:00:00', '2024-01-15 10:15:00', 3200.00, 180, 130, 'Boeing 737'),
('6E203', 2, 3, 4, '2024-01-15 15:30:00', '2024-01-15 16:45:00', 2800.00, 180, 155, 'Airbus A320'),

-- Delhi to Bangalore flights
('AI104', 1, 1, 3, '2024-01-15 11:30:00', '2024-01-15 14:00:00', 6800.00, 180, 85, 'Boeing 777'),
('6E204', 2, 1, 3, '2024-01-15 17:00:00', '2024-01-15 19:30:00', 5900.00, 180, 100, 'Airbus A320'),

-- Mumbai to Delhi flights (return)
('AI105', 1, 2, 1, '2024-01-15 10:00:00', '2024-01-15 12:30:00', 5800.00, 180, 90, 'Boeing 737'),
('6E205', 2, 2, 1, '2024-01-15 18:30:00', '2024-01-15 21:00:00', 5100.00, 180, 125, 'Airbus A320');

-- Sample complex queries demonstrating SQL concepts

-- 1. JOIN query - Flight search with airline and airport details
SELECT 
    f.flight_no,
    a.name as airline_name,
    orig.iata_code as origin_code,
    orig.city as origin_city,
    dest.iata_code as destination_code,
    dest.city as destination_city,
    f.departure_time,
    f.arrival_time,
    f.base_fare,
    f.seats_available,
    TIMEDIFF(f.arrival_time, f.departure_time) as duration
FROM flights f
JOIN airlines a ON f.airline_id = a.id
JOIN airports orig ON f.origin_id = orig.id
JOIN airports dest ON f.destination_id = dest.id
WHERE orig.iata_code = 'DEL' 
AND dest.iata_code = 'BOM'
AND DATE(f.departure_time) = '2024-01-15'
AND f.status = 'SCHEDULED'
AND f.seats_available > 0
ORDER BY f.departure_time;

-- 2. Aggregation query - Booking statistics by airline
SELECT 
    a.name as airline_name,
    COUNT(b.id) as total_bookings,
    SUM(b.final_fare) as total_revenue,
    AVG(b.final_fare) as avg_fare,
    COUNT(CASE WHEN b.booking_status = 'CONFIRMED' THEN 1 END) as confirmed_bookings,
    COUNT(CASE WHEN b.booking_status = 'CANCELLED' THEN 1 END) as cancelled_bookings
FROM airlines a
LEFT JOIN flights f ON a.id = f.airline_id
LEFT JOIN bookings b ON f.id = b.flight_id
GROUP BY a.id, a.name
HAVING total_bookings > 0
ORDER BY total_revenue DESC;

-- 3. Subquery - Flights with above average occupancy
SELECT 
    f.flight_no,
    a.name as airline,
    f.total_seats - f.seats_available as occupied_seats,
    ROUND(((f.total_seats - f.seats_available) / f.total_seats) * 100, 2) as occupancy_percentage
FROM flights f
JOIN airlines a ON f.airline_id = a.id
WHERE (f.total_seats - f.seats_available) > (
    SELECT AVG(total_seats - seats_available) 
    FROM flights 
    WHERE status = 'SCHEDULED'
)
ORDER BY occupancy_percentage DESC;

-- 4. Window function - Ranking flights by fare within each route
SELECT 
    f.flight_no,
    a.name as airline,
    orig.iata_code as origin,
    dest.iata_code as destination,
    f.base_fare,
    RANK() OVER (
        PARTITION BY f.origin_id, f.destination_id 
        ORDER BY f.base_fare
    ) as fare_rank
FROM flights f
JOIN airlines a ON f.airline_id = a.id
JOIN airports orig ON f.origin_id = orig.id
JOIN airports dest ON f.destination_id = dest.id
WHERE f.status = 'SCHEDULED';

-- 5. Transaction example for booking process
DELIMITER //
CREATE PROCEDURE BookFlight(
    IN p_flight_id INT,
    IN p_passenger_name VARCHAR(200),
    IN p_passenger_age INT,
    IN p_passenger_phone VARCHAR(15),
    IN p_seat_number VARCHAR(5),
    IN p_final_fare DECIMAL(10,2),
    OUT p_pnr VARCHAR(10),
    OUT p_result VARCHAR(100)
)
BEGIN
    DECLARE v_seats_available INT;
    DECLARE v_pnr VARCHAR(10);
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result = 'Booking failed due to error';
    END;

    START TRANSACTION;
    
    -- Lock and check seat availability
    SELECT seats_available INTO v_seats_available
    FROM flights 
    WHERE id = p_flight_id 
    FOR UPDATE;
    
    IF v_seats_available <= 0 THEN
        ROLLBACK;
        SET p_result = 'No seats available';
    ELSE
        -- Generate PNR
        SET v_pnr = CONCAT('AI', LPAD(FLOOR(RAND() * 999999), 6, '0'));
        
        -- Insert booking
        INSERT INTO bookings (
            pnr, flight_id, passenger_name, passenger_age, 
            passenger_phone, seat_number, final_fare, 
            booking_status, payment_status
        ) VALUES (
            v_pnr, p_flight_id, p_passenger_name, p_passenger_age,
            p_passenger_phone, p_seat_number, p_final_fare,
            'CONFIRMED', 'SUCCESS'
        );
        
        -- Update seat availability
        UPDATE flights 
        SET seats_available = seats_available - 1 
        WHERE id = p_flight_id;
        
        COMMIT;
        SET p_pnr = v_pnr;
        SET p_result = 'Booking successful';
    END IF;
END //
DELIMITER ;

-- 6. View for flight search results with calculated fields
CREATE VIEW flight_search_view AS
SELECT 
    f.id,
    f.flight_no,
    a.name as airline_name,
    a.code as airline_code,
    orig.iata_code as origin_code,
    orig.name as origin_name,
    orig.city as origin_city,
    dest.iata_code as destination_code,
    dest.name as destination_name,
    dest.city as destination_city,
    f.departure_time,
    f.arrival_time,
    f.base_fare,
    f.seats_available,
    f.total_seats,
    ROUND(((f.total_seats - f.seats_available) / f.total_seats) * 100, 2) as occupancy_percentage,
    TIMEDIFF(f.arrival_time, f.departure_time) as duration_time,
    TIME_TO_SEC(TIMEDIFF(f.arrival_time, f.departure_time)) / 3600 as duration_hours
FROM flights f
JOIN airlines a ON f.airline_id = a.id
JOIN airports orig ON f.origin_id = orig.id
JOIN airports dest ON f.destination_id = dest.id
WHERE f.status = 'SCHEDULED';

-- 7. Indexes for performance optimization
CREATE INDEX idx_flight_search ON flights(origin_id, destination_id, departure_time, status);
CREATE INDEX idx_booking_passenger ON bookings(passenger_phone, booking_status);
CREATE INDEX idx_fare_analysis ON fare_history(flight_id, recorded_at, demand_level);

-- 8. Sample data for testing different scenarios
INSERT INTO bookings (pnr, flight_id, passenger_name, passenger_age, passenger_phone, seat_number, booking_status, final_fare, payment_status) VALUES
('AI123456', 1, 'John Doe', 35, '+919876543210', '12A', 'CONFIRMED', 6500.00, 'SUCCESS'),
('AI123457', 1, 'Jane Smith', 28, '+919876543211', '12B', 'CONFIRMED', 6500.00, 'SUCCESS'),
('AI123458', 2, 'Bob Johnson', 42, '+919876543212', '15C', 'CONFIRMED', 5200.00, 'SUCCESS'),
('AI123459', 3, 'Alice Brown', 31, '+919876543213', '8A', 'CANCELLED', 4500.00, 'SUCCESS');

-- Update seats_available after sample bookings
UPDATE flights SET seats_available = seats_available - 2 WHERE id = 1;
UPDATE flights SET seats_available = seats_available - 1 WHERE id = 2;

-- Sample fare history data
INSERT INTO fare_history (flight_id, calculated_fare, seats_remaining, demand_level, time_to_departure, seat_factor, time_factor, demand_factor) VALUES
(1, 6500.00, 118, 'HIGH', 48, 1.20, 1.10, 1.30),
(1, 7200.00, 115, 'HIGH', 24, 1.25, 1.40, 1.30),
(2, 5200.00, 94, 'MEDIUM', 48, 1.50, 1.10, 1.15),
(3, 4500.00, 150, 'LOW', 72, 0.95, 1.00, 1.00);