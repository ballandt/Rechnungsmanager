import datetime
import os
import shutil
import filecmp
import sqlite3
import tkinter
from tkinter import ttk
from tkinter import filedialog
from tkinter.messagebox import askyesno, showinfo, showwarning, showerror

from tkcalendar import DateEntry

import database
from pdfcreator import Bill as PdfBill, BillOverview as PdfBillOverview
from database import Db
from version import _VERSION


class ValidateDbWindow:
    def __init__(self, master, db):
        self.master = master
        self.db = db
        self.direction = db
        self.is_valid_var = True
        self.root = tkinter.Toplevel(self.master.root)
        self.progress_label = tkinter.Label(self.root)
        self.progress_bar = ttk.Progressbar(self.root, length=200, orient="horizontal", mode="determinate")
        self.progress_label.pack()
        self.progress_bar.pack()
        self.progress_label["text"] = "Überprüfe sqlite-Kompatibilität"
        if self.check_sqlite_compatibility():
            self.progress_bar["value"] += 10
        self.progress_label["text"] = "Überprüfe Tabellen"
        if self.check_tables():
            self.progress_bar["value"] += 40
        self.progress_label["text"] = "Überprüfe Version"
        if self.check_version():
            self.progress_bar["value"] += 20
        if self.check_for_identical_db():
            self.progress_bar["value"] += 30


    def check_sqlite_compatibility(self):
        try:
            self.db = database.Db(self.db)
            return True
        except sqlite3.Error:
            showerror("Importfehler", "Bei der Datei handelt es sich nicht um eine kompatible Datenbank.")
            self.is_valid_var = False

    def check_tables(self):
        given_tables = self.db.tables()
        needed_tables = [('customer',), ('serviceComplex',), ('service',), ('bill',), ('provider',), ('VERSION_INFO',)]
        if all(i in given_tables for i in needed_tables):
            return True
        else:
            showerror("Fehlende Datensätze", "Der Datei fehlen Datensätze")
            self.is_valid_var = False
            return False

    def check_version(self):
        version = self.db.version()
        if version[0] == 0:
            if version[1] != Db._DB_VERSION[1]:
                showwarning("Unterschiedliche Versionen", "Die Version der Datenbank entspricht nicht der Version des Programmes. Es kann zu Fehlern kommen.", parent=self.root)
        else:
            if version[0] != Db._DB_VERSION[0]:
                showwarning("Unterschiedliche Versionen", "Die Version der Datenbank entspricht nicht der Version des Programmes. Es kann zu Fehlern kommen.", parent=self.root)
        return True

    def check_for_identical_db(self):
        databases = os.listdir(os.getcwd()+"\\databases\\")
        if not all([filecmp.cmp(self.direction, os.getcwd()+"\\databases\\"+ele) for ele in databases]):
            return True
        else:
            showinfo("Datensatz vorhanden", "Dieser Datensatz ist bereits vorhanden.")
            self.is_valid_var = False
            return False

    def is_valid(self):
        self.root.destroy()
        return self.is_valid

    def setup_info(self):
        return " ".join(self.db.provider_for_setup_info())


class DeleteProviderWindow:
    def __init__(self, setup, master):
        self.setup = setup
        self.master = master
        self.root = tkinter.Toplevel(self.master.root)
        tkinter.Label(self.root, text="Dienstleister zum Löschen auswählen:").pack()
        self.providers = [ele[0]+f" ({str(ele[3])})" for ele in self.setup.all_providers()]
        self.provider_box = ttk.Combobox(self.root, values=self.providers, state="readonly")
        self.provider_box.pack()
        tkinter.Button(self.root, text="Dienstleister löschen", command=self.delete).pack()

    def delete(self):
        index = int(self.provider_box.get().split("(")[1][:-1])
        if index == self.setup.active_provider_id():
            showinfo("Info", "Der aktive Dienstleister kann nicht gelöscht werden", parent=self.root)
            return
        proceed = askyesno("Dienstleister löschen", "Möchten Sie den Dienstleister wirklich löschen?", parent=self.root)
        if proceed:
            self.setup.delete_provider(index)
            os.remove(os.getcwd()+"\\databases\\"+str(index)+".rmdb")
            self.master.refresh_provider_menu()
            self.root.destroy()


