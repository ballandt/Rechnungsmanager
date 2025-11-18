import ui
import database
import os

os.makedirs("/databases/", exist_ok=True)
os.makedirs("/setup/", exist_ok=True)
setup = database.Setup()

if not setup.active_provider():
    ui.NewProviderWindow(setup)

db = setup.active_provider()[0][1]
base = database.Db(os.getcwd() + db)


app = ui.MainWindow(base, setup)
