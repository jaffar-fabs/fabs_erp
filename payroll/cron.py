from datetime import datetime
from django.core.mail import EmailMessage
from django.conf import settings
from payroll.models import NotificationMaster, Employee, EmployeeDocument


def send_notification(request):
    try:
        today = datetime.now().date()
        notifications = NotificationMaster.objects.filter(is_active=True)

        # Employee model document types
        employee_doc_types = {
            'PASSPORT': 'expiry_date',
            'ILOE': 'iloe_expiry',
            'EMIRATES_ID': 'emirate_expiry',
            'WORK_PERMIT': 'work_permit_expiry',
            'VISA': 'visa_expiry',
        }

        # EmployeeDocument model document types
        emp_doc_types = ['LICENSE', 'SITE MEDICAL', 'SITE PASS']

        # Handle Employee model docs
        for doc_type, expiry_field in employee_doc_types.items():
            doc_notifications = notifications.filter(doc_type=doc_type)
            if not doc_notifications.exists():
                continue

            for notification in doc_notifications:
                comp_code = notification.comp_code
                employees = Employee.objects.filter(
                    comp_code=comp_code,
                    emp_status='ACTIVE',
                ).exclude(**{f"{expiry_field}__isnull": True})

                expiring_docs = []
                for emp in employees:
                    expiry_date = getattr(emp, expiry_field)
                    days_until_expiry = (expiry_date - today).days

                    if notification.before_or_after_flag.lower() == 'before':
                        if 0 <= days_until_expiry <= notification.no_of_days:
                            expiring_docs.append((emp, days_until_expiry))
                    elif notification.before_or_after_flag.lower() == 'after':
                        if 0 < -days_until_expiry <= notification.no_of_days:
                            expiring_docs.append((emp, days_until_expiry))

                if expiring_docs:
                    to_emails = [email.strip() for email in notification.to_emails.split(',') if email.strip()]
                    cc_emails = [email.strip() for email in notification.cc_emails.split(',') if email.strip()]
                    table_rows = "".join(
                        f"<tr><td>{doc.emp_code}</td><td>{doc.emp_name}</td><td>{getattr(doc, expiry_field)}</td><td>{abs(days)} days {'remaining' if days > 0 else 'overdue'}</td></tr>"
                        for doc, days in expiring_docs
                    )
                    email_body = f"""
                    Dear Team,<br><br>
                    {notification.email_body}<br><br>
                    {doc_type} Alert for employees:<br><br>
                    <table border="1" cellpadding="5" cellspacing="0">
                        <tr>
                            <th>Emp Code</th>
                            <th>Name</th>
                            <th>Expiry Date</th>
                            <th>Status</th>
                        </tr>
                        {table_rows}
                    </table>
                    <br>
                    <b>Alert Condition:</b> {'Expires within' if notification.before_or_after_flag.lower() == 'before' else 'Expired since'} {notification.no_of_days} days<br><br>
                    Best regards,<br>
                    HR Department
                    """
                    email = EmailMessage(
                        subject=f"{doc_type} Expiry Notification - {notification.before_or_after_flag} {notification.no_of_days} days",
                        body=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=to_emails,
                        cc=cc_emails,
                    )
                    email.content_subtype = "html"
                    email.send(fail_silently=False)
                    print(f'{doc_type} Expiry Notification sent to', to_emails)

        # Handle EmployeeDocument model docs
        for doc_type in emp_doc_types:
            doc_notifications = notifications.filter(doc_type=doc_type)
            if not doc_notifications.exists():
                continue

            for notification in doc_notifications:
                comp_code = notification.comp_code
                # First, get all active employees with their details
                active_employees = Employee.objects.filter(comp_code=comp_code, emp_status='ACTIVE').values('emp_code', 'emp_name')

                # Create a mapping of emp_code to emp_name for quick lookup
                emp_code_to_name = {emp['emp_code']: emp['emp_name'] for emp in active_employees}

                documents = EmployeeDocument.objects.filter(
                    comp_code=comp_code,
                    document_type=doc_type,
                    expiry_date__isnull=False,
                    emp_code__in=emp_code_to_name.keys()  # Only documents belonging to active employees
                )

                expiring_docs = []
                for doc in documents:
                    days_until_expiry = (doc.expiry_date - today).days
                    
                    # Get employee details from our mapping
                    emp_name = emp_code_to_name.get(doc.emp_code, 'Unknown')
                    
                    if notification.before_or_after_flag.lower() == 'before':
                        if 0 <= days_until_expiry <= notification.no_of_days:
                            expiring_docs.append((doc.emp_code, emp_name, doc.expiry_date, days_until_expiry))
                    elif notification.before_or_after_flag.lower() == 'after':
                        if 0 < -days_until_expiry <= notification.no_of_days:
                            expiring_docs.append((doc.emp_code, emp_name, doc.expiry_date, days_until_expiry))

                if expiring_docs:
                    to_emails = [email.strip() for email in notification.to_emails.split(',') if email.strip()]
                    cc_emails = [email.strip() for email in notification.cc_emails.split(',') if email.strip()]
                    table_rows = "".join(
                        f"<tr><td>{emp_code}</td><td>{emp_name}</td><td>{expiry_date}</td><td>{abs(days)} days {'remaining' if days > 0 else 'overdue'}</td></tr>"
                        for emp_code, emp_name, expiry_date, days in expiring_docs
                    )
                    email_body = f"""
                    Dear Team,<br><br>
                    {notification.email_body}<br><br>
                    {doc_type} Alert for employees:<br><br>
                    <table border="1" cellpadding="5" cellspacing="0">
                        <tr>
                            <th>Emp Code</th>
                            <th>Name</th>
                            <th>Expiry Date</th>
                            <th>Status</th>
                        </tr>
                        {table_rows}
                    </table>
                    <br>
                    <b>Alert Condition:</b> {'Expires within' if notification.before_or_after_flag.lower() == 'before' else 'Expired since'} {notification.no_of_days} days<br><br>
                    Best regards,<br>
                    HR Department
                    """
                    email = EmailMessage(
                        subject=f"{doc_type} Expiry Notification - {notification.before_or_after_flag} {notification.no_of_days} days",
                        body=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=to_emails,
                        cc=cc_emails,
                    )
                    email.content_subtype = "html"
                    email.send(fail_silently=False)
                    print(f'{doc_type} Expiry Notification sent to', to_emails)

        return True
    except Exception as e:
        print("Error in send_notification:", str(e))
        return False