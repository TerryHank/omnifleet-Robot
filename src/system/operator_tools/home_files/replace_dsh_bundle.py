from pathlib import Path


BUNDLE = Path("/opt/Foxglove-Studio-CN/resources/app-web/4936.33f3ad98e1e1f7b86b00.js")
SOURCE = Path("/home/iecme/omnifleet_t2_ws/foxglove/dsh_diagnostic_panel/DshDiagnosticPanel.js")
START = "/*OMNIFLEET_DSH_DIAGNOSTIC_START*/"
END = "/*OMNIFLEET_DSH_DIAGNOSTIC_END*/"


bundle = BUNDLE.read_text()
source = SOURCE.read_text().replace("export function initDshDiagnosticPanel", "function initDshDiagnosticPanel", 1)
start = bundle.index(START)
end = bundle.index(END, start) + len(END)
replacement = START + "\n" + source + "\n" + END
BUNDLE.write_text(bundle[:start] + replacement + bundle[end:])
print("DSH_BUNDLE_UPDATED")
