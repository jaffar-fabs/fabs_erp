# import os
# import time
# import schedule
# import django
# from django.core.mail import send_mail
# from django.db import connection

# # Setup Django environment
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "payroll.settings")
# django.setup()

# def run_leave_update():
#     print("Running leave and days update...")

#     try:
#         with connection.cursor() as cursor:
#             # Step 1: Call the stored procedure
#             cursor.execute("CALL update_employee_leave_and_days();")
#             print("Procedure executed.")

#             # Step 2: Fetch users with no_of_days = 50
#             cursor.execute("""
#                 SELECT pp.emp_code, e.email
#                 FROM payroll_employeeppdetails pp
#                 JOIN payroll_employee e ON pp.emp_code = e.emp_code
#                 WHERE pp.no_of_days = 50
#             """)
#             rows = cursor.fetchall()

#             # Step 3: Send email to each user
#             for emp_code, email in rows:
#                 subject = "Alert: 50 Days Mark Reached"
#                 message = f"Dear Employee {emp_code},\n\nYou have reached 50 days since your landing date.\nPlease take the necessary action.\n\nRegards,\nHR Department"
#                 send_mail(
#                     subject,
#                     message,
#                     "hr@example.com",  # From email
#                     [email],
#                     fail_silently=False,
#                 )
#                 print(f"Email sent to {email}")

#     except Exception as e:
#         print(f"Error during processing: {e}")

# # Schedule for 12:01 AM daily
# schedule.every().day.at("02:04").do(run_leave_update)

# print("Scheduler running... waiting for 12:01 AM")

# while True:
#     schedule.run_pending()
#     time.sleep(60)
