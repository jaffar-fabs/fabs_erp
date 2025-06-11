SELECT 
    ID,
    ORDER_NUMBER,
    ORDER_DATE,
    CUSTOMER_ID,
    CUSTOMER_NAME,
    DUE_DATE,
    PASS_TYPE,
    REMARKS AS "ORDER DESCRIPTION",
    VACANCIES,
    COMPANY || ' - ' || (
        SELECT COMPANY_NAME
        FROM ADD_COMPANY
        WHERE COMPANY_ID = COMPANY
    ) AS COMPANY,
    APEX_ITEM.SELECT_LIST_FROM_QUERY(
        2,
        null,
        'SELECT application_number || '':'' || applicant_name as display_value, application_number as return_value FROM mio_profiles WHERE company_code = ''1000'' AND profile_status = ''SLT'' ORDER BY application_number',
        'style="width:150px"',
        'YES',
        '- Select -'
    ) || apex_item.hidden(3, ID) AS DROPDOWN_SELECT,
    SELECTT
FROM MIO_SALE_ORDER 

BACKEND
DECLARE
    l_order_id          NUMBER;
    l_order_number      VARCHAR2(255);
    l_dropdown_value    VARCHAR2(255);
    l_count             NUMBER := 0;
    l_error_message     VARCHAR2(4000);
    l_profile_count     NUMBER;
BEGIN
    -- Process each dropdown value
    FOR i IN 1..apex_application.g_f02.COUNT LOOP
        BEGIN
            -- Get the ID from hidden field
            l_order_id := TO_NUMBER(apex_application.g_f03(i));
            
            -- Get order number from ID
            BEGIN
                SELECT ORDER_NUMBER INTO l_order_number
                FROM MIO_SALE_ORDER
                WHERE ID = l_order_id;
                
                -- Verify order details
                apex_debug.message('Processing row ' || i || ': Order ID: ' || l_order_id || ', Order Number: ' || l_order_number);

                -- Get the dropdown value (now directly the application_number)
                l_dropdown_value := apex_application.g_f02(i);
                
                -- Verify dropdown value
                apex_debug.message('Row ' || i || ': Selected application number: ' || l_dropdown_value);

                IF l_dropdown_value IS NOT NULL AND l_dropdown_value != '- Select -' THEN
                    -- Check if profile exists with given conditions
                    SELECT COUNT(*)
                    INTO l_profile_count
                    FROM mio_profiles
                    WHERE APPLICATION_NUMBER = l_dropdown_value
                    AND company_code = '1000'
                    AND profile_status = 'SLT';
                    
                    apex_debug.message('Row ' || i || ': Found ' || l_profile_count || ' matching profiles');

                    IF l_profile_count > 0 THEN
                        UPDATE mio_profiles
                        SET
                            res_order_no   = l_order_number,
                            res_order_date = SYSDATE,
                            profile_status = 'RES'
                        WHERE
                            APPLICATION_NUMBER = l_dropdown_value
                            AND company_code = '1000'
                            AND profile_status = 'SLT';

                        l_count := l_count + SQL%ROWCOUNT;
                        apex_debug.message('Row ' || i || ': Updated ' || SQL%ROWCOUNT || ' rows');
                    ELSE
                        apex_debug.message('Row ' || i || ': No matching profile found for update');
                    END IF;
                END IF;
            EXCEPTION
                WHEN NO_DATA_FOUND THEN
                    apex_debug.message('Row ' || i || ': Order ID ' || l_order_id || ' not found in MIO_SALE_ORDER');
            END;

        EXCEPTION
            WHEN OTHERS THEN
                l_error_message := 'Error updating profile for row ' || i || ', order ID ' || l_order_id || ', application number '
                                   || l_dropdown_value
                                   || ': '
                                   || SQLERRM;

                apex_debug.message(l_error_message);
        END;
    END LOOP;

    COMMIT;

    apex_application.g_print_success_message := 'Successfully updated ' || l_count || ' profile(s).';

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;

        apex_application.g_print_success_message := 'Error updating profiles: ' || SQLERRM;

        apex_debug.error('Error in PL/SQL process: ' || SQLERRM || CHR(10) || DBMS_UTILITY.FORMAT_ERROR_BACKTRACE);

        RAISE;
END; 