class NewProviderWindow:
    def __init__(self, setup, master=None):
        self.setup = setup
        self.master = master
        if not self.master:
            self.root = tkinter.Tk()
        else:
            self.root = tkinter.Toplevel(self.master.root)
        tkinter.Label(self.root, text="Dienstleister erstellen").grid(row=0, column=0, columnspan=2)
        tkinter.Label(self.root, text="Steueridentifikationsnummer:").grid(row=1, column=0)
        self.tax_id_entry = tkinter.Entry(self.root)
        self.tax_id_entry.grid(row=1, column=1)
        tkinter.Label(self.root, text="Vorname:").grid(row=2, column=0)
        self.first_name_entry = tkinter.Entry(self.root)
        self.first_name_entry.grid(row=2, column=1)
        tkinter.Label(self.root, text="Nachname:").grid(row=3, column=0)
        self.last_name_entry = tkinter.Entry(self.root)
        self.last_name_entry.grid(row=3, column=1)
        tkinter.Label(self.root, text="Geschlecht:").grid(row=4, column=0)
        self.genders = ["weiblich", "männlich", "divers"]
        self.gender_box = ttk.Combobox(self.root, values=self.genders, state="readonly")
        self.gender_box.grid(row=4, column=1, sticky=tkinter.EW)
        tkinter.Label(self.root, text="Straße:").grid(row=5, column=0)
        self.street_entry = tkinter.Entry(self.root)
        self.street_entry.grid(row=5, column=1)
        tkinter.Label(self.root, text="Nummer:").grid(row=6, column=0)
        self.number_entry = tkinter.Entry(self.root)
        self.number_entry.grid(row=6, column=1)
        tkinter.Label(self.root, text="Postleitzahl:").grid(row=7, column=0)
        self.postalcode_entry = tkinter.Entry(self.root)
        self.postalcode_entry.grid(row=7, column=1)
        tkinter.Label(self.root, text="Ort:").grid(row=8, column=0)
        self.place_entry = tkinter.Entry(self.root)
        self.place_entry.grid(row=8, column=1)
        tkinter.Label(self.root, text="Telefonnummer:").grid(row=9, column=0)
        self.telephone_entry = tkinter.Entry(self.root)
        self.telephone_entry.grid(row=9, column=1)
        tkinter.Label(self.root, text="Email:").grid(row=10, column=0)
        self.email_entry = tkinter.Entry(self.root)
        self.email_entry.grid(row=10, column=1)
        tkinter.Label(self.root, text="IBAN:").grid(row=11, column=0)
        self.iban_entry = tkinter.Entry(self.root)
        self.iban_entry.grid(row=11, column=1)
        tkinter.Label(self.root, text="BIC:").grid(row=12, column=0)
        self.bic_entry = tkinter.Entry(self.root)
        self.bic_entry.grid(row=12, column=1)
        tkinter.Label(self.root, text="Website:").grid(row=13, column=0)
        self.website_entry = tkinter.Entry(self.root)
        self.website_entry.grid(row=13, column=1)
        self.save_button = tkinter.Button(self.root, text="Speichern", command=self.save)
        self.save_button.grid(row=14, column=1)
        self.root.mainloop()

    def save(self):
        tax_id = self.tax_id_entry.get()
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        gender = ["weiblich", "männlich", "divers"].index(self.gender_box.get())
        street = self.street_entry.get()
        number = self.number_entry.get()
        postalcode = self.postalcode_entry.get()
        place = self.place_entry.get()
        telephone = self.telephone_entry.get()
        email = self.email_entry.get()
        iban = self.iban_entry.get()
        bic = self.bic_entry.get()
        website = self.website_entry.get()
        direction = "\\databases\\" + str(self.setup.provider_next_id()) + ".rmdb"
        self.setup.new_provider(" ".join([first_name, last_name]), direction)
        db = Db(os.getcwd() + direction)
        db.new_provider(tax_id, first_name, last_name, gender, street, number, postalcode, place, telephone, email, iban, bic, website)
        self.root.destroy()
        if self.master:
            self.master.refresh_provider_menu()
            self.master.provider_var.set(self.setup.active_provider_id())
            self.master.refresh_database()


class PrintBillOverviewWindow:
    def __init__(self, master):
        self.master = master
        self.root = tkinter.Toplevel(master.root)

        tkinter.Label(self.root, text="Auftraggeber auswählen").grid(row=0, column=0)
        self.customers = self.master.database.customers_with_bills()
        self.customer_short = ["Alle"]
        for ele in self.customers:
            if ele[3] != "":
                self.customer_short.append(ele[3])
                if ele[2] != "":
                    self.customer_short[-1] += ": " + ele[2]
                    if ele[1] != "":
                        self.customer_short[-1] += ", " + ele[1]
            elif ele[2] != "":
                self.customer_short.append(ele[2])
                if ele[1]:
                    self.customer_short[-1] += ", " + ele[1]
        self.customer_box = ttk.Combobox(self.root, values=self.customer_short, state="readonly")
        self.customer_box.grid(row=0, column=1)
        self.customer_box.set("Alle")
        tkinter.Label(self.root, text="Datum Beginn:").grid(row=1, column=0)
        self.begin_entry = DateEntry(self.root, locale='de_DE', date_pattern='dd.mm.yyyy')
        self.begin_entry.grid(row=1, column=1)
        self.begin_entry.set_date("01.01."+str(datetime.datetime.today().year))
        tkinter.Label(self.root, text="Datum Ende:").grid(row=2, column=0)
        self.end_entry = DateEntry(self.root, locale='de_DE', date_pattern='dd.mm.yyyy')
        self.end_entry.grid(row=2, column=1)
        tkinter.Button(self.root, text="Drucken", command=self.save).grid(row=3, column=1)

    def save(self):
        customer = self.customer_box.get()
        if customer == "Alle":
            customer = "*"
        else:
            customer = self.customers[self.customer_short.index(customer)-1]
        begin_date = self.begin_entry.get().split(".")
        end_date = self.end_entry.get().split(".")
        bills = self.master.database.bill_overview(customer, *begin_date, *end_date)
        name = "Rechnungsübersicht.pdf"
        direction = filedialog.asksaveasfilename(initialfile=name, filetypes=[("PDF-Datei", ".pdf")], parent=self.root)
        overview = PdfBillOverview(bills, begin_date, end_date, self.master.database.provider_info(), direction)
        overview.save()
        self.root.destroy()




class ShowBillsWindow:
    def __init__(self, master):
        self.root = tkinter.Toplevel(master.root)
        self.master = master
        self.database = self.master.database

        self.bill_table = ttk.Treeview(self.root)
        self.bill_table["columns"] = ("Rechnungsnummer", "Auftraggeber", "Stichwort", "Preis")
        self.bill_table.column("#0", width=0, stretch=tkinter.NO)
        self.bill_table.column("Rechnungsnummer", anchor="w", width=100)
        self.bill_table.column("Auftraggeber", anchor="w", width=200)
        self.bill_table.column("Stichwort", anchor="w", width=100)
        self.bill_table.column("Preis", anchor="e", width=100)

        self.bill_table.heading("#0", text="", anchor="w")
        self.bill_table.heading("Rechnungsnummer", text="Rechnungsnummer", anchor="w")
        self.bill_table.heading("Auftraggeber", text="Auftraggeber", anchor="w")
        self.bill_table.heading("Stichwort", text="Stichwort", anchor="w")
        self.bill_table.heading("Preis", text="Preis", anchor="e")
        self.bill_table.grid(row=6, column=0, sticky=tkinter.EW)
        self.bill_table.bind("<Double-1>", lambda event: self.edit_bill())
        tkinter.Button(self.root, text="Rechnungsübersicht drucken", command=lambda: PrintBillOverviewWindow(self)).grid(row=7, column=0, sticky=tkinter.EW)

        self.bill_table_fill()

    def bill_table_fill(self):
        bill_table_data = []
        for ele in self.master.database.all_bills_table_query():
            bill_table_data.append([])
            bill_table_data[-1].append(str(ele[1]) + "-" + str(ele[0]))
            if ele[3]:
                bill_table_data[-1].append(ele[3])
            else:
                bill_table_data[-1].append(ele[2])
            bill_table_data[-1].append(ele[4])
            if ele[5] is None:
                bill_table_data[-1].append("0,00 €")
            else:
                bill_table_data[-1].append("{:.2f} €".format(float(ele[5])).replace(".", ","))
        for i in range(len(bill_table_data)):
            if i % 2 == 0:
                self.bill_table.insert(parent='', index=i, values=bill_table_data[i], tags=('evenrow',))
            else:
                self.bill_table.insert(parent='', index=i, values=bill_table_data[i], tags=('oddrow',))

    def edit_bill(self):
        if self.bill_table.item(self.bill_table.focus())["values"]:
            EditBillWindow(self)

    def refresh_bill_table(self):
        self.bill_table.delete(*self.bill_table.get_children())
        self.bill_table_fill()


