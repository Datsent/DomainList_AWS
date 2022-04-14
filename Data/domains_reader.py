
from Data import data, Collector

def main():
    try:
        domains_list = data.load_db_into_list()
        print(domains_list)
    except:
        data.create_db()
        domains_list = data.load_db_into_list()
        print(domains_list)
    if domains_list != []:
        new_list = Collector.get_param(domains_list)
        data.create_db()
        data.add_list_to_db(new_list)
    data.print_db()


if __name__ == '__main__':
    main()
    #data.add_new_domain('booking.com')
