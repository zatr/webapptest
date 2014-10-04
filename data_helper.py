import pyodbc
from settings import db_connect_string


def db_connect():
    try:
        return pyodbc.connect(''.join(db_connect_string))
    except:
        raise Exception('SQL Error: Failed to connect to server: ' +
                        db_connect_string[0] +
                        db_connect_string[1] +
                        db_connect_string[2] +
                        db_connect_string[3] +
                        'PWD=********;' +
                        db_connect_string[5])


import inspect


def whoisparent():
    return inspect.stack()[2][3]


def exec_sql_read(query):
    cursor = db_connect().cursor()
    try:
        cursor.execute(query)
        results = []
        while 1:
            row = cursor.fetchone()
            if not row:
                break
            results.append(row)
        return results
    except:
        print 'SQL Error: Query failed in function: %s' % whoisparent()
    finally:
        cursor.close()


def exec_sql_cud(query):
    cursor = db_connect().cursor()
    try:
        cursor.execute(query)
        cursor.commit()
    except:
        print 'SQL Error: Query failed in function: %s' % whoisparent()
    finally:
        cursor.close()


def get_appterms():
    query_app_terms = ("select sys_setting_caption, sys_setting_value "
                       "from setting where sys_setting_section = '03:Application Terms' "
                       "order by sys_setting_order")
    return exec_sql_read(query_app_terms)


def get_end_users():
    query_end_users = ('select sys_eusername, sys_company_id, sys_eclient_id, sys_forename, '
                       'sys_surname, sys_phone, sys_email, sys_siteid, sys_disabled '
                       'from euser')
    return exec_sql_read(query_end_users)


def get_users():
    query_users = ('select sys_username, sys_forename, sys_surname, sys_email, sys_disabled '
                   'from [user]')
    return exec_sql_read(query_users)


def get_active_end_users():
    end_users = get_end_users()
    for i in end_users:
        if i[8] == 1:
            del i
    return end_users


def get_active_users():
    users = get_users()
    for i in users:
        if i[4] == 1:
            del i
    return users


def move_data_outside_of_tuple(data):
    if data:
        items = []
        for i in data:
            items.append(i[0])
        return items


def get_request_types():
    query_req_types = ('select sys_requesttype_id from requesttype')
    results = exec_sql_read(query_req_types)
    return move_data_outside_of_tuple(results)


def validate_result_count(elements, expected):
    length = len(elements)
    if length != expected:
        if length > expected:
            print 'Results expected: %i' % expected
        if length < expected:
            print 'Results expected: %i' % expected
        return False
    return True


def menu_select_result(resultset):
    print 'Menu triggered for result set'
    while 1:
        print '\nindex\titem'
        for index, result in enumerate(resultset):
            print index, '\t\t', result
        try:
            choice = int(raw_input('\nEnter the desired result from the Index column: '))
            if choice in range(len(resultset)):
                print 'Selected item: ', resultset[choice]
                return resultset[choice]
            else:
                int('x')
        except ValueError:
            print 'Invalid entry. Enter an integer from the Index column.'


def return_or_select_result(resultset):
    if resultset:
        results = move_data_outside_of_tuple(resultset)
        if not validate_result_count(results, 1):
            return menu_select_result(results)
        else:
            return results[0]


def get_request_classes():
    query_req_classes = ('select sys_requestclass_desc from requestclass')
    results = exec_sql_read(query_req_classes)
    return move_data_outside_of_tuple(results)


def get_form_table_name(form_name):
    terms = build_dict_appterms()
    if form_name == 'Problem':
        return 'problem'
    elif form_name == 'Change':
        return 'change'
    elif form_name == terms['action']:
        return 'action'
    elif form_name in get_request_classes():
        return 'request'


