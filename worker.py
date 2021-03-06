from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from settings import *


def click(driver, element):
    ActionChains(driver).move_to_element(element).click().perform()


def hover_click(driver, element_hover, element_click):
    ActionChains(
        driver).move_to_element(element_hover).click(element_click).perform()


def element_wait(driver, element, by_attr, wait_seconds=10):
    return WebDriverWait(driver, wait_seconds).until(
        EC.presence_of_element_located((by_attr, element)))


def elements_wait(driver, element, by_attr, wait_seconds=10):
    return WebDriverWait(driver, wait_seconds).until(
        EC.presence_of_all_elements_located((by_attr, element)))


def frame_wait(driver, frame):
    return WebDriverWait(driver, 10).until(
        EC.frame_to_be_available_and_switch_to_it(frame)
    )


def switch_to_frame_usermenu(driver):
    driver.switch_to.default_content()
    frame_wait(driver, 'UserMenu')


def switch_to_frame_innercontentfrm(driver):
    switch_to_frame_usermenu(driver)
    frame_wait(driver, 'innerContentFrm')


def open_browser_connect_to_site(site, assert_text):
    dvr = webdriver.Firefox()
    dvr.get(site)
    assert assert_text == dvr.title
    return dvr


def login_analyst(driver):
    driver.switch_to.frame('main')
    login = driver.find_element_by_id('hlsys_button1')
    login.send_keys(Keys.RETURN)
    username = element_wait(driver, 'textsys_field3', By.ID)
    username.send_keys(app_username)
    password = driver.find_element_by_id('textsys_field2')
    password.send_keys(app_password)
    password.send_keys(Keys.ENTER)


def get_menu_new_items(driver):
    switch_to_frame_usermenu(driver)
    return elements_wait(
        driver, 'igdm_%sMenuLv2MenuItemVertical' % element_prefix, By.CLASS_NAME)


def get_menu_new(driver):
    switch_to_frame_usermenu(driver)
    menu_bar = element_wait(
        driver,
        "//div[@id='UpdatePanel2']//div[@id='WebDataMenu2']" +
        "/ul[@class='igdm_%sMenuLv2MenuGroupHorizontalRoot ']" % element_prefix,
        By.XPATH)
    menu_bar_items = menu_bar.find_elements_by_xpath('//li')
    for i in menu_bar_items:
        if i.text == 'New':
            return i


from datetime import datetime


def populate_field_text(driver, element_id, value=None):

    def enter_value():
        time.sleep(1)
        element = driver.find_element_by_id(element_id)
        element.send_keys(Keys.CONTROL, 'a')
        element.send_keys(value)

    if not value:
        timestamp = str(datetime.now())
        value = 'Test data generated: %s' % timestamp
        enter_value()
        return timestamp
    else:
        enter_value()


def get_popup_window(driver, open_windows_before_popup):
    for w in driver.window_handles:
        if w not in open_windows_before_popup:
            return w


def get_table_items(table, item_id):
    items = []
    for item in table:
        if item_id in item.get_attribute('id'):
            items.append(item)
    return items


def click_clear(driver):
    clear = driver.find_element_by_id('ctl00_ContentPlaceHolder1_hlClear')
    clear.click()


