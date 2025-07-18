WITH emp_list AS (
    SELECT DISTINCT emp_code 
    FROM payroll_employee
    WHERE comp_code = '1000'
)
SELECT * FROM (
    -- Passport for all employees
    SELECT 
        e.emp_code,
        e.emp_name,
        e.prj_code,
        e.date_of_join,
        e.category,
        e.department,
        'Passport' AS document_type,
        e.passport_details AS doc_number,
        CASE WHEN e.passport_document IS NOT NULL THEN 'Available' ELSE 'Missing' END AS doc_status,
        CASE WHEN e.passport_document IS NULL THEN 'Not submitted' ELSE NULL END AS remarks
    FROM payroll_employee e
    JOIN emp_list l ON e.emp_code = l.emp_code
    WHERE e.passport_details IS NOT NULL
    
    UNION ALL
    
    -- Visa for all employees
    SELECT 
        e.emp_code,
        e.emp_name,
        e.prj_code,
        e.date_of_join,
        e.category,
        e.department,
        'VISA' AS document_type,
        e.visa_no AS doc_number,
        CASE WHEN e.visa_document IS NOT NULL THEN 'Available' ELSE 'Missing' END AS doc_status,
        CASE WHEN e.visa_document IS NULL THEN 'Not submitted' ELSE NULL END AS remarks
    FROM payroll_employee e
    JOIN emp_list l ON e.emp_code = l.emp_code
    WHERE e.visa_no IS NOT NULL
    
    UNION ALL
    
    -- Emirates ID for all employees
    SELECT 
        e.emp_code,
        e.emp_name,
        e.prj_code,
        e.date_of_join,
        e.category,
        e.department,
        'Emirates ID' AS document_type,
        e.emirates_no AS doc_number,
        CASE WHEN e.emirate_document IS NOT NULL THEN 'Available' ELSE 'Missing' END AS doc_status,
        CASE WHEN e.emirate_document IS NULL THEN 'Not submitted' ELSE NULL END AS remarks
    FROM payroll_employee e
    JOIN emp_list l ON e.emp_code = l.emp_code
    WHERE e.emirates_no IS NOT NULL
    
    UNION ALL
    
    -- Work Permit for all employees
    SELECT 
        e.emp_code,
        e.emp_name,
        e.prj_code,
        e.date_of_join,
        e.category,
        e.department,
        'Work Permit' AS document_type,
        e.work_permit_number AS doc_number,
        CASE WHEN e.work_permit_document IS NOT NULL THEN 'Available' ELSE 'Missing' END AS doc_status,
        CASE WHEN e.work_permit_document IS NULL THEN 'Not submitted' ELSE NULL END AS remarks
    FROM payroll_employee e
    JOIN emp_list l ON e.emp_code = l.emp_code
    WHERE e.work_permit_number IS NOT NULL
    
    UNION ALL
    
    -- ILOE for all employees
    SELECT 
        e.emp_code,
        e.emp_name,
        e.prj_code,
        e.date_of_join,
        e.category,
        e.department,
        'ILOE' AS document_type,
        e.iloe_no AS doc_number,
        CASE WHEN e.iloe_document IS NOT NULL THEN 'Available' ELSE 'Missing' END AS doc_status,
        CASE WHEN e.iloe_document IS NULL THEN 'Not submitted' ELSE NULL END AS remarks
    FROM payroll_employee e
    JOIN emp_list l ON e.emp_code = l.emp_code
    WHERE e.iloe_no IS NOT NULL
    
    UNION ALL
    
    -- Additional documents
    SELECT 
        e.emp_code,
        e.emp_name,
        e.prj_code,
        e.date_of_join,
        e.category,
        e.department,
        d.document_type,
        d.document_number,
        CASE WHEN d.document_file IS NOT NULL THEN 'Available' ELSE 'Missing' END AS doc_status,
        CASE WHEN d.document_file IS NULL THEN 'Not submitted' ELSE NULL END AS remarks
    FROM payroll_employee e
    JOIN payroll_employeedocument d ON e.emp_code = d.emp_code AND e.comp_code = d.comp_code
    JOIN emp_list l ON e.emp_code = l.emp_code
    WHERE d.document_number IS NOT NULL
) final_result
ORDER BY emp_code, document_type;