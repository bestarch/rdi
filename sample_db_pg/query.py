import psycopg2
from psycopg2.extras import RealDictCursor
import random
import os
import time
from datetime import datetime, timedelta
from faker import Faker
import uuid


# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('POSTGRES_DB', 'localhost'),
    'database': 'employee_db',
    'user': os.getenv('POSTGRES_USER', 'admin'),
    'password': os.getenv('POSTGRES_PASSWORD', 'admin'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}


class Query:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to PostgreSQL database with retry logic"""
        max_retries = 30
        retry_count = 0

        while retry_count < max_retries:
            try:
                self.conn = psycopg2.connect(**DB_CONFIG)
                self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
                print("Connected to PostgreSQL database successfully!")
                return True
            except Exception as e:
                retry_count += 1
                print(f"Connection attempt {retry_count}/{max_retries} failed: {e}")
                if retry_count < max_retries:
                    print("Retrying in 2 seconds...")
                    time.sleep(2)
                else:
                    print("Max retries reached. Could not connect to database.")
                    raise


    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed.")

    def query_employees(self, limit=10):
        """Query and display employee information"""

        query = """
        SELECT 
            p.first_name,
            p.last_name,
            p.date_of_birth,
            c.email,
            c.phone_primary,
            c.city,
            c.state,
            e.employee_number,
            e.department,
            e.position,
            e.salary,
            e.employment_status,
            d.education_level,
            d.performance_rating
        FROM employee p
        JOIN contact_info c ON p.employee_id = c.employee_id
        JOIN employment_info e ON p.employee_id = e.employee_id
        JOIN employee_details d ON p.employee_id = d.employee_id
        WHERE e.employment_status = 'Active'
        ORDER BY p.last_name, p.first_name
        LIMIT %s;
        """

        try:
            self.cursor.execute(query, (limit,))
            employees = self.cursor.fetchall()

            print(f"\n--- Employee Information (First {limit} Active Employees) ---")
            for emp in employees:
                print(f"Name: {emp['first_name']} {emp['last_name']}")
                print(f"Employee Number: {emp['employee_number']}")
                print(f"Department: {emp['department']}")
                print(f"Position: {emp['position']}")
                print(f"Email: {emp['email']}")
                print(f"Location: {emp['city']}, {emp['state']}")
                print(f"Salary: ${emp['salary']:,.2f}")
                print(f"Performance Rating: {emp['performance_rating']}/5.0")
                print("-" * 50)

        except Exception as e:
            print(f"Error querying employees: {e}")


    def get_department_statistics(self):
        """Get statistics by department"""

        query = """
        SELECT 
            e.department,
            COUNT(*) as employee_count,
            AVG(e.salary) as avg_salary,
            MIN(e.salary) as min_salary,
            MAX(e.salary) as max_salary,
            AVG(d.performance_rating) as avg_performance
        FROM employment_info e
        JOIN employee_details d ON e.employee_id = d.employee_id
        WHERE e.employment_status = 'Active'
        GROUP BY e.department
        ORDER BY employee_count DESC;
        """

        try:
            self.cursor.execute(query)
            departments = self.cursor.fetchall()

            print(f"\n--- Department Statistics ---")
            for dept in departments:
                print(f"Department: {dept['department']}")
                print(f"  Employee Count: {dept['employee_count']}")
                print(f"  Average Salary: ${dept['avg_salary']:,.2f}")
                print(f"  Salary Range: ${dept['min_salary']:,.2f} - ${dept['max_salary']:,.2f}")
                print(f"  Average Performance: {dept['avg_performance']:.2f}/5.0")
                print("-" * 40)

        except Exception as e:
            print(f"Error getting department statistics: {e}")


if __name__ == "__main__":
    db = Query()
    try:
        # Connect to database
        db.connect()

        # Query and display some employees
        db.query_employees(10)

        # Show department statistics
        db.get_department_statistics()

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close database connection
        db.disconnect()