def populate_field_selector(driver, element_id):
    switch_to_frame_innercontentfrm(driver)
    existing_windows = driver.window_handles
    selector = element_wait(driver, element_id, By.ID)
    selector.click()
    pop_up = get_popup_window(driver, existing_windows)
    driver.switch_to.window(pop_up)
    try:
        tree_panel = element_wait(
            driver, 'ctl00_ContentPlaceHolder1_UpdatePanel1', By.ID, 2)
        items = tree_panel.find_elements_by_xpath('//div/ul/li/ul/li/a')
        if not items:
            items = tree_panel.find_elements_by_xpath('//div/ul/li/ul/li/div/a')
        selection = items[random.randrange(0, len(items))]
        selection.click()
        # TODO: Make this select child nodes
    except:
        pass
    try:
        table = elements_wait(driver, '//tr/td/a', By.XPATH)
        item_id = 'ctl00_ContentPlaceHolder1_dg_it0'
        items = get_table_items(table, item_id)
        selection = items[random.randrange(0, len(items))]
        selection.click()
    except:
        pass
    try:
        table = elements_wait(driver, '//tr/td/a', By.XPATH)
        item_id = 'ctl00_ContentPlaceHolder1_dg_it1'
        items = get_table_items(table, item_id)
        selection = items[random.randrange(0, len(items))]
        selection.click()
    except:
        pass
    try:
        driver.switch_to.alert.accept()
    except:
        pass
    driver.switch_to.window(driver.window_handles[0])


import time


def populate_field_dropdown(driver, element_id, dropdown_start_position=0):
    switch_to_frame_innercontentfrm(driver)
    dropdown = element_wait(driver, element_id, By.ID)
    button = dropdown.find_element_by_class_name(
        'igdd_%sDropDownButton ' % element_prefix)
    button.click()
    time.sleep(1)
    list_items = dropdown.find_elements_by_class_name(
        'igdd_%sListItem ' % element_prefix)
    if list_items:
        random_list_item_position = random.randrange(
            dropdown_start_position, len(list_items))
        selection = list_items[random_list_item_position]
        selection.click()
        return True
    else:
        return False


def populate_multiple_type_fields(driver, type_fields):
    print 'Multiple type fields detected.'
    list_length = len(type_fields)
    if list_length > 1:
        for i in range(list_length):
            print 'Populating field:', type_fields[i][0]['app_field']
            time.sleep(1)
            dropdown_field_id = 'ctl00_ContentPlaceHolder1_ddsys_requesttype_id%i' % (i+1)
            if not populate_field_dropdown(driver, dropdown_field_id, 1):
                break


def populate_field_type(driver, type_fields):
    if len(type_fields) > 1:
        populate_multiple_type_fields(driver, type_fields)
    else:
        print 'Populating field:', type_fields[0][0]['app_field']
        populate_field_selector(driver, type_fields[0][5]['element_id'])


def get_html_tab_list(driver):
    try:
        switch_to_frame_innercontentfrm(driver)
        tabs = driver.find_element_by_id('ctl00_ContentPlaceHolder1_tabMain')
        tablist = tabs.find_elements_by_class_name('igtab_%sTHTab' % element_prefix)
        return tablist
    except:
        pass


def get_dropdown_fields():
    return 'sys_requestpriority', 'sys_urgency', 'sys_impact', 'sys_change_type'


def get_and_check_field_element_id(driver, xml_element):
    switch_to_frame_innercontentfrm(driver)
    app_field = xml_element[0]['app_field']
    xml_tag = xml_element[1]['xml_tag']
    html_editor = xml_element[4]['html_editor']
    if xml_tag:
        if html_editor:
            return 'ctl00_ContentPlaceHolder1_tabMain_html%s_contentIframe' % xml_tag
        else:
            if 'fieldcombo' in xml_tag or app_field in get_dropdown_fields():
                dropdown_field_id = 'ctl00_ContentPlaceHolder1_dd%s' % xml_tag
                return dropdown_field_id
            elif app_field == 'sys_eusername':
                text_field_id = 'ctl00_ContentPlaceHolder1_text%s' % xml_tag
                return text_field_id
            elif app_field == 'sys_siteid':
                selector_id = 'ctl00_ContentPlaceHolder1_hl%sselsite' % xml_tag
                return selector_id
            else:
                try:
                    selector_id = 'ctl00_ContentPlaceHolder1_hl%s' % xml_tag
                    driver.find_element_by_id(selector_id)
                    return selector_id
                except:
                    try:
                        text_field_id = 'ctl00_ContentPlaceHolder1_text%s' % xml_tag
                        driver.find_element_by_id(text_field_id)
                        return text_field_id
                    except:
                        try:
                            text_field_id = 'ctl00_ContentPlaceHolder1_tabMain_text%s' % xml_tag
                            driver.find_element_by_id(text_field_id)
                            return text_field_id
                        except:
                            pass


