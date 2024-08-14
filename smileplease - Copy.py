import mysql.connector 
import random
import string
import webbrowser

class BookingSystem:
    def __init__(self, conn):
        self.conn = conn

    def fetch_all(self, query, values):
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        result = cursor.fetchall()
        cursor.close()
        return result

    def check_availability(self, name, age):
        query = "SELECT * FROM tickets WHERE name = %s AND age = %s"
        values = (name, age)
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, values)
            tickets = cursor.fetchall()
            cursor.close()

            if tickets:
                print("Ticket is found.")
            else:
                print("Ticket is not available.")
        
        except mysql.connector.Error as err:
            print(f"Error: {err}")

    def cancel_ticket(self, name, age, gender, ticket_id):
        cursor = self.conn.cursor()
        query = "DELETE FROM tickets WHERE name = %s AND age = %s AND gender = %s AND ticket_id = %s"
        values = (name, age, gender, ticket_id)
        try:
            cursor=self.conn.cursor()
            cursor.execute(query,values)
            if cursor.rowcount>0:
                print("ticket cancel")
            else:
                print("ticket not found")
            cursor.close()
        except mysql.connector.Error as f:
            print(f"mysql Error:{f}")

    def book_ticket(self, start_line, end_line, start_station, end_station, name, age, gender):
        cursor = self.conn.cursor()

        def fetch_distance_and_fare(line, station):
            query = f"SELECT distance_km, fare_inr FROM {line} WHERE station = %s"
            cursor.execute(query, (station,))
            return cursor.fetchone()

        try:
            start_distance, start_fare = fetch_distance_and_fare(start_line, start_station)
            end_distance, end_fare = fetch_distance_and_fare(end_line, end_station)

            if not start_distance or not end_distance:
                print("Invalid stations selected.")
                return

            total_distance = abs(end_distance - start_distance)
            total_fare = (start_fare if start_fare is not None else 0) + (end_fare if end_fare is not None else 0)

            if age < 5:
                age_group = 'Child'# 10%discount
            elif age >= 60:
                age_group = 'Senior'
            else:
                age_group = 'Adult'

            fare = self.calculate_fare(total_distance, total_fare, age_group)

            ticket_id = self.generate_ticket_id()
            print(f"Ticket booked with ID: {ticket_id}")
            print(f"From {start_station} ({start_line} Line) to {end_station} ({end_line} Line).")
            print(f"Passenger Details: Age - {age}, Gender - {gender}")
            print(f"Total Distance: {total_distance} km")
            print(f"Total Fare: {fare} rs")
            if start_line =='redline'and end_line=='blueline':
                print("note: please change the line in ammerpet for buleline")
            elif start_line == 'blueline' and end_line == 'greenline':
                print("Note:  a change at MG Bus Station for greenline.")
            elif start_line=='greenline' and end_line=='blueline':
                print("note:change in mgbs")
            else:
                print("Note: Your journey involves  no changes.")

            # Insert into database
            query =  "INSERT INTO tickets ( name, age, gender,ticket_id) VALUES (%s, %s, %s, %s)"
            values = (name, age,gender,ticket_id)
            cursor.execute(query, values)
            self.conn.commit()

        except mysql.connector.Error as e:
            print(f"MySQL Error: {e}")

        finally:
            cursor.close()

    def generate_ticket_id(self):
        ticket_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return ticket_id

    def calculate_fare(self, distance, fare_per_km, age_group):
        if age_group == 'Child':
            fare_per_km *= 0.5
        elif age_group == 'Senior':
            fare_per_km *= 0.7
        return distance * fare_per_km

def connect_to_database():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='siva',
            user='root',
            password='siva8686'
        )
        if conn.is_connected():
            print('Connected to MySQL database')
            return conn
    except mysql.connector.Error as e:
        print(f'Error connecting to MySQL database: {e}')
        return None

def fetch_station_names(conn, table_name):
    cursor = conn.cursor()
    query = f'SELECT station FROM {table_name}'
    cursor.execute(query)
    stations = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return stations

def open_scanner():
    scanner_url = "https://youtube.com/shorts/h3YLy2Sva44?si=qJoB4RLTjvlxpCMi"
    webbrowser.open(scanner_url)
    print("Scanner opened successfully.")

def main():
    conn = connect_to_database()
    if not conn:
        return

    booking_system = BookingSystem(conn)

    while True:
        red_line_stations = fetch_station_names(conn, 'redline')
        blue_line_stations = fetch_station_names(conn, 'blueline')
        green_line_stations = fetch_station_names(conn, 'greenline')

        print("\nAvailable Metro Lines:")
        print("1. Red Line")
        print("2. Blue Line")
        print("3. Green Line")
        print("4. Exit")
        print("5. View Tickets and Open Scanner")
        print("6. Check Ticket Availability")
        print("7. Cancel My Ticket")

        choice = input("Enter your choice: ")

        if choice == '1':
            start_line = 'redline'
            start_stations = red_line_stations
        elif choice == '2':
            start_line = 'blueline'
            start_stations = blue_line_stations
        elif choice == '3':
            start_line = 'greenline'
            start_stations = green_line_stations
        elif choice == '4':
            print("Exiting the program. Goodbye!")
            return
        elif choice == '5':
            open_scanner()
        elif choice == '6':
            name = input("Enter a name: ")
            age = int(input("Enter an age: "))
            booking_system.check_availability(name, age)
        elif choice == '7':
            name = input("Enter a name: ")
            age = int(input("Enter an age: "))
            gender = input("Enter a gender (male/female): ")
            ticket_id = input("Enter a ticket ID: ")
            booking_system.cancel_ticket(name, age, gender, ticket_id)
            continue
        else:
            print("Invalid choice.")
            continue

        end_choice = input("Enter your end choice: ")

        if end_choice == '1':
            end_line = 'redline'
            end_stations = red_line_stations
        elif end_choice == '2':
            end_line = 'blueline'
            end_stations = blue_line_stations
        elif end_choice == '3':
            end_line = 'greenline'
            end_stations = green_line_stations
        elif end_choice == '4':
            print("Exiting the program. Goodbye!")
            return
        else:
            print("Invalid choice.")
            continue

        print(f"\nStations on {start_line.split('_')[-1].title()} Line:")
        for i, station in enumerate(start_stations, start=1):
            print(f"{i}. {station}")

        start_index = int(input("Enter start station number: ")) - 1
        start_station = start_stations[start_index]

        print(f"\nStations on {end_line.split('_')[-1].title()} Line:")
        for i, station in enumerate(end_stations, start=1):
            print(f"{i}. {station}")

        end_index = int(input("Enter end station number: ")) - 1
        end_station = end_stations[end_index]
        name = input("Enter passenger name: ")
        age = int(input("Enter passenger age: "))
        gender = input("Enter passenger gender (male/female): ")

        booking_system.book_ticket(start_line, end_line, start_station, end_station, name, age, gender)

if __name__ == "__main__":
    main()