class CreateBillWindow:
    def __init__(self, sc_id, master):
        self.sc_id = sc_id
        self.master = master
        self.database = self.master.database
        self.root = tkinter.Toplevel(self.master.root)
        self.create_bill_data = list(map(list, self.database.create_bill_data(self.sc_id)))
        for i in range(3):
            if not self.create_bill_data[1][i]:
                self.create_bill_data[1][i] = ""
        tkinter.Label(self.root, text=self.create_bill_data[1][2]).grid(row=0, column=0, sticky=tkinter.W, padx=10)
        tkinter.Label(self.root, text=" ".join(self.create_bill_data[1][:2])).grid(row=1, column=0, sticky=tkinter.W, padx=10)
        self.date_entry = DateEntry(self.root, locale='de_DE', date_pattern='dd.mm.yyyy')
        self.date_entry.grid(row=1, column=1)
        tkinter.Label(self.root, text=" ".join(self.create_bill_data[0][2:4])).grid(row=0, column=2, sticky=tkinter.E, padx=10)
        tkinter.Label(self.root, text=" ".join(self.create_bill_data[1][3:5])).grid(row=1, column=0, sticky=tkinter.W, padx=10)
        tkinter.Label(self.root, text=" ".join(self.create_bill_data[0][5:7])).grid(row=1, column=2, sticky=tkinter.E, padx=10)
        tkinter.Label(self.root, text=" ".join(self.create_bill_data[1][7:9])).grid(row=2, column=0, sticky=tkinter.W, padx=10)
        tkinter.Label(self.root, text=" ".join(self.create_bill_data[0][7:9])).grid(row=2, column=2, sticky=tkinter.E, padx=10)
        tkinter.Label(self.root, text="Tel.:"+self.create_bill_data[0][9]).grid(row=3, column=2, sticky=tkinter.E, padx=10)
        tkinter.Label(self.root, text="E-Mail:" + self.create_bill_data[0][10]).grid(row=4, column=2, sticky=tkinter.E, padx=10)
        tkinter.Label(self.root, text="Betreff:").grid(row=5, column=0, pady=10)
        self.keyword_entry = tkinter.Entry(self.root)
        self.keyword_entry.grid(row=5, column=1, sticky=tkinter.EW, pady=10)

        self.table = ttk.Treeview(self.root, height=4)

        self.table["columns"] = ("ID", "Beschreibung", "Kosten", "Zusätzliche Kosten", "Datum")
        self.table.column("#0", width=0, stretch=tkinter.NO)
        self.table.column("ID", anchor="w", width=50)
        self.table.column("Beschreibung", anchor="w", width=150)
        self.table.column("Kosten", anchor="e", width=80)
        self.table.column("Zusätzliche Kosten", anchor="e", width=80)
        self.table.column("Datum", anchor="w", width=100)

        self.table.heading("#0", text="", anchor="w")
        self.table.heading("ID", text="ID", anchor="w")
        self.table.heading("Beschreibung", text="Beschreibung", anchor="w")
        self.table.heading("Kosten", text="Kosten", anchor="e")
        self.table.heading("Zusätzliche Kosten", text="Zusätzliche Kosten", anchor="e")
        self.table.heading("Datum", text="Datum", anchor="w")
        self.table.grid(row=6, column=0, sticky=tkinter.EW, columnspan=3, padx=10)
        self.table_fill()

        tkinter.Label(self.root, text="Kommentar:").grid(row=8, column=0, pady=10)
        self.comment_entry = tkinter.Text(self.root, width=80, height=3)
        self.comment_entry.grid(row=9, column=0, sticky=tkinter.EW, columnspan=3, padx=10)
        self.sbo_var = tkinter.IntVar()
        self.sbo_checkbox = tkinter.Checkbutton(self.root, text="Kleinunternehmer", variable=self.sbo_var)
        self.sbo_checkbox.select()
        self.sbo_checkbox.grid(row=10, column=0, sticky=tkinter.W, padx=10)
        tkinter.Label(self.root, text="IBAN: "+self.create_bill_data[0][11]).grid(row=11, column=0, sticky=tkinter.W, padx=10)
        tkinter.Label(self.root, text="BIC: "+self.create_bill_data[0][12]).grid(row=12, column=0, sticky=tkinter.W, padx=10)
        self.save_button = tkinter.Button(self.root, text="Rechnung erstellen", command=self.save)
        self.save_button.grid(row=13, column=2, padx=10, pady=10)

    def table_fill(self):
        self.table_data = self.database.services_of_sc(self.sc_id)
        self.table_data = list(map(list, self.table_data))
        for i in range(len(self.table_data)):
            for j in range(2, 4):
                if self.table_data[i][j] is None:
                    self.table_data[i][j] = "0,00 €"
                else:
                    self.table_data[i][j] = "{:.2f} €".format(float(self.table_data[i][j])).replace(".", ",")
            self.table_data[i][4] = ".".join([str(ele) for ele in self.table_data[i][4:7]])
            if i % 2 == 0:
                self.table.insert(parent='', index=i, values=self.table_data[i], tags=('evenrow',))
            else:
                self.table.insert(parent='', index=i, values=self.table_data[i], tags=('oddrow',))

    def save(self):
        keyword = self.keyword_entry.get()
        comment = self.comment_entry.get("1.0","end-1c")
        day, month, year = map(int, self.date_entry.get().split("."))
        sbo = bool(self.sbo_var.get())
        self.database.new_bill(self.sc_id, self.create_bill_data[0][0], day, month, year, keyword, comment, sbo, True, False)
        self.root.destroy()
        self.master.root.destroy()
        self.master.master.refresh_sc_table()
        self.master.master.refresh_bill_table()



