def send_notification(request):
    set_comp_code(request)
    try:
        today = datetime.now().date()

        # Get all active notifications grouped by document type
        notifications = NotificationMaster.objects.filter(is_active=True, comp_code=COMP_CODE)
        
        # Process passport notifications
        passport_notifications = notifications.filter(doc_type='PASSPORT')
        if passport_notifications.exists():
            passport_documents = Employee.objects.filter(
                comp_code=COMP_CODE,
                expiry_date__isnull=False,
                emp_status='ACTIVE'
            )
            for notification in passport_notifications:
                expiring_passports = []
                for doc in passport_documents:
                    days_until_expiry = (doc.expiry_date - today).days
                    if notification.before_or_after_flag.lower() == 'before':
                        if 0 <= days_until_expiry <= notification.no_of_days:
                            expiring_passports.append((doc, days_until_expiry))
                    elif notification.before_or_after_flag.lower() == 'after':
                        if 0 < -days_until_expiry <= notification.no_of_days:
                            expiring_passports.append((doc, days_until_expiry))
                if expiring_passports:
                    to_emails = [email.strip() for email in notification.to_emails.split(',') if email.strip()]
                    cc_emails = [email.strip() for email in notification.cc_emails.split(',') if email.strip()]
                    
                    table_rows = "".join(
                        f"<tr><td>{doc.emp_code}</td><td>{doc.emp_name}</td><td>{doc.expiry_date}</td><td>{abs(days)} days {'remaining' if days > 0 else 'overdue'}</td></tr>"
                        for doc, days in expiring_passports
                    )
                    
                    email_body = f"""
                    Dear Team,<br><br>
                    Passport Alert for employees:<br><br>
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
                    <b>Alert Condition:</b> {'Expires within' if notification.before_or_after_flag == 'AFTER' else 'Expired since'} {notification.no_of_days} days<br><br>
                    Best regards,<br>
                    HR Department
                    """
                    
                    email = EmailMessage(
                        subject=f"Passport Expiry Notification - {notification.before_or_after_flag} {notification.no_of_days} days",
                        body=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=to_emails,
                        cc=cc_emails,
                    )
                    email.content_subtype = "html"
                    email.send(fail_silently=False)
                    print('Passport Expiry Notification sent to', to_emails)

        # Process visa notifications
        visa_notifications = notifications.filter(doc_type='VISA')
        if visa_notifications.exists():
            visa_documents = Employee.objects.filter(
                comp_code=COMP_CODE,
                visa_expiry_date__isnull=False,
                emp_status='ACTIVE'
            )
            
            for notification in visa_notifications:
                expiring_visas = []
                for doc in visa_documents:
                    days_until_expiry = (doc.visa_expiry_date - today).days
                    if notification.before_or_after_flag.lower() == 'before':
                        if 0 <= days_until_expiry <= notification.no_of_days:
                            expiring_visas.append((doc, days_until_expiry))
                    elif notification.before_or_after_flag.lower() == 'after':
                        if 0 < -days_until_expiry <= notification.no_of_days:
                            expiring_visas.append((doc, days_until_expiry))
                
                if expiring_visas:
                    to_emails = [email.strip() for email in notification.to_emails.split(',') if email.strip()]
                    cc_emails = [email.strip() for email in notification.cc_emails.split(',') if email.strip()]
                    
                    table_rows = "".join(
                        f"<tr><td>{doc.emp_code}</td><td>{doc.emp_name}</td><td>{doc.visa_expiry_date}</td><td>{abs(days)} days {'remaining' if days > 0 else 'overdue'}</td></tr>"
                        for doc, days in expiring_visas
                    )
                    
                    email_body = f"""
                    Dear Team,<br><br>
                    Visa Alert for employees:<br><br>
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
                    <b>Alert Condition:</b> {'Expires within' if notification.before_or_after_flag == 'AFTER' else 'Expired since'} {notification.no_of_days} days<br><br>
                    Best regards,<br>
                    HR Department
                    """
                    
                    email = EmailMessage(
                        subject=f"Visa Expiry Notification - {notification.before_or_after_flag} {notification.no_of_days} days",
                        body=email_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=to_emails,
                        cc=cc_emails,
                    )
                    email.content_subtype = "html"
                    email.send(fail_silently=False)
                    print('Visa Expiry Notification sent to', to_emails)
        return True

    except Exception as e:
        print(f"Error sending notifications: {str(e)}")
        return False