from data_helper import get_active_end_users


def populate_html_editor(driver, tab_id, frame_id):
    tab = element_wait(driver, tab_id, By.ID)
    tab.click()
    frame_wait(driver, frame_id)
    html_field = driver.switch_to_active_element()
    html_field.send_keys(Keys.CONTROL, 'a')
    timestamp = str(datetime.now())
    html_field.send_keys('Test data generated: %s' % timestamp)
    return timestamp


def populate_phone_field(driver, element_id):
    sep_list = ['-', '.', ' ']
    sep = sep_list[random.randint(0, 2)]
    phone = str(random.randint(201, 990)) + sep + \
            str(random.randint(201, 990)) + sep + \
            str(random.randint(0101, 9999))
    populate_field_text(driver, element_id, phone)


import random


def get_random_item(items):
    i = random.randrange(0, len(items))
    return items[i]


def populate_field(driver, xml_element, field_data_type=type('1')):
    switch_to_frame_innercontentfrm(driver)
    app_field = xml_element[0]['app_field']
    print 'Populating field:', app_field
    html_editor = xml_element[4]['html_editor']
    element_id = xml_element[5]['element_id']
    tab_id = xml_element[6]['tab_id']
    if html_editor:
        return populate_html_editor(driver, tab_id, element_id)
    elif 'phone' in app_field:
        populate_phone_field(driver, element_id)
    elif app_field == 'sys_eusername':
        value = get_random_item(get_active_end_users())[0]
        populate_field_text(driver, element_id, value)
    elif app_field == 'sys_siteid':
        populate_field_selector(driver, element_id)
    elif app_field in get_dropdown_fields():
        populate_field_dropdown(driver, element_id, 1)
    else:
        if element_id:
            if 'ctl00_ContentPlaceHolder1_dd' in element_id:
                populate_field_dropdown(driver, element_id)
            elif 'text' in element_id:
                if field_data_type is int:
                    populate_field_text(driver, element_id, str(random.randint(0, 23)))
                else:
                    return populate_field_text(driver, element_id)
            elif 'ctl00_ContentPlaceHolder1_hl' in element_id:
                populate_field_selector(driver, element_id)


def add_html_tab_ids_to_form_field_dict(driver, fields):
    tab_list = get_html_tab_list(driver)
    for key in fields.keys():
        for field in fields[key]:
            if field[4]['html_editor'] and tab_list:
                for tab in tab_list:
                    switch_to_frame_innercontentfrm(driver)
                    tab.click()
                    tab_id = tab.get_attribute('id')
                    frame_wait(driver, field[5]['element_id'])
                    html_field = driver.switch_to_active_element()
                    try:
                        html_field.send_keys('test')
                        html_field.send_keys(Keys.CONTROL, 'a')
                        html_field.send_keys(Keys.DELETE)
                        field.append({'tab_id': tab_id})
                        tab_list.index(tab)
                        del tab_list[tab_list.index(tab)]
                        break
                    except:
                        pass
            else:
                field.append({'tab_id': None})
    return fields


from data_helper import get_dict_editable_form_fields


def add_element_ids_to_form_field_dict(driver, fields):
    for key in fields.keys():
        request_type_counter = 1
        fields_length = len(fields[key])
        for i in range(fields_length):
            if fields[key][i][0]['app_field'] == 'sys_requesttype_id':
                if fields_length > 1:
                    dropdown_field_id = 'ctl00_ContentPlaceHolder1_ddsys_requesttype_id%i' % request_type_counter
                    fields[key][i].append({'element_id': dropdown_field_id})
                    request_type_counter += 1
                else:
                    selector_field_id = 'ctl00_ContentPlaceHolder1_hl%s' % fields[key][i][1]['xml_tag']
                    fields[key][i].append({'element_id': selector_field_id})
            else:
                element_id = get_and_check_field_element_id(driver, fields[key][i])
                fields[key][i].append({'element_id': element_id})
    return fields