class EditBillWindow:
    def __init__(self, master):
        self.master = master
        self.root = tkinter.Toplevel(self.master.root)
        self.bill_year, self.bill_id = self.master.bill_table.item(master.bill_table.focus())["values"][0].split("-")

        self.bill_data = list(map(list, self.master.database.bill_data(self.bill_id, self.bill_year)))
        for i in range(3):
            if not self.bill_data[2][i]:
                self.bill_data[2][i] = ""

        tkinter.Label(self.root, text=self.bill_data[2][2]).grid(row=0, column=0, sticky=tkinter.W, padx=10)
        tkinter.Label(self.root, text=" ".join(self.bill_data[2][:2])).grid(row=1, column=0, sticky=tkinter.W,
                                                                                   padx=10)
        self.date_entry = DateEntry(self.root, locale='de_DE', date_pattern='dd.mm.yyyy')
        self.date_entry.set_date(".".join(map(str, self.bill_data[0][3:6])))
        self.date_entry["state"] = "disabled"
        self.date_entry.grid(row=1, column=1)
        tkinter.Label(self.root, text=" ".join(self.bill_data[1][2:4])).grid(row=0, column=2, sticky=tkinter.E,
                                                                                    padx=10)
        tkinter.Label(self.root, text=" ".join(self.bill_data[2][3:5])).grid(row=1, column=0, sticky=tkinter.W,
                                                                                    padx=10)
        tkinter.Label(self.root, text=" ".join(self.bill_data[1][5:7])).grid(row=1, column=2, sticky=tkinter.E,
                                                                                    padx=10)
        tkinter.Label(self.root, text=" ".join(self.bill_data[1][7:9])).grid(row=2, column=0, sticky=tkinter.W,
                                                                                    padx=10)
        tkinter.Label(self.root, text=" ".join(self.bill_data[1][7:9])).grid(row=2, column=2, sticky=tkinter.E,
                                                                                    padx=10)
        tkinter.Label(self.root, text="Tel.:" + self.bill_data[1][9]).grid(row=3, column=2, sticky=tkinter.E,
                                                                                  padx=10)
        tkinter.Label(self.root, text="E-Mail:" + self.bill_data[1][10]).grid(row=4, column=2, sticky=tkinter.E,
                                                                                     padx=10)
        tkinter.Label(self.root, text="Betreff:").grid(row=5, column=0, pady=10)
        keyword = tkinter.StringVar()
        keyword.set(self.bill_data[0][6])
        self.keyword_entry = tkinter.Entry(self.root, textvariable=keyword, state="disabled")
        self.keyword_entry.grid(row=5, column=1, sticky=tkinter.EW, pady=10)

        self.table = ttk.Treeview(self.root, height=4)

        self.table["columns"] = ("ID", "Beschreibung", "Kosten", "Zusätzliche Kosten", "Datum")
        self.table.column("#0", width=0, stretch=tkinter.NO)
        self.table.column("ID", anchor="w", width=50)
        self.table.column("Beschreibung", anchor="w", width=150)
        self.table.column("Kosten", anchor="e", width=80)
        self.table.column("Zusätzliche Kosten", anchor="e", width=80)
        self.table.column("Datum", anchor="w", width=100)

        self.table.heading("#0", text="", anchor="w")
        self.table.heading("ID", text="ID", anchor="w")
        self.table.heading("Beschreibung", text="Beschreibung", anchor="w")
        self.table.heading("Kosten", text="Kosten", anchor="e")
        self.table.heading("Zusätzliche Kosten", text="Zusätzliche Kosten", anchor="e")
        self.table.heading("Datum", text="Datum", anchor="w")
        self.table.grid(row=6, column=0, sticky=tkinter.EW, columnspan=3, padx=10)
        self.table_fill()

        tkinter.Label(self.root, text="Kommentar:").grid(row=8, column=0, pady=10)
        self.comment_entry = tkinter.Text(self.root, width=80, height=3)
        self.comment_entry.insert(tkinter.END, self.bill_data[0][7])
        self.comment_entry["state"] = tkinter.DISABLED
        self.comment_entry.grid(row=9, column=0, sticky=tkinter.EW, columnspan=3, padx=10)
        self.sbo_checkbox = tkinter.Checkbutton(self.root, text="Kleinunternehmer")
        if self.bill_data[0][8]:
            self.sbo_checkbox.select()
        self.sbo_checkbox["state"] = tkinter.DISABLED
        self.sbo_checkbox.grid(row=10, column=0, sticky=tkinter.W, padx=10)
        tkinter.Label(self.root, text="IBAN: " + self.bill_data[1][11]).grid(row=11, column=0, sticky=tkinter.W,
                                                                                    padx=10)
        tkinter.Label(self.root, text="BIC: " + self.bill_data[1][12]).grid(row=12, column=0, sticky=tkinter.W,
                                                                                   padx=10)
        self.valid = tkinter.BooleanVar(value=True)
        self.valid_checkbox = tkinter.Checkbutton(self.root, text="Rechnung gültig", variable=self.valid)
        self.valid_checkbox.grid(row=13, column=0, sticky=tkinter.W, padx=10)
        self.paid = tkinter.IntVar(value=self.bill_data[0][10])
        self.paid_checkbox = tkinter.Checkbutton(self.root, text="Rechnung bezahlt", variable=self.paid)
        self.paid_checkbox.grid(row=14, column=0, sticky=tkinter.W, padx=10)
        tkinter.Button(self.root, text="Speichern", command=self.save).grid(row=15, column=2, sticky=tkinter.E, padx=10, pady=10)
        tkinter.Button(self.root, text="Rechnung drucken", command=self.print).grid(row=16, column=2, sticky=tkinter.E, padx=10, pady=10)

    def save(self):
        self.master.database.update_bill(self.bill_id, self.bill_year, self.valid.get(), self.paid.get())
        self.root.destroy()
        self.master.refresh_bill_table()

    def print(self):
        name = str(self.bill_year) + f"{int(self.bill_id):03d}" + ".pdf" # Why is ID a string?
        direction = filedialog.asksaveasfilename(initialfile=name, filetypes=[("PDF-Datei", ".pdf")], parent=self.root)
        pdf = PdfBill(self.bill_id, self.bill_year, self.master.database, direction)
        pdf.save()
        self.root.destroy()

    def table_fill(self):
        self.table_data = self.master.database.services_of_sc(self.bill_data[0][1])
        self.table_data = list(map(list, self.table_data))
        for i in range(len(self.table_data)):
            for j in range(2, 4):
                if self.table_data[i][j] is None:
                    self.table_data[i][j] = "0,00 €"
                else:
                    self.table_data[i][j] = "{:.2f} €".format(float(self.table_data[i][j])).replace(".", ",")
            self.table_data[i][4] = ".".join([str(ele) for ele in self.table_data[i][4:7]])
            if i % 2 == 0:
                self.table.insert(parent='', index=i, values=self.table_data[i], tags=('evenrow',))
            else:
                self.table.insert(parent='', index=i, values=self.table_data[i], tags=('oddrow',))



