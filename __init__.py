import ui
import database
import os

# connects to setup database
setup = database.Setup()

# creates first provider when app is opened for the first time
if not setup.active_provider():
    ui.NewProviderWindow(setup)

# select active provider for opening screen
db = setup.active_provider()[0][1]
# connects provider database
base = database.Db(os.getcwd() + db)

# starts app
app = ui.MainWindow(base, setup)