def get_form_fields_dict(driver, form_name):
    editable_fields = get_dict_editable_form_fields(form_name)
    fields_with_ids = add_element_ids_to_form_field_dict(driver, editable_fields)
    fields = add_html_tab_ids_to_form_field_dict(driver, fields_with_ids)
    return fields


def click_save(driver):
    switch_to_frame_innercontentfrm(driver)
    save = element_wait(driver, '//input[contains(@title,"Save")]', By.XPATH)
    save.click()


def delete_element_return_result(fields, delete_field):
    for f in fields:
        if f == delete_field:
            del f
    return fields


def check_field_validation_prompt(driver):
    time.sleep(2)
    try:
        field_validation_prompt = element_wait(
            driver, 'ctl00_ContentPlaceHolder1_dialogMsg_tmpl_lbMsg', By.ID, 2)
        if field_validation_prompt.text:
            print 'Detected required field prompt:', field_validation_prompt.text
            return field_validation_prompt
    except:
        pass
    return False


def get_field_data_type(driver):
    required_field_prompt = element_wait(
        driver, 'ctl00_ContentPlaceHolder1_dialogMsg_tmpl_lbMsg', By.ID, 2)
    if 'numeric' in required_field_prompt.text:
        return type(1)
    else:
        return type('1')


def get_field_caption(driver):
    field_validation_prompt = element_wait(
        driver, 'ctl00_ContentPlaceHolder1_dialogMsg_tmpl_lbMsg', By.ID, 2)
    field_validation_msg = field_validation_prompt.text
    if 'You must enter a value in the box' in field_validation_msg:
        field_caption = ''
    elif 'You must enter a numeric ' in field_validation_msg:
        field_caption = field_validation_msg.replace(
            'You must enter a numeric value in the ', '').replace(' box.', '')
    else:
        field_caption = field_validation_msg.replace(
            'You must enter a value in the ', '').replace(' box.', '')
    return field_caption


def get_field_count(last_field, current_field, counter):
    if current_field == last_field:
        return counter + 1
    else:
        return 1


from data_helper import get_type_fields, get_field_for_caption


def submit_form(driver, fields):
    click_save(driver)
    field_counter = 1
    last_field = str()
    while field_counter < 3 and check_field_validation_prompt(driver):
        field_caption = get_field_caption(driver)
        field_data_type = get_field_data_type(driver)
        field_counter = get_field_count(last_field, field_caption, field_counter)
        last_field = field_caption
        close_prompt = driver.find_element_by_id('x:237751999.4:mkr:Close')
        close_prompt.click()
        element = get_field_for_caption(fields, field_caption)
        populate_field(driver, element, field_data_type)
        click_save(driver)


from data_helper import build_dict_appterms_reverse


def check_item_against_appterms(item_text):
    try:
        return build_dict_appterms_reverse()[item_text]
    except KeyError:
        return item_text


def open_menu_new_item(driver, item):
    menu_new = get_menu_new(driver)
    item_text = item.find_element_by_tag_name('span').get_attribute('innerHTML')
    print 'Opening %s' % item_text
    hover_click(driver, menu_new, item)
    return item_text


from data_helper import get_request_classes


def get_menu_item(driver, target_item):
    menu_new_items = get_menu_new_items(driver)
    return_items = []
    for item in menu_new_items:
        switch_to_frame_usermenu(driver)
        item_text = item.find_element_by_tag_name('span').get_attribute('innerHTML')
        if target_item == 'all':
            return menu_new_items
        elif target_item == 'all requests':
            if item_text in get_request_classes():
                return_items.append(item)
        elif item_text == target_item or item_text == check_item_against_appterms(target_item):
            return [item]
        elif item == menu_new_items[len(menu_new_items) - 1]:
            raise Exception('No matches in menu new items for: %s' % target_item)
    return return_items