class EditSCWindow:
    def __init__(self, master):
        self.master = master
        self.database = master.database
        self.customer = master.sc_table.item(master.sc_table.focus())["values"][1]

        self.root = tkinter.Toplevel(master.root)
        tkinter.Button(self.root, text="Auftrag löschen", command=self.delete).grid(row=0, column=0, padx=10, pady=10)
        tkinter.Label(self.root, text="Auftraggeber:").grid(row=1, column=0, padx=10, pady=10)
        self.customer_button = tkinter.Button(self.root, text=self.customer, command=lambda: ChooseCustomer(self))
        self.customer_button.grid(row=1, column=1, padx=10, pady=10)
        self.table = ttk.Treeview(self.root)

        self.table["columns"] = ("ID", "Beschreibung", "Kosten", "Zusätzliche Kosten", "Datum")
        self.table.column("#0", width=0, stretch=tkinter.NO)
        self.table.column("ID", anchor="w", width=50)
        self.table.column("Beschreibung", anchor="w", width=160)
        self.table.column("Kosten", anchor="e", width=80)
        self.table.column("Zusätzliche Kosten", anchor="e", width=120)
        self.table.column("Datum", anchor="w", width=100)

        self.table.heading("#0", text="", anchor="w")
        self.table.heading("ID", text="ID", anchor="w")
        self.table.heading("Beschreibung", text="Beschreibung", anchor="w")
        self.table.heading("Kosten", text="Kosten", anchor="e")
        self.table.heading("Zusätzliche Kosten", text="Zusätzliche Kosten", anchor="e")
        self.table.heading("Datum", text="Datum", anchor="w")
        self.table.grid(row=2, column=0, sticky=tkinter.EW, columnspan=2, padx=10)
        self.table.bind("<Double-1>", lambda event: EditServiceWindow(self))
        self.table_fill()
        tkinter.Button(self.root, text="+", command=lambda: NewServiceWindow(self)).grid(row=3, column=0, sticky=tkinter.EW, columnspan=2, padx=10)

        tkinter.Button(self.root, text="Speichern", command=self.save).grid(row=4, column=2, padx=10, pady=10)
        tkinter.Button(self.root, text="Rechnung erstellen", command=self.create_bill).grid(row=5, column=2, padx=10, pady=10)

    def create_bill(self):
        sc_id = self.master.sc_table.item(self.master.sc_table.focus())["values"][0]
        CreateBillWindow(sc_id, self)

    def table_fill(self):
        self.table_data = self.master.database.services_of_sc(self.master.sc_table.item(self.master.sc_table.focus())["values"][0])
        self.table_data = list(map(list, self.table_data))
        for i in range(len(self.table_data)):
            for j in range(2, 4):
                if self.table_data[i][j] == "" or self.table_data[i][j] is None:
                    self.table_data[i][j] = "0,00 €"
                else:
                    self.table_data[i][j] = "{:.2f} €".format(float(self.table_data[i][j])).replace(".", ",")
            self.table_data[i][4] = ".".join([str(ele) for ele in self.table_data[i][4:7]])
            if i % 2 == 0:
                self.table.insert(parent='', index=i, values=self.table_data[i], tags=('evenrow',))
            else:
                self.table.insert(parent='', index=i, values=self.table_data[i], tags=('oddrow',))

    def update_customer(self, customer):
        self.customer = customer
        self.customer_button["text"] = customer[4] if customer[4] else customer[2]

    def save(self):
        if type(self.customer) != str:
            self.master.database.change_sc(self.master.sc_table.item(self.master.sc_table.focus())["values"][0], self.customer[0])
        self.master.refresh_sc_table()
        self.root.destroy()

    def delete(self):
        confirm = tkinter.messagebox.askyesno(title="Auftrag löschen", message="Möchten Sie den Auftrag löschen?",
                                              parent=self.root)
        if confirm:
            self.master.database.delete_sc(self.master.sc_table.item(self.master.sc_table.focus())["values"][0])
            self.master.refresh_sc_table()
            self.root.destroy()

    def new_service(self, description, price, additional_price, day, month, year):
        self.master.database.new_service(
            self.master.sc_table.item(self.master.sc_table.focus())["values"][0],
            description,
            price,
            additional_price,
            day,
            month,
            year
        )
        self.refresh_table()

    def change_service(self, s_id, description, price, additional_price, day, month, year):
        self.master.database.change_service(
            s_id,
            description,
            price,
            additional_price,
            day,
            month,
            year
        )
        self.refresh_table()

    def delete_service(self, s_id):
        self.master.database.delete_service(s_id)
        self.refresh_table()

    def refresh_table(self):
        self.table.delete(*self.table.get_children())
        self.table_fill()


