from pdfcreator import Bill as PdfBill
import ui
# from database.queries import sc_table_query
import database
import os

setup = database.Setup()
if not setup.active_provider():
    ui.NewProviderWindow(setup)

db = setup.active_provider()[0][1]
base = database.Db(os.getcwd() + db)


app = ui.MainWindow(base, setup)