from data_helper import get_record_with_timestamp, delete_timestamp


def create_default_menu_new_item(driver, target_item):
    item_list = get_menu_item(driver, target_item)
    for item in item_list:
        item_text = open_menu_new_item(driver, item)
        fields = get_form_fields_dict(driver, check_item_against_appterms(item_text))
        type_fields = get_type_fields(fields)
        if type_fields:
            populate_field_type(driver, type_fields)
        desc_fields = ('sys_problemdesc',
                       'sys_problem_description',
                       'sys_change_description',
                       'actiondesc',
                       )
        for field in fields:
            if field in desc_fields:
                timestamp = populate_field(driver, fields[field][0])
        submit_form(driver, fields)
        print 'Saved item:', item_text
        print 'Checking database for new record...'
        time.sleep(1)
        new_record = get_record_with_timestamp(item_text, timestamp)
        if new_record:
            print 'Success! New record confirmed: %s %s\n' % (item_text, new_record[0])
            delete_timestamp(item_text, timestamp)
        else:
            raise Exception('New record not found in database.')


def create_empty_menu_new_item(driver, target_item):
    item_list = get_menu_item(driver, target_item)
    for item in item_list:
        item_text = open_menu_new_item(driver, item)
        click_save(driver)
        print 'Saved item:', item_text


def create_new_change_click_cab_group(driver):
    item = get_menu_item(driver, 'Change')[0]
    open_menu_new_item(driver, item)
    switch_to_frame_innercontentfrm(driver)
    cab_group = element_wait(driver, '//input[contains(@title,"Cab Group")]', By.XPATH)
    cab_group.click()
    print 'Clicked in to CAB Group\n'


def open_admin(driver):
    driver.switch_to.default_content()
    frame_wait(driver, 'UserMenu')
    admin = element_wait(driver, 'x:1557894678.4:adr:1', By.ID)
    click(driver, admin)


def select_dropdown_item_by_link_text(driver, button_id, list_id, link_text):
    dropdown_button = element_wait(driver, button_id, By.ID)
    dropdown_button.click()
    time.sleep(1)
    list_items_container = driver.find_element_by_id(list_id)
    item = list_items_container.find_element_by_link_text(link_text)
    item.click()
    time.sleep(1)


from data_helper import get_request_status


