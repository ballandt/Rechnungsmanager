import ui
import database
import os

setup = database.Setup()

if not setup.active_provider():
    ui.NewProviderWindow(setup)

db = setup.active_provider()[0][1]
base = database.Db(os.getcwd() + db)


app = ui.MainWindow(base, setup)