class NewSCWindow:
    def __init__(self, master):
        self.master = master
        self.database = master.database
        self.customer = None
        self.root = tkinter.Toplevel(master.root)
        tkinter.Label(self.root, text="Auftraggeber:").grid(row=0, column=0, padx=10, pady=10, sticky=tkinter.W)
        self.customer_button = tkinter.Button(self.root, text="Auswählen", command=lambda: ChooseCustomer(self))
        self.customer_button.grid(row=0, column=1, padx=10, pady=10)
        tkinter.Label(self.root, text="Id:").grid(row=1, column=0, padx=10, sticky=tkinter.W)
        tkinter.Label(self.root, text=master.database.next_sc_id()).grid(row=1, column=1, padx=10, pady=10)
        self.enter_button = tkinter.Button(self.root, text="Hinzufügen", state=tkinter.DISABLED, command= self.new_sc)
        self.enter_button.grid(row=2, column=2, padx=10, pady=10)

    def update_customer(self, customer):
        self.customer = customer
        self.customer_button["text"] = self.customer[2] if customer[2] else customer[4]
        self.enter_button["state"] = tkinter.ACTIVE

    def new_sc(self):
        self.master.new_sc(self.customer)
        self.root.destroy()


class ChooseCustomer:
    def __init__(self, master):
        self.master = master
        self.database = master.database
        self.root = tkinter.Toplevel(self.master.root)
        self.table = ttk.Treeview(self.root)
        self.c_table_data = []
        self.table["columns"] = ("ID", "Vorname", "Nachname", "Geschlecht", "Institution", "Straße", "Nummer", "PLZ", "Ort")
        self.table.column("#0", width=0, stretch=tkinter.NO)
        self.table.column("ID", anchor=tkinter.W, width=50)
        self.table.column("Vorname", anchor=tkinter.W, width=100)
        self.table.column("Nachname", anchor=tkinter.W, width=100)
        self.table.column("Geschlecht", anchor=tkinter.W, width=80)
        self.table.column("Institution", anchor=tkinter.W, width=100)
        self.table.column("Straße", anchor=tkinter.W, width=100)
        self.table.column("Nummer", anchor=tkinter.W, width=80)
        self.table.column("PLZ", anchor=tkinter.W, width=80)
        self.table.column("Ort", anchor=tkinter.W, width=100)

        self.table.heading("#0", text="", anchor=tkinter.W)
        self.table.heading("ID", text="ID", anchor=tkinter.W)
        self.table.heading("Vorname", text="Vorname", anchor=tkinter.W)
        self.table.heading("Nachname", text="Nachname", anchor=tkinter.W)
        self.table.heading("Geschlecht", text="Geschlecht", anchor=tkinter.W)
        self.table.heading("Institution", text="Institution", anchor=tkinter.W)
        self.table.heading("Straße", text="Straße", anchor=tkinter.W)
        self.table.heading("Nummer", text="Nummer", anchor=tkinter.W)
        self.table.heading("PLZ", text="PLZ", anchor=tkinter.W)
        self.table.heading("Ort", text="Ort", anchor=tkinter.W)

        self.c_table_fill()

        self.table.grid(row=0, column=0, sticky=tkinter.EW)
        self.table.bind("<Double-1>", self.return_customer)

        tkinter.Button(self.root, text="Neuer Auftraggeber", command=lambda: NewCustomer(self)).grid(row=1, column=0)

    def c_table_fill(self):
        self.c_table_data = self.master.database.customers_long()
        for i in range(len(self.c_table_data)):
            if i % 2 == 0:
                self.table.insert(parent='', index=i, values=self.c_table_data[i], tags=('evenrow',))
            else:
                self.table.insert(parent='', index=i, values=self.c_table_data[i], tags=('oddrow',))

    def return_customer(self, event):
        self.master.update_customer(self.table.item(self.table.focus())["values"])
        self.root.destroy()

    def create_customer(self, customer):
        self.database.new_customer(*customer)
        self.table.delete(*self.table.get_children())
        self.c_table_fill()


class NewCustomer:
    def __init__(self, master):
        self.master = master
        self.database = master.database
        self.root = tkinter.Toplevel(master.root)

        tkinter.Label(self.root, text="Vorname:").grid(row=0, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="Nachname:").grid(row=1, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="Geschlecht:").grid(row=2, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="Institution:").grid(row=3, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="Straße:").grid(row=4, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="Nummer:").grid(row=5, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="PLZ:").grid(row=6, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="Ort:").grid(row=7, column=0, sticky=tkinter.W, padx=10, pady=10)

        self.first_name_entry = tkinter.Entry(self.root)
        self.first_name_entry.grid(row=0, column=1, padx=10, sticky=tkinter.EW)
        self.last_name_entry = tkinter.Entry(self.root)
        self.last_name_entry.grid(row=1, column=1, padx=10, sticky=tkinter.EW)
        self.genders = ["weiblich", "männlich", "divers"]
        self.gender_box = ttk.Combobox(self.root, values=self.genders, state="readonly")
        self.gender_box.grid(row=2, column=1, padx=10, sticky=tkinter.EW)
        self.institution_entry = tkinter.Entry(self.root)
        self.institution_entry.grid(row=3, column=1, padx=10, sticky=tkinter.EW)
        self.street_entry = tkinter.Entry(self.root)
        self.street_entry.grid(row=4, column=1, padx=10, sticky=tkinter.EW)
        self.number_entry = tkinter.Entry(self.root)
        self.number_entry.grid(row=5, column=1, padx=10, sticky=tkinter.EW)
        self.postal_code_entry = tkinter.Entry(self.root)
        self.postal_code_entry.grid(row=6, column=1, padx=10, sticky=tkinter.EW)
        self.place_entry = tkinter.Entry(self.root)
        self.place_entry.grid(row=7, column=1, padx=10, sticky=tkinter.EW)

        tkinter.Button(self.root, text="Erstellen", command=self.create).grid(row=8, column=2, padx=10, pady=10)

    def create(self):
        self.master.create_customer([
            self.first_name_entry.get(),
            self.last_name_entry.get(),
            self.genders.index(self.gender_box.get()),
            self.institution_entry.get(),
            self.street_entry.get(),
            self.number_entry.get(),
            self.postal_code_entry.get(),
            self.place_entry.get()
        ])
        self.root.destroy()


