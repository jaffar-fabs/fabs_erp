DECLARE
    vSerl number := 0;
    vDocumentNo varchar2(30) := apex_application.g_x01;    
    vID number := 0;
    
    -- Header variables
    vCustomer varchar2(100) := '';
    vCustomerName varchar2(100) := '';
    vPrimaryNo varchar2(100) := '';
    vEmail varchar2(100) := '';
    vLocation varchar2(100) := '';
    vAddress varchar2(100) := '';
    vPaymentType varchar2(100) := '';
    vAlternateNo varchar2(100) := '';
    vDate varchar2(100) := '';
    vTotal varchar2(100) := 0;
    vPaymentMode varchar2(100) := '';
    vTranNumber varchar2(100) := '';
    vTotalInWords varchar2(100) := '';
    vToken varchar2(100) := '';
    vDiscount varchar2(50) := '';
    vSubTot varchar2(50) := '';
    vVat varchar(50) := '';
    vOrderId number := :P12_ORDER_ID;

    vTranCount number := 0;
    vDetailsCount NUMBER := 0;
    vGlobalDiscount NUMBER := 0;

BEGIN
    -- Get new document number if not provided
    IF nvl(vDocumentNo,'0') = '0' THEN
        FF_GET_SEED_NO(:COMP_CODE,'','INV',vDocumentNo);
    END IF;

    -- Get header data from ORDER_HEADER and SHIPPING tables
    SELECT 
        oh.ORDER_ID,
        oh.CUSTOMER_ID,
        oh.ORDER_DATE,
        oh.TOTAL_AMOUNT,
        oh.DISCOUNT_AMOUNT,
        oh.ORDER_INFO,
        oh.STATUS,
        oh.SHIPPING_ID,
        oh.ESTIMATED_DELIVERY,
        s.FIRST_NAME,
        s.LAST_NAME,
        s.PHONE,
        s.WHATSAPP,
        s.EMIRATE,
        s.POSTAL_CODE,
        s.STREET_ADDRESS,
        s.NOTE,
        s.PAYMENT_METHOD,
        s.EMAIL,
        s.FLAT,
        s.BUILDING,
        s.AREA
    INTO 
        vOrderId,
        vCustomer,
        vDate,
        vTotal,
        vDiscount,
        vToken,
        vPaymentType,
        vLocation,
        vAlternateNo,
        vCustomerName,
        vPrimaryNo,
        vEmail,
        vAddress,
        vPaymentMode,
        vTranNumber,
        vSubTot,
        vVat
    FROM ORDER_HEADER oh
    LEFT JOIN SHIPPING s ON oh.SHIPPING_ID = s.SHIPPING_ID
    WHERE oh.ORDER_ID = :P12_ORDER_ID;

    -- Set customer name as combination of first and last name
    vCustomerName := vCustomerName || ' ' || vPrimaryNo;
    
    -- Set address as complete address
    vAddress := vAddress || ', ' || vLocation || ', ' || vPaymentMode || ', ' || vTranNumber;
    
    -- Set phone as primary contact
    vPrimaryNo := vEmail;
    
    -- Set alternate number as WhatsApp
    vAlternateNo := vAlternateNo;
    
    -- Set payment mode
    vPaymentMode := vPaymentMode;
    
    -- Set total in words (you may need to implement a function for this)
    vTotalInWords := 'Total Amount in Words'; -- Placeholder
    
    -- Set transaction number
    vTranNumber := vOrderId;

    -- Insert/Update customer if needed
    IF vCustomer IS NULL THEN
        FF_GET_SEED_NO(:COMP_CODE,NULL,'CUS',vCustomer);

        INSERT INTO ff_customer_master(
            comp_code, customer_no, customer_name, customer_phone_number,
            customer_email, location, CUSTOMER_ADDRESS_1, payment_mode,
            customer_alternate_phone, is_active
        ) VALUES (
            :COMP_CODE, vCustomer, vCustomerName, vPrimaryNo,
            vEmail, vLocation, vAddress, vPaymentType,
            vAlternateNo, 'Y'
        );
    END IF;

    -- Insert header
    INSERT INTO FF_INVOICE_HEADER (
        COMP_CODE, DOCUMENT_NUMBER, DOCUMENT_TYPE, DOCUMENT_DATE,
        CUSTOMER, SALES_MAN, PAYMENT_TYPE, IS_ACTIVE,
        IS_APPROVED, CREATED_BY, CREATED_ON, TOTAL_AMOUNT,
        PAYMENT_MODE, REF_NUMBER, AMOUNT_IN_WORDS, TOKEN_NO, VAT, DISCOUNT, SUB_TOTAL
    ) VALUES (
        :COMP_CODE, vDocumentNo, 'INV', to_date(vDate,'DD-MON-YYYY'),
        vCustomer, NULL, vPaymentType, 'Y',
        'Y', :APP_USER, SYSDATE, vTotal,
        vPaymentMode, vTranNumber, vTotalInWords, vToken, vVat, vDiscount, vSubTot
    ) RETURNING ID INTO vID;

    :P87_VID := vID;

    -- Process details (you may need to add logic to get order details from another table)
    -- For now, this section is commented out as we need order details table
    /*
    FOR dy IN (
        SELECT * FROM ORDER_DETAILS 
        WHERE ORDER_ID = :P12_ORDER_ID
    ) LOOP
        vSerl := vSerl + 1;
        
        INSERT INTO FF_INVOICE_DETAILS (
            COMP_CODE, REQUEST_ID, ITEM_CODE, ITEM_DESC,
            ITEMS_SIZES, ITEM_COLOR, ACTUAL_PRICE, PRICE,
            QUANTITY, ITEM_DISCOUNT, AMOUNT, SERL_NUMBER,
            ITEM_VAT, ITEM_TOTAL, IS_ACTIVE, CREATED_BY, CREATED_ON
        ) VALUES (
            :COMP_CODE, vID, dy.PRODUCT_ID, dy.PRODUCT_NAME,
            dy.SIZE, dy.COLOR, dy.PRICE, dy.PRICE,
            dy.QUANTITY, dy.DISCOUNT, dy.SUBTOTAL, vSerl,
            dy.VAT, dy.TOTAL, 'Y', :APP_USER, SYSDATE
        );
    END LOOP;
    */

    COMMIT;
    htp.p('{"Status" : 1, "Msg" : "'|| vDocumentNo ||'","ID" : "'|| vID ||'"}');
EXCEPTION 
    WHEN OTHERS THEN
        ROLLBACK;
        htp.p('{"Status" : 2, "Msg" : "'|| SQLERRM ||'" }');
END;
    