def create_new_request_status(driver, **kwargs):

    def generate_name():
        with open('test_data/adjective') as f:
            name = get_random_item(f.readlines())[:-1]
            return name[0].upper() + name[1:]

    def get_random_color():
        with open('test_data/colors') as f:
            return get_random_item(f.readlines())[:-1]

    open_admin(driver)
    frame_wait(driver, 'innerContentFrm')
    request_statuses = element_wait(driver, 'Request Statuses', By.LINK_TEXT)
    click(driver, request_statuses)
    add_new = element_wait(driver, 'ctl00_ContentPlaceHolder1_btnAddPre', By.ID)
    click(driver, add_new)
    if not 'automatic_closure' in kwargs:
        if not 'status_name' in kwargs:
            kwargs['status_name'] = generate_name()
        if not 'on_status' in kwargs:
            kwargs['on_status'] = get_random_item(('Continue',
                                                   'Suspend',
                                                   'Closed',))
        kwargs['solution'] = str(datetime.now())
    elif 'automatic_closure' in kwargs:
        if not 'on_status' in kwargs:
            kwargs['on_status'] = get_random_item(('Continue', 'Suspend'))
        if not 'close_when' in kwargs:
            kwargs['close_when'] = get_random_item(('Open Date',
                                                    'Current Status'))
        if not 'exceeds_these_days' in kwargs:
            kwargs['exceeds_these_days'] = str(random.randint(0, 999))
        if not 'status_name' in kwargs:
            name = (generate_name(), ' - ',
                    kwargs['on_status'], ', ',
                    kwargs['close_when'], ', ',
                    kwargs['exceeds_these_days'])
            kwargs['status_name'] = ''.join(name)
        select_dropdown_item_by_link_text(
            driver, 'x:972688325.3:mkr:Button', 'x:972688325.7:mkr:List:nw:1',
            kwargs['close_when'])
        exceeds_days_id = 'ctl00_ContentPlaceHolder1_dialogInfo_tmpl_txtNoOfDays'
        driver.find_element_by_id(exceeds_days_id).send_keys(kwargs['exceeds_these_days'])
    if not 'allow_end_user' in kwargs:
        kwargs['allow_end_user'] = get_random_item(('Yes', 'No'))
    if not 'force_status_color' in kwargs:
        kwargs['force_status_color'] = get_random_item(('Yes', 'No'))
    if not 'status_color' in kwargs:
        kwargs['status_color'] = get_random_color()
    if not 'solution' in kwargs:
        kwargs['solution'] = get_random_item(
            ('',
             'This is an automatically generated solution for Request Status: %s' %
             (kwargs['status_name'])))
    status_name = element_wait(
        driver, 'ctl00_ContentPlaceHolder1_dialogInfo_tmpl_textStatus', By.ID)
    status_name.send_keys(kwargs['status_name'])
    select_dropdown_item_by_link_text(
        driver, 'x:1681566268.3:mkr:Button',
        'x:1681566268.7:mkr:List:nw:1', kwargs['on_status'])
    select_dropdown_item_by_link_text(
        driver, 'x:1774636839.3:mkr:Button',
        'x:1774636839.7:mkr:List:nw:1', kwargs['allow_end_user'])
    select_dropdown_item_by_link_text(
        driver, 'x:157696233.3:mkr:Button',
        'x:157696233.7:mkr:List:nw:1', kwargs['force_status_color'])
    status_color_id = 'ctl00_ContentPlaceHolder1_dialogInfo_tmpl_textFieldColor'
    status_color = driver.find_element_by_id(status_color_id)
    status_color.clear()
    status_color.send_keys(kwargs['status_color'])
    solution_id = 'ctl00_ContentPlaceHolder1_dialogInfo_tmpl_txtSolution'
    driver.find_element_by_id(solution_id).send_keys(kwargs['solution'])
    save_id = 'ctl00_ContentPlaceHolder1_dialogInfo_tmpl_btnUpdate'
    save = element_wait(driver, save_id, By.ID)
    click(driver, save)
    print 'Saved Request Status:', kwargs['status_name']
    time.sleep(1)
    if get_request_status(**kwargs):
        print 'Success! New record confirmed: %s\n' % kwargs['status_name']
    else:
        raise Exception('New record not found in database.')


import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--all_requests', help='Create all requests', action='store_true')
    parser.add_argument('-A', '--all_items', help='Create all items', action='store_true')
    parser.add_argument('-p', '--problem', help='Create problem', action='store_true')
    parser.add_argument('-c', '--change', help='Create change', action='store_true')
    args = parser.parse_args()
    if args.all_requests:
        driver = open_browser_connect_to_site(target_url, assert_text)
        login_analyst(driver)
        create_default_menu_new_item(driver, 'all requests')
    elif args.all_items:
        driver = open_browser_connect_to_site(target_url, assert_text)
        login_analyst(driver)
        create_default_menu_new_item(driver, 'all')
    elif args.problem:
        driver = open_browser_connect_to_site(target_url, assert_text)
        login_analyst(driver)
        create_default_menu_new_item(driver, 'problem')
    elif args.change:
        driver = open_browser_connect_to_site(target_url, assert_text)
        login_analyst(driver)
        create_default_menu_new_item(driver, 'change')
    driver.quit()


if __name__ == '__main__':
    main()