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

fake = Faker()


class EmployeeDatabase:
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

    def create_tables(self):
        """Create all required tables"""

        # Table 1: Personal Information
        employee_table = """
        CREATE TABLE IF NOT EXISTS employee (
            employee_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            middle_name VARCHAR(50),
            date_of_birth DATE NOT NULL,
            gender VARCHAR(10) CHECK (gender IN ('Male', 'Female', 'Other')),
            nationality VARCHAR(50),
            marital_status VARCHAR(20) CHECK (marital_status IN ('Single', 'Married', 'Divorced', 'Widowed')),
            social_security_number VARCHAR(20) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Table 2: Contact Information
        contact_info_table = """
        CREATE TABLE IF NOT EXISTS contact_info (
            contact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID REFERENCES employee(employee_id) ON DELETE CASCADE,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone_primary VARCHAR(20) NOT NULL,
            phone_secondary VARCHAR(20),
            address_line1 VARCHAR(200) NOT NULL,
            address_line2 VARCHAR(200),
            city VARCHAR(100) NOT NULL,
            state VARCHAR(100) NOT NULL,
            postal_code VARCHAR(20) NOT NULL,
            country VARCHAR(100) NOT NULL,
            emergency_contact_name VARCHAR(100),
            emergency_contact_phone VARCHAR(20),
            emergency_contact_relation VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Table 3: Employment Information
        employment_info_table = """
        CREATE TABLE IF NOT EXISTS employment_info (
            employment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID REFERENCES employee(employee_id) ON DELETE CASCADE,
            employee_number VARCHAR(20) UNIQUE NOT NULL,
            department VARCHAR(100) NOT NULL,
            position VARCHAR(100) NOT NULL,
            job_level VARCHAR(50) NOT NULL,
            employment_type VARCHAR(50) CHECK (employment_type IN ('Full-time', 'Part-time', 'Contract', 'Temporary')),
            hire_date DATE NOT NULL,
            termination_date DATE,
            employment_status VARCHAR(20) CHECK (employment_status IN ('Active', 'Inactive', 'Terminated', 'On Leave')),
            manager_id UUID REFERENCES employee(employee_id),
            work_location VARCHAR(100),
            salary DECIMAL(12, 2),
            currency VARCHAR(10) DEFAULT 'USD',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        # Table 4: Additional Employee Details
        employee_details_table = """
        CREATE TABLE IF NOT EXISTS employee_details (
            detail_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            employee_id UUID REFERENCES employee(employee_id) ON DELETE CASCADE,
            education_level VARCHAR(50),
            university VARCHAR(100),
            degree VARCHAR(100),
            graduation_year INTEGER,
            skills TEXT[],
            certifications TEXT[],
            languages TEXT[],
            previous_experience_years INTEGER,
            employee_photo_url VARCHAR(500),
            notes TEXT,
            performance_rating DECIMAL(3, 2) CHECK (performance_rating >= 1.0 AND performance_rating <= 5.0),
            last_promotion_date DATE,
            next_review_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        try:
            # Execute table creation
            self.cursor.execute(employee_table)
            self.cursor.execute(contact_info_table)
            self.cursor.execute(employment_info_table)
            self.cursor.execute(employee_details_table)

            self.conn.commit()
            print("All tables created successfully!")

        except Exception as e:
            self.conn.rollback()
            print(f"Error creating tables: {e}")
            raise

    def generate_sample_data(self, num_employees=100):
        """Generate sample data for 100 employees"""

        departments = ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'IT', 'Legal',
                       'Customer Service']
        positions = {
            'Engineering': ['Software Engineer', 'Senior Software Engineer', 'Lead Engineer', 'Engineering Manager',
                            'DevOps Engineer'],
            'Marketing': ['Marketing Specialist', 'Digital Marketing Manager', 'Content Manager', 'Brand Manager',
                          'Marketing Director'],
            'Sales': ['Sales Representative', 'Sales Manager', 'Account Executive', 'Sales Director',
                      'Business Development Manager'],
            'HR': ['HR Specialist', 'HR Manager', 'Recruiter', 'HR Director', 'HR Business Partner'],
            'Finance': ['Financial Analyst', 'Accountant', 'Finance Manager', 'CFO', 'Budget Analyst'],
            'Operations': ['Operations Manager', 'Operations Analyst', 'Operations Director', 'Process Manager',
                           'Quality Analyst'],
            'IT': ['IT Support Specialist', 'System Administrator', 'IT Manager', 'Network Engineer', 'IT Director'],
            'Legal': ['Legal Counsel', 'Legal Assistant', 'Compliance Officer', 'Legal Director', 'Contract Manager'],
            'Customer Service': ['Customer Service Rep', 'Customer Success Manager', 'Support Manager',
                                 'Customer Service Director']
        }

        job_levels = ['Entry', 'Mid', 'Senior', 'Lead', 'Manager', 'Director', 'VP', 'C-Level']
        employment_types = ['Full-time', 'Part-time', 'Contract', 'Temporary']
        education_levels = ['High School', 'Associate', 'Bachelor', 'Master', 'PhD']
        skills_pool = ['Python', 'JavaScript', 'SQL', 'Project Management', 'Data Analysis', 'Marketing', 'Sales',
                       'Communication', 'Leadership', 'Excel', 'PowerBI', 'Tableau', 'AWS', 'Azure', 'Docker',
                       'Kubernetes']

        employees_data = []

        for i in range(num_employees):
            # Generate personal info
            first_name = fake.first_name()[:50]  # Limit to 50 chars
            last_name = fake.last_name()[:50]  # Limit to 50 chars
            middle_name = fake.first_name()[:50] if random.choice([True, False]) else None
            date_of_birth = fake.date_of_birth(minimum_age=22, maximum_age=65)
            gender = random.choice(['Male', 'Female', 'Other'])
            nationality = fake.country()[:50]  # Limit to 50 chars
            marital_status = random.choice(['Single', 'Married', 'Divorced', 'Widowed'])
            # Generate a simple SSN format: XXX-XX-XXXX (11 chars including dashes)
            ssn = f"{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(1000, 9999)}"

            # Generate contact info
            email = f"{first_name.lower()}.{last_name.lower()}{i + 1}@company.com"
            phone_primary = fake.phone_number()[:20]  # Limit to 20 chars
            phone_secondary = fake.phone_number()[:20] if random.choice([True, False]) else None
            address_line1 = fake.street_address()[:200]  # Limit to 200 chars
            address_line2 = fake.secondary_address()[:200] if random.choice([True, False]) else None
            city = fake.city()[:100]  # Limit to 100 chars
            state = fake.state()[:100]  # Limit to 100 chars
            postal_code = fake.postcode()[:20]  # Limit to 20 chars
            country = fake.country()[:100]  # Limit to 100 chars
            emergency_contact_name = fake.name()[:100]  # Limit to 100 chars
            emergency_contact_phone = fake.phone_number()[:20]  # Limit to 20 chars
            emergency_contact_relation = random.choice(['Spouse', 'Parent', 'Sibling', 'Friend', 'Child'])

            # Generate employment info
            employee_number = f"EMP{str(i + 1).zfill(5)}"  # Format: EMP00001
            department = random.choice(departments)
            position = random.choice(positions[department])[:100]  # Limit to 100 chars
            job_level = random.choice(job_levels)
            employment_type = random.choice(employment_types)
            hire_date = fake.date_between(start_date='-10y', end_date='today')
            employment_status = random.choice(
                ['Active', 'Active', 'Active', 'Active', 'On Leave', 'Inactive'])  # Weighted toward Active
            work_location = fake.city()[:100]  # Limit to 100 chars
            salary = round(random.uniform(40000, 200000), 2)

            # Generate employee details
            education_level = random.choice(education_levels)
            university = (fake.company() + " University")[:100]  # Limit to 100 chars
            degree = f"{education_level} in {random.choice(['Computer Science', 'Business', 'Engineering', 'Marketing', 'Finance', 'Psychology'])}"[
                     :100]  # Limit to 100 chars
            graduation_year = random.randint(1995, 2023)
            skills = random.sample(skills_pool, random.randint(3, 8))
            certifications = [
                f"{random.choice(['AWS', 'Microsoft', 'Google', 'Salesforce'])} {random.choice(['Certified', 'Professional', 'Expert'])}"] if random.choice(
                [True, False]) else []
            languages = ['English'] + random.sample(['Spanish', 'French', 'German', 'Chinese', 'Japanese'],
                                                    random.randint(0, 2))
            previous_experience_years = random.randint(0, 20)
            performance_rating = round(random.uniform(2.5, 5.0), 2)
            last_promotion_date = fake.date_between(start_date=hire_date, end_date='today') if random.choice(
                [True, False]) else None
            next_review_date = fake.date_between(start_date='today', end_date='+1y')

            employee_data = {
                'personal': (first_name, last_name, middle_name, date_of_birth, gender, nationality, marital_status,
                             ssn),
                'contact': (email, phone_primary, phone_secondary, address_line1, address_line2, city, state,
                            postal_code, country, emergency_contact_name, emergency_contact_phone,
                            emergency_contact_relation),
                'employment': (employee_number, department, position, job_level, employment_type, hire_date, None,
                               employment_status, None, work_location, salary, 'USD'),
                'details': (education_level, university, degree, graduation_year, skills, certifications, languages,
                            previous_experience_years, None, None, performance_rating, last_promotion_date,
                            next_review_date)
            }

            employees_data.append(employee_data)

        return employees_data

    def insert_sample_data(self, employees_data):
        """Insert generated sample data into tables"""

        try:
            for employee_data in employees_data:
                # Insert personal info
                personal_query = """
                INSERT INTO employee (first_name, last_name, middle_name, date_of_birth, gender, nationality, marital_status, social_security_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING employee_id;
                """
                self.cursor.execute(personal_query, employee_data['personal'])
                employee_id = self.cursor.fetchone()['employee_id']

                # Insert contact info
                contact_query = """
                INSERT INTO contact_info (employee_id, email, phone_primary, phone_secondary, address_line1, address_line2, city, state, postal_code, country, emergency_contact_name, emergency_contact_phone, emergency_contact_relation)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                self.cursor.execute(contact_query, (employee_id,) + employee_data['contact'])

                # Insert employment info
                employment_query = """
                INSERT INTO employment_info (employee_id, employee_number, department, position, job_level, employment_type, hire_date, termination_date, employment_status, manager_id, work_location, salary, currency)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                self.cursor.execute(employment_query, (employee_id,) + employee_data['employment'])

                # Insert employee details
                details_query = """
                INSERT INTO employee_details (employee_id, education_level, university, degree, graduation_year, skills, certifications, languages, previous_experience_years, employee_photo_url, notes, performance_rating, last_promotion_date, next_review_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                self.cursor.execute(details_query, (employee_id,) + employee_data['details'])

            self.conn.commit()
            print(f"Successfully inserted {len(employees_data)} employees into the database!")

        except Exception as e:
            self.conn.rollback()
            print(f"Error inserting sample data: {e}")
            raise


def main():
    """Main function to run the employee database system"""

    print("Starting Employee Database System...")
    print(f"Connecting to database at {DB_CONFIG['host']}:{DB_CONFIG['port']}")

    # Initialize database
    db = EmployeeDatabase()

    try:
        # Connect to database
        db.connect()

        # Create tables
        print("Creating database tables...")
        db.create_tables()

        # Generate sample data
        print("Generating sample data for 100 employees...")
        employees_data = db.generate_sample_data(100)

        # Insert sample data
        print("Inserting sample data...")
        db.insert_sample_data(employees_data)
        print("\nEmployee database setup completed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close database connection
        db.disconnect()


if __name__ == "__main__":
    main()