class EditServiceWindow:
    def __init__(self, master):
        self.master = master
        self.root = tkinter.Toplevel(self.master.root)
        self.root.title("Dienstleistung bearbeiten")

        self.service_id = self.master.table.item(self.master.table.focus())["values"][0]
        self.service_info = self.master.database.service_info(self.service_id)

        tkinter.Label(self.root, text="Beschreibung:").grid(row=0, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="Kosten:").grid(row=1, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="Zusätzliche Kosten:").grid(row=2, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="Datum:").grid(row=3, column=0, sticky=tkinter.W, padx=10, pady=10)

        self.description_entry = tkinter.Entry(self.root)
        self.description_entry.insert(0, self.service_info[0][0])
        self.description_entry.grid(row=0, column=1, padx=10, pady=10)
        self.price_entry = tkinter.Entry(self.root)
        self.price_entry.insert(0, "{:.2f}".format(self.service_info[0][1]).replace(".", ","))
        self.price_entry.grid(row=1, column=1, padx=10, pady=10)
        self.additional_price_entry = tkinter.Entry(self.root)
        self.additional_price_entry.insert(0, "{:.2f}".format(self.service_info[0][2]).replace(".", ","))
        self.additional_price_entry.grid(row=2, column=1, padx=10, pady=10)
        self.date_entry = DateEntry(self.root, locale='de_DE', date_pattern='dd.mm.yyyy')
        self.date_entry.set_date(".".join([str(ele) for ele in self.service_info[0][3:6]]))
        self.date_entry.grid(row=3, column=1, padx=10, pady=10)
        tkinter.Button(self.root, text="Löschen", command=self.delete).grid(row=4, column=2, padx=10, pady=10)
        tkinter.Button(self.root, text="Speichern", command=self.save).grid(row=5, column=2, padx=10, pady=10)

    def save(self):
        self.master.change_service(
            self.service_id,
            self.description_entry.get(),
            float(self.price_entry.get().replace(",", ".")) if self.price_entry.get() != "" else 0.0,
            float(self.additional_price_entry.get().replace(",", ".")) if self.additional_price_entry.get() != "" else 0.0,
            *[int(ele) for ele in self.date_entry.get().split(".")]
        )
        self.root.destroy()

    def delete(self):
        self.master.delete_service(self.service_id)
        self.root.destroy()


class NewServiceWindow:
    def __init__(self, master):
        self.master = master
        self.root = tkinter.Toplevel(self.master.root)
        self.root.title("Neue Dienstleistung")

        tkinter.Label(self.root, text="Beschreibung:").grid(row=0, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="Kosten:").grid(row=1, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="Zusätzliche Kosten:").grid(row=2, column=0, sticky=tkinter.W, padx=10, pady=10)
        tkinter.Label(self.root, text="Datum:").grid(row=3, column=0, sticky=tkinter.W, padx=10, pady=10)

        self.description_entry = tkinter.Entry(self.root)
        self.description_entry.grid(row=0, column=1, padx=10, pady=10)
        self.price_entry = tkinter.Entry(self.root)
        self.price_entry.grid(row=1, column=1, padx=10, pady=10)
        self.additional_price_entry = tkinter.Entry(self.root)
        self.additional_price_entry.grid(row=2, column=1, padx=10, pady=10)
        self.date_entry = DateEntry(self.root, locale='de_DE', date_pattern='dd.mm.yyyy')
        self.date_entry.grid(row=3, column=1, padx=10, pady=10)

        tkinter.Button(self.root, text="Speichern", command=self.save).grid(row=4, column=2, padx=10, pady=10)
    def save(self):
        self.master.new_service(
            self.description_entry.get(),
            float(self.price_entry.get().replace(",", ".")) if self.price_entry.get() != "" else 0.0,
            float(self.additional_price_entry.get().replace(",", ".")) if self.additional_price_entry.get() != "" else 0.0,
            *[int(ele) for ele in self.date_entry.get().split(".")]
        )
        self.root.destroy()




