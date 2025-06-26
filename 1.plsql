DECLARE
    vSerl number := 0;
    vDocumentNo varchar2(30) := '';    
    vID number := 0;
    vComp varchar(50) := '1000';
    
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
    vTotal number := 0;  -- Changed to number
    vPaymentMode varchar2(100) := '';
    vTranNumber varchar2(100) := '';
    vTotalInWords varchar2(100) := '';
    vToken varchar2(100) := '';
    vDiscount number := 0;  -- Changed to number
    vSubTot number := 0;    -- Changed to number
    vVat number := 0;       -- Changed to number
    vOrderId number := :P12_ORDER_ID;

    vTranCount number := 0;
    vDetailsCount NUMBER := 0;
    vGlobalDiscount NUMBER := 0;
    
    -- Item calculation variables
    vItemAmount NUMBER := 0;
    vItemDiscount NUMBER := 0;
    vItemVat NUMBER := 0;
    vItemTotal NUMBER := 0;

BEGIN
    -- Debug: Check if order exists
    htp.p('{"Debug" : "Processing Order ID: ' || :P12_ORDER_ID || '"}');
    
    -- Check if order exists first
    SELECT COUNT(*) INTO vTranCount FROM ORDER_HEADER WHERE ORDER_ID = :P12_ORDER_ID;
    htp.p('{"Debug" : "Order count found: ' || vTranCount || '"}');
    
    IF vTranCount = 0 THEN
        htp.p('{"Status" : 2, "Msg" : "Order ID ' || :P12_ORDER_ID || ' not found"}');
        RETURN;
    END IF;
    
    -- Get new document number if not provided
    IF vDocumentNo = '' THEN
        FF_GET_SEED_NO(vComp,'','ONINV',vDocumentNo);
        htp.p('{"Debug" : "Generated Document No: ' || vDocumentNo || '"}');
    END IF;

    -- Get header data from ORDER_HEADER and SHIPPING tables
    SELECT 
        oh.ORDER_ID,
        oh.CUSTOMER_ID,
        oh.ORDER_DATE,
        oh.TOTAL_AMOUNT,
        oh.DISCOUNT_AMOUNT,
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
        vVat,
        vToken,
        vPaymentMode,
        vPaymentMode,
        vPaymentMode,
        vPaymentMode
    FROM ORDER_HEADER oh
    LEFT JOIN SHIPPING s ON oh.SHIPPING_ID = s.SHIPPING_ID
    WHERE oh.ORDER_ID = :P12_ORDER_ID;

    -- Debug: Check retrieved values
    htp.p('{"Debug" : "Customer: ' || vCustomer || '"}');
    htp.p('{"Debug" : "Customer Name: ' || vCustomerName || '"}');
    htp.p('{"Debug" : "Total: ' || vTotal || '"}');
    htp.p('{"Debug" : "Date: ' || vDate || '"}');

    -- Set customer name as combination of first and last name
    vCustomerName := NVL(vCustomerName, '') || ' ' || NVL(vPrimaryNo, '');
    
    -- Set address as complete address
    vAddress := NVL(vAddress, '') || ', ' || NVL(vLocation, '') || ', ' || NVL(vPaymentMode, '') || ', ' || NVL(vTranNumber, '');
    
    -- Set phone as primary contact
    vPrimaryNo := NVL(vEmail, '');
    
    -- Set alternate number as WhatsApp
    vAlternateNo := NVL(vAlternateNo, '');
    
    -- Set payment mode
    vPaymentMode := NVL(vPaymentMode, '');
    
    -- Set total in words (you may need to implement a function for this)
    vTotalInWords := 'Total Amount in Words'; -- Placeholder
    
    -- Set transaction number
    vTranNumber := TO_CHAR(vOrderId);

    -- Debug: Check processed values
    htp.p('{"Debug" : "Processed Customer Name: ' || vCustomerName || '"}');
    htp.p('{"Debug" : "Processed Address: ' || vAddress || '"}');
    htp.p('{"Debug" : "Document No: ' || vDocumentNo || '"}');

    -- Check if FF_INVOICE_HEADER table exists and is accessible
    BEGIN
        SELECT COUNT(*) INTO vTranCount FROM FF_INVOICE_HEADER WHERE ROWNUM = 1;
        htp.p('{"Debug" : "FF_INVOICE_HEADER table accessible"}');
    EXCEPTION
        WHEN OTHERS THEN
            htp.p('{"Status" : 2, "Msg" : "FF_INVOICE_HEADER table not accessible: ' || SQLERRM || '"}');
            RETURN;
    END;

    -- Insert header
    INSERT INTO FF_INVOICE_HEADER (
        COMP_CODE, DOCUMENT_NUMBER, DOCUMENT_TYPE, DOCUMENT_DATE,
        CUSTOMER, SALES_MAN, PAYMENT_TYPE, IS_ACTIVE,
        IS_APPROVED, CREATED_BY, CREATED_ON, TOTAL_AMOUNT,
        PAYMENT_MODE, REF_NUMBER, AMOUNT_IN_WORDS, TOKEN_NO, VAT, DISCOUNT, SUB_TOTAL
    ) VALUES (
        vComp, vDocumentNo, 'INV', TO_DATE(vDate,'DD-MON-YYYY'),
        vCustomer, NULL, vPaymentType, 'Y',
        'Y', :APP_USER, SYSDATE, vTotal,
        vPaymentMode, vTranNumber, vTotalInWords, vToken, vVat, vDiscount, vSubTot
    ) RETURNING ID INTO vID;

    htp.p('{"Debug" : "Inserted Header ID: ' || vID || '"}');
    :P12_VID := vID;

    -- Check if ORDER_DETAIL has data
    SELECT COUNT(*) INTO vDetailsCount FROM ORDER_DETAIL WHERE ORDER_ID = :P12_ORDER_ID;
    htp.p('{"Debug" : "Order details count: ' || vDetailsCount || '"}');

    -- Process details from ORDER_DETAIL table
    FOR dy IN (
        SELECT 
            od.DETAIL_ID,
            od.ORDER_ID,
            od.PRODUCT_ID,
            od.SKU_ID,
            od.SSIZE,
            od.SCOLOR,
            od.QUANTITY,
            od.UNIT_PRICE,
            od.IMG_SRC,
            od.TITLE
        FROM ORDER_DETAIL od
        WHERE od.ORDER_ID = :P12_ORDER_ID
    ) LOOP
        vSerl := vSerl + 1;
        
        -- Calculate amounts
        vItemAmount := dy.QUANTITY * dy.UNIT_PRICE;
        vItemDiscount := 0; -- Set discount as needed
        vItemVat := 0; -- Set VAT as needed
        vItemTotal := vItemAmount - vItemDiscount + vItemVat;
        
        htp.p('{"Debug" : "Processing Detail - Product: ' || dy.PRODUCT_ID || ', Qty: ' || dy.QUANTITY || ', Amount: ' || vItemAmount || '"}');
        
        INSERT INTO FF_INVOICE_DETAILS (
            COMP_CODE, REQUEST_ID, ITEM_CODE, ITEM_DESC,
            QUANTITY, PRICE, AMOUNT, SERL_NUMBER,
            IS_ACTIVE, CREATED_BY, CREATED_ON
        ) VALUES (
            vComp, vID, dy.PRODUCT_ID, dy.TITLE,
            dy.QUANTITY, dy.UNIT_PRICE, vItemAmount, vSerl,
            'Y', :APP_USER, SYSDATE
        );
    END LOOP;

    htp.p('{"Debug" : "Total Details Processed: ' || vSerl || '"}');
    COMMIT;
    htp.p('{"Status" : 1, "Msg" : "'|| vDocumentNo ||'","ID" : "'|| vID ||'"}');
EXCEPTION 
    WHEN NO_DATA_FOUND THEN
        ROLLBACK;
        htp.p('{"Status" : 2, "Msg" : "No data found for Order ID: ' || :P12_ORDER_ID || '" }');
    WHEN OTHERS THEN
        ROLLBACK;
        htp.p('{"Status" : 2, "Msg" : "'|| SQLERRM ||'", "Error_Code" : "'|| SQLCODE ||'" }');
END;