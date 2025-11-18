import sqlite3 as sql
import tkinter.messagebox


class Setup:
    __provider_table = """CREATE TABLE IF NOT EXISTS provider (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT,
    dir TEXT,
    active BOOLEAN
    )
    """
    def __init__(self):
        self.conn = sql.connect("setup/setup.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(Setup.__provider_table)

    def __del__(self):
        self.conn.close()

    def new_provider(self, keyword, direction):
        self.cursor.execute("""UPDATE provider SET active = FALSE""")
        self.cursor.execute("""INSERT INTO provider(keyword,dir,active) VALUES (?,?,?)""", (keyword,direction,True))
        self.conn.commit()

    def all_providers(self):
        self.cursor.execute("SELECT keyword, dir, active, id FROM provider")
        return self.cursor.fetchall()

    def active_provider(self):
        self.cursor.execute("SELECT keyword, dir, active FROM provider WHERE active = TRUE")
        return self.cursor.fetchall()

    def active_provider_id(self):
        self.cursor.execute("SELECT id FROM provider WHERE active = TRUE")
        return self.cursor.fetchall()[0][0]

    def activate_provider(self, provider_id):
        self.cursor.execute("""UPDATE provider SET active = FALSE""")
        self.cursor.execute("UPDATE provider SET active = TRUE WHERE id = ?", (provider_id,))
        self.conn.commit()

    def provider_next_id(self):
        self.cursor.execute("SELECT MAX(id) FROM provider")
        current_id = self.cursor.fetchall()[0][0]
        if type(current_id) is int:
            return current_id + 1
        else:
            return 1

    def delete_provider(self, provider_id):
        self.cursor.execute("""DELETE FROM provider WHERE id = ?""", (provider_id,))
        self.conn.commit()



class Db:
    _DB_VERSION = (0,1,0,"a1")
    __customer_table = """CREATE TABLE IF NOT EXISTS customer (
    id INTEGER PRIMARY KEY,
    firstName TEXT,
    lastName TEXT,
    gender INTEGER,
    institution TEXT,
    street TEXT,
    number TEXT,
    postalCode TEXT,
    place TEXT
    );
    """

    __service_complex_table = """CREATE TABLE IF NOT EXISTS serviceComplex (
    id INTEGER PRIMARY KEY,
    customerId INTEGER,
    FOREIGN KEY (customerId) REFERENCES customer(id)
    );
    """

    __service_table = """CREATE TABLE IF NOT EXISTS service (
    id INTEGER PRIMARY KEY,
    serviceComplexId INTEGER,
    description TEXT,
    price REAL,
    additionalPrice REAL,
    day INTEGER,
    month INTEGER,
    year INTEGER,
    FOREIGN KEY (serviceComplexId) REFERENCES serviceComplex(id)
    );
    """

    __bill_table = """CREATE TABLE IF NOT EXISTS bill (
    id INTEGER,
    serviceComplexId INTEGER,
    providerId INTEGER,
    day INTEGER,
    month INTEGER,
    year INTEGER,
    keyword TEXT,
    comment TEXT,
    smallBusinessOwner BOOL,
    valid BOOL,
    paid BOOL,
    FOREIGN KEY (serviceComplexId) REFERENCES serviceComplex(id),
    FOREIGN KEY (providerId) REFERENCES provider(id),
    PRIMARY KEY (id, year)
    );
    """

    __provider_table = """CREATE TABLE IF NOT EXISTS provider (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    taxId TEXT,
    firstName TEXT,
    lastName TEXT,
    gender INTEGER,
    street TEXT,
    number TEXT,
    postalCode TEXT,
    place TEXT,
    telephone TEXT,
    email TEXT,
    IBAN TEXT,
    BIC TEXT,
    WEBSITE TEXT,
    ACTIVE BOOL
    );
    """

    __version_info_table = """CREATE TABLE IF NOT EXISTS VERSION_INFO(
    major INTEGER,
    minor INTEGER,
    patch INTEGER,
    additional TEXT
    );
    """

    def __init__(self, direction):
        self.conn = sql.connect(direction)
        self.cursor = self.conn.cursor()

        self.cursor.execute(Db.__customer_table)
        self.cursor.execute(Db.__service_complex_table)
        self.cursor.execute(Db.__service_table)
        self.cursor.execute(Db.__bill_table)
        self.cursor.execute(Db.__provider_table)
        self.cursor.execute(Db.__version_info_table)
        self.update_version()

    def __del__(self):
        self.conn.commit()

    def update_version(self):
        self.cursor.execute("SELECT * FROM VERSION_INFO")
        if not self.cursor.fetchall():
            self.cursor.execute("INSERT INTO VERSION_INFO VALUES (?,?,?,?)", Db._DB_VERSION)
        self.conn.commit()

    def tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return self.cursor.fetchall()

    def version(self):
        self.cursor.execute("SELECT * FROM VERSION_INFO")
        return self.cursor.fetchall()[0]

    def sc_table_query(self):
        """Data for UI service complex table"""
        self.cursor.execute("SELECT serviceComplex.id, customer.lastName, customer.institution from customer, serviceComplex WHERE (serviceComplex.id NOT IN (SELECT serviceComplexId FROM bill) AND customer.id = serviceComplex.CustomerId)")
        res = self.cursor.fetchall()
        res_add = []
        for i in res:
            self.cursor.execute(f"SELECT COUNT(*), SUM(price) + SUM(additionalPrice) FROM service WHERE serviceComplexId = {i[0]}")
            res_add.append(self.cursor.fetchall()[0])
        self.conn.commit()
        ret = []
        for i in range(len(res)):
            ret.append([*res[i], *res_add[i]])
        return ret

    def next_sc_id(self):
        self.cursor.execute("SELECT MAX(id) FROM serviceComplex")
        current_id = self.cursor.fetchall()[0][0]
        return current_id + 1 if type(current_id) is int else 0

    def customer_short(self):
        """List of short names of customers"""
        self.cursor.execute("SELECT lastName, institution FROM customer")
        res = self.cursor.fetchall()
        ret = []
        for ele in res:
            if ele[0] and ele[1]:
                ret.append(ele[1]+":"+ele[0])
            elif ele[0]:
                ret.append(ele[0])
            else:
                ret.append(ele[1])
        return ret

    def n_of_sc(self):
        self.cursor.execute("SELECT COUNT(id) FROM serviceComplex")
        res = self.cursor.fetchall()[0]
        self.conn.commit()
        return res

    def customers_long(self):
        self.cursor.execute("SELECT * FROM customer")
        res = self.cursor.fetchall()
        return res

    def new_sc(self, customer_id):
        self.cursor.execute("SELECT MAX(id) FROM serviceComplex")
        current_id = self.cursor.fetchall()[0][0]
        if type(current_id) is int:
            next_id = current_id + 1
        else:
            next_id = 0
        self.cursor.execute("INSERT INTO serviceComplex VALUES (?,?)", (next_id, customer_id))
        self.conn.commit()

    def new_customer(self, first_name, last_name, gender, institution, street, number, postal_code, place):
        self.cursor.execute("SELECT MAX(id) FROM customer")
        current_id = self.cursor.fetchall()[0][0]
        if type(current_id) is int:
            next_id = current_id + 1
        else:
            next_id = 0
        self.cursor.execute(f"INSERT INTO customer VALUES (?,?,?,?,?,?,?,?,?)",
                           (next_id, first_name, last_name, gender, institution, street, number, postal_code, place))
        self.conn.commit()

    def change_sc(self, sc_id, customer_id):
        self.cursor.execute(f"UPDATE serviceComplex SET customerId = {customer_id} WHERE id = {sc_id}")
        self.conn.commit()

    def delete_sc(self, sc_id):
        self.cursor.execute(f"DELETE FROM serviceComplex WHERE id = {sc_id}")
        self.cursor.execute(f"DELETE FROM service WHERE serviceComplexId = {sc_id}")
        self.conn.commit()

    def services_of_sc(self, sc_id):
        self.cursor.execute(f"SELECT id, description, price, additionalPrice, day, month, year FROM service WHERE serviceComplexId = {sc_id}")
        res = self.cursor.fetchall()
        self.conn.commit()
        return res

    def new_service(self, sc_id, description, price, additional_price, day, month, year):
        self.cursor.execute("SELECT MAX(id) FROM service")
        current_id = self.cursor.fetchall()[0][0]
        if type(current_id) is int:
            next_id = current_id + 1
        else:
            next_id = 0
        self.cursor.execute(f"INSERT INTO service VALUES (?,?,?,?,?,?,?,?)", (next_id, sc_id, description, price, additional_price, day, month, year))
        self.conn.commit()

    def service_info(self, s_id):
        self.cursor.execute(f"SELECT description, price, additionalPrice, day, month, year FROM service WHERE id = {s_id}")
        res = self.cursor.fetchall()
        self.conn.commit()
        return res

    def change_service(self, s_id, description, price, additional_price, day, month, year):
        self.cursor.execute(f"UPDATE service SET description = '{description}', price={price}, additionalPrice={additional_price}, day={day}, month={month}, year={year} WHERE id = {s_id}")
        self.conn.commit()

    def bill_table_query(self):
        self.cursor.execute("SELECT bill.id, bill.year, customer.lastName, customer.institution, bill.keyword from customer, bill, serviceComplex WHERE (bill.serviceComplexId = serviceComplex.id AND customer.id = serviceComplex.customerId AND bill.paid = FALSE)")
        res = self.cursor.fetchall()
        res_add = []
        for i in res:
            self.cursor.execute(f"SELECT SUM(price) + SUM(additionalPrice) FROM service WHERE serviceComplexId = (SELECT serviceComplexId FROM bill WHERE id = {i[0]})")
            res_add.append(self.cursor.fetchall()[0])
        self.conn.commit()
        ret = []
        for i in range(len(res)):
            ret.append([*res[i], *res_add[i]])
        return ret

    def all_bills_table_query(self):
        self.cursor.execute("SELECT bill.id, bill.year, customer.lastName, customer.institution, bill.keyword from customer, bill, serviceComplex WHERE (bill.serviceComplexId = serviceComplex.id AND customer.id = serviceComplex.customerId)")
        res = self.cursor.fetchall()
        res_add = []
        for i in res:
            self.cursor.execute(f"SELECT SUM(price) + SUM(additionalPrice) FROM service WHERE serviceComplexId = (SELECT serviceComplexId FROM bill WHERE id = {i[0]})")
            res_add.append(self.cursor.fetchall()[0])
        self.conn.commit()
        ret = []
        for i in range(len(res)):
            ret.append([*res[i], *res_add[i]])
        return ret

    def new_bill(self, sc_id, provider_id, day, month, year, keyword, comment, sbo, valid, paid):
        self.cursor.execute(f"SELECT COUNT(*) FROM bill WHERE year={year}")
        count = self.cursor.fetchall()[0][0]
        if type(count) is int:
            next_id = count + 1
        else:
            next_id = 0
        self.cursor.execute(f"INSERT INTO bill VALUES (?,?,?,?,?,?,?,?,?,?,?)", (next_id, sc_id, provider_id, day, month, year, keyword, comment, sbo, valid, paid))
        self.conn.commit()

    def provider_info(self):
        self.cursor.execute("SELECT * FROM provider WHERE ACTIVE = TRUE")
        return self.cursor.fetchall()[0]

    def create_bill_data(self, sc_id):
        self.cursor.execute("SELECT * FROM provider WHERE ACTIVE = TRUE")
        provider_info = self.cursor.fetchall()[0]
        self.cursor.execute(f"SELECT customer.firstName, customer.lastName, customer.institution, customer.street, customer.number, customer.postalCode, customer.place FROM customer, ServiceComplex WHERE customer.id = ServiceComplex.customerId AND ServiceComplex.id = {sc_id}")
        customer_info = self.cursor.fetchall()[0]
        self.conn.commit()
        return provider_info, customer_info

    def bill_data(self, bill_id, year):
        self.cursor.execute(f"SELECT * FROM bill WHERE id = {bill_id} AND year = {year}")
        bill_part = self.cursor.fetchall()[0]
        self.cursor.execute(f"SELECT * FROM provider WHERE id = {bill_part[2]}")
        provider_part = self.cursor.fetchall()[0]
        self.cursor.execute(f"SELECT customer.firstName, customer.lastName, customer.institution, customer.street, customer.number, customer.postalCode, customer.place FROM customer, serviceComplex WHERE serviceComplex.id = {bill_part[1]} AND customer.id = serviceComplex.customerId")
        customer_part = self.cursor.fetchall()[0]
        self.conn.commit()
        return bill_part, provider_part, customer_part

    def update_bill(self, bill_id, bill_year, valid, paid):
        self.cursor.execute("UPDATE bill SET valid = ?, paid = ? WHERE id = ? AND year = ?", (valid, paid, bill_id, bill_year))
        self.conn.commit()

    def bill_provider_info(self, bill_id, bill_year):
        self.cursor.execute("SELECT * FROM provider WHERE id = (SELECT providerId FROM bill WHERE id = ? and year = ?)", (bill_id, bill_year))
        return self.cursor.fetchall()[0]

    def bill_info(self, bill_id, bill_year):
        self.cursor.execute("SELECT * FROM bill WHERE id = ? and year = ?", (bill_id, bill_year))
        return self.cursor.fetchall()[0]

    def bill_customer_info(self, bill_id, bill_year):
        self.cursor.execute("SELECT * FROM customer WHERE id = (SELECT customerId FROM serviceComplex WHERE id = (SELECT serviceComplexId FROM bill WHERE id = ? and year = ?))", (bill_id, bill_year))
        return self.cursor.fetchall()[0]

    def bill_services_info(self, bill_id, bill_year):
        self.cursor.execute("SELECT * FROM service WHERE serviceComplexId = (SELECT serviceComplexId FROM bill WHERE id = ? and year = ?) ORDER BY year, month, day", (bill_id, bill_year))
        res = self.cursor.fetchall()
        if res:
            return res
        else:
            return ()

    def delete_service(self, service_id):
        self.cursor.execute(f"DELETE FROM service WHERE id = {service_id}")
        self.conn.commit()

    def new_provider(self, tax_id, first_name, last_name, gender, street, number, postalcode, place, telephone, email, iban, bic, website):
        self.cursor.execute("UPDATE provider SET active = FALSE")
        self.cursor.execute("INSERT INTO provider(taxId, firstName, lastName, gender, street, number, postalCode, place, telephone, email, iban, bic, website, active) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (tax_id, first_name, last_name, gender, street, number, postalcode, place, telephone, email, iban, bic, website, True))

    def provider_for_setup_info(self):
        self.cursor.execute("SELECT firstName, lastName FROM provider WHERE active = TRUE")
        return self.cursor.fetchall()[0]

    def customers_with_bills(self):
        self.cursor.execute("SELECT id, firstName, lastName, institution FROM customer WHERE id = (SELECT customerId FROM serviceComplex WHERE id = (SELECT serviceComplexId FROM bill))")
        return self.cursor.fetchall()

    def bill_overview(self, customer, bday, bmonth, byear, eday, emonth, eyear):
        if customer == "*":
            self.cursor.execute("SELECT customer.firstName, customer.lastName, customer.institution, bill.id, bill.keyword, bill.day, bill.month, bill.year, service.price, service.additionalPrice, bill.valid, bill.paid FROM customer, bill, serviceComplex, service WHERE bill.serviceComplexId = serviceComplex.id AND serviceComplex.customerId = customer.id AND service.ServiceComplexId = serviceComplex.id ORDER BY customer.id, serviceComplex.id")
            bills = self.cursor.fetchall()
            ret = []
            for ele in bills:
                if int(bday) <= ele[5] <= int(eday) and int(bmonth) <= ele[6] <= int(emonth) and int(byear) <= ele[7] <= int(eyear):
                    ret.append(ele)
            return ret
