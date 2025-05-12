import os
import time
import datetime
import django
from django.core.mail import send_mail
from django.db import connection

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "payroll.settings")
django.setup()

def run_leave_update():
    print("Running leave and days update...")

    try:
        print("Starting leave and days update...")
        with connection.cursor() as cursor:
            # Step 1: Call the stored procedure
            cursor.execute("CALL update_employee_leave_and_days();")
            print("Procedure executed.")

            # Step 2: Fetch users with no_of_days = 50
            cursor.execute("""
                SELECT pp.emp_code, e.email
                FROM payroll_employeeppdetails pp
                JOIN payroll_employee e ON pp.emp_code = e.emp_code
                WHERE pp.no_of_days = 50
            """)
            rows = cursor.fetchall()

            # Step 3: Send email to each user
            for emp_code, email in rows:
                subject = "Alert: 50 Days Mark Reached"
                message = f"Dear Employee {emp_code},\n\nYou have reached 50 days since your landing date.\nPlease take the necessary action.\n\nRegards,\nHR Department"
                send_mail(
                    subject,
                    message,
                    "hr@example.com",  # From email
                    [email],
                    fail_silently=False,
                )
                print(f"Email sent to {email}")

    except Exception as e:
        print(f"Error during processing: {e}")

def wait_until(target_time):
    """Wait until the target time is reached"""
    while True:
        now = datetime.datetime.now()
        if now.hour == target_time.hour and now.minute == target_time.minute:
            return
        time.sleep(30)  # Check every 30 seconds

# Set target time to 20:38
target_time = datetime.time(14, 27)
print(f"Scheduler running... waiting for {target_time}")

while True:
    wait_until(target_time)
    run_leave_update()
    time.sleep(60)  # Wait a minute after execution to avoid multiple runs
