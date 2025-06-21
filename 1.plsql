declare
vSerl number := 0;
vDocumentNo varchar2(30) :=  '';    
vID number := 0;
vData clob := apex_application.g_clob_01;
vHeaderCount number := 0;
vDetailCount number := 0;
vJsonValid boolean := false;
vSeedError boolean := false;
vTranType varchar2(30) := '';
vTranDate date := sysdate;

begin

--FF_GET_SEED_NO_THAILAND('1000',null, apex_application.g_x02, to_date(apex_application.g_x01,'DD-MON-YYYY'), vDocumentNo);
-- Try to generate document number, but don't fail if seed is not set
begin
    FF_GET_SEED_NO_THAILAND_INVENTORY('1000',null, apex_application.g_x02, to_date(apex_application.g_x01,'DD-MON-YYYY'), vDocumentNo);
    htp.p('<!-- Debug: Document number generated: ' || vDocumentNo || ' -->');
exception
    when others then
        vSeedError := true;
        vDocumentNo := 'TEMP_' || to_char(sysdate, 'YYYYMMDDHH24MISS');
        htp.p('<!-- Debug: Seed generation failed, using temporary number: ' || vDocumentNo || ' -->');
end;

-- Debug: Log the incoming data
htp.p('<!-- Debug: Incoming data length: ' || length(vData) || ' -->');

-- Debug: Show first 500 characters of the data
if length(vData) > 0 then
    htp.p('<!-- Debug: Data preview: ' || substr(vData, 1, 500) || ' -->');
else
    htp.p('<!-- Debug: No data received (empty CLOB) -->');
end if;

-- Check if JSON is valid
begin
    select count(*) into vHeaderCount from json_table(vData, '$.header' columns (dummy varchar2(1) path '$.ttype'));
    vJsonValid := true;
    htp.p('<!-- Debug: JSON structure is valid -->');
exception
    when others then
        vJsonValid := false;
        htp.p('<!-- Debug: JSON structure is invalid, trying alternative parsing -->');
end;

if vJsonValid then
    -- Extract header and details from the JSON structure
    for dx in (
        select * from json_table(vData,
                '$.header'
                columns
                     ttype varchar2(250) path '$.ttype',
                     tdate varchar2(30) path '$.tdate',
                     tnumb varchar2(30) path '$.tnumb',
                     tstat varchar2(30) path '$.tstat',
                     suppc varchar2(100) path '$.suppc',
                     suppn varchar2(100) path '$.suppn',
                     addr1 varchar2(100) path '$.addr1',
                     addr2 varchar2(100) path '$.addr2',
                     cprsn varchar2(100) path '$.cprsn',
                     mobil varchar2(20) path '$.mobil',
                     email varchar2(100) path '$.email',
                     refce varchar2(100) path '$.refce',
                     discp number path '$.discp',
                     disca number path '$.disca',
                     taxxp number path '$.taxxp',
                     taxxa number path '$.taxxa',
                     totla number path '$.totla',
                     lpoam number path '$.lpoam',
                     rmark varchar2(500) path '$.rmark'
             )
        )
    loop
        vHeaderCount := vHeaderCount + 1;
        
        -- Store transaction type and date for use in details
        vTranType := dx.ttype;
        if dx.tdate is not null then
            vTranDate := to_date(dx.tdate, 'DD-MON-YYYY');
        end if;
        
        -- Debug: Log header data
        htp.p('<!-- Debug: Header found - Supplier: ' || dx.suppn || ', Date: ' || dx.tdate || ', Type: ' || dx.ttype || ' -->');
        
        if nvl(:P19_ID_NUMBER,'0') = '0' then
            insert into FF_MMLPOHDR (
        	   COMP_CODE,TRAN_TYPE,TRAN_DATE,TRAN_NUMB,SUPL_CODE,SUPL_NAME,SUPL_ADD1,SUPL_ADD2,SUPL_ADD3,
        			CONT_NAME,MOBL_NUMB,TELN_NUMB,MAIL_ADDR,REFN_NUMB,REFN_DATE,TRAN_REMK,TOTL_AMNT,
               DISC_PRCT,DISC_AMNT,TAXX_PRCT,TAXX_AMNT,LPOO_AMNT,PRNT_FLAG,STAT_CODE,CRTE_USER,CRTE_DATE) values
        	   ('1000', dx.ttype, to_date(dx.tdate, 'DD-MON-YYYY'), vDocumentNo, dx.suppc, dx.suppn, dx.addr1, dx.addr2, '',
                    dx.cprsn, dx.mobil, '', dx.email, dx.refce, '', dx.rmark, dx.totla,
                dx.discp, dx.disca, dx.taxxp, dx.taxxa, dx.lpoam, 'Y', 'A', :APP_USER, sysdate )
            returning id_number into vID;
            
            -- Debug: Log header insert
            htp.p('<!-- Debug: Header inserted with ID: ' || vID || ' -->');
        end if;
    end loop;

    -- Debug: Log header count
    htp.p('<!-- Debug: Header records processed: ' || vHeaderCount || ' -->');

    if vID is not null then
        for dy in (
        select * from json_table(vData,
                '$.tranDetails[*]'
                columns
                sr number path '$.sr',
                products varchar2(250) path '$.products',
                sizes varchar2(50) path '$.sizes',
                colors varchar2(50) path '$.colors',
                prices number path '$.prices',
                quantity number path '$.quantity',
                discount number path '$.discount',
                subtotal number path '$.subtotal',
                vat number path '$.vat',
                total number path '$.total',
                is_deleted varchar2(1) path '$.is_deleted',
                is_New varchar2(1) path '$.is_New',
                id number path '$.id')
            )
            loop
                vDetailCount := vDetailCount + 1;
                
                -- Debug: Log detail data
                htp.p('<!-- Debug: Detail found - Product: ' || dy.products || ', Qty: ' || dy.quantity || ', Deleted: ' || dy.is_deleted || ' -->');
                
                -- Only process non-deleted records
                if dy.is_deleted = 'N' then
                    vSerl := vSerl + 1;
                    insert into FF_MMLPODTL (
                        ID_NUMBER,COMP_CODE,TRAN_TYPE,TRAN_DATE,TRAN_NUMB,TRAN_SRNO,
                		ITEM_CODE,ITEM_DESC,ITEM_UNIT,ITEM_QNTY,ITEM_RATE,
                	ITEM_DISC,ITEM_AMNT,RECV_QNTY,CRTE_USER,CRTE_DATE, ITEM_SIZE) values
                	('','1000',vTranType,vTranDate,vDocumentNo,vSerl,
                    dy.products, dy.products, 'PCS', dy.quantity, dy.prices,
                    dy.discount, dy.total, 0, :APP_USER, sysdate, dy.sizes);
                    
                    -- Debug: Log detail insert
                    htp.p('<!-- Debug: Detail inserted - Sr: ' || vSerl || ', Product: ' || dy.products || ' -->');
                end if;
            end loop;
    end if;