def get_xml_form(form_name):
    table = get_form_table_name(form_name)
    query_request_forms = ("SET TEXTSIZE 2147483647 "
                           "select cast(sys_requestclass_xmluserform as text) "
                           "from requestclass "
                           "where sys_requestclass_desc = '%s'") % form_name
    query_other_forms = ("SET TEXTSIZE 2147483647 "
                         "select cast(sys_formprofile_xml as text) "
                         "from formprofile "
                         "where sys_formprofile_id = '%s' ") % form_name
    if table == 'request':
        query = query_request_forms
    else:
        query = query_other_forms
    return return_or_select_result(exec_sql_read(query))


def get_description_column(table):
    if table == 'request':
        return 'sys_problemdesc'
    elif table == 'problem':
        return 'sys_problem_description'
    elif table == 'change':
        return 'sys_change_description'
    elif table == 'action':
        return 'actiondesc'


def get_record_with_timestamp(form_name, timestamp):
    table = get_form_table_name(form_name)
    desc_column = get_description_column(table)
    query = "select sys_%s_id from %s where %s like '%%%s%%'" % (table, table, desc_column, timestamp)
    results = exec_sql_read(query)
    return move_data_outside_of_tuple(results)


def delete_timestamp(form_name, timestamp):
    table = get_form_table_name(form_name)
    desc_column = get_description_column(table)
    query = "update %s set %s = 'test' where %s like '%%%s%%'" % (table, desc_column, desc_column, timestamp)
    exec_sql_cud(query)


def convert_string_true_false(string):
    if string == 'true':
        return True
    if string == 'false':
        return False


from xml.etree.ElementTree import fromstring
from collections import defaultdict


def build_dict_form_fields(form_name):
    xml_form = get_xml_form(form_name)
    if xml_form:
        l = list(fromstring(xml_form))
        d = defaultdict(list)
        for element in l:
            d[element.text].append([{'app_field': element.text},
                                    {'xml_tag': element.tag},
                                    {'caption': element.attrib.get('caption')},
                                    {'required_field': convert_string_true_false(element.attrib.get('userreq'))},
                                    {'html_editor': convert_string_true_false(element.attrib.get('htmleditor'))}]
                                   )
        return d
    else:
        raise Exception('No XML form found for form name: %s' % form_name)


def get_dict_editable_form_fields(form_name):
    fields = build_dict_form_fields(form_name)
    uneditable_field_strings = ('label', 'readonly', 'image', 'tab', 'hyperlink', 'button')
    for key in fields.keys():
        for i in range(len(fields[key])):
            if any(u in fields[key][i][1]['xml_tag'] for u in uneditable_field_strings):
                del fields[key]
                break
    return fields


def build_dict_appterms():
    l = get_appterms()
    d = defaultdict()
    for k, v in l:
        d[k.replace(' Term', '').lower()] = v
    return d


def build_dict_appterms_reverse():
    d = defaultdict()
    app_terms = build_dict_appterms()
    for key in app_terms.keys():
        d[app_terms[key]] = key
    return d


def get_list_of_required_fields(fields):
    required_fields = []
    for key in fields.keys():
        for field in fields[key]:
            if field[3]['required_field']:
                required_fields.append(field)
    return required_fields


def get_type_fields(fields):
    type_fields = []
    type_field_names = ('sys_requesttype_id', 'sys_actiontype_id', 'sys_change_requesttype')
    for key in fields.keys():
        for field in fields[key]:
            if key in type_field_names:
                type_fields.append(field)
    return type_fields


def get_field_for_caption(fields, field_caption):
    if not field_caption:
        required_fields = get_list_of_required_fields(fields)
        if len(required_fields) == 1:
            return required_fields[0]
        else:
            return menu_select_result(required_fields)
    elements = defaultdict(list)
    for key in fields.keys():
        for field in fields[key]:
            if field[2]['caption'] == field_caption:
                elements[key].append(field)
    sorted_elements = sorted(elements)
    if validate_result_count(elements, 1):
        return elements[sorted_elements[0]][0]
    else:
        if elements:
            element = menu_select_result(elements)[0]
            return element
        else:
            print 'No elements found for caption: "%s"' % field_caption
            return menu_select_result(get_list_of_required_fields(fields))[0]