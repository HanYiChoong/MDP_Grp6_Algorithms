from configs.gui_config import GUI_TITLE
from gui import SimulatorGUI

app = SimulatorGUI()
app.title(GUI_TITLE)
app.resizable(False, False)
app.mainloop()