else
    -- Alternative parsing for different JSON structure
    htp.p('<!-- Debug: Using alternative JSON parsing -->');
    
    -- Try to parse as array structure
    for dx in (
        select * from json_table(vData,
                '$[0]'
                columns
                     ttype varchar2(250) path '$.ttype',
                     tdate varchar2(30) path '$.tdate',
                     tnumb varchar2(30) path '$.tnumb',
                     tstat varchar2(30) path '$.tstat',
                     suppc varchar2(100) path '$.suppc',
                     suppn varchar2(100) path '$.suppn',
                     addr1 varchar2(100) path '$.addr1',
                     addr2 varchar2(100) path '$.addr2',
                     cprsn varchar2(100) path '$.cprsn',
                     mobil varchar2(20) path '$.mobil',
                     email varchar2(100) path '$.email',
                     refce varchar2(100) path '$.refce',
                     discp number path '$.discp',
                     disca number path '$.disca',
                     taxxp number path '$.taxxp',
                     taxxa number path '$.taxxa',
                     totla number path '$.totla',
                     lpoam number path '$.lpoam',
                     rmark varchar2(500) path '$.rmark'
             )
        )
    loop
        vHeaderCount := vHeaderCount + 1;
        htp.p('<!-- Debug: Alternative Header found - Supplier: ' || dx.suppn || ' -->');
        
        if nvl(:P19_ID_NUMBER,'0') = '0' then
            insert into FF_MMLPOHDR (
        	   COMP_CODE,TRAN_TYPE,TRAN_DATE,TRAN_NUMB,SUPL_CODE,SUPL_NAME,SUPL_ADD1,SUPL_ADD2,SUPL_ADD3,
        			CONT_NAME,MOBL_NUMB,TELN_NUMB,MAIL_ADDR,REFN_NUMB,REFN_DATE,TRAN_REMK,TOTL_AMNT,
               DISC_PRCT,DISC_AMNT,TAXX_PRCT,TAXX_AMNT,LPOO_AMNT,PRNT_FLAG,STAT_CODE,CRTE_USER,CRTE_DATE) values
        	   ('1000', dx.ttype, to_date(dx.tdate, 'DD-MON-YYYY'), vDocumentNo, dx.suppc, dx.suppn, dx.addr1, dx.addr2, '',
                    dx.cprsn, dx.mobil, '', dx.email, dx.refce, '', dx.rmark, dx.totla,
                dx.discp, dx.disca, dx.taxxp, dx.taxxa, dx.lpoam, 'Y', 'A', :APP_USER, sysdate )
            returning id_number into vID;
        end if;
    end loop;

    if vID is not null then
        for dy in (
        select * from json_table(vData,
                '$[1][*]'
                columns
                sr number path '$.sr',
                products varchar2(250) path '$.products',
                sizes varchar2(50) path '$.sizes',
                colors varchar2(50) path '$.colors',
                prices number path '$.prices',
                quantity number path '$.quantity',
                discount number path '$.discount',
                subtotal number path '$.subtotal',
                vat number path '$.vat',
                total number path '$.total',
                is_deleted varchar2(1) path '$.is_deleted',
                is_New varchar2(1) path '$.is_New',
                id number path '$.id')
            )
            loop
                vDetailCount := vDetailCount + 1;
                htp.p('<!-- Debug: Alternative Detail found - Product: ' || dy.products || ' -->');
                
                if dy.is_deleted = 'N' then
                    vSerl := vSerl + 1;
                    insert into FF_MMLPODTL (
                        ID_NUMBER,COMP_CODE,TRAN_TYPE,TRAN_DATE,TRAN_NUMB,TRAN_SRNO,
                		ITEM_CODE,ITEM_DESC,ITEM_UNIT,ITEM_QNTY,ITEM_RATE,
                	ITEM_DISC,ITEM_AMNT,RECV_QNTY,CRTE_USER,CRTE_DATE, ITEM_SIZE) values
                	('','1000',vTranType,vTranDate,vDocumentNo,vSerl,
                    dy.products, dy.products, 'PCS', dy.quantity, dy.prices,
                    dy.discount, dy.total, 0, :APP_USER, sysdate, dy.sizes);
                end if;
            end loop;
    end if;
    
    -- If still no data found, try parsing as direct object
    if vHeaderCount = 0 then
        htp.p('<!-- Debug: Trying direct object parsing -->');
        
        for dx in (
            select * from json_table(vData,
                    '$'
                    columns
                         ttype varchar2(250) path '$.ttype',
                         tdate varchar2(30) path '$.tdate',
                         tnumb varchar2(30) path '$.tnumb',
                         tstat varchar2(30) path '$.tstat',
                         suppc varchar2(100) path '$.suppc',
                         suppn varchar2(100) path '$.suppn',
                         addr1 varchar2(100) path '$.addr1',
                         addr2 varchar2(100) path '$.addr2',
                         cprsn varchar2(100) path '$.cprsn',
                         mobil varchar2(20) path '$.mobil',
                         email varchar2(100) path '$.email',
                         refce varchar2(100) path '$.refce',
                         discp number path '$.discp',
                         disca number path '$.disca',
                         taxxp number path '$.taxxp',
                         taxxa number path '$.taxxa',
                         totla number path '$.totla',
                         lpoam number path '$.lpoam',
                         rmark varchar2(500) path '$.rmark'
                 )
            )
        loop
            vHeaderCount := vHeaderCount + 1;
            htp.p('<!-- Debug: Direct Header found - Supplier: ' || dx.suppn || ' -->');
            
            if nvl(:P19_ID_NUMBER,'0') = '0' then
                insert into FF_MMLPOHDR (
            	   COMP_CODE,TRAN_TYPE,TRAN_DATE,TRAN_NUMB,SUPL_CODE,SUPL_NAME,SUPL_ADD1,SUPL_ADD2,SUPL_ADD3,
            			CONT_NAME,MOBL_NUMB,TELN_NUMB,MAIL_ADDR,REFN_NUMB,REFN_DATE,TRAN_REMK,TOTL_AMNT,
                   DISC_PRCT,DISC_AMNT,TAXX_PRCT,TAXX_AMNT,LPOO_AMNT,PRNT_FLAG,STAT_CODE,CRTE_USER,CRTE_DATE) values
            	   ('1000', dx.ttype, to_date(dx.tdate, 'DD-MON-YYYY'), vDocumentNo, dx.suppc, dx.suppn, dx.addr1, dx.addr2, '',
                        dx.cprsn, dx.mobil, '', dx.email, dx.refce, '', dx.rmark, dx.totla,
                    dx.discp, dx.disca, dx.taxxp, dx.taxxa, dx.lpoam, 'Y', 'A', :APP_USER, sysdate )
                returning id_number into vID;
            end if;
        end loop;
    end if;
end if;

-- Debug: Log final counts
htp.p('<!-- Debug: Total details processed: ' || vDetailCount || ', Details inserted: ' || vSerl || ' -->');

htp.p('{"Status" : "1", "dNo": "'|| vDocumentNo ||'", "ID" : "'|| vID ||'", "Msg": "Transaction saved successfully", "HeaderCount": "'|| vHeaderCount ||'", "DetailCount": "'|| vDetailCount ||'", "InsertedCount": "'|| vSerl ||'"}');
exception 
    when others then
    htp.p('{"Status" : "2", "msg" : "'|| SQLERRM ||'", "HeaderCount": "'|| vHeaderCount ||'", "DetailCount": "'|| vDetailCount ||'", "InsertedCount": "'|| vSerl ||'"}');
end;



