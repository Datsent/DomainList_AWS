import ssl, requests, datetime, socket, urllib.request
from lxml import html

def notification(date):
    '''
    Function check if need send notification. If remaining 60 days to Expires On day.
    :param date: str.
    :return: return "Yes" or "No" to do notification.
    '''
    if date != 'N/A':
        date_date = datetime.datetime.strptime(date, '%d-%m-%Y')
        print(date_date)
        now = datetime.datetime.now()
        diff = date_date - now
        print(diff.days)
        return diff.days
    else:
        return 'N/A'


def ssl_expiry_datetime(hostname):
    '''
    Function to get ssl expiry date.
    :param hostname: str of domain name
    :return: str of date of expiry on day
    '''
    ssl_dateformat = r'%b %d %H:%M:%S %Y %Z'

    context = ssl.create_default_context()
    context.check_hostname = False

    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
    )
    # 5 second timeout
    conn.settimeout(5.0)
    try:
        conn.connect((hostname, 443))
        ssl_info = conn.getpeercert()
        exp_date = datetime.datetime.strptime(ssl_info['notAfter'], ssl_dateformat)
        return exp_date.strftime('%d-%m-%Y')
    except BaseException:
        return 'N/A'

def validity_date(domain):
    '''
    Function to get domain registry expiry date.
    :param domain: str of domain name
    :return: str of date of expiry on day
    '''
    my_request = urllib.request.urlopen("https://who.is/whois/%s" % domain)
    my_HTML = my_request.read().decode()
    list_HTML = list(my_HTML.split("\n"))
    data_str = ''
    for k, line in enumerate(list_HTML):
        if line.find('validity') != -1:
            line_num = k
            date_str = list_HTML[line_num].strip('validity:     ')
            if date_str != 'N/A':
                date_object = datetime.datetime.strptime(date_str, '%d-%m-%Y').date()
                return str(date_object.strftime('%d-%m-%Y'))
            else:
                return date_str
    if not data_str:
        page = requests.get(f"https://who.is/whois/{domain}")
        tree = html.fromstring(page.content)
        date_str = ', '.join(tree.xpath('/html/body/div[3]/div[2]/div[5]/div[1]/div[5]/div/div[1]/div[2]/text()'))
        date_object = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        return str(date_object.strftime('%d-%m-%Y'))

def get_param(list_db):
    '''
    Get all parameters for domains (date of valid domain, expire day of ssl, notification needed)
    :param Lines: List of lines from file
    :return: List of update lines of file
    '''
    today = datetime.date.today()
    new_list = []
    for domain in list_db:

        print(f'Geting Data for: {domain[0]}...')
        tem = list(domain)
        tem[1] = validity_date(tem[0])
        tem[2] = ssl_expiry_datetime(tem[0])
        remain_days = notification(tem[1])
        if remain_days == 'N/A':
            print('No need notification')
        elif remain_days < 60 and domain[2] == '' and domain[2] != 'N/A':
                #send_notificate.send_email(line_list[0], remain_days)
                print('eMail send')
                print(today.strftime("%d/%m/%Y"))
        new_list.append(tem)


        '''remain_days = notification(line_list[3])
        if remain_days == 'N/A':
            line_list[4] = 'N/A'
        elif remain_days < 60 and line_list[4] == '' and line_list[4] != 'N/A':
                send_notificate.send_email(line_list[0], remain_days)
                print('eMail send')
                line_list[4] = today.strftime("%d-%m-%Y")

        new_list.append(','.join(line_list))'''
    return new_list