class MainWindow:
    def __init__(self, database, setup):
        self.database = database
        self.setup = setup

        self.root = tkinter.Tk()
        self.root.geometry("1080x1920")
        self.root.state("zoomed")
        self.root.title("Rechnungsmanager")

        self.menubar = tkinter.Menu(self.root)
        self.database_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.database_menu.add_command(label="Importieren", command=self.import_db)
        self.database_menu.add_command(label="Exportieren", command=self.export_db)
        self.database_menu.add_separator()
        self.database_menu.add_command(label="Neu")
        self.database_menu.add_command(label="Löschen")
        self.menubar.add_cascade(label="Datenbank", menu=self.database_menu)

        self.provider_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.provider_var = tkinter.IntVar(value=self.setup.active_provider_id())
        self.refresh_provider_menu()
        self.menubar.add_cascade(label="Dienstleister", menu=self.provider_menu)

        self.help_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label="Anleitung online ansehen")
        self.help_menu.add_command(label="Versionsanzeige", command=self.show_version)
        self.help_menu.add_command(label="Lizenz", command=self.show_license)
        self.menubar.add_cascade(label="Hilfe", menu=self.help_menu)

        self.root.config(menu=self.menubar)

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, minsize=50)
        self.root.rowconfigure(4, minsize=50)

        self.sc_table_label = tkinter.Label(self.root, text="Offene Aufträge:")
        self.sc_table_label.grid(row=1, column=0)

        self.sc_table = ttk.Treeview(self.root)
        self.sc_table["columns"] = ("Auftrags-ID", "Auftraggeber", "Dienstleistungen", "Preis")
        self.sc_table.column("#0", width=0, stretch=tkinter.NO)
        self.sc_table.column("Auftrags-ID", anchor="w", width=100)
        self.sc_table.column("Auftraggeber", anchor="w", width=200)
        self.sc_table.column("Dienstleistungen", anchor="w", width=100)
        self.sc_table.column("Preis", anchor="e", width=100)

        self.sc_table.heading("#0", text="", anchor="w")
        self.sc_table.heading("Auftrags-ID", text="Auftrags-ID", anchor="w")
        self.sc_table.heading("Auftraggeber", text="Auftraggeber", anchor="w")
        self.sc_table.heading("Dienstleistungen", text="Dienstleistungen", anchor="w")
        self.sc_table.heading("Preis", text="Preis", anchor="e")
        self.sc_table.grid(row=2, column=0, sticky=tkinter.EW, padx=300)
        self.sc_table.bind("<Double-1>", lambda event: EditSCWindow(self))

        self.sc_table_fill()

        self.new_sc_button = tkinter.Button(self.root, text="+", command=lambda: NewSCWindow(self))
        self.new_sc_button.grid(row=3, column=0, sticky=tkinter.EW, padx=300)

        self.bill_table_label = tkinter.Label(self.root, text="Offene Rechnungen:")
        self.bill_table_label.grid(row=5, column=0)

        self.bill_table = ttk.Treeview(self.root)
        self.bill_table["columns"] = ("Rechnungsnummer", "Auftraggeber", "Stichwort", "Preis")
        self.bill_table.column("#0", width=0, stretch=tkinter.NO)
        self.bill_table.column("Rechnungsnummer", anchor=tkinter.W, width=100)
        self.bill_table.column("Auftraggeber", anchor=tkinter.W, width=200)
        self.bill_table.column("Stichwort", anchor=tkinter.W, width=100)
        self.bill_table.column("Preis", anchor="e", width=100)

        self.bill_table.heading("#0", text="", anchor=tkinter.W)
        self.bill_table.heading("Rechnungsnummer", text="Rechnungsnummer", anchor=tkinter.W)
        self.bill_table.heading("Auftraggeber", text="Auftraggeber", anchor=tkinter.W)
        self.bill_table.heading("Stichwort", text="Stichwort", anchor=tkinter.W)
        self.bill_table.heading("Preis", text="Preis", anchor="e")
        self.bill_table.grid(row=6, column=0, sticky=tkinter.EW, padx=300)
        self.bill_table.bind("<Double-1>", lambda event: self.edit_bill())

        self.bill_table_fill()
        tkinter.Button(self.root, text="Alle Rechnungen anzeigen", command=lambda: ShowBillsWindow(self)).grid(row=7, column=0, sticky=tkinter.EW, padx=300)

        # === Root mainloop

        self.root.mainloop()

    def sc_table_fill(self):
        sc_table_data = []
        for ele in self.database.sc_table_query():
            sc_table_data.append([])
            sc_table_data[-1].append(ele[0])
            if ele[2]:
                sc_table_data[-1].append(ele[2])
            else:
                sc_table_data[-1].append(ele[1])
            sc_table_data[-1].append(ele[3])
            if ele[4] is None:
                sc_table_data[-1].append("0,00 €")
            else:
                sc_table_data[-1].append("{:.2f} €".format(float(ele[4])).replace(".", ","))
        for i in range(len(sc_table_data)):
            if i % 2 == 0:
                self.sc_table.insert(parent='', index=i, values=sc_table_data[i], tags=('evenrow',))
            else:
                self.sc_table.insert(parent='', index=i, values=sc_table_data[i], tags=('oddrow',))

    def bill_table_fill(self):
        bill_table_data = []
        for ele in self.database.bill_table_query():
            bill_table_data.append([])
            bill_table_data[-1].append(str(ele[1]) + "-" + str(ele[0]))
            if ele[3]:
                bill_table_data[-1].append(ele[3])
            else:
                bill_table_data[-1].append(ele[2])
            bill_table_data[-1].append(ele[4])
            if ele[5] is None:
                bill_table_data[-1].append("0,00 €")
            else:
                bill_table_data[-1].append("{:.2f} €".format(float(ele[5])).replace(".", ","))
        for i in range(len(bill_table_data)):
            if i % 2 == 0:
                self.bill_table.insert(parent='', index=i, values=bill_table_data[i], tags=('evenrow',))
            else:
                self.bill_table.insert(parent='', index=i, values=bill_table_data[i], tags=('oddrow',))

    def new_sc(self, customer):
        """New service complex"""
        self.database.new_sc(customer[0])
        self.refresh_sc_table()

    def refresh_provider_menu(self):
        self.provider_menu.delete(0, tkinter.END)
        for ele in self.setup.all_providers():
            self.provider_menu.add_checkbutton(label=ele[0], variable=self.provider_var, onvalue=ele[3], offvalue=ele[3], command=self.activate_provider)
        self.provider_menu.add_separator()
        self.provider_menu.add_command(label="Hinzufügen", command=self.add_provider)
        self.provider_menu.add_command(label="Löschen", command=self.delete_provider)

    def activate_provider(self):
        self.setup.activate_provider(self.provider_var.get())
        self.database = Db(os.getcwd() + self.setup.active_provider()[0][1])
        self.refresh_sc_table()
        self.refresh_bill_table()

    def add_provider(self):
        NewProviderWindow(self.setup, self)

    def delete_provider(self):
        DeleteProviderWindow(self.setup, self)


    def refresh_sc_table(self):
        self.sc_table.delete(*self.sc_table.get_children())
        self.sc_table_fill()

    def refresh_bill_table(self):
        self.bill_table.delete(*self.bill_table.get_children())
        self.bill_table_fill()

    def edit_bill(self):
        if self.bill_table.item(self.bill_table.focus())["values"]:
            EditBillWindow(self)

    def import_db(self):
        old_dir = filedialog.askopenfilename(parent=self.root)
        validation = ValidateDbWindow(self, old_dir)
        if validation.is_valid():
            shutil.copyfile(old_dir, os.getcwd() + "\\databases\\" + str(self.setup.provider_next_id()) + ".rmdb")
            self.setup.new_provider(validation.setup_info(), "\\databases\\" + str(self.setup.provider_next_id()) + ".rmdb")
            self.refresh_provider_menu()
            self.provider_var.set(self.setup.active_provider_id())

    def export_db(self):
        old_dir = os.getcwd() + self.setup.active_provider()[0][1]
        new_dir = filedialog.asksaveasfilename(initialfile=self.setup.active_provider()[0][0].replace(" ", ""), filetypes=[("Rechnungsmanager-Datei", ".rmdb"), ("Sqlite-Datenbank", ".db")], defaultextension=[("Rechnungsmanager-Datei", ".rmdb"), ("Sqlite-Datenbank", ".db")], parent=self.root)
        shutil.copyfile(old_dir, new_dir)

    def show_version(self):
        showinfo("Versionsanzeige", "Version " + ".".join(map(str,_VERSION[:3])) + _VERSION[3])

    def show_license(self):
        with open("LICENSE.txt", "r") as file:
            text = file.read()
            showinfo("Lizenz", text)

    def refresh_database(self):
        path = os.getcwd() + self.setup.active_provider()[0][1]
        self.database = database.Db(path)
        self.refresh_sc_table()
        self.refresh_bill_table()
