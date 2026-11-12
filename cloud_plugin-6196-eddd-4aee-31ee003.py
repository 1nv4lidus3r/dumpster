# /// script
# dependencies = []
# requires-python = ">=3.12"
# [tool.orcaslicer.plugin]
# name = "PrinterAssist"
# description = "PrinterAssist analyse les réglages actifs dans OrcaSlicer et propose des conseils simples pour améliorer la qualité, la solidité ou la rapidité des impressions. Il signale aussi certaines erreurs G-code, sans modifier vos paramètres."
# author = "Fabien"
# version = "34.6.0"
# icon = "printer.svg"
# ///

import orca
import math
from pathlib import Path

PLUGIN_ICON_PATH = Path(__file__).resolve().parent / "printer.svg"
ORIGINAL_ICON_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="128" height="128">\n  <!-- Fond du badge -->\n  <rect width="100" height="100" rx="18" fill="#1E1E2E" />\n  \n  <!-- Structure de l\'imprimante -->\n  <rect x="20" y="20" width="60" height="60" rx="8" fill="none" stroke="#E0E6ED" stroke-width="4" />\n  <line x1="20" y1="35" x2="80" y2="35" stroke="#E0E6ED" stroke-width="3" />\n  <rect x="25" y="70" width="50" height="4" rx="2" fill="#00C853" />\n  \n  <!-- Tête d\'impression -->\n  <rect x="44" y="30" width="12" height="10" rx="2" fill="#8892B0" />\n  <polygon points="47,40 53,40 50,46" fill="#8892B0" />\n  \n  <!-- Pièce en cours d\'impression -->\n  <polygon points="32,68 46,48 60,68" fill="#00C853" opacity="0.85" />\n  \n  <!-- Symbole d\'assistance -->\n  <circle cx="68" cy="65" r="14" fill="#FFB74D" stroke="#1E1E2E" stroke-width="2" />\n  <text x="68" y="72" font-family="Arial, sans-serif" font-size="16" font-weight="bold" fill="#1E1E2E" text-anchor="middle">i</text>\n</svg>'


def icon_path():
    """Même principe que Print Calculator : fournir un vrai fichier SVG local."""
    try:
        if not PLUGIN_ICON_PATH.is_file():
            PLUGIN_ICON_PATH.write_text(ORIGINAL_ICON_SVG + "\n", encoding="utf-8")
        return str(PLUGIN_ICON_PATH.resolve())
    except OSError:
        return str(PLUGIN_ICON_PATH.resolve()) if PLUGIN_ICON_PATH.is_file() else ""


def _orca_language():
    try:
        info = orca.host.app_info()
        raw = (info.get('language') if isinstance(info, dict) else getattr(info, 'language', '')) or ''
    except Exception:
        raw = ''
    if not raw:
        try:
            import locale
            raw = locale.getlocale()[0] or ''
        except Exception:
            raw = ''
    raw = str(raw).replace('-', '_').lower()
    if raw.startswith(('zh_cn','zh_hans','chinese_simplified')): return 'zh_CN'
    for code in ('fr','en','es','de','it','pt','nl','pl','ja'):
        if raw.startswith(code): return code
    return 'en'

HTML = r'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
:root{color-scheme:dark}body{font:14px 'Segoe UI',sans-serif;background:var(--orca-bg,#1c2026);color:var(--orca-fg,#e7e9ec);padding:20px}h1{font-size:22px}.pa-heading{display:flex;align-items:center;gap:12px}.pa-logo{width:44px;height:44px;flex-shrink:0}.pa-controls{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;width:100%;box-sizing:border-box}.pa-control-group{display:flex;align-items:center;gap:7px;white-space:nowrap}.pa-control-group select{margin:0}.pa-control-language{margin-left:auto}select{background:#293039;color:#fff;padding:9px;border:1px solid #68717b;border-radius:7px;margin:0 12px 8px 5px}button{background:#009688;color:white;border:0;padding:10px 18px;border-radius:7px;cursor:pointer}table{border-collapse:collapse;width:100%;margin-top:14px}td,th{padding:10px;text-align:left;border-bottom:1px solid #5555}th{opacity:.75}.ok{color:#49c9a5}.warn{color:#f0b45d}.err{color:#ff7777}.muted{opacity:.7}.go-setting{display:inline-flex;align-items:center;justify-content:center;width:19px;height:19px;padding:0;margin-left:6px;border:1px solid #009688;border-radius:50%;background:transparent;color:#009688;font-size:12px;font-weight:bold;vertical-align:middle;line-height:1}.go-setting:hover,.go-setting:focus{background:#009688;color:white}.hint-wrap{display:inline-block;position:relative;vertical-align:middle;margin-left:5px}.hint-tip{display:none;position:absolute;z-index:1000;bottom:calc(100% + 9px);right:-12px;width:290px;max-width:70vw;padding:11px 13px;border:1px solid #009688;border-radius:8px;background:#252c34;color:#f1f3f5;box-shadow:0 4px 16px #0007;font-size:12px;font-weight:normal;line-height:1.5;text-align:left;white-space:normal;pointer-events:none}.hint-wrap:hover .hint-tip,.hint-wrap:focus-within .hint-tip{display:block}.hint-tip:after{content:"";position:absolute;top:100%;right:14px;border:7px solid transparent;border-top-color:#009688}.hint-tip strong{color:#7ee0d0}.go-setting:focus-visible{outline:2px solid #fff;outline-offset:2px}section{padding:14px;margin:14px 0;border:1px solid #7775;border-radius:10px}code{white-space:pre-wrap}#status{margin-top:12px}.disclaimer{margin-top:18px;padding:12px 14px;border:1px solid #7775;border-radius:9px;font-size:12px;line-height:1.5;color:var(--orca-fg,#e7e9ec);opacity:.85}</style></head><body>
<div class="pa-heading"><img class="pa-logo" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIiB3aWR0aD0iMTI4IiBoZWlnaHQ9IjEyOCI+CiAgPCEtLSBGb25kIGR1IGJhZGdlIC0tPgogIDxyZWN0IHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiByeD0iMTgiIGZpbGw9IiMxRTFFMkUiIC8+CiAgCiAgPCEtLSBTdHJ1Y3R1cmUgZGUgbCdpbXByaW1hbnRlIC0tPgogIDxyZWN0IHg9IjIwIiB5PSIyMCIgd2lkdGg9IjYwIiBoZWlnaHQ9IjYwIiByeD0iOCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjRTBFNkVEIiBzdHJva2Utd2lkdGg9IjQiIC8+CiAgPGxpbmUgeDE9IjIwIiB5MT0iMzUiIHgyPSI4MCIgeTI9IjM1IiBzdHJva2U9IiNFMEU2RUQiIHN0cm9rZS13aWR0aD0iMyIgLz4KICA8cmVjdCB4PSIyNSIgeT0iNzAiIHdpZHRoPSI1MCIgaGVpZ2h0PSI0IiByeD0iMiIgZmlsbD0iIzAwQzg1MyIgLz4KICAKICA8IS0tIFTDqnRlIGQnaW1wcmVzc2lvbiAtLT4KICA8cmVjdCB4PSI0NCIgeT0iMzAiIHdpZHRoPSIxMiIgaGVpZ2h0PSIxMCIgcng9IjIiIGZpbGw9IiM4ODkyQjAiIC8+CiAgPHBvbHlnb24gcG9pbnRzPSI0Nyw0MCA1Myw0MCA1MCw0NiIgZmlsbD0iIzg4OTJCMCIgLz4KICAKICA8IS0tIFBpw6hjZSBlbiBjb3VycyBkJ2ltcHJlc3Npb24gLS0+CiAgPHBvbHlnb24gcG9pbnRzPSIzMiw2OCA0Niw0OCA2MCw2OCIgZmlsbD0iIzAwQzg1MyIgb3BhY2l0eT0iMC44NSIgLz4KICAKICA8IS0tIFN5bWJvbGUgZCdhc3Npc3RhbmNlIC0tPgogIDxjaXJjbGUgY3g9IjY4IiBjeT0iNjUiIHI9IjE0IiBmaWxsPSIjRkZCNzREIiBzdHJva2U9IiMxRTFFMkUiIHN0cm9rZS13aWR0aD0iMiIgLz4KICA8dGV4dCB4PSI2OCIgeT0iNzIiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNiIgZm9udC13ZWlnaHQ9ImJvbGQiIGZpbGw9IiMxRTFFMkUiIHRleHQtYW5jaG9yPSJtaWRkbGUiPmk8L3RleHQ+Cjwvc3ZnPg==" alt="Logo PrinterAssist"><h1>PrinterAssist v34.6</h1></div><p data-pa="subtitle">Analyse des profils actifs directement depuis OrcaSlicer. Aucune modification des réglages.</p>
<div class="pa-controls"><div class="pa-control-group"><label for="goal" data-pa="goal">Objectif d’impression : </label><select id="goal" onchange="analyse()"><option value="balanced" data-pa="balanced">Équilibré</option><option value="quality" data-pa="quality">Qualité</option><option value="strength" data-pa="strength">Solidité</option><option value="speed" data-pa="speed">Rapidité</option></select></div><div class="pa-control-group pa-control-language"><label for="pa-language" data-pa="language">Langue :</label><select id="pa-language" onchange="paChangeLanguage()"><option value="auto">Comme OrcaSlicer</option><option value="fr">Français</option><option value="en">English</option><option value="es">Español</option><option value="de">Deutsch</option><option value="it">Italiano</option><option value="pt">Português</option><option value="zh_CN">简体中文</option></select></div></div><div id="status" data-pa="waiting">En attente...</div><div id="report"></div><div class="disclaimer"><strong data-pa="disclaimer">Avertissement :</strong> <span data-pa="disclaimer_body">PrinterAssist fournit uniquement des recommandations indicatives, sans garantie de résultat ni de compatibilité avec chaque imprimante. Vous restez responsable des modifications apportées à vos réglages et devez vérifier leur adéquation avec les consignes du fabricant. Les développeurs de PrinterAssist ne sauraient être tenus responsables des dysfonctionnements ou dommages résultant de l’application de ces conseils, dans les limites autorisées par la loi.</span></div>
<script>
const PA_FIELD_EN={"Hauteur de couche": "Layer height", "Nombre de parois": "Wall loops", "Densité de remplissage": "Infill density", "Motif de remplissage": "Infill pattern", "Vitesse paroi externe": "Outer wall speed", "Vitesse paroi interne": "Inner wall speed", "Vitesse remplissage": "Infill speed", "Vitesse remplissage plein": "Solid infill speed", "Vitesse surface supérieure": "Top surface speed", "Vitesse première couche": "First layer speed", "Vitesse déplacement": "Travel speed", "Accélération impression": "Print acceleration", "Accélération paroi externe": "Outer wall acceleration", "Accélération déplacement": "Travel acceleration", "Diamètre de buse": "Nozzle diameter", "Température buse": "Nozzle temperature", "Température plateau": "Bed temperature", "Débit volumétrique filament": "Maximum filament volumetric speed", "Ratio de débit": "Flow ratio", "Couches supérieures": "Top layers", "Couches inférieures": "Bottom layers", "Ventilation maximale": "Maximum cooling fan", "Éviter de traverser les parois": "Avoid crossing walls", "Détection des parois fines": "Detect thin walls", "Levage Z pendant la rétraction": "Z hop on retraction", "Lissage des surfaces": "Surface ironing", "Supports activés": "Supports enabled", "Ventilateur de refroidissement": "Cooling fan", "Activé": "Enabled", "Désactivé": "Disabled", "Activée": "Enabled", "Désactivée": "Disabled", "Non disponible": "Unavailable", "À vérifier": "Check", "Attention": "Warning", "Critique": "Critical", "Normal": "Normal", "Aucun signal détecté": "No issue detected", "Valeur non reconnue": "Unrecognized value"};
function paText(s){if(paLang==='fr')return s;const local=(PA_V346[paLang]||{})[String(s)]||(PA_V345[paLang]||{})[String(s)]||(PA_RESULT_EXTRA[paLang]||{})[String(s)];return local||paResultText(s)||PA_FIELD_EN[String(s)]||s;}

const PA_RESULT_EN={"Profils actifs": "Active profiles", "Impression : ": "Process: ", "Imprimante : ": "Printer: ", "Filament(s) : ": "Filament(s): ", "Conseil": "Advice", "Grille": "Grid", "Rectiligne": "Rectilinear", "Gyroïde": "Gyroid", "À vérifier selon la pièce": "Check for this model", "À vérifier": "Check", "Activée": "Enabled", "Désactivée": "Disabled", "Activé": "Enabled", "Désactivé": "Disabled", "Compromis hauteur / finition": "Layer height / surface finish trade-off", "Motif de remplissage": "Infill pattern", "Supports activés": "Supports enabled", "La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.": "Grid infill lines intersect within the same layer. Rectilinear reduces intersections; gyroid works well for many shapes.", "En présence de surplombs non imprimables, examiner les supports ou l’orientation.": "For overhangs that cannot be printed without support, consider enabling supports or changing the model orientation.", "Hauteur de 0.28 mm avec buse de 0.4 mm : pour un aspect plus fin, comparer avec environ 0.20 mm, sans obligation de modifier le profil.": "Layer height of 0.28 mm with a 0.4 mm nozzle: for a finer finish, compare with about 0.20 mm. Changing the profile is optional.", "Vérifier dans l’aperçu que les supports sont nécessaires.": "Check in the preview whether supports are necessary.", "Vérifier les surfaces de contact des supports dans l’aperçu.": "Check support contact surfaces in the preview.", "Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.": "If overhangs cannot be printed, consider supports or changing orientation.", "En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.": "If travel marks appear, try this option and compare travel paths in the preview.", "Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.": "If fine details are missing in the preview, try this option; its usefulness depends on the wall generator.", "Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.": "Z-hop can increase travel time; keep it if it prevents collisions.", "Le lissage augmente le temps d’impression : vérifier son utilité sur la pièce.": "Ironing increases print time: check whether it is useful for this model.", "Pour une surface supérieure plane et visible, le lissage peut être testé.": "For a flat visible top surface, consider testing ironing.", "Processus": "Process", "Qualité": "Quality", "Résistance": "Strength", "Vitesse": "Speed", "Hauteur de couche": "Layer height", "Nombre de parois": "Wall loops", "Densité du remplissage": "Infill density", "Paroi externe": "Outer wall", "Paroi interne": "Inner wall", "Remplissage": "Infill", "Surface supérieure": "Top surface", "Première couche": "First layer", "Déplacement": "Travel", "Accélération par défaut": "Default acceleration", "Accélération paroi externe": "Outer wall acceleration", "Couches supérieures": "Top layers", "Couches inférieures": "Bottom layers", "Filament": "Filament", "Avancé": "Advanced", "Vitesse volumétrique maximale": "Maximum volumetric speed", "Ratio de débit": "Flow ratio", "Température de buse": "Nozzle temperature", "Température du plateau": "Bed temperature", "Éviter de traverser les parois": "Avoid crossing walls", "Détecter les parois fines": "Detect thin walls", "Lissage": "Ironing", "Supports": "Supports", "Activer les supports": "Enable supports", "Ordre des parois": "Wall order", "Aucun signal détecté": "No issue detected", "Attention": "Warning", "Critique": "Critical", "Verifier": "Check", "Vérifier": "Check"};
const PA_RESULT_EXTRA={"de":{"Profils actifs":"Aktive Profile","Impression : ":"Druckprofil: ","Imprimante : ":"Drucker: ","Filament(s) : ":"Filamente: ","Conseil":"Hinweis","Grille":"Gitter","Rectiligne":"Geradlinig","Gyroïde":"Gyroid","Motif de remplissage":"Füllmuster","Supports activés":"Stützstrukturen aktiviert","Désactivée":"Deaktiviert","Désactivé":"Deaktiviert","Activée":"Aktiviert","Activé":"Aktiviert","À vérifier selon la pièce":"Je nach Modell prüfen","À vérifier":"Prüfen","Compromis hauteur / finition":"Schichthöhe / Oberflächenqualität","La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.":"Beim Gittermuster kreuzen sich Linien innerhalb derselben Schicht. Geradlinige Füllung reduziert Kreuzungen; Gyroid eignet sich für viele Geometrien.","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"Bei nicht druckbaren Überhängen Stützstrukturen oder eine andere Ausrichtung prüfen.","Processus":"Prozess","Qualité":"Qualität","Résistance":"Festigkeit","Vitesse":"Geschwindigkeit","Hauteur de couche":"Schichthöhe","Nombre de parois":"Wandlinien","Densité du remplissage":"Fülldichte","Paroi externe":"Außenwand","Paroi interne":"Innenwand","Remplissage":"Füllung","Surface supérieure":"Obere Oberfläche","Première couche":"Erste Schicht","Déplacement":"Verfahrbewegung","Couches supérieures":"Obere Schalenschichten","Couches inférieures":"Untere Schalenschichten","Avancé":"Erweitert","Ratio de débit":"Flussverhältnis","Température de buse":"Düsentemperatur","Température du plateau":"Druckbetttemperatur","Supports":"Stützstrukturen","Lissage":"Glätten","Attention":"Warnung","Critique":"Kritisch","Vérifier":"Prüfen","Aucun signal détecté":"Keine Probleme erkannt","Température buse":"Düsentemperatur","Température plateau":"Druckbetttemperatur","Vérifier dans l’aperçu que les supports sont nécessaires.":"In der Vorschau prüfen, ob Stützstrukturen nötig sind.","Le lissage augmente le temps d’impression : vérifier son utilité sur la pièce.":"Glätten verlängert die Druckzeit: Prüfen, ob es für das Modell nötig ist.","Conforme":"In Ordnung","Non disponible":"Nicht verfügbar","Non renseignée":"Nicht angegeben","Non vérifiable":"Nicht überprüfbar","Information":"Information","À examiner":"Prüfen","Optimisation":"Optimierung","Anomalie":"Fehler","Matière du filament":"Filamentmaterial","Débit volumétrique filament":"Volumenstrom des Filaments","Densité de remplissage":"Fülldichte","Ventilation maximale":"Maximale Lüfterdrehzahl","Accélération impression":"Druckbeschleunigung","Filament":"Filament","La densité de remplissage doit être comprise entre 0 et 100 %. Vérifier le profil.":"Die Fülldichte muss zwischen 0 und 100 % liegen. Profil prüfen.","Remplissage très élevé : vérifier si la pièce exige cette densité. Des parois supplémentaires sont souvent plus efficaces pour certaines sollicitations.":"Sehr hohe Fülldichte: Prüfen, ob das Modell sie benötigt. Zusätzliche Wände sind bei manchen Belastungen wirksamer.","Remplissage élevé : essayer 15 à 25 % si la géométrie et la résistance le permettent ; comparer également la consommation de matière.":"Hohe Fülldichte: Falls Geometrie und Festigkeit es zulassen, 15–25 % testen und den Materialverbrauch vergleichen.","Remplissage faible pour un objectif de solidité : vérifier les charges, l’orientation et les parois avant d’augmenter la densité.":"Geringe Fülldichte für hohe Festigkeit: Vor einer Erhöhung Belastung, Ausrichtung und Wände prüfen.","Aucune paroi : vérifier que le modèle et le mode d’impression le permettent.":"Keine Wände: Prüfen, ob Modell und Druckmodus dies zulassen.","Une seule paroi peut être fragile : envisager 2 à 3 parois selon la pièce.":"Eine einzelne Wand kann instabil sein: Je nach Modell 2–3 Wände erwägen.","Pour une pièce sollicitée, envisager 3 à 4 parois ; deux parois ne sont pas une erreur en soi.":"Bei belasteten Teilen 3–4 Wände erwägen; zwei Wände sind nicht grundsätzlich falsch.","Remplissage élevé avec deux parois : envisager une paroi supplémentaire et moins de remplissage, après essai.":"Hohe Fülldichte bei zwei Wänden: Eine zusätzliche Wand und weniger Füllung testen.","La grille peut accumuler du plastique aux croisements. Pour gagner du temps, comparer avec un remplissage rectiligne dans l’aperçu et le temps estimé.":"Gitterfüllung kann an Kreuzungen Material ansammeln. Für kürzere Druckzeiten geradlinige Füllung in Vorschau und Zeitschätzung vergleichen.","Pour une pièce mécanique, comparer grille, cubique et gyroïde selon la direction des efforts ; l’orientation et les parois restent déterminantes.":"Bei mechanischen Teilen Gitter, kubische und Gyroid-Füllung je nach Belastungsrichtung vergleichen; Ausrichtung und Wände bleiben entscheidend.","Les croisements de la grille peuvent créer des surépaisseurs et des contacts avec la buse. Tester le rectiligne ou le gyroïde si ce défaut apparaît.":"Gitterkreuzungen können Materialanhäufungen und Düsenkontakte verursachen. Bei diesem Problem geradlinige oder Gyroid-Füllung testen.","Très peu de couches supérieures : risque de fermeture incomplète au-dessus du remplissage.":"Zu wenige obere Schichten: Die Oberfläche über der Füllung könnte nicht vollständig geschlossen werden.","Très peu de couches inférieures : vérifier la tenue du fond de la pièce.":"Zu wenige untere Schichten: Festigkeit des Bodens prüfen.","Première couche rapide : en cas de défaut d’adhérence, tester une vitesse inférieure. Ce seuil est indicatif, pas constructeur.":"Schnelle erste Schicht: Bei Haftungsproblemen geringere Geschwindigkeit testen. Der Schwellenwert ist nur ein Richtwert.","Ventilation hors plage 0–100 % : vérifier la valeur et son unité.":"Lüfterwert außerhalb von 0–100 %: Wert und Einheit prüfen.","Hauteur supérieure à 80 % du diamètre de buse : réduire la hauteur (règle indicative).":"Schichthöhe über 80 % des Düsendurchmessers: Höhe reduzieren (Richtwert).","Hauteur très faible pour cette buse : impression potentiellement longue sans gain visible sur toutes les pièces.":"Sehr geringe Schichthöhe für diese Düse: Längere Druckzeit ohne sichtbaren Vorteil bei jedem Modell möglich.","Type de matière non renseigné : aucun débit conseillé fiable sans identification du filament.":"Filamentmaterial nicht angegeben: Ohne Materialangabe keine verlässliche Durchflussempfehlung.","Ratio de débit nul ou négatif : vérifier le profil filament.":"Flussverhältnis null oder negativ: Filamentprofil prüfen.","Débit volumétrique non positif ou non exploitable : vérifier le profil filament.":"Volumenstrom null, negativ oder ungültig: Filamentprofil prüfen.","La consigne minimale dépasse la maximale : vérifier le profil.":"Der Mindestwert liegt über dem Höchstwert: Profil prüfen."},"es":{"Profils actifs":"Perfiles activos","Impression : ":"Impresión: ","Imprimante : ":"Impresora: ","Filament(s) : ":"Filamentos: ","Conseil":"Consejo","Motif de remplissage":"Patrón de relleno","Supports activés":"Soportes activados","Grille":"Rejilla","Désactivée":"Desactivada","À vérifier selon la pièce":"Comprobar según la pieza","À vérifier":"Comprobar","Compromis hauteur / finition":"Altura de capa / acabado","Processus":"Proceso","Qualité":"Calidad","Résistance":"Resistencia","Vitesse":"Velocidad","Conforme":"Correcto","Non disponible":"No disponible","Non renseignée":"No indicado","Non vérifiable":"No verificable","Information":"Información","À examiner":"Revisar","Optimisation":"Optimización","Anomalie":"Anomalía","Attention":"Advertencia","Critique":"Crítico","Activé":"Activado","Désactivé":"Desactivado","Activée":"Activada","Matière du filament":"Material del filamento","Débit volumétrique filament":"Caudal volumétrico del filamento","Ratio de débit":"Relación de flujo","Température buse":"Temperatura de la boquilla","Température plateau":"Temperatura de la cama","Nombre de parois":"Número de paredes","Densité de remplissage":"Densidad de relleno","Hauteur de couche":"Altura de capa","Ventilation maximale":"Ventilación máxima","Accélération impression":"Aceleración de impresión","Couches supérieures":"Capas superiores","Couches inférieures":"Capas inferiores","Première couche":"Primera capa","Filament":"Filamento","Rectiligne":"Rectilíneo","Gyroïde":"Giroide","La densité de remplissage doit être comprise entre 0 et 100 %. Vérifier le profil.":"La densidad de relleno debe estar entre el 0 y el 100 %. Revisa el perfil.","Remplissage très élevé : vérifier si la pièce exige cette densité. Des parois supplémentaires sont souvent plus efficaces pour certaines sollicitations.":"Relleno muy alto: comprueba si la pieza necesita esa densidad. Más paredes suelen ser más eficaces ante ciertas cargas.","Remplissage élevé : essayer 15 à 25 % si la géométrie et la résistance le permettent ; comparer également la consommation de matière.":"Relleno alto: prueba entre el 15 y el 25 % si la geometría y la resistencia lo permiten; compara también el consumo.","Remplissage faible pour un objectif de solidité : vérifier les charges, l’orientation et les parois avant d’augmenter la densité.":"Relleno bajo para un objetivo de resistencia: comprueba cargas, orientación y paredes antes de aumentarlo.","Aucune paroi : vérifier que le modèle et le mode d’impression le permettent.":"Sin paredes: comprueba que el modelo y el modo de impresión lo permitan.","Une seule paroi peut être fragile : envisager 2 à 3 parois selon la pièce.":"Una sola pared puede ser frágil: considera 2 o 3 paredes según la pieza.","Pour une pièce sollicitée, envisager 3 à 4 parois ; deux parois ne sont pas une erreur en soi.":"Para una pieza sometida a esfuerzos, considera 3 o 4 paredes; dos paredes no son necesariamente un error.","Remplissage élevé avec deux parois : envisager une paroi supplémentaire et moins de remplissage, après essai.":"Relleno alto con dos paredes: prueba una pared más y menos relleno.","La grille peut accumuler du plastique aux croisements. Pour gagner du temps, comparer avec un remplissage rectiligne dans l’aperçu et le temps estimé.":"La rejilla puede acumular plástico en los cruces. Para ahorrar tiempo, compara el relleno rectilíneo en la vista previa y el tiempo estimado.","Pour une pièce mécanique, comparer grille, cubique et gyroïde selon la direction des efforts ; l’orientation et les parois restent déterminantes.":"Para una pieza mecánica, compara rejilla, cúbico y giroide según la dirección de la carga; la orientación y las paredes siguen siendo decisivas.","Les croisements de la grille peuvent créer des surépaisseurs et des contacts avec la buse. Tester le rectiligne ou le gyroïde si ce défaut apparaît.":"Los cruces de la rejilla pueden crear acumulaciones y rozar la boquilla. Prueba rectilíneo o giroide si ocurre.","Très peu de couches supérieures : risque de fermeture incomplète au-dessus du remplissage.":"Muy pocas capas superiores: la superficie podría no cerrarse por completo sobre el relleno.","Très peu de couches inférieures : vérifier la tenue du fond de la pièce.":"Muy pocas capas inferiores: comprueba la resistencia de la base.","Première couche rapide : en cas de défaut d’adhérence, tester une vitesse inférieure. Ce seuil est indicatif, pas constructeur.":"Primera capa rápida: si hay problemas de adhesión, prueba una velocidad menor. El umbral es orientativo, no del fabricante.","Ventilation hors plage 0–100 % : vérifier la valeur et son unité.":"Ventilación fuera del intervalo 0–100 %: comprueba el valor y la unidad.","Hauteur supérieure à 80 % du diamètre de buse : réduire la hauteur (règle indicative).":"Altura de capa superior al 80 % del diámetro de la boquilla: redúcela (valor orientativo).","Hauteur très faible pour cette buse : impression potentiellement longue sans gain visible sur toutes les pièces.":"Altura de capa muy baja para esta boquilla: la impresión puede tardar mucho más sin una mejora visible en todas las piezas.","Type de matière non renseigné : aucun débit conseillé fiable sans identification du filament.":"Material del filamento no indicado: no se puede recomendar un caudal fiable sin identificarlo.","Ratio de débit nul ou négatif : vérifier le profil filament.":"Relación de flujo nula o negativa: revisa el perfil del filamento.","Débit volumétrique non positif ou non exploitable : vérifier le profil filament.":"Caudal volumétrico nulo, negativo o no válido: revisa el perfil del filamento.","La consigne minimale dépasse la maximale : vérifier le profil.":"El valor mínimo supera al máximo: revisa el perfil.","Vérifier dans l’aperçu que les supports sont nécessaires.":"Comprueba en la vista previa si se necesitan soportes.","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"Si hay voladizos imposibles de imprimir, considera soportes u otra orientación.","Le lissage augmente le temps d’impression : vérifier son utilité sur la pièce.":"El alisado aumenta el tiempo de impresión: comprueba si la pieza lo necesita."},"it":{"Profils actifs":"Profili attivi","Impression : ":"Stampa: ","Imprimante : ":"Stampante: ","Filament(s) : ":"Filamenti: ","Conseil":"Consiglio","Motif de remplissage":"Schema di riempimento","Supports activés":"Supporti attivati","Grille":"Griglia","Désactivée":"Disattivata","À vérifier selon la pièce":"Verificare in base al modello","À vérifier":"Verificare","Compromis hauteur / finition":"Altezza strato / finitura","Processus":"Processo","Qualité":"Qualità","Résistance":"Resistenza","Vitesse":"Velocità","Conforme":"Conforme","Non disponible":"Non disponibile","Non renseignée":"Non specificato","Non vérifiable":"Non verificabile","Information":"Informazione","À examiner":"Da verificare","Optimisation":"Ottimizzazione","Anomalie":"Anomalia","Attention":"Attenzione","Critique":"Critico","Activé":"Attivato","Désactivé":"Disattivato","Activée":"Attivata","Matière du filament":"Materiale del filamento","Débit volumétrique filament":"Portata volumetrica del filamento","Ratio de débit":"Rapporto di flusso","Température buse":"Temperatura ugello","Température plateau":"Temperatura del piano","Nombre de parois":"Numero di pareti","Densité de remplissage":"Densità riempimento","Hauteur de couche":"Altezza strato","Ventilation maximale":"Ventilazione massima","Accélération impression":"Accelerazione di stampa","Couches supérieures":"Strati superiori","Couches inférieures":"Strati inferiori","Première couche":"Primo strato","Filament":"Filamento","Rectiligne":"Rettilineo","Gyroïde":"Giroide","La densité de remplissage doit être comprise entre 0 et 100 %. Vérifier le profil.":"La densità di riempimento deve essere compresa tra 0 e 100 %. Controlla il profilo.","Remplissage très élevé : vérifier si la pièce exige cette densité. Des parois supplémentaires sont souvent plus efficaces pour certaines sollicitations.":"Riempimento molto elevato: verifica se il modello richiede questa densità. Pareti aggiuntive sono spesso più efficaci per alcuni carichi.","Remplissage élevé : essayer 15 à 25 % si la géométrie et la résistance le permettent ; comparer également la consommation de matière.":"Riempimento elevato: prova il 15–25% se geometria e resistenza lo consentono; confronta anche il consumo di materiale.","Remplissage faible pour un objectif de solidité : vérifier les charges, l’orientation et les parois avant d’augmenter la densité.":"Riempimento basso per un obiettivo di resistenza: verifica carichi, orientamento e pareti prima di aumentarlo.","Aucune paroi : vérifier que le modèle et le mode d’impression le permettent.":"Nessuna parete: verifica che il modello e la modalità di stampa lo consentano.","Une seule paroi peut être fragile : envisager 2 à 3 parois selon la pièce.":"Una sola parete può essere fragile: valuta 2–3 pareti in base al modello.","Pour une pièce sollicitée, envisager 3 à 4 parois ; deux parois ne sont pas une erreur en soi.":"Per un pezzo sollecitato, valuta 3–4 pareti; due pareti non sono necessariamente sbagliate.","Remplissage élevé avec deux parois : envisager une paroi supplémentaire et moins de remplissage, après essai.":"Riempimento elevato con due pareti: prova una parete in più e meno riempimento.","La grille peut accumuler du plastique aux croisements. Pour gagner du temps, comparer avec un remplissage rectiligne dans l’aperçu et le temps estimé.":"La griglia può accumulare materiale negli incroci. Per risparmiare tempo, confronta il riempimento rettilineo nell’anteprima e la durata stimata.","Pour une pièce mécanique, comparer grille, cubique et gyroïde selon la direction des efforts ; l’orientation et les parois restent déterminantes.":"Per un pezzo meccanico, confronta griglia, cubico e giroide secondo la direzione dei carichi; orientamento e pareti restano fondamentali.","Les croisements de la grille peuvent créer des surépaisseurs et des contacts avec la buse. Tester le rectiligne ou le gyroïde si ce défaut apparaît.":"Gli incroci della griglia possono creare accumuli e urti con l’ugello. Se accade, prova rettilineo o giroide.","Très peu de couches supérieures : risque de fermeture incomplète au-dessus du remplissage.":"Troppi pochi strati superiori: la superficie potrebbe non chiudersi completamente sopra il riempimento.","Très peu de couches inférieures : vérifier la tenue du fond de la pièce.":"Troppi pochi strati inferiori: verifica la resistenza della base.","Première couche rapide : en cas de défaut d’adhérence, tester une vitesse inférieure. Ce seuil est indicatif, pas constructeur.":"Primo strato veloce: in caso di scarsa adesione, prova una velocità inferiore. La soglia è indicativa, non del produttore.","Ventilation hors plage 0–100 % : vérifier la valeur et son unité.":"Ventilazione fuori dall’intervallo 0–100%: verifica il valore e l’unità.","Hauteur supérieure à 80 % du diamètre de buse : réduire la hauteur (règle indicative).":"Altezza strato oltre l’80% del diametro dell’ugello: riducila (indicazione generale).","Hauteur très faible pour cette buse : impression potentiellement longue sans gain visible sur toutes les pièces.":"Altezza strato molto bassa per questo ugello: stampa potenzialmente più lunga senza benefici visibili su tutti i modelli.","Type de matière non renseigné : aucun débit conseillé fiable sans identification du filament.":"Materiale del filamento non specificato: impossibile consigliare una portata affidabile senza identificarlo.","Ratio de débit nul ou négatif : vérifier le profil filament.":"Rapporto di flusso nullo o negativo: verifica il profilo del filamento.","Débit volumétrique non positif ou non exploitable : vérifier le profil filament.":"Portata volumetrica nulla, negativa o non valida: verifica il profilo del filamento.","La consigne minimale dépasse la maximale : vérifier le profil.":"Il valore minimo supera quello massimo: verifica il profilo.","Vérifier dans l’aperçu que les supports sont nécessaires.":"Verifica nell’anteprima se i supporti sono necessari.","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"In presenza di sporgenze non stampabili, valuta i supporti o modifica l’orientamento.","Le lissage augmente le temps d’impression : vérifier son utilité sur la pièce.":"La stiratura aumenta il tempo di stampa: verifica se serve al modello."},"pt":{"Profils actifs":"Perfis ativos","Impression : ":"Impressão: ","Imprimante : ":"Impressora: ","Filament(s) : ":"Filamentos: ","Conseil":"Recomendação","Motif de remplissage":"Padrão de preenchimento","Supports activés":"Suportes ativados","Grille":"Grade","Désactivée":"Desativada","À vérifier selon la pièce":"Verificar conforme o modelo","À vérifier":"Verificar","Compromis hauteur / finition":"Altura da camada / acabamento","Conforme":"Conforme","Non disponible":"Indisponível","Non renseignée":"Não informado","Non vérifiable":"Não verificável","Information":"Informação","À examiner":"Verificar","Optimisation":"Otimização","Anomalie":"Anomalia","Attention":"Atenção","Critique":"Crítico","Activé":"Ativado","Désactivé":"Desativado","Activée":"Ativada","Matière du filament":"Material do filamento","Débit volumétrique filament":"Fluxo volumétrico do filamento","Ratio de débit":"Razão de fluxo","Température buse":"Temperatura do bico","Température plateau":"Temperatura da mesa","Nombre de parois":"Número de paredes","Densité de remplissage":"Densidade de preenchimento","Hauteur de couche":"Altura da camada","Ventilation maximale":"Ventilação máxima","Accélération impression":"Aceleração de impressão","Couches supérieures":"Camadas superiores","Couches inférieures":"Camadas inferiores","Première couche":"Primeira camada","Filament":"Filamento","Processus":"Processo","Qualité":"Qualidade","Résistance":"Resistência","Vitesse":"Velocidade","Rectiligne":"Retilíneo","Gyroïde":"Giroide","La densité de remplissage doit être comprise entre 0 et 100 %. Vérifier le profil.":"A densidade de preenchimento deve estar entre 0 e 100%. Verifique o perfil.","Remplissage très élevé : vérifier si la pièce exige cette densité. Des parois supplémentaires sont souvent plus efficaces pour certaines sollicitations.":"Preenchimento muito alto: verifique se a peça precisa dessa densidade. Paredes extras costumam ser mais eficazes para certas cargas.","Remplissage élevé : essayer 15 à 25 % si la géométrie et la résistance le permettent ; comparer également la consommation de matière.":"Preenchimento alto: teste 15 a 25% se a geometria e a resistência permitirem; compare também o consumo de material.","Remplissage faible pour un objectif de solidité : vérifier les charges, l’orientation et les parois avant d’augmenter la densité.":"Preenchimento baixo para uma peça resistente: verifique cargas, orientação e paredes antes de aumentar a densidade.","Aucune paroi : vérifier que le modèle et le mode d’impression le permettent.":"Sem paredes: verifique se o modelo e o modo de impressão permitem isso.","Une seule paroi peut être fragile : envisager 2 à 3 parois selon la pièce.":"Uma única parede pode ser frágil: considere 2 a 3 paredes conforme a peça.","Pour une pièce sollicitée, envisager 3 à 4 parois ; deux parois ne sont pas une erreur en soi.":"Para uma peça sujeita a esforços, considere 3 a 4 paredes; duas paredes não são necessariamente um erro.","Remplissage élevé avec deux parois : envisager une paroi supplémentaire et moins de remplissage, après essai.":"Preenchimento alto com duas paredes: teste mais uma parede e menos preenchimento.","La grille peut accumuler du plastique aux croisements. Pour gagner du temps, comparer avec un remplissage rectiligne dans l’aperçu et le temps estimé.":"A grade pode acumular plástico nos cruzamentos. Para economizar tempo, compare o preenchimento retilíneo na prévia e a duração estimada.","Pour une pièce mécanique, comparer grille, cubique et gyroïde selon la direction des efforts ; l’orientation et les parois restent déterminantes.":"Para uma peça mecânica, compare grade, cúbico e giroide conforme a direção das forças; orientação e paredes continuam importantes.","Les croisements de la grille peuvent créer des surépaisseurs et des contacts avec la buse. Tester le rectiligne ou le gyroïde si ce défaut apparaît.":"Os cruzamentos da grade podem criar acúmulos e contato com o bico. Se ocorrer, teste retilíneo ou giroide.","Très peu de couches supérieures : risque de fermeture incomplète au-dessus du remplissage.":"Poucas camadas superiores: a superfície pode não fechar totalmente sobre o preenchimento.","Très peu de couches inférieures : vérifier la tenue du fond de la pièce.":"Poucas camadas inferiores: verifique a resistência da base da peça.","Première couche rapide : en cas de défaut d’adhérence, tester une vitesse inférieure. Ce seuil est indicatif, pas constructeur.":"Primeira camada rápida: se houver falhas de adesão, teste uma velocidade menor. O limite é indicativo, não do fabricante.","Ventilation hors plage 0–100 % : vérifier la valeur et son unité.":"Ventilação fora da faixa de 0–100%: verifique o valor e a unidade.","Hauteur supérieure à 80 % du diamètre de buse : réduire la hauteur (règle indicative).":"Altura da camada acima de 80% do diâmetro do bico: reduza-a (orientação geral).","Hauteur très faible pour cette buse : impression potentiellement longue sans gain visible sur toutes les pièces.":"Altura da camada muito baixa para este bico: a impressão pode demorar mais sem benefício visível em todas as peças.","Type de matière non renseigné : aucun débit conseillé fiable sans identification du filament.":"Material do filamento não informado: não é possível recomendar um fluxo confiável sem identificar o material.","Ratio de débit nul ou négatif : vérifier le profil filament.":"Razão de fluxo zero ou negativa: verifique o perfil do filamento.","Débit volumétrique non positif ou non exploitable : vérifier le profil filament.":"Fluxo volumétrico zero, negativo ou inválido: verifique o perfil do filamento.","La consigne minimale dépasse la maximale : vérifier le profil.":"O valor mínimo excede o máximo: verifique o perfil.","Vérifier dans l’aperçu que les supports sont nécessaires.":"Confira na prévia se os suportes são necessários.","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"Se houver saliências que não possam ser impressas, avalie os suportes ou mude a orientação.","Le lissage augmente le temps d’impression : vérifier son utilité sur la pièce.":"O alisamento aumenta o tempo de impressão: verifique se é necessário."},"zh_CN":{"Profils actifs":"当前配置文件","Impression : ":"打印: ","Imprimante : ":"打印机: ","Filament(s) : ":"耗材: ","Conseil":"建议","Motif de remplissage":"填充图案","Supports activés":"启用支撑","Grille":"网格","Désactivée":"已禁用","À vérifier selon la pièce":"根据模型检查","À vérifier":"检查","Compromis hauteur / finition":"层高与表面质量","Conforme":"正常","Non disponible":"不可用","Non renseignée":"未指定","Non vérifiable":"无法验证","Information":"信息","À examiner":"需要检查","Optimisation":"优化","Anomalie":"异常","Attention":"注意","Critique":"严重","Activé":"已启用","Désactivé":"已禁用","Activée":"已启用","Matière du filament":"耗材材料","Débit volumétrique filament":"耗材体积流量","Ratio de débit":"流量比例","Température buse":"喷嘴温度","Température plateau":"热床温度","Nombre de parois":"墙壁圈数","Densité de remplissage":"填充密度","Hauteur de couche":"层高","Ventilation maximale":"最大风扇速度","Accélération impression":"打印加速度","Couches supérieures":"顶部壳层","Couches inférieures":"底部壳层","Première couche":"首层","Filament":"耗材","Processus":"工艺","Qualité":"质量","Résistance":"强度","Vitesse":"速度","Rectiligne":"直线","Gyroïde":"陀螺","La densité de remplissage doit être comprise entre 0 et 100 %. Vérifier le profil.":"填充密度必须介于 0% 和 100% 之间。请检查配置。","Remplissage très élevé : vérifier si la pièce exige cette densité. Des parois supplémentaires sont souvent plus efficaces pour certaines sollicitations.":"填充密度很高：请确认模型是否需要。对于某些受力情况，增加墙壁圈数通常更有效。","Remplissage élevé : essayer 15 à 25 % si la géométrie et la résistance le permettent ; comparer également la consommation de matière.":"填充密度较高：如果形状和强度允许，可尝试 15%–25%，并比较耗材用量。","Remplissage faible pour un objectif de solidité : vérifier les charges, l’orientation et les parois avant d’augmenter la densité.":"对于强度目标，填充密度偏低：提高密度前请检查载荷、打印方向和墙壁圈数。","Aucune paroi : vérifier que le modèle et le mode d’impression le permettent.":"没有墙壁：请确认模型和打印模式允许这样设置。","Une seule paroi peut être fragile : envisager 2 à 3 parois selon la pièce.":"单层墙壁可能较脆弱：可根据模型考虑使用 2–3 层墙壁。","Pour une pièce sollicitée, envisager 3 à 4 parois ; deux parois ne sont pas une erreur en soi.":"对于承力零件，可考虑 3–4 层墙壁；两层墙壁并非一定错误。","Remplissage élevé avec deux parois : envisager une paroi supplémentaire et moins de remplissage, après essai.":"两层墙壁且填充密度较高：可测试增加一层墙壁并降低填充密度。","La grille peut accumuler du plastique aux croisements. Pour gagner du temps, comparer avec un remplissage rectiligne dans l’aperçu et le temps estimé.":"网格填充可能在交叉处堆积塑料。若要节省时间，请在预览中比较直线填充和预计打印时间。","Pour une pièce mécanique, comparer grille, cubique et gyroïde selon la direction des efforts ; l’orientation et les parois restent déterminantes.":"对于机械零件，请根据受力方向比较网格、立方体和陀螺填充；打印方向和墙壁仍很重要。","Les croisements de la grille peuvent créer des surépaisseurs et des contacts avec la buse. Tester le rectiligne ou le gyroïde si ce défaut apparaît.":"网格交叉处可能堆料并碰到喷嘴。如果出现这种问题，可尝试直线或陀螺填充。","Très peu de couches supérieures : risque de fermeture incomplète au-dessus du remplissage.":"顶部层数过少：填充上方可能无法完全封闭。","Très peu de couches inférieures : vérifier la tenue du fond de la pièce.":"底部层数过少：请检查零件底部强度。","Première couche rapide : en cas de défaut d’adhérence, tester une vitesse inférieure. Ce seuil est indicatif, pas constructeur.":"首层速度较快：若附着不良，请尝试降低速度。该阈值仅供参考，并非厂商限制。","Ventilation hors plage 0–100 % : vérifier la valeur et son unité.":"风扇速度超出 0%–100% 范围：请检查数值和单位。","Hauteur supérieure à 80 % du diamètre de buse : réduire la hauteur (règle indicative).":"层高超过喷嘴直径的 80%：建议降低层高（仅供参考）。","Hauteur très faible pour cette buse : impression potentiellement longue sans gain visible sur toutes les pièces.":"对于该喷嘴，层高很低：打印时间可能大幅增加，但并非所有模型都能获得明显改善。","Type de matière non renseigné : aucun débit conseillé fiable sans identification du filament.":"未指定耗材材料：无法在不知道材料的情况下可靠地推荐流量。","Ratio de débit nul ou négatif : vérifier le profil filament.":"流量比例为零或负数：请检查耗材配置。","Débit volumétrique non positif ou non exploitable : vérifier le profil filament.":"体积流量为零、负数或无效：请检查耗材配置。","La consigne minimale dépasse la maximale : vérifier le profil.":"最小设定值高于最大值：请检查配置。","Vérifier dans l’aperçu que les supports sont nécessaires.":"请在预览中检查是否需要支撑。","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"如果存在无法打印的悬垂部分，请考虑支撑或调整模型方向。","Le lissage augmente le temps d’impression : vérifier son utilité sur la pièce.":"熨烫会增加打印时间：请确认模型是否需要。"}};
const PA_ADVICE_TRANSLATIONS={"de":{"La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.":"Beim Gittermuster kreuzen sich die Linien in derselben Schicht. Geradlinige Füllung verringert Kreuzungen; Gyroid eignet sich für viele Formen.","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"Bei nicht druckbaren Überhängen Stützstrukturen oder eine andere Modellausrichtung prüfen."},"es":{"La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.":"Las líneas del relleno de rejilla se cruzan en una misma capa. El relleno rectilíneo reduce los cruces; el giroide funciona bien con muchas geometrías.","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"Si hay voladizos que no se pueden imprimir, revisa los soportes o la orientación de la pieza."},"it":{"La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.":"Nel riempimento a griglia le linee si incrociano nello stesso strato. Il riempimento rettilineo riduce gli incroci; il giroide è adatto a molte geometrie.","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"In presenza di sporgenze non stampabili, valuta i supporti o modifica l’orientamento del modello."},"pt":{"La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.":"As linhas do preenchimento em grade cruzam-se na mesma camada. O preenchimento retilíneo reduz os cruzamentos; o giroide adapta-se a muitas geometrias.","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"Se existirem saliências que não possam ser impressas, avalie os suportes ou a orientação da peça."},"nl":{"La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.":"Bij rastervulling kruisen lijnen elkaar binnen dezelfde laag. Rechtlijnige vulling vermindert kruisingen; gyroid is geschikt voor veel vormen.","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"Controleer bij niet-printbare overhangen of ondersteuning of een andere modeloriëntatie nodig is."},"pl":{"La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.":"Wypełnienie siatkowe powoduje przecinanie się linii w tej samej warstwie. Wypełnienie prostoliniowe ogranicza przecięcia, a gyroid sprawdza się w wielu kształtach.","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"Jeśli występują zwisy niemożliwe do wydrukowania, sprawdź podpory lub orientację modelu."},"ja":{"La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.":"グリッド充填では同じ層内で線が交差します。直線充填は交差を減らし、ジャイロイド充填はさまざまな形状に適しています。","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"印刷できないオーバーハングがある場合は、サポート材の使用またはモデルの向きを確認してください。"},"zh_CN":{"La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.":"网格填充的线条会在同一层内交叉。直线填充可减少交叉；陀螺填充适用于多种几何形状。","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"如果存在无法直接打印的悬垂部分，请检查是否需要支撑或调整模型方向。"},"en":{"La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.":"Grid infill lines intersect within the same layer. Rectilinear infill reduces intersections; gyroid works well for many shapes.","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"For overhangs that cannot be printed, consider supports or changing the model orientation."}};
const PA_LAYER_ADVICE={"de":"Schichthöhe {a} mm bei einer {b}-mm-Düse: Für eine feinere Oberfläche etwa {c} mm testen. Eine Änderung ist nicht zwingend erforderlich.","es":"Altura de capa de {a} mm con boquilla de {b} mm: para un acabado más fino, prueba aproximadamente {c} mm. No es obligatorio modificar el perfil.","it":"Altezza dello strato di {a} mm con ugello da {b} mm: per una finitura più fine, prova circa {c} mm. Non è necessario modificare il profilo.","pt":"Altura de camada de {a} mm com bico de {b} mm: para um acabamento mais fino, experimente cerca de {c} mm. Não é obrigatório alterar o perfil.","nl":"Laaghoogte {a} mm met een nozzle van {b} mm: probeer voor een fijnere afwerking ongeveer {c} mm. Aanpassen van het profiel is niet verplicht.","pl":"Wysokość warstwy {a} mm przy dyszy {b} mm: dla gładszej powierzchni wypróbuj około {c} mm. Zmiana profilu nie jest obowiązkowa.","ja":"ノズル径{b} mmで積層ピッチが{a} mmです。表面をより滑らかにするには約{c} mmを試してください。設定変更は必須ではありません。","zh_CN":"使用{b} mm喷嘴时层高为{a} mm。若希望表面更细腻，可尝试约{c} mm；不一定需要修改配置。","en":"Layer height {a} mm with a {b} mm nozzle: for a finer finish, try about {c} mm. Changing the profile is optional."};
const PA_DYNAMIC_TEMPLATES=[{"re":"Pour\\ privilégier\\ la\\ finition,\\ essayer\\ une\\ hauteur\\ de\\ couche\\ de\\ ([0-9]+(?:[.,][0-9]+)?)\\ à\\ ([0-9]+(?:[.,][0-9]+)?)\\ mm\\ avec\\ une\\ buse\\ de\\ ([0-9]+(?:[.,][0-9]+)?)\\ mm\\ ;\\ ([0-9]+(?:[.,][0-9]+)?)\\ mm\\ est\\ un\\ compromis\\ qualité/temps\\.\\ La\\ hauteur\\ actuelle\\ de\\ ([0-9]+(?:[.,][0-9]+)?)\\ mm\\ privilégie\\ davantage\\ la\\ rapidité\\.\\ Ces\\ valeurs\\ sont\\ indicatives\\.","translations":{"en":"To prioritize finish, try a layer height of {a}–{b} mm with a {c} mm nozzle; {d} mm balances quality and time. The current {e} mm favors speed. These are guidelines.","de":"Für bessere Oberflächenqualität {a}–{b} mm Schichthöhe bei einer {c}-mm-Düse testen; {d} mm ist ein Kompromiss zwischen Qualität und Zeit. Die aktuellen {e} mm begünstigen die Geschwindigkeit. Nur Richtwerte.","es":"Para mejorar el acabado, prueba una altura de capa de {a} a {b} mm con boquilla de {c} mm; {d} mm equilibra calidad y tiempo. La altura actual de {e} mm prioriza la velocidad. Valores orientativos.","it":"Per migliorare la finitura, prova strati da {a} a {b} mm con un ugello da {c} mm; {d} mm è un compromesso tra qualità e tempo. Gli attuali {e} mm favoriscono la velocità. Valori indicativi.","pt":"Para melhorar o acabamento, teste camadas de {a} a {b} mm com bico de {c} mm; {d} mm equilibra qualidade e tempo. Os {e} mm atuais favorecem a velocidade. Valores indicativos.","zh_CN":"为改善表面效果，可使用 {c} mm 喷嘴测试 {a}–{b} mm 层高；{d} mm 是质量与时间的折中。当前 {e} mm 层高更偏向速度。这些数值仅供参考。"}},{"re":"Épaisseur\\ supérieure\\ ≈\\ ([0-9]+(?:[.,][0-9]+)?)\\ mm\\.\\ Envisager\\ environ\\ 0,6\\ à\\ 1\\ mm\\ selon\\ matériau,\\ portée\\ et\\ finition\\.","translations":{"en":"Top thickness ≈ {a} mm. Consider about 0.6–1 mm depending on material, span and finish.","de":"Obere Schalendicke ≈ {a} mm. Je nach Material, Spannweite und Oberfläche etwa 0,6–1 mm erwägen.","es":"Espesor superior ≈ {a} mm. Considera unos 0,6–1 mm según el material, la distancia entre apoyos y el acabado.","it":"Spessore superiore ≈ {a} mm. Valuta circa 0,6–1 mm in base a materiale, luce e finitura.","pt":"Espessura superior ≈ {a} mm. Considere cerca de 0,6 a 1 mm conforme material, vão e acabamento.","zh_CN":"顶部厚度约为 {a} mm。可根据材料、跨度和表面要求考虑约 0.6–1 mm。"}},{"re":"Température\\ supérieure\\ à\\ la\\ limite\\ machine\\ déclarée\\ \\(([0-9]+(?:[.,][0-9]+)?)\\ °C\\)\\.","translations":{"en":"Temperature exceeds the declared machine limit ({a} °C).","de":"Temperatur überschreitet das angegebene Maschinenlimit ({a} °C).","es":"La temperatura supera el límite declarado de la máquina ({a} °C).","it":"La temperatura supera il limite dichiarato della macchina ({a} °C).","pt":"A temperatura excede o limite declarado da máquina ({a} °C).","zh_CN":"温度超过机器配置中声明的上限（{a} °C）。"}},{"re":"Accélération\\ demandée\\ supérieure\\ à\\ la\\ limite\\ déclarée\\ dans\\ le\\ profil\\ machine\\ \\(([0-9]+(?:[.,][0-9]+)?)\\ mm/s²\\)\\.\\ Vérifier\\ le\\ firmware\\ et\\ le\\ profil\\.","translations":{"en":"Requested acceleration exceeds the machine profile limit ({a} mm/s²). Check firmware and profile.","de":"Geforderte Beschleunigung übersteigt das Maschinenprofil-Limit ({a} mm/s²). Firmware und Profil prüfen.","es":"La aceleración solicitada supera el límite del perfil de máquina ({a} mm/s²). Revisa el firmware y el perfil.","it":"L’accelerazione richiesta supera il limite del profilo macchina ({a} mm/s²). Verifica firmware e profilo.","pt":"A aceleração solicitada excede o limite do perfil da máquina ({a} mm/s²). Verifique o firmware e o perfil.","zh_CN":"请求的加速度超过机器配置限制（{a} mm/s²）。请检查固件和配置。"}}];

// Traductions complémentaires v34.5 : libellés, états et conseils selon les objectifs.
const PA_V345={"en":{"Éviter de traverser les parois":"Avoid crossing walls","Détection des parois fines":"Detect thin walls","Lissage des surfaces":"Surface ironing","Levage Z pendant la rétraction":"Z-hop during retraction","Parois et temps":"Walls and print time","Optimisation conditionnelle":"Conditional optimization","Hauteur configurée :":"Configured height:"," (mode : Aucun lissage)":" (mode: no ironing)"," (mode :":" (mode:"," (nulle)":" (zero)","Valeur à interpréter :":"Value to interpret:","Paroi externe en premier":"Outer wall first","Paroi interne en premier":"Inner wall first","Ordre d’impression des parois":"Wall printing order","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"For significant overhangs, check the preview and orientation before deciding supports are unnecessary.","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"If travel marks appear, consider this option and compare travel paths in the preview.","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"If fine details are missing in the preview, try this option; its usefulness depends on the wall generator.","Pour une surface supérieure plane et visible, le lissage peut être testé.":"For a flat, visible top surface, consider testing ironing.","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"If some overhangs cannot be printed, consider supports or a different orientation.","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"Z-hop can increase travel time; keep it if it prevents collisions."},"de":{"Éviter de traverser les parois":"Wandüberquerungen vermeiden","Détection des parois fines":"Dünne Wände erkennen","Lissage des surfaces":"Oberflächen glätten","Levage Z pendant la rétraction":"Z-Anhebung beim Rückzug","Parois et temps":"Wände und Druckzeit","Optimisation conditionnelle":"Bedingte Optimierung","Hauteur configurée :":"Eingestellte Höhe:"," (mode : Aucun lissage)":" (Modus: kein Glätten)"," (mode :":" (Modus:"," (nulle)":" (null)","Valeur à interpréter :":"Wert prüfen:","Paroi externe en premier":"Außenwand zuerst","Paroi interne en premier":"Innenwand zuerst","Ordre d’impression des parois":"Reihenfolge der Wände","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"Bei großen Überhängen Vorschau und Ausrichtung prüfen, bevor Stützen als unnötig gelten.","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"Bei Fahrspuren diese Option erwägen und die Verfahrwege in der Vorschau vergleichen.","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"Fehlen feine Details in der Vorschau, diese Option testen; der Nutzen hängt vom Wandgenerator ab.","Pour une surface supérieure plane et visible, le lissage peut être testé.":"Für eine ebene, sichtbare Oberseite kann Glätten getestet werden.","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"Wenn Überhänge nicht druckbar sind, Stützen oder eine andere Ausrichtung prüfen.","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"Die Z-Anhebung kann die Verfahrzeit verlängern; beibehalten, wenn sie Kollisionen verhindert."},"es":{"Éviter de traverser les parois":"Evitar cruzar paredes","Détection des parois fines":"Detectar paredes finas","Lissage des surfaces":"Alisado de superficies","Levage Z pendant la rétraction":"Elevación Z durante la retracción","Parois et temps":"Paredes y tiempo","Optimisation conditionnelle":"Optimización condicional","Hauteur configurée :":"Altura configurada:"," (mode : Aucun lissage)":" (modo: sin alisado)"," (mode :":" (modo:"," (nulle)":" (cero)","Valeur à interpréter :":"Valor por interpretar:","Paroi externe en premier":"Pared exterior primero","Paroi interne en premier":"Pared interior primero","Ordre d’impression des parois":"Orden de impresión de paredes","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"Para voladizos importantes, revisa la vista previa y la orientación antes de descartar los soportes.","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"Si aparecen marcas de desplazamiento, considera esta opción y compara las trayectorias en la vista previa.","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"Si faltan detalles finos en la vista previa, prueba esta opción; su utilidad depende del generador de paredes.","Pour une surface supérieure plane et visible, le lissage peut être testé.":"Para una superficie superior plana y visible, puedes probar el alisado.","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"Si algunos voladizos no se pueden imprimir, revisa los soportes o la orientación.","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"La elevación Z puede aumentar el tiempo de desplazamiento; mantenla si evita colisiones."},"it":{"Éviter de traverser les parois":"Evitare di attraversare le pareti","Détection des parois fines":"Rileva pareti sottili","Lissage des surfaces":"Stiratura delle superfici","Levage Z pendant la rétraction":"Sollevamento Z durante la retrazione","Parois et temps":"Pareti e tempo","Optimisation conditionnelle":"Ottimizzazione condizionata","Hauteur configurée :":"Altezza impostata:"," (mode : Aucun lissage)":" (modalità: nessuna stiratura)"," (mode :":" (modalità:"," (nulle)":" (zero)","Valeur à interpréter :":"Valore da interpretare:","Paroi externe en premier":"Parete esterna per prima","Paroi interne en premier":"Parete interna per prima","Ordre d’impression des parois":"Ordine di stampa delle pareti","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"Per sporgenze importanti, controlla anteprima e orientamento prima di escludere i supporti.","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"Se compaiono segni di spostamento, valuta questa opzione e confronta i percorsi nell’anteprima.","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"Se mancano dettagli sottili nell’anteprima, prova questa opzione; l’utilità dipende dal generatore di pareti.","Pour une surface supérieure plane et visible, le lissage peut être testé.":"Per una superficie superiore piana e visibile, puoi provare la stiratura.","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"Se alcune sporgenze non sono stampabili, valuta i supporti o un diverso orientamento.","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"Il sollevamento Z può aumentare i tempi di spostamento; mantienilo se evita collisioni."},"pt":{"Éviter de traverser les parois":"Evitar cruzar paredes","Détection des parois fines":"Detectar paredes finas","Lissage des surfaces":"Alisamento de superfícies","Levage Z pendant la rétraction":"Elevação Z durante a retração","Parois et temps":"Paredes e tempo","Optimisation conditionnelle":"Otimização condicional","Hauteur configurée :":"Altura configurada:"," (mode : Aucun lissage)":" (modo: sem alisamento)"," (mode :":" (modo:"," (nulle)":" (zero)","Valeur à interpréter :":"Valor a interpretar:","Paroi externe en premier":"Parede externa primeiro","Paroi interne en premier":"Parede interna primeiro","Ordre d’impression des parois":"Ordem de impressão das paredes","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"Para balanços acentuados, confira a prévia e a orientação antes de dispensar os suportes.","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"Se aparecerem marcas de deslocamento, considere esta opção e compare os trajetos na prévia.","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"Se faltarem detalhes finos na prévia, teste esta opção; a utilidade depende do gerador de paredes.","Pour une surface supérieure plane et visible, le lissage peut être testé.":"Para uma superfície superior plana e visível, experimente o alisamento.","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"Se alguns balanços não puderem ser impressos, avalie os suportes ou a orientação.","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"A elevação Z pode aumentar o tempo de deslocamento; mantenha-a se evitar colisões."},"zh_CN":{"Éviter de traverser les parois":"避免跨越墙壁","Détection des parois fines":"检测薄壁","Lissage des surfaces":"表面熨烫","Levage Z pendant la rétraction":"回抽时 Z 抬升","Parois et temps":"墙壁与打印时间","Optimisation conditionnelle":"有条件优化","Hauteur configurée :":"设定高度："," (mode : Aucun lissage)":"（模式：不熨烫）"," (mode :":"（模式："," (nulle)":"（零）","Valeur à interpréter :":"待解释的值：","Paroi externe en premier":"先打印外墙","Paroi interne en premier":"先打印内墙","Ordre d’impression des parois":"墙壁打印顺序","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"对于较大的悬垂结构，请先检查预览和方向，再判断是否无需支撑。","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"如果出现空驶痕迹，可考虑启用此选项并在预览中比较移动路径。","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"如果预览中缺少细节，可尝试此选项；效果取决于墙壁生成器。","Pour une surface supérieure plane et visible, le lissage peut être testé.":"对于平坦且可见的顶面，可以尝试熨烫。","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"如果某些悬垂结构无法打印，请考虑支撑或调整方向。","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"Z 抬升可能增加空驶时间；如果能避免碰撞，建议保留。"}};

const PA_V346={"en":{"Éviter de traverser les parois":"Avoid crossing walls","Détection des parois fines":"Detect thin walls","Lissage des surfaces":"Surface ironing","Levage Z pendant la rétraction":"Z-hop during retraction","Parois et temps":"Walls and print time","Optimisation conditionnelle":"Conditional optimization","Aucun lissage":"No ironing","Hauteur configurée : ":"Configured height: ","Paroi externe":"Outer wall","Paroi interne":"Inner wall","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"For significant overhangs, check the preview and orientation before deciding that supports are unnecessary.","Pour une surface supérieure plane et visible, le lissage peut être testé.":"For a flat, visible top surface, consider testing ironing.","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"If travel marks appear, try this option and compare travel paths in the preview.","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"If fine details are missing in the preview, try this option; its usefulness depends on the wall generator.","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"If overhangs cannot be printed, consider supports or changing orientation.","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"Z-hop may increase travel time; keep it if it prevents collisions."},"de":{"Éviter de traverser les parois":"Wandkreuzungen vermeiden","Détection des parois fines":"Dünne Wände erkennen","Lissage des surfaces":"Oberflächen glätten","Levage Z pendant la rétraction":"Z-Hop beim Rückzug","Parois et temps":"Wände und Druckzeit","Optimisation conditionnelle":"Bedingte Optimierung","Aucun lissage":"Kein Glätten","Hauteur configurée : ":"Eingestellte Höhe: ","Paroi externe":"Außenwand","Paroi interne":"Innenwand","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"Bei starken Überhängen Vorschau und Ausrichtung prüfen, bevor Stützstrukturen als unnötig gelten.","Pour une surface supérieure plane et visible, le lissage peut être testé.":"Bei einer ebenen, sichtbaren Oberseite kann Glätten getestet werden.","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"Bei Verfahrspuren diese Option testen und die Bewegungswege in der Vorschau vergleichen.","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"Fehlen feine Details in der Vorschau, diese Option testen; der Nutzen hängt vom Wandgenerator ab.","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"Sind Überhänge nicht druckbar, Stützstrukturen oder eine andere Ausrichtung prüfen.","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"Z-Hop kann die Verfahrzeit verlängern; beibehalten, wenn er Kollisionen verhindert."},"es":{"Éviter de traverser les parois":"Evitar cruzar paredes","Détection des parois fines":"Detectar paredes finas","Lissage des surfaces":"Alisado de superficies","Levage Z pendant la rétraction":"Elevación Z durante la retracción","Parois et temps":"Paredes y tiempo de impresión","Optimisation conditionnelle":"Optimización condicional","Aucun lissage":"Sin alisado","Hauteur configurée : ":"Altura configurada: ","Paroi externe":"Pared exterior","Paroi interne":"Pared interior","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"Para voladizos importantes, revisa la vista previa y la orientación antes de concluir que los soportes no son necesarios.","Pour une surface supérieure plane et visible, le lissage peut être testé.":"Para una superficie superior plana y visible, prueba el alisado.","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"Si aparecen marcas de desplazamiento, prueba esta opción y compara las trayectorias en la vista previa.","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"Si faltan detalles finos en la vista previa, prueba esta opción; su utilidad depende del generador de paredes.","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"Si los voladizos no se pueden imprimir, considera los soportes o cambia la orientación.","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"La elevación Z puede aumentar el tiempo de desplazamiento; mantenla si evita colisiones."},"it":{"Éviter de traverser les parois":"Evita di attraversare le pareti","Détection des parois fines":"Rilevamento delle pareti sottili","Lissage des surfaces":"Stiratura delle superfici","Levage Z pendant la rétraction":"Sollevamento Z durante la retrazione","Parois et temps":"Pareti e tempo di stampa","Optimisation conditionnelle":"Ottimizzazione condizionata","Aucun lissage":"Nessuna stiratura","Hauteur configurée : ":"Altezza impostata: ","Paroi externe":"Parete esterna","Paroi interne":"Parete interna","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"Per sporgenze importanti, controlla anteprima e orientamento prima di concludere che i supporti non servono.","Pour une surface supérieure plane et visible, le lissage peut être testé.":"Per una superficie superiore piana e visibile, valuta la stiratura.","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"Se compaiono segni di spostamento, prova questa opzione e confronta i percorsi nell’anteprima.","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"Se mancano dettagli sottili nell’anteprima, prova questa opzione; l’utilità dipende dal generatore di pareti.","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"Se le sporgenze non sono stampabili, valuta i supporti o modifica l’orientamento.","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"Il sollevamento Z può aumentare il tempo di spostamento; mantienilo se evita collisioni."},"pt":{"Éviter de traverser les parois":"Evitar cruzar paredes","Détection des parois fines":"Detectar paredes finas","Lissage des surfaces":"Alisamento de superfícies","Levage Z pendant la rétraction":"Elevação Z durante a retração","Parois et temps":"Paredes e tempo de impressão","Optimisation conditionnelle":"Otimização condicional","Aucun lissage":"Sem alisamento","Hauteur configurée : ":"Altura configurada: ","Paroi externe":"Parede externa","Paroi interne":"Parede interna","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"Para balanços acentuados, confira a prévia e a orientação antes de concluir que os suportes são desnecessários.","Pour une surface supérieure plane et visible, le lissage peut être testé.":"Para uma superfície superior plana e visível, considere testar o alisamento.","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"Se surgirem marcas de deslocamento, teste esta opção e compare os trajetos na prévia.","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"Se faltarem detalhes finos na prévia, teste esta opção; sua utilidade depende do gerador de paredes.","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"Se os balanços não puderem ser impressos, considere suportes ou outra orientação.","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"A elevação Z pode aumentar o tempo de deslocamento; mantenha-a se evitar colisões."},"zh_CN":{"Éviter de traverser les parois":"避免跨越墙壁","Détection des parois fines":"检测薄壁","Lissage des surfaces":"表面熨烫","Levage Z pendant la rétraction":"回抽时 Z 轴抬升","Parois et temps":"墙壁与打印时间","Optimisation conditionnelle":"有条件优化","Aucun lissage":"不熨烫","Hauteur configurée : ":"设置高度：","Paroi externe":"外墙","Paroi interne":"内墙","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"对于较大的悬垂结构，请先检查预览和模型方向，再判断是否无需支撑。","Pour une surface supérieure plane et visible, le lissage peut être testé.":"对于平整且可见的顶面，可以尝试熨烫。","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"如果出现移动痕迹，请尝试此选项并在预览中比较移动路径。","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"如果预览中缺少细节，请尝试此选项；效果取决于墙壁生成器。","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"如果悬垂结构无法打印，请考虑添加支撑或调整模型方向。","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"Z 轴抬升可能增加移动时间；若能避免碰撞则可以保留。"}};
// ---- English completion layer: fills every French result string the dictionaries above do not cover. ----
// Exact strings, numeric templates and sub-strings; the author's own English entries always take precedence.
const PA_EN_FIX={"exact":{"Même principe que Print Calculator : fournir un vrai fichier SVG local.":"Same approach as Print Calculator: provide a real local SVG file.","Interne → externe":"Inner → outer","Externe → interne":"Outer → inner","Interne → externe → interne":"Inner → outer → inner","Activé":"Enabled","Désactivé":"Disabled","Convertit les booléens du profil sans confondre une valeur inconnue avec False.":"Converts the profile’s booleans without mistaking an unknown value for False.","Interprète le type de lissage OrcaSlicer sans faux positif sur 'no ironing'.":"Interprets the OrcaSlicer ironing type without a false positive on 'no ironing'.","Conseils non intrusifs fondés sur la configuration active résolue.":"Non-intrusive advice based on the resolved active configuration.","V32.4 : vérifications croisées contextuelles sans supposer la géométrie.":"V32.4: contextual cross-checks without assuming the geometry.","Démarrage":"Start","Fin":"End","Changement de filament":"Filament change","Démarrage filament":"Filament start","Fin filament":"Filament end","Audit statique conservateur des scripts personnalisés, sans exécution.\n\n    Ne prétend pas interpréter les macros propriétaires ni le G-code généré\n    après découpage. Les limites machine ne sont utilisées que si explicites.\n    ":"Conservative static audit of custom scripts, without execution.\n\n    Does not claim to interpret proprietary macros or the G-code generated\n    after slicing. Machine limits are only used when explicit.\n    ","Hauteur de couche":"Layer height","Nombre de parois":"Wall loops","Densité de remplissage":"Infill density","Motif de remplissage":"Infill pattern","Vitesse paroi externe":"Outer wall speed","Vitesse paroi interne":"Inner wall speed","Vitesse remplissage":"Infill speed","Vitesse remplissage plein":"Solid infill speed","Vitesse surface supérieure":"Top surface speed","Vitesse première couche":"First layer speed","Vitesse déplacement":"Travel speed","Accélération impression":"Print acceleration","Accélération paroi externe":"Outer wall acceleration","Accélération déplacement":"Travel acceleration","Diamètre de buse":"Nozzle diameter","Température buse":"Nozzle temperature","Température plateau":"Bed temperature","Débit volumétrique filament":"Filament volumetric flow","Ratio de débit":"Flow ratio","Couches supérieures":"Top shell layers","Couches inférieures":"Bottom shell layers","Ventilation maximale":"Maximum fan speed","Non disponible":"Not available","Éviter de traverser les parois":"Avoid crossing walls","Détection des parois fines":"Thin wall detection","Supports activés":"Supports enabled","Levage Z pendant la rétraction":"Z lift during retraction","Lissage des surfaces":"Surface ironing","Ventilateur de refroidissement":"Cooling fan","Rétraction":"Retraction","Ordre d’impression des parois":"Wall printing order","PLA standard":"Standard PLA","PETG standard":"Standard PETG","ABS standard":"Standard ABS","ASA standard":"Standard ASA","TPU souple":"Flexible TPU","Conforme":"OK","À vérifier":"To check","Activée":"Enabled","Désactivée":"Disabled","Le lissage augmente le temps d’impression : vérifier son utilité sur la pièce.":"Ironing increases print time: check whether it is useful for the part.","Consigne hors de la plage 0–100 % : vérifier le profil.":"Setpoint outside the 0–100% range: check the profile.","Si des marques de déplacement apparaissent, essayer d’activer cette option ; vérifier l’aperçu des trajectoires.":"If travel marks appear, try enabling this option; check the path preview.","Cette option peut rallonger les déplacements : comparer les temps estimés avant de la désactiver.":"This option can lengthen travel moves: compare the estimated times before disabling it.","Si des détails fins disparaissent dans l’aperçu, tester cette option et comparer les trajectoires.":"If fine details disappear in the preview, test this option and compare the paths.","Vérifier que cette option est nécessaire pour la géométrie ; elle peut générer de petits mouvements.":"Check that this option is needed for the geometry; it can generate small movements.","Contrôler les surplombs dans l’aperçu : supprimer uniquement les supports inutiles.":"Check the overhangs in the preview: remove only the unnecessary supports.","Si les supports consomment beaucoup de filament, vérifier les surplombs et comparer une autre orientation ; ne retirer que les supports inutiles.":"If the supports use a lot of filament, check the overhangs and compare another orientation; remove only the unnecessary supports.","Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.":"For significant overhangs, check the preview and the orientation before concluding that supports are unnecessary.","Type de matière non renseigné : aucun débit conseillé fiable sans identification du filament.":"Material type not specified: no reliable recommended flow without identifying the filament.","Optimisation possible":"Possible optimization","Calibration conseillée":"Calibration advised","Non vérifiable":"Cannot be verified","Anomalie":"Anomaly","Ratio de débit nul ou négatif : vérifier le profil filament.":"Flow ratio is zero or negative: check the filament profile.","Calibration prioritaire":"Calibration priority","Matière du filament":"Filament material","Compromis hauteur / finition":"Height / finish trade-off","Temps et hauteur de couche":"Time and layer height","Temps et remplissage":"Time and infill","Motif et temps":"Pattern and time","Parois et temps":"Walls and time","Remplissage et temps":"Infill and time","Temps et épaisseur supérieure":"Time and top thickness","Hauteur de couche et débit":"Layer height and flow","Cohésion des couches":"Layer cohesion","Compromis parois / remplissage":"Walls / infill trade-off","Résistance et matière":"Strength and material","Épaisseur du fond":"Bottom thickness","Accélération des contours":"Outline acceleration","Qualité des dessus":"Top surface quality","Fines couches et dessus":"Thin layers and top surface","Dessus et faible remplissage":"Top surface and low infill","Finition des parois":"Wall finish","Surface supérieure":"Top surface","Adhérence première couche":"First layer adhesion","Fermeture des surfaces":"Surface closure","Supports et rapidité":"Supports and speed","Lissage et temps":"Ironing and time","Refroidissement":"Cooling","Refroidissement et matière":"Cooling and material","Les supports peuvent rallonger l’impression. Conseil : vérifiez dans l’aperçu s’ils sont nécessaires ou si une autre orientation permet de les réduire.":"Supports can lengthen the print. Tip: check in the preview whether they are necessary or whether another orientation can reduce them.","Incohérence":"Inconsistency","La rétraction ne peut pas avoir une longueur négative. Conseil : corrigez ce réglage dans le profil.":"Retraction cannot have a negative length. Tip: correct this setting in the profile.","Largeur et diamètre de buse":"Width and nozzle diameter","Incohérence possible":"Possible inconsistency","Première couche et buse":"First layer and nozzle","Matière et solidité":"Material and strength","Un dessus très épais peut allonger l’impression. Conseil : si cette surface n’a pas besoin d’être résistante, testez moins de couches supérieures en vérifiant qu’aucun trou n’apparaît.":"A very thick top can lengthen the print. Tip: if this surface does not need to be strong, test fewer top layers, checking that no holes appear.","Des couches plus épaisses ne rendent pas toujours l’impression plus rapide : le filament peut atteindre sa limite de débit. Conseil : comparez le temps estimé et la vue « débit volumétrique » dans l’aperçu.":"Thicker layers do not always make the print faster: the filament may reach its flow limit. Tip: compare the estimated time and the \"volumetric flow\" view in the preview.","Clé absente de la configuration active.":"Key missing from the active configuration.","À vérifier selon la pièce":"Check depending on the part","Valeur à interpréter : ":"Value to interpret: ","Clé source : ":"Source key: ",". Cette valeur ne correspond pas à un booléen reconnu.":". This value does not match a recognized boolean.","En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.":"If travel marks appear, consider this option, then compare the paths in the preview.","Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.":"If fine details are missing in the preview, try this option; its usefulness depends on the wall generator.","Valeur non reconnue":"Unrecognized value"," (mode : ":" (mode: ","Pour une surface supérieure plane et visible, le lissage peut être testé.":"For a flat, visible top surface, ironing can be tested.","Vérifier dans l’aperçu que les supports sont nécessaires.":"Check in the preview that the supports are necessary.","Vérifier les surfaces de contact des supports dans l’aperçu.":"Check the support contact surfaces in the preview.","En présence de surplombs non imprimables, examiner les supports ou l’orientation.":"If there are overhangs that cannot be printed, review the supports or the orientation.","Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.":"If overhangs cannot be printed, review the supports or the orientation.","Consignes : ":"Setpoints: ","Valeur : ":"Value: ","La consigne minimale dépasse la maximale : vérifier le profil.":"The minimum setpoint exceeds the maximum: check the profile.","Longueur configurée : ":"Configured length: "," ; rétraction firmware activée":"; firmware retraction enabled","Débit volumétrique non positif ou non exploitable : vérifier le profil filament.":"Volumetric flow is non-positive or unusable: check the filament profile.","Pas de plage indicative disponible pour ":"No indicative range available for "," : consulter la fiche fabricant et calibrer le débit maximal.":": consult the manufacturer datasheet and calibrate the maximum flow.","À confirmer":"To confirm","Débit configuré : ":"Configured flow: "," mm³/s, inférieur au repère indicatif de ":" mm³/s, below the indicative reference of "," mm³/s pour ":" mm³/s for ",". Cela ne présente pas de risque de sous-extrusion en soi, mais peut ralentir fortement l’impression. Si la qualité est bonne, essayer progressivement ":". This does not in itself present a risk of under-extrusion, but can slow the print down considerably. If quality is good, gradually try "," mm³/s, puis calibrer le débit maximal pour ce filament, cette température et cette tête d’impression. Ne pas augmenter sans vérification.":" mm³/s, then calibrate the maximum flow for this filament, this temperature and this print head. Do not increase it without checking."," mm³/s. Pour ":" mm³/s. For ",", plage de départ conseillée : ":", recommended starting range: "," mm³/s (repère indicatif, non constructeur). Essayer au plus ":" mm³/s (indicative reference, not from the manufacturer). Try at most "," mm³/s en attendant une calibration du débit maximal, puis retenir la valeur mesurée pour ce filament, cette température et cette tête d’impression.":" mm³/s while waiting for a maximum flow calibration, then keep the value measured for this filament, this temperature and this print head.","Ratio configuré : ":"Configured ratio: ",". Valeur très éloignée de 1,00 ; risque de sous-extrusion ou de surextrusion. Vérifier les unités et réaliser une calibration du ratio de débit dans OrcaSlicer avant de modifier le profil.":". Value very far from 1.00; risk of under-extrusion or over-extrusion. Check the units and perform a flow ratio calibration in OrcaSlicer before changing the profile.",", inférieur au repère indicatif 0,95–1,05. Cela peut être normal après calibration. Si aucune calibration n’a été faite, tester le ratio de débit avec le filament et la température actifs ; ne pas augmenter automatiquement.":", below the indicative reference of 0.95–1.05. This may be normal after calibration. If no calibration has been done, test the flow ratio with the active filament and temperature; do not increase it automatically.",", supérieur au repère indicatif 0,95–1,05. Cela peut être normal après calibration. Si aucune calibration n’a été faite, vérifier le ratio de débit pour éviter une éventuelle surextrusion ; ne pas diminuer automatiquement.":", above the indicative reference of 0.95–1.05. This may be normal after calibration. If no calibration has been done, check the flow ratio to avoid possible over-extrusion; do not decrease it automatically.","profil":"profile","Non renseignée":"Not specified","Paroi externe (":"Outer wall ("," mm/s) plus rapide que la paroi interne (":" mm/s) faster than the inner wall ("," mm/s). Conseil : ralentissez légèrement la paroi externe pour améliorer l’aspect, puis comparez sur une pièce test.":" mm/s). Tip: slow the outer wall down slightly to improve appearance, then compare on a test part.","Surface supérieure à ":"Top surface at "," mm/s contre ":" mm/s versus "," mm/s pour la paroi externe : le dessus peut présenter davantage de marques. Conseil : essayez de réduire la vitesse du dessus et comparez le résultat.":" mm/s for the outer wall: the top may show more marks. Tip: try reducing the top surface speed and compare the result.","Première couche à ":"First layer at "," mm/s, plus rapide que la paroi externe (":" mm/s, faster than the outer wall ("," mm/s). une première couche trop rapide peut moins bien adhérer. Conseil : ralentissez-la si vous constatez un décollement.":" mm/s). A first layer that is too fast may adhere less well. Tip: slow it down if you notice lifting.","Épaisseur de dessus ≈ ":"Top thickness ≈ "," mm sur remplissage ":" mm over "," %. le dessus risque de laisser voir le remplissage. Conseil : ajoutez des couches supérieures si des trous ou des marques apparaissent.":"% infill. The top may let the infill show through. Tip: add top layers if holes or marks appear.","Le lissage peut augmenter le temps d’impression. Conseil : comparez la durée avec et sans lissage et désactivez-le si la finition du dessus est inutile.":"Ironing can increase print time. Tip: compare the duration with and without ironing and disable it if the top finish is unnecessary.","Consigne minimale (":"Minimum setpoint ("," %) supérieure à la maximale (":"%) is higher than the maximum ("," %) : contrôler le profil filament.":"%): check the filament profile.","Ventilation minimale de ":"Minimum fan speed of "," % avec ":"% with "," : vérifier la compatibilité avec le filament et le risque de déformation. Les ventilateurs de ponts peuvent avoir d’autres consignes.":": check compatibility with the filament and the risk of warping. Bridge fans may have other setpoints.","Rétraction de ":"Retraction of "," mm : valeur élevée pour de nombreuses configurations ; vérifier le type d’extrudeur et les tests de rétraction, sans appliquer une valeur universelle.":" mm: a high value for many setups; check the extruder type and retraction tests, without applying a universal value.","Largeur de ligne ":"Line width "," mm pour une buse de ":" mm for a "," mm : vérifier la largeur choisie et la compatibilité avec le profil.":" mm nozzle: check the chosen width and its compatibility with the profile.","Première couche de ":"First layer of "," mm avec une buse de ":" mm with a "," mm : hauteur supérieure au repère indicatif de 80 % du diamètre. Vérifier l’adhérence et la calibration.":" mm nozzle: height above the indicative reference of 80% of the diameter. Check adhesion and calibration.","Le dessus mesure environ ":"The top is about "," mm, mais le remplissage est de ":" mm thick, but infill is "," %. Une grande portée entre lignes de remplissage peut marquer le dessus : vérifier les pontages dans l’aperçu.":"%. A large span between infill lines can mark the top: check the bridges in the preview."," parois et ":" walls and "," % de remplissage : forte consommation potentielle. La résistance dépend aussi de l’orientation, de l’adhésion des couches et du sens de charge ; tester une éprouvette avant d’augmenter davantage la matière.":"% infill: potentially high consumption. Strength also depends on orientation, layer adhesion and load direction; test a specimen before adding more material.","Couches fines (":"Thin layers ("," mm) mais surface supérieure à ":" mm) but top surface at "," mm/s pour la paroi externe : la finition du dessus peut limiter le gain de qualité. Comparer une vitesse supérieure plus modérée sur une pièce test.":" mm/s for the outer wall: the top finish may limit the quality gain. Compare a more moderate top surface speed on a test part.","Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.":"Lifting can increase travel time; keep it if it prevents collisions.","Ventilation permanente : ":"Always-on fan: "," : ":": ","Cette option ne suffit pas à déterminer les vitesses réelles du ventilateur.":"This option alone cannot determine the actual fan speeds.","Longueur de rétraction non numérique.":"Non-numeric retraction length."," ; rétraction firmware désactivée":"; firmware retraction disabled","La longueur de rétraction n’est pas exposée : impossible de conclure sur la rétraction effective.":"The retraction length is not exposed: unable to conclude about effective retraction.","Ordre configuré : ":"Configured order: ","Paroi externe en premier":"Outer wall first","Paroi interne en premier":"Inner wall first","Optimisation conditionnelle":"Conditional optimization"," mm³/s. Le repère pour ":" mm³/s. The reference for "," est ":" is "," mm³/s, mais ce filament semble haute vitesse : ne pas lui appliquer ce plafond standard. Débit conseillé : celui mesuré par calibration sur cette imprimante, à la température utilisée, ou la valeur documentée par le fabricant.":" mm³/s, but this filament appears to be high-speed: do not apply this standard ceiling to it. Recommended flow: the one measured by calibration on this printer, at the temperature used, or the value documented by the manufacturer."," mm³/s, inférieur même au repère standard de ":" mm³/s, even below the standard reference of ",". Ce filament semble haute vitesse : sa plage réelle doit être confirmée par le fabricant ou par calibration. Un débit aussi bas peut ralentir l’impression, sans être dangereux.":". This filament appears to be high-speed: its actual range must be confirmed by the manufacturer or by calibration. A flow this low can slow the print down, without being dangerous."," % de remplissage : selon les efforts, essayer une paroi supplémentaire et un remplissage plus modéré, puis comparer temps et résistance.":"% infill: depending on the loads, try an extra wall and a more moderate infill, then compare time and strength.","Hauteur de ":"Height of "," mm avec buse de ":" mm with a "," mm : pour un aspect plus fin, comparer avec environ ":" mm nozzle: for a finer look, compare with about "," mm, sans obligation de modifier le profil.":" mm, with no obligation to change the profile.","Finition des surfaces":"Surface finish","Contrôles croisés":"Cross checks","Aucun signal détecté":"No signal detected","Aucune incohérence démontrable avec les paramètres croisés disponibles. Cela ne valide pas la géométrie ni la calibration du filament.":"No demonstrable inconsistency with the available cross parameters. This does not validate the geometry or the filament calibration.","Corriger la valeur numérique.":"Correct the numeric value.","Indisponible":"Unavailable","Profil actif":"Active profile","Hauteur non numérique (clé : ":"Non-numeric height (key: ","Hauteur négative inhabituelle : vérifier le profil.":"Unusual negative height: check the profile.","oui":"yes","non":"no","La densité de remplissage doit être comprise entre 0 et 100 %. Vérifier le profil.":"Infill density must be between 0 and 100%. Check the profile."," mm/s et paroi externe à ":" mm/s and outer wall at "," mm/s : si des marques apparaissent sur le dessus, tester une vitesse supérieure plus proche de celle des parois.":" mm/s: if marks appear on the top, try a top surface speed closer to the wall speed.","Accélération externe ":"Outer acceleration "," mm/s² égale ou supérieure à celle d’impression (":" mm/s² equal to or higher than the print acceleration ("," mm/s²) : si des vibrations marquent les contours, essayer une accélération externe plus basse après calibration.":" mm/s²): if vibrations mark the outlines, try a lower outer acceleration after calibration."," % de remplissage et ":"% infill and "," couches supérieures : vérifier dans l’aperçu la portée des pontages sous les surfaces visibles ; renforcer le dessus si des creux apparaissent.":" top layers: check the bridge spans under visible surfaces in the preview; reinforce the top if dips appear.","Ligne ":"Line ","paramètre ":"malformed "," mal formé dans ":" parameter in ","Utiliser une avance strictement positive en mm/min.":"Use a strictly positive feed rate in mm/min.","Vérifier la quantité extrudée et le mode M83 ; certains scripts de purge sont spécifiques.":"Check the extruded amount and M83 mode; some purge scripts are specific.","extrusion avant attente de chauffe M109 visible dans ce script.":"extrusion before an M109 heat-up wait is visible in this script.","Vérifier si la chauffe est assurée par le firmware ou une macro ; sinon attendre la température.":"Check whether heating is handled by the firmware or a macro; otherwise wait for the temperature.","Contrôler la commande de ventilation et le firmware.":"Check the fan command and the firmware.","Rétraction firmware ":"Firmware retraction ","Option firmware : ":"Firmware option: ","Conseil":"Tip","Remplissage très élevé : vérifier si la pièce exige cette densité. Des parois supplémentaires sont souvent plus efficaces pour certaines sollicitations.":"Very high infill: check whether the part requires this density. Extra walls are often more effective for certain loads.","À examiner":"To review","Aucune paroi : vérifier que le modèle et le mode d’impression le permettent.":"No walls: check that the model and print mode allow it."," % de remplissage avec ":"% infill with "," parois : envisager davantage de parois plutôt qu’un remplissage encore plus dense, puis tester la pièce dans son sens de sollicitation.":" walls: consider more walls rather than an even denser infill, then test the part in its loading direction."," mm proche de la limite indicative de la buse (":" mm close to the indicative nozzle limit ("," mm). Pour une pièce sollicitée, comparer une couche plus modérée et vérifier la température et l’adhésion inter-couches.":" mm). For a part under load, compare a more moderate layer height and check the temperature and inter-layer adhesion.","Fond ≈ ":"Bottom ≈ "," mm : si la pièce doit supporter des efforts ou des fixations, envisager davantage de couches inférieures selon la géométrie.":" mm: if the part must withstand loads or fasteners, consider more bottom layers depending on the geometry.","Supprimer ou corriger cette consigne avant toute impression.":"Remove or correct this setpoint before any printing.","Contrôler la consigne et les limites réelles de la machine avant impression.":"Check the setpoint and the machine’s actual limits before printing."," contient une avance F=":" contains a non-positive feed rate F="," non positive.":".","extrusion relative E=":"relative extrusion E="," mm inhabituellement élevée.":" mm unusually high."," hors plage habituelle 0–255.":" outside the usual 0–255 range.","Vérifier la signification du paramètre pour le firmware utilisé.":"Check the meaning of the parameter for the firmware in use.","Hauteur configurée : ":"Configured height: "," (nulle)":" (zero)","activée":"enabled","désactivée":"disabled","Optimisation":"Optimization","Remplissage élevé : essayer 15 à 25 % si la géométrie et la résistance le permettent ; comparer également la consommation de matière.":"High infill: try 15 to 25% if the geometry and strength allow it; also compare material consumption.","Une seule paroi peut être fragile : envisager 2 à 3 parois selon la pièce.":"A single wall can be fragile: consider 2 to 3 walls depending on the part."," mm : une hauteur proche de ":" mm nozzle: a height close to "," mm peut réduire le nombre de couches, si la finition et les détails le permettent.":" mm can reduce the number of layers, if finish and details allow it.","Le remplissage est à ":"Infill is at "," %. Pour une pièce décorative, essayez 15 à 20 % et comparez le temps estimé. Vérifiez que les couches du dessus restent bien soutenues.":"%. For a decorative part, try 15 to 20% and compare the estimated time. Check that the top layers remain well supported.","Motif ":"Pattern "," : le rectiligne peut être plus rapide sur certaines pièces. Comparer le temps estimé et conserver le motif actuel si ses propriétés mécaniques sont nécessaires.":": rectilinear can be faster on some parts. Compare the estimated time and keep the current pattern if its mechanical properties are needed.","Paroi externe à ":"Outer wall at "," mm/s en interne : si l’aspect est secondaire, comparer une vitesse externe un peu plus élevée, dans les limites validées de la machine et du filament.":" mm/s for the inner wall: if appearance is secondary, compare a slightly higher outer speed, within the validated limits of the machine and the filament.","Remplissage à ":"Infill at "," mm/s pour les contours : si le profil est calibré, comparer un remplissage plus rapide sans dépasser les limites de débit ni dégrader l’adhérence.":" mm/s for the outlines: if the profile is calibrated, compare a faster infill without exceeding the flow limits or degrading adhesion."," demande ":" requests "," °C (température négative).":" °C (negative temperature)."," °C, valeur exceptionnellement élevée.":" °C, an exceptionally high value.","Vérifier les dimensions et les décalages du plateau ; la zone utile peut être décentrée.":"Check the bed dimensions and offsets; the usable area may be off-center."," contient une valeur négative.":" contains a negative value.","Remplissage faible pour un objectif de solidité : vérifier les charges, l’orientation et les parois avant d’augmenter la densité.":"Low infill for a strength goal: check the loads, orientation and walls before increasing the density.","Pour une pièce sollicitée, envisager 3 à 4 parois ; deux parois ne sont pas une erreur en soi.":"For a part under load, consider 3 to 4 walls; two walls are not an error in themselves.","Pour privilégier la finition, essayer une hauteur de couche de ":"To favor finish, try a layer height of "," à ":" to "," mm ; ":" mm nozzle; "," mm est un compromis qualité/temps. La hauteur actuelle de ":" mm is a quality/time compromise. The current height of "," mm privilégie davantage la rapidité. Ces valeurs sont indicatives.":" mm favors speed more. These values are indicative.","La grille peut accumuler du plastique aux croisements. Pour gagner du temps, comparer avec un remplissage rectiligne dans l’aperçu et le temps estimé.":"Grid can build up plastic at the crossings. To save time, compare with a rectilinear infill in the preview and the estimated time.","coordonnée ":"coordinate "," hors plage indicative 0–":" outside the indicative range 0–","Remplissage élevé avec deux parois : envisager une paroi supplémentaire et moins de remplissage, après essai.":"High infill with two walls: consider an extra wall and less infill, after testing.","Hauteur supérieure à 80 % du diamètre de buse : réduire la hauteur (règle indicative).":"Height above 80% of the nozzle diameter: reduce the height (indicative rule).","Hauteur très faible pour cette buse : impression potentiellement longue sans gain visible sur toutes les pièces.":"Very low height for this nozzle: potentially long print without a visible gain on every part.","Pour une pièce mécanique, comparer grille, cubique et gyroïde selon la direction des efforts ; l’orientation et les parois restent déterminantes.":"For a mechanical part, compare grid, cubic and gyroid depending on the direction of the forces; orientation and walls remain decisive.","Hauteur élevée pour une buse de ":"High layer height for a "," mm : en mode Qualité, essayer ":" mm nozzle: in Quality mode, try ","Les croisements de la grille peuvent créer des surépaisseurs et des contacts avec la buse. Tester le rectiligne ou le gyroïde si ce défaut apparaît.":"Grid crossings can create extra thickness and contact with the nozzle. Test rectilinear or gyroid if this defect appears.","La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.":"Grid crosses lines within a single layer. Rectilinear limits crossings; gyroid suits many geometries.","Très peu de couches supérieures : risque de fermeture incomplète au-dessus du remplissage.":"Very few top layers: risk of incomplete closure above the infill.","Très peu de couches inférieures : vérifier la tenue du fond de la pièce.":"Very few bottom layers: check the strength of the bottom of the part.","Première couche rapide : en cas de défaut d’adhérence, tester une vitesse inférieure. Ce seuil est indicatif, pas constructeur.":"Fast first layer: if adhesion is poor, try a lower speed. This threshold is indicative, not from the manufacturer.","Épaisseur supérieure ≈ ":"Top thickness ≈ "," mm. Envisager environ 0,6 à 1 mm selon matériau, portée et finition.":" mm. Consider roughly 0.6 to 1 mm depending on material, span and finish.","Ventilation hors plage 0–100 % : vérifier la valeur et son unité.":"Fan speed outside the 0–100% range: check the value and its unit.","Accélération demandée supérieure à la limite déclarée dans le profil machine (":"Requested acceleration exceeds the limit declared in the machine profile ("," mm/s²). Vérifier le firmware et le profil.":" mm/s²). Check the firmware and the profile.","Température supérieure à la limite machine déclarée (":"Temperature exceeds the declared machine limit (","Grille":"Grid","Gyroïde":"Gyroid","Rectiligne":"Rectilinear","Rectiligne aligné":"Aligned rectilinear","Lignes":"Lines","Cubique":"Cubic","Cubique adaptatif":"Adaptive cubic","Cubique de soutien":"Support cubic","Nid d’abeilles":"Honeycomb","Nid d’abeilles 3D":"3D honeycomb","Tri-hexagonal":"Tri-hexagon","Concentrique":"Concentric","Cordes d’Archimède":"Archimedean chords","Spirale octagramme":"Octagram spiral","Courbe de Hilbert":"Hilbert curve","Éclair":"Lightning","Hachures croisées":"Cross hatch","Zigzag":"Zig zag","Monotone":"Monotonic","Lignes monotones":"Monotonic lines","Aucun lissage":"No ironing","Aucun":"None","Surfaces supérieures":"Top surfaces","Surfaces supérieures les plus hautes":"Topmost surfaces","Toutes les surfaces pleines":"All solid surfaces","Toutes les surfaces supérieures":"All top surfaces"},"templates":[{"re":"^Débit configuré : (.+?) mm³\\/s, inférieur au repère indicatif de (.+?)–(.+?) mm³\\/s pour (.+?)\\. Cela ne présente pas de risque de sous-extrusion en soi, mais peut ralentir fortement l’impression\\. Si la qualité est bonne, essayer progressivement (.+?) mm³\\/s, puis calibrer le débit maximal pour ce filament, cette température et cette tête d’impression\\. Ne pas augmenter sans vérification\\.$","en":"Configured flow: {0} mm³/s, below the indicative reference of {1}–{2} mm³/s for {3}. This does not in itself present a risk of under-extrusion, but can slow the print down considerably. If quality is good, gradually try {1} mm³/s, then calibrate the maximum flow for this filament, this temperature and this print head. Do not increase it without checking."},{"re":"^Débit configuré : (.+?) mm³\\/s\\. Le repère pour (.+?) est (.+?)–(.+?) mm³\\/s, mais ce filament semble haute vitesse : ne pas lui appliquer ce plafond standard\\. Débit conseillé : celui mesuré par calibration sur cette imprimante, à la température utilisée, ou la valeur documentée par le fabricant\\.$","en":"Configured flow: {0} mm³/s. The reference for {1} is {2}–{3} mm³/s, but this filament appears to be high-speed: do not apply this standard ceiling to it. Recommended flow: the one measured by calibration on this printer, at the temperature used, or the value documented by the manufacturer."},{"re":"^Débit configuré : (.+?) mm³\\/s\\. Pour (.+?), plage de départ conseillée : (.+?)–(.+?) mm³\\/s \\(repère indicatif, non constructeur\\)\\. Essayer au plus (.+?) mm³\\/s en attendant une calibration du débit maximal, puis retenir la valeur mesurée pour ce filament, cette température et cette tête d’impression\\.$","en":"Configured flow: {0} mm³/s. For {1}, recommended starting range: {2}–{3} mm³/s (indicative reference, not from the manufacturer). Try at most {3} mm³/s while waiting for a maximum flow calibration, then keep the value measured for this filament, this temperature and this print head."},{"re":"^Débit configuré : (.+?) mm³\\/s, inférieur même au repère standard de (.+?)–(.+?) mm³\\/s pour (.+?)\\. Ce filament semble haute vitesse : sa plage réelle doit être confirmée par le fabricant ou par calibration\\. Un débit aussi bas peut ralentir l’impression, sans être dangereux\\.$","en":"Configured flow: {0} mm³/s, even below the standard reference of {1}–{2} mm³/s for {3}. This filament appears to be high-speed: its actual range must be confirmed by the manufacturer or by calibration. A flow this low can slow the print down, without being dangerous."},{"re":"^Ratio configuré : (.+?), inférieur au repère indicatif 0,95–1,05\\. Cela peut être normal après calibration\\. Si aucune calibration n’a été faite, tester le ratio de débit avec le filament et la température actifs ; ne pas augmenter automatiquement\\.$","en":"Configured ratio: {0}, below the indicative reference of 0.95–1.05. This may be normal after calibration. If no calibration has been done, test the flow ratio with the active filament and temperature; do not increase it automatically."},{"re":"^Ratio configuré : (.+?), supérieur au repère indicatif 0,95–1,05\\. Cela peut être normal après calibration\\. Si aucune calibration n’a été faite, vérifier le ratio de débit pour éviter une éventuelle surextrusion ; ne pas diminuer automatiquement\\.$","en":"Configured ratio: {0}, above the indicative reference of 0.95–1.05. This may be normal after calibration. If no calibration has been done, check the flow ratio to avoid possible over-extrusion; do not decrease it automatically."},{"re":"^Pour privilégier la finition, essayer une hauteur de couche de (.+?) à (.+?) mm avec une buse de (.+?) mm ; (.+?) mm est un compromis qualité\\/temps\\. La hauteur actuelle de (.+?) mm privilégie davantage la rapidité\\. Ces valeurs sont indicatives\\.$","en":"To favor finish, try a layer height of {0} to {1} mm with a {2} mm nozzle; {3} mm is a quality/time compromise. The current height of {4} mm favors speed more. These values are indicative."},{"re":"^(.+?) parois et (.+?) % de remplissage : forte consommation potentielle\\. La résistance dépend aussi de l’orientation, de l’adhésion des couches et du sens de charge ; tester une éprouvette avant d’augmenter davantage la matière\\.$","en":"{0} walls and {1}% infill: potentially high consumption. Strength also depends on orientation, layer adhesion and load direction; test a specimen before adding more material."},{"re":"^Couches fines \\((.+?) mm\\) mais surface supérieure à (.+?) mm\\/s contre (.+?) mm\\/s pour la paroi externe : la finition du dessus peut limiter le gain de qualité\\. Comparer une vitesse supérieure plus modérée sur une pièce test\\.$","en":"Thin layers ({0} mm) but top surface at {1} mm/s versus {2} mm/s for the outer wall: the top finish may limit the quality gain. Compare a more moderate top surface speed on a test part."},{"re":"^Ratio configuré : (.+?)\\. Valeur très éloignée de 1,00 ; risque de sous-extrusion ou de surextrusion\\. Vérifier les unités et réaliser une calibration du ratio de débit dans OrcaSlicer avant de modifier le profil\\.$","en":"Configured ratio: {0}. Value very far from 1.00; risk of under-extrusion or over-extrusion. Check the units and perform a flow ratio calibration in OrcaSlicer before changing the profile."},{"re":"^Surface supérieure à (.+?) mm\\/s contre (.+?) mm\\/s pour la paroi externe : le dessus peut présenter davantage de marques\\. Conseil : essayez de réduire la vitesse du dessus et comparez le résultat\\.$","en":"Top surface at {0} mm/s versus {1} mm/s for the outer wall: the top may show more marks. Tip: try reducing the top surface speed and compare the result."},{"re":"^Accélération externe (.+?) mm\\/s² égale ou supérieure à celle d’impression \\((.+?) mm\\/s²\\) : si des vibrations marquent les contours, essayer une accélération externe plus basse après calibration\\.$","en":"Outer acceleration {0} mm/s² equal to or higher than the print acceleration ({1} mm/s²): if vibrations mark the outlines, try a lower outer acceleration after calibration."},{"re":"^Première couche à (.+?) mm\\/s, plus rapide que la paroi externe \\((.+?) mm\\/s\\)\\. une première couche trop rapide peut moins bien adhérer\\. Conseil : ralentissez-la si vous constatez un décollement\\.$","en":"First layer at {0} mm/s, faster than the outer wall ({1} mm/s). A first layer that is too fast may adhere less well. Tip: slow it down if you notice lifting."},{"re":"^Paroi externe à (.+?) mm\\/s contre (.+?) mm\\/s en interne : si l’aspect est secondaire, comparer une vitesse externe un peu plus élevée, dans les limites validées de la machine et du filament\\.$","en":"Outer wall at {0} mm/s versus {1} mm/s for the inner wall: if appearance is secondary, compare a slightly higher outer speed, within the validated limits of the machine and the filament."},{"re":"^Hauteur de (.+?) mm proche de la limite indicative de la buse \\((.+?) mm\\)\\. Pour une pièce sollicitée, comparer une couche plus modérée et vérifier la température et l’adhésion inter-couches\\.$","en":"Height of {0} mm close to the indicative nozzle limit ({1} mm). For a part under load, compare a more moderate layer height and check the temperature and inter-layer adhesion."},{"re":"^Épaisseur de dessus ≈ (.+?) mm sur remplissage (.+?) %\\. le dessus risque de laisser voir le remplissage\\. Conseil : ajoutez des couches supérieures si des trous ou des marques apparaissent\\.$","en":"Top thickness ≈ {0} mm over {1}% infill. The top may let the infill show through. Tip: add top layers if holes or marks appear."},{"re":"^Remplissage à (.+?) mm\\/s contre (.+?) mm\\/s pour les contours : si le profil est calibré, comparer un remplissage plus rapide sans dépasser les limites de débit ni dégrader l’adhérence\\.$","en":"Infill at {0} mm/s versus {1} mm/s for the outlines: if the profile is calibrated, compare a faster infill without exceeding the flow limits or degrading adhesion."},{"re":"^Paroi externe \\((.+?) mm\\/s\\) plus rapide que la paroi interne \\((.+?) mm\\/s\\)\\. Conseil : ralentissez légèrement la paroi externe pour améliorer l’aspect, puis comparez sur une pièce test\\.$","en":"Outer wall ({0} mm/s) faster than the inner wall ({1} mm/s). Tip: slow the outer wall down slightly to improve appearance, then compare on a test part."},{"re":"^Le dessus mesure environ (.+?) mm, mais le remplissage est de (.+?) %\\. Une grande portée entre lignes de remplissage peut marquer le dessus : vérifier les pontages dans l’aperçu\\.$","en":"The top is about {0} mm thick, but infill is {1}%. A large span between infill lines can mark the top: check the bridges in the preview."},{"re":"^Motif (.+?) : le rectiligne peut être plus rapide sur certaines pièces\\. Comparer le temps estimé et conserver le motif actuel si ses propriétés mécaniques sont nécessaires\\.$","en":"Pattern {0}: rectilinear can be faster on some parts. Compare the estimated time and keep the current pattern if its mechanical properties are needed."},{"re":"^Ventilation minimale de (.+?) % avec (.+?) : vérifier la compatibilité avec le filament et le risque de déformation\\. Les ventilateurs de ponts peuvent avoir d’autres consignes\\.$","en":"Minimum fan speed of {0}% with {1}: check compatibility with the filament and the risk of warping. Bridge fans may have other setpoints."},{"re":"^Rétraction de (.+?) mm : valeur élevée pour de nombreuses configurations ; vérifier le type d’extrudeur et les tests de rétraction, sans appliquer une valeur universelle\\.$","en":"Retraction of {0} mm: a high value for many setups; check the extruder type and retraction tests, without applying a universal value."},{"re":"^(.+?) % de remplissage et (.+?) couches supérieures : vérifier dans l’aperçu la portée des pontages sous les surfaces visibles ; renforcer le dessus si des creux apparaissent\\.$","en":"{0}% infill and {1} top layers: check the bridge spans under visible surfaces in the preview; reinforce the top if dips appear."},{"re":"^Surface supérieure à (.+?) mm\\/s et paroi externe à (.+?) mm\\/s : si des marques apparaissent sur le dessus, tester une vitesse supérieure plus proche de celle des parois\\.$","en":"Top surface at {0} mm/s and outer wall at {1} mm/s: if marks appear on the top, try a top surface speed closer to the wall speed."},{"re":"^(.+?) % de remplissage avec (.+?) parois : envisager davantage de parois plutôt qu’un remplissage encore plus dense, puis tester la pièce dans son sens de sollicitation\\.$","en":"{0}% infill with {1} walls: consider more walls rather than an even denser infill, then test the part in its loading direction."},{"re":"^Le remplissage est à (.+?) %\\. Pour une pièce décorative, essayez 15 à 20 % et comparez le temps estimé\\. Vérifiez que les couches du dessus restent bien soutenues\\.$","en":"Infill is at {0}%. For a decorative part, try 15 to 20% and compare the estimated time. Check that the top layers remain well supported."},{"re":"^(.+?) parois et (.+?) % de remplissage : selon les efforts, essayer une paroi supplémentaire et un remplissage plus modéré, puis comparer temps et résistance\\.$","en":"{0} walls and {1}% infill: depending on the loads, try an extra wall and a more moderate infill, then compare time and strength."},{"re":"^Première couche de (.+?) mm avec une buse de (.+?) mm : hauteur supérieure au repère indicatif de 80 % du diamètre\\. Vérifier l’adhérence et la calibration\\.$","en":"First layer of {0} mm with a {1} mm nozzle: height above the indicative reference of 80% of the diameter. Check adhesion and calibration."},{"re":"^Hauteur de (.+?) mm pour une buse de (.+?) mm : une hauteur proche de (.+?) mm peut réduire le nombre de couches, si la finition et les détails le permettent\\.$","en":"Height of {0} mm for a {1} mm nozzle: a height close to {2} mm can reduce the number of layers, if finish and details allow it."},{"re":"^Fond ≈ (.+?) mm : si la pièce doit supporter des efforts ou des fixations, envisager davantage de couches inférieures selon la géométrie\\.$","en":"Bottom ≈ {0} mm: if the part must withstand loads or fasteners, consider more bottom layers depending on the geometry."},{"re":"^Hauteur de (.+?) mm avec buse de (.+?) mm : pour un aspect plus fin, comparer avec environ (.+?) mm, sans obligation de modifier le profil\\.$","en":"Height of {0} mm with a {1} mm nozzle: for a finer look, compare with about {2} mm, with no obligation to change the profile."},{"re":"^Accélération demandée supérieure à la limite déclarée dans le profil machine \\((.+?) mm\\/s²\\)\\. Vérifier le firmware et le profil\\.$","en":"Requested acceleration exceeds the limit declared in the machine profile ({0} mm/s²). Check the firmware and the profile."},{"re":"^Largeur de ligne (.+?) mm pour une buse de (.+?) mm : vérifier la largeur choisie et la compatibilité avec le profil\\.$","en":"Line width {0} mm for a {1} mm nozzle: check the chosen width and its compatibility with the profile."},{"re":"^Pas de plage indicative disponible pour (.+?) : consulter la fiche fabricant et calibrer le débit maximal\\.$","en":"No indicative range available for {0}: consult the manufacturer datasheet and calibrate the maximum flow."},{"re":"^Épaisseur supérieure ≈ (.+?) mm\\. Envisager environ 0,6 à 1 mm selon matériau, portée et finition\\.$","en":"Top thickness ≈ {0} mm. Consider roughly 0.6 to 1 mm depending on material, span and finish."},{"re":"^Consigne minimale \\((.+?) %\\) supérieure à la maximale \\((.+?) %\\) : contrôler le profil filament\\.$","en":"Minimum setpoint ({0}%) is higher than the maximum ({1}%): check the filament profile."},{"re":"^Hauteur élevée pour une buse de (.+?) mm : en mode Qualité, essayer (.+?) à (.+?) mm\\.$","en":"High layer height for a {0} mm nozzle: in Quality mode, try {1} to {2} mm."},{"re":"^Clé source : (.+?)\\. Cette valeur ne correspond pas à un booléen reconnu\\.$","en":"Source key: {0}. This value does not match a recognized boolean."},{"re":"^Température supérieure à la limite machine déclarée \\((.+?) °C\\)\\.$","en":"Temperature exceeds the declared machine limit ({0} °C)."},{"re":"^extrusion relative E=(.+?) mm inhabituellement élevée\\.$","en":"relative extrusion E={0} mm unusually high."},{"re":"^(.+?) demande (.+?) °C, valeur exceptionnellement élevée\\.$","en":"{0} requests {1} °C, an exceptionally high value."},{"re":"^coordonnée (.+?)=(.+?) hors plage indicative 0–(.+?) mm\\.$","en":"coordinate {0}={1} outside the indicative range 0–{2} mm."},{"re":"^(.+?) contient une avance F=(.+?) non positive\\.$","en":"{0} contains a non-positive feed rate F={1}."},{"re":"^(.+?) demande (.+?) °C \\(température négative\\)\\.$","en":"{0} requests {1} °C (negative temperature)."},{"re":"^M106 S(.+?) hors plage habituelle 0–255\\.$","en":"M106 S{0} outside the usual 0–255 range."},{"re":"^Hauteur non numérique \\(clé : (.+?)\\)\\.$","en":"Non-numeric height (key: {0})."},{"re":"^(.+?) (.+?)(.+?) contient une valeur négative\\.$","en":"{0} {1}{2} contains a negative value."},{"re":"^paramètre (.+?) mal formé dans (.+?)\\.$","en":"malformed {0} parameter in {1}."},{"re":"^Longueur configurée : (.+?) mm$","en":"Configured length: {0} mm"},{"re":"^Hauteur configurée : (.+?) mm$","en":"Configured height: {0} mm"},{"re":"^Valeur à interpréter : (.+?)$","en":"Value to interpret: {0}"},{"re":"^Ordre configuré : (.+?)$","en":"Configured order: {0}"},{"re":"^Option firmware : (.+?)$","en":"Firmware option: {0}"},{"re":"^ \\(mode : (.+?)\\)$","en":" (mode: {0})"},{"re":"^Option (.+?) : (.+?)$","en":"Option {0}: {1}"},{"re":"^Valeur : (.+?)$","en":"Value: {0}"},{"re":"^Ligne (.+?) : (.+?)$","en":"Line {0}: {1}"}]};
let paEnSubList=null;
function paEnGroup(g){return /[A-Za-zÀ-ÿ]{3,}/.test(g)?paResultText(g):g;}
function paEnExact(original){
 if(Object.prototype.hasOwnProperty.call(PA_EN_FIX.exact,original))return PA_EN_FIX.exact[original];
 for(const t of PA_EN_FIX.templates){
  const m=original.match(new RegExp(t.re));
  if(m)return t.en.replace(/\{(\d+)\}/g,(_,i)=>paEnGroup(m[Number(i)+1]));
 }
 return null;
}
function paEnSub(text){
 if(!paEnSubList){
  const all=Object.assign({},PA_EN_FIX.exact,PA_FIELD_EN,PA_RESULT_EN);
  paEnSubList=Object.entries(all).filter(([fr])=>fr.length>=8).sort((a,b)=>b[0].length-a[0].length);
 }
 let r=text;
 for(const [fr,en] of paEnSubList){if(r.includes(fr))r=r.split(fr).join(en);}
 const L='A-Za-zÀ-ÿ';
 for(const [re,en] of [['(?<![%L])Désactivée?(?![%L])','Disabled'],['(?<![%L])Activée?(?![%L])','Enabled'],['(?<![%L])désactivée?(?![%L])','disabled'],['(?<![%L])activée?(?![%L])','enabled']])r=r.replace(new RegExp(re.split('%L').join(L),'g'),en);
 return r;
}
function paResultText(v){
 if(v===null||v===undefined||paLang==='fr')return v;
 const original=String(v);
 const local=Object.assign({},PA_RESULT_EXTRA[paLang]||{},PA_V345[paLang]||{},PA_V346[paLang]||{});
 const advice=PA_ADVICE_TRANSLATIONS[paLang]||{};
 if(Object.prototype.hasOwnProperty.call(advice,original))return advice[original];
 if(Object.prototype.hasOwnProperty.call(local,original))return local[original];
 if(paLang==='en'&&Object.prototype.hasOwnProperty.call(PA_RESULT_EN,original))return PA_RESULT_EN[original];
 const compare=original.match(/^Paroi externe à ([0-9.,]+) mm\/s contre ([0-9.,]+) mm\/s en interne : si l’aspect est secondaire, comparer une vitesse externe un peu plus élevée, dans les limites validées de la machine et du filament\.$/);
 if(compare){
  const t={en:'Outer wall at {a} mm/s versus {b} mm/s for inner walls: if appearance is secondary, compare a slightly higher outer-wall speed within the verified printer and filament limits.',de:'Außenwand mit {a} mm/s gegenüber {b} mm/s innen: Wenn die Optik zweitrangig ist, eine etwas höhere Außenwandgeschwindigkeit innerhalb der geprüften Drucker- und Filamentgrenzen vergleichen.',es:'Pared exterior a {a} mm/s frente a {b} mm/s en el interior: si el acabado es secundario, compara una velocidad exterior algo mayor dentro de los límites verificados de la impresora y el filamento.',it:'Parete esterna a {a} mm/s rispetto a {b} mm/s per quella interna: se la finitura è secondaria, confronta una velocità esterna leggermente maggiore entro i limiti verificati della stampante e del filamento.',pt:'Parede externa a {a} mm/s contra {b} mm/s na interna: se o acabamento for secundário, compare uma velocidade externa um pouco maior dentro dos limites verificados da impressora e do filamento.',zh_CN:'外墙速度为 {a} mm/s，内墙为 {b} mm/s：如果外观要求较低，可在已验证的打印机和耗材限制内比较略高的外墙速度。'};
  return (t[paLang]||t.en).replace('{a}',compare[1]).replace('{b}',compare[2]);
 }
 const layer=original.match(/^Hauteur de ([0-9.,]+) mm avec buse de ([0-9.,]+) mm : pour un aspect plus fin, comparer avec environ ([0-9.,]+) mm, sans obligation de modifier le profil\.$/);
 if(layer){
   const tpl=PA_LAYER_ADVICE[paLang]||PA_LAYER_ADVICE.en;
   return tpl.replace(/\{a\}/g,layer[1]).replace(/\{b\}/g,layer[2]).replace(/\{c\}/g,layer[3]);
 }
 for(const item of PA_DYNAMIC_TEMPLATES){
   const m=original.match(new RegExp('^'+item.re+'$'));
   if(m){let out=(item.translations[paLang]||item.translations.en);
     for(let j=1;j<m.length;j++)out=out.split('{'+String.fromCharCode(96+j)+'}').join(m[j]);
     return out;
   }
 }
 if(paLang==='en'){const fixed=paEnExact(original);if(fixed!==null)return fixed;}
 // Prefer native-language translations, then English only for advice not translated yet.
 const sources=[local,advice];
 let result=original;
 for(const dictionary of sources){
   for(const [fr,tr] of Object.entries(dictionary).sort((a,b)=>b[0].length-a[0].length)){
     if(fr.length>=8 && result.includes(fr))result=result.split(fr).join(tr);
   }
 }
 return paLang==='en'?paEnSub(result):result;
}

const PA_I18N={"fr":{"subtitle":"Analyse des profils actifs directement depuis OrcaSlicer. Aucune modification des réglages.","goal":"Objectif d’impression :","balanced":"Équilibré","quality":"Qualité","strength":"Solidité","speed":"Rapidité","language":"Langue :","auto":"Comme OrcaSlicer","waiting":"En attente...","loading":"Lecture des profils...","error":"Erreur : ","unknown":"inconnue","loaded":"Configuration chargée : {n} clés disponibles.","profiles":"Profils actifs","process":"Impression : ","printer":"Imprimante : ","filaments":"Filament(s) : ","empty":"Aucune anomalie ni optimisation particulière détectée dans les éléments analysés.","empty_note":"Cela ne garantit pas l’absence de problème lors de l’impression.","parameters":"Paramètres à examiner","filament_advice":"Conseils par filament","options":"Options à examiner","cross":"Analyse croisée","gcode":"Alertes G-code","parameter":"Paramètre","value":"Valeur réelle","state":"État","advice":"Conseil","option":"Option","evaluation":"Évaluation","theme":"Thème","diagnostic":"Diagnostic","section":"Section","problem":"Problème","path":"Emplacement dans OrcaSlicer","current":"Valeur actuelle : ","see":"Voir le profil actif","disclaimer":"Avertissement :","disclaimer_body":"PrinterAssist fournit uniquement des recommandations indicatives, sans garantie de résultat ni de compatibilité avec chaque imprimante. Vous restez responsable des modifications apportées à vos réglages et devez vérifier leur adéquation avec les consignes du fabricant. Les développeurs de PrinterAssist ne sauraient être tenus responsables des dysfonctionnements ou dommages résultant de l’application de ces conseils, dans les limites autorisées par la loi."},"en":{"subtitle":"Analyze active profiles directly from OrcaSlicer. Settings are never changed.","goal":"Print goal:","balanced":"Balanced","quality":"Quality","strength":"Strength","speed":"Speed","language":"Language:","auto":"Same as OrcaSlicer","waiting":"Waiting...","loading":"Reading profiles...","error":"Error: ","unknown":"unknown","loaded":"Configuration loaded: {n} available keys.","profiles":"Active profiles","process":"Process: ","printer":"Printer: ","filaments":"Filament(s): ","empty":"No specific problems or optimizations were found in the checked settings.","empty_note":"This does not guarantee a trouble-free print.","parameters":"Settings to review","filament_advice":"Advice by filament","options":"Options to review","cross":"Cross-checks","gcode":"G-code alerts","parameter":"Setting","value":"Actual value","state":"Status","advice":"Advice","option":"Option","evaluation":"Assessment","theme":"Topic","diagnostic":"Diagnosis","section":"Section","problem":"Problem","path":"Where to find this setting in OrcaSlicer","current":"Current value: ","see":"See active profile","disclaimer":"Warning:","disclaimer_body":"PrinterAssist offers guidance only, without guaranteeing results or compatibility with every printer. You are responsible for any changes to your settings and should follow the printer manufacturer’s instructions. The developers of PrinterAssist are not liable for problems or damage resulting from these recommendations, to the extent permitted by law."},"es":{"subtitle":"Analiza los perfiles activos de OrcaSlicer. No se modifica ningún ajuste.","goal":"Objetivo de impresión:","balanced":"Equilibrado","quality":"Calidad","strength":"Resistencia","speed":"Velocidad","language":"Idioma:","auto":"Como OrcaSlicer","waiting":"En espera...","loading":"Leyendo perfiles...","error":"Error: ","unknown":"desconocido","loaded":"Configuración cargada: {n} claves disponibles.","profiles":"Perfiles activos","process":"Impresión: ","printer":"Impresora: ","filaments":"Filamentos: ","empty":"No se han detectado problemas ni optimizaciones específicas en los ajustes revisados.","empty_note":"Esto no garantiza una impresión sin problemas.","parameters":"Parámetros a revisar","filament_advice":"Consejos por filamento","options":"Opciones a revisar","cross":"Análisis cruzado","gcode":"Alertas de G-code","parameter":"Parámetro","value":"Valor real","state":"Estado","advice":"Consejo","option":"Opción","evaluation":"Evaluación","theme":"Tema","diagnostic":"Diagnóstico","section":"Sección","problem":"Problema","path":"Dónde encontrar este ajuste en OrcaSlicer","current":"Valor actual: ","see":"Ver perfil activo","disclaimer":"Aviso:","disclaimer_body":"PrinterAssist solo ofrece recomendaciones orientativas, sin garantizar resultados ni compatibilidad con todas las impresoras. Eres responsable de los cambios en tus ajustes y debes seguir las indicaciones del fabricante. Los desarrolladores no se hacen responsables de los problemas o daños derivados de estas recomendaciones, en la medida permitida por la ley."},"de":{"subtitle":"Aktive Profile direkt aus OrcaSlicer analysieren. Einstellungen werden nicht verändert.","goal":"Druckziel:","balanced":"Ausgewogen","quality":"Qualität","strength":"Festigkeit","speed":"Geschwindigkeit","language":"Sprache:","auto":"Wie OrcaSlicer","waiting":"Warten...","loading":"Profile werden gelesen...","error":"Fehler: ","unknown":"unbekannt","loaded":"Configuration loaded: {n} available keys.","profiles":"Aktive Profile","process":"Druck: ","printer":"Drucker: ","filaments":"Filamente: ","empty":"In den geprüften Einstellungen wurden keine besonderen Probleme oder Optimierungen gefunden.","empty_note":"Dies garantiert keinen fehlerfreien Druck.","parameters":"Einstellungen prüfen","filament_advice":"Hinweise je Filament","options":"Optionen prüfen","cross":"Quervergleiche","gcode":"G-Code-Warnungen","parameter":"Einstellung","value":"Istwert","state":"Status","advice":"Empfehlung","option":"Option","evaluation":"Bewertung","theme":"Thema","diagnostic":"Diagnose","section":"Abschnitt","problem":"Problem","path":"Einstellung in OrcaSlicer finden","current":"Aktueller Wert: ","see":"Aktives Profil ansehen","disclaimer":"Hinweis:","disclaimer_body":"PrinterAssist gibt nur unverbindliche Hinweise und garantiert weder Ergebnisse noch die Kompatibilität mit jedem Drucker. Du bist für Änderungen an deinen Einstellungen verantwortlich und musst die Vorgaben des Druckerherstellers beachten. Die Entwickler haften im gesetzlich zulässigen Umfang nicht für Probleme oder Schäden infolge dieser Empfehlungen."},"it":{"subtitle":"Analizza i profili attivi di OrcaSlicer. Le impostazioni non vengono modificate.","goal":"Obiettivo di stampa:","balanced":"Bilanciato","quality":"Qualità","strength":"Resistenza","speed":"Velocità","language":"Lingua:","auto":"Come OrcaSlicer","waiting":"In attesa...","loading":"Lettura dei profili...","error":"Errore: ","unknown":"sconosciuto","loaded":"Configuration loaded: {n} available keys.","profiles":"Profili attivi","process":"Stampa: ","printer":"Stampante: ","filaments":"Filamenti: ","empty":"Nessun problema o ottimizzazione particolare rilevato nelle impostazioni controllate.","empty_note":"Questo non garantisce una stampa priva di problemi.","parameters":"Parametri da controllare","filament_advice":"Consigli per filamento","options":"Opzioni da controllare","cross":"Controlli incrociati","gcode":"Avvisi G-code","parameter":"Parametro","value":"Valore effettivo","state":"Stato","advice":"Consiglio","option":"Opzione","evaluation":"Valutazione","theme":"Argomento","diagnostic":"Diagnosi","section":"Sezione","problem":"Problema","path":"Dove trovare questa impostazione in OrcaSlicer","current":"Valore attuale: ","see":"Vedi profilo attivo","disclaimer":"Avvertenza:","disclaimer_body":"PrinterAssist fornisce solo consigli indicativi, senza garantire risultati o compatibilità con tutte le stampanti. Sei responsabile delle modifiche alle impostazioni e devi rispettare le indicazioni del produttore. Gli sviluppatori non rispondono di problemi o danni derivanti da questi consigli, nei limiti consentiti dalla legge."},"pt":{"subtitle":"Analisa os perfis ativos do OrcaSlicer. As definições não são alteradas.","goal":"Objetivo de impressão:","balanced":"Equilibrado","quality":"Qualidade","strength":"Resistência","speed":"Velocidade","language":"Idioma:","auto":"Como OrcaSlicer","waiting":"A aguardar...","loading":"A ler perfis...","error":"Erro: ","unknown":"desconhecido","loaded":"Configuration loaded: {n} available keys.","profiles":"Perfis ativos","process":"Impressão: ","printer":"Impressora: ","filaments":"Filamentos: ","empty":"Nenhum problema ou otimização específica foi encontrado nas configurações verificadas.","empty_note":"Isso não garante uma impressão sem problemas.","parameters":"Parâmetros a verificar","filament_advice":"Recomendações por filamento","options":"Opções a verificar","cross":"Verificações cruzadas","gcode":"Alertas de G-code","parameter":"Parâmetro","value":"Valor real","state":"Estado","advice":"Conselho","option":"Opção","evaluation":"Avaliação","theme":"Tema","diagnostic":"Diagnóstico","section":"Seção","problem":"Problema","path":"Onde encontrar esta configuração no OrcaSlicer","current":"Valor atual: ","see":"Ver perfil ativo","disclaimer":"Aviso:","disclaimer_body":"O PrinterAssist fornece apenas recomendações orientativas, sem garantir resultados ou compatibilidade com todas as impressoras. Você é responsável pelas alterações nas configurações e deve seguir as orientações do fabricante. Os desenvolvedores não se responsabilizam por problemas ou danos decorrentes destas recomendações, nos limites permitidos por lei."},"zh_CN":{"subtitle":"直接分析 OrcaSlicer 当前配置，不会修改设置。","goal":"打印目标：","balanced":"均衡","quality":"质量","strength":"强度","speed":"速度","language":"语言：","auto":"跟随 OrcaSlicer","waiting":"等待中...","loading":"正在读取配置...","error":"错误：","unknown":"未知","loaded":"Configuration loaded: {n} available keys.","profiles":"当前配置","process":"打印配置：","printer":"打印机：","filaments":"耗材：","empty":"在已检查的设置中未发现明显问题或优化项。","empty_note":"这并不保证打印过程不会出现问题。","parameters":"需要检查的参数","filament_advice":"按耗材分类的建议","options":"需要检查的选项","cross":"交叉检查","gcode":"G-code 警告","parameter":"参数","value":"实际值","state":"状态","advice":"建议","option":"选项","evaluation":"评估","theme":"项目","diagnostic":"诊断","section":"部分","problem":"问题","path":"在 OrcaSlicer 中查找此设置","current":"当前值：","see":"查看当前配置","disclaimer":"警告：","disclaimer_body":"PrinterAssist 仅提供参考建议，不保证打印效果或与所有打印机兼容。你需要自行负责设置更改，并遵循打印机制造商的说明。在法律允许的范围内，开发者不对采用这些建议导致的问题或损失承担责任。"}};
let paSystemLang='fr',paLanguageChoice='auto',paLang='fr';
function T(key,vars){let v=(PA_I18N[paLang]||PA_I18N.fr)[key]||PA_I18N.fr[key]||key;return v.replace(/\{(\w+)\}/g,(_,k)=>vars&&vars[k]!==undefined?vars[k]:'');}
function paApplyLanguage(){paLang=paLanguageChoice==='auto'?paSystemLang:paLanguageChoice;document.documentElement.lang=paLang;document.querySelectorAll('[data-pa]').forEach(el=>{el.textContent=T(el.dataset.pa)});const auto=document.querySelector('#pa-language option[value="auto"]');auto.textContent=T('auto');}
function paChangeLanguage(){paLanguageChoice=document.getElementById('pa-language').value;try{localStorage.setItem('printerassist.language',paLanguageChoice)}catch(e){}paApplyLanguage();analyse();}
try{paLanguageChoice=localStorage.getItem('printerassist.language')||'auto'}catch(e){}
if(paLanguageChoice!=='auto' && !PA_I18N[paLanguageChoice])paLanguageChoice='auto';
document.getElementById("pa-language").value=paLanguageChoice;paApplyLanguage();
function esc(v){return String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
let adviceIndex=[];
// Chemins documentés dans l'interface de préparation OrcaSlicer.
// Aucune infobulle si le chemin n'est pas connu avec assez de confiance.
const SETTING_PATHS={
 'layer_height':['Processus','Qualité','Hauteur de couche'],
 'wall_loops':['Processus','Résistance','Nombre de parois'],
 'perimeters':['Processus','Résistance','Nombre de parois'],
 'sparse_infill_density':['Processus','Résistance','Densité du remplissage'],
 'fill_density':['Processus','Résistance','Densité du remplissage'],
 'sparse_infill_pattern':['Processus','Résistance','Motif de remplissage'],
 'fill_pattern':['Processus','Résistance','Motif de remplissage'],
 'outer_wall_speed':['Processus','Vitesse','Paroi externe'],
 'external_perimeter_speed':['Processus','Vitesse','Paroi externe'],
 'inner_wall_speed':['Processus','Vitesse','Paroi interne'],
 'perimeter_speed':['Processus','Vitesse','Paroi interne'],
 'sparse_infill_speed':['Processus','Vitesse','Remplissage'],
 'infill_speed':['Processus','Vitesse','Remplissage'],
 'top_surface_speed':['Processus','Vitesse','Surface supérieure'],
 'top_solid_infill_speed':['Processus','Vitesse','Surface supérieure'],
 'initial_layer_speed':['Processus','Vitesse','Première couche'],
 'first_layer_speed':['Processus','Vitesse','Première couche'],
 'travel_speed':['Processus','Vitesse','Déplacement'],
 'default_acceleration':['Processus','Vitesse','Accélération par défaut'],
 'outer_wall_acceleration':['Processus','Vitesse','Accélération paroi externe'],
 'top_shell_layers':['Processus','Résistance','Couches supérieures'],
 'top_solid_layers':['Processus','Résistance','Couches supérieures'],
 'bottom_shell_layers':['Processus','Résistance','Couches inférieures'],
 'bottom_solid_layers':['Processus','Résistance','Couches inférieures'],
 'filament_max_volumetric_speed':['Filament','Avancé','Vitesse volumétrique maximale'],
 'filament_flow_ratio':['Filament','Filament','Ratio de débit'],
 'nozzle_temperature':['Filament','Filament','Température de buse'],
 'temperature':['Filament','Filament','Température de buse'],
 'hot_plate_temp':['Filament','Filament','Température du plateau'],
 'bed_temperature':['Filament','Filament','Température du plateau'],
 'reduce_crossing_wall':['Processus','Qualité','Éviter de traverser les parois'],
 'avoid_crossing_perimeters':['Processus','Qualité','Éviter de traverser les parois'],
 'detect_thin_wall':['Processus','Qualité','Détecter les parois fines'],
 'thin_walls':['Processus','Qualité','Détecter les parois fines'],
 'ironing_type':['Processus','Qualité','Lissage'],
 'ironing':['Processus','Qualité','Lissage'],
 'enable_support':['Processus','Supports','Activer les supports'],
 'support_material':['Processus','Supports','Activer les supports'],
 'wall_sequence':['Processus','Qualité','Ordre des parois'],
 'outer_wall_first':['Processus','Qualité','Ordre des parois'],
 'external_perimeters_first':['Processus','Qualité','Ordre des parois']
};
let hintNumber=0;
function adviceCell(p){
 if(!p.comment)return '';
 const comment=esc(paResultText(p.comment));
 if(p.level==='ok'||p.status==='Aucun signal détecté'||!p.key)return comment;
 const path=SETTING_PATHS[p.key];
 if(!path)return comment;
 const id='pa-hint-'+(++hintNumber);
 const details='<strong>'+T('path')+'</strong><div>'+path.map(x=>esc(paResultText(x))).join(' → ')+'</div>'+
 '<div>'+T('current')+esc(paResultText(p.value||T('see')))+'</div>';
 return comment+' <span class="hint-wrap"><button class="go-setting" type="button" aria-label="Emplacement du réglage '+esc(paText(p.name))+'" aria-describedby="'+id+'">?</button><span class="hint-tip" role="tooltip" id="'+id+'">'+details+'</span></span>';
}
function analyse(){document.getElementById('status').textContent=T('loading');orca.postMessage({type:'analyze_active',goal:document.getElementById('goal').value});}
orca.onMessage(function(d){if(d&&d.type==='pa_language'){paSystemLang=PA_I18N[d.language]?d.language:'en';paApplyLanguage();return;}if(!d||d.type!=='analysis_result')return;const status=document.getElementById('status'),root=document.getElementById('report');if(!d.success){status.textContent=T('error')+(d.error||T('unknown'));return;}status.textContent='';hintNumber=0;let html='<section><b>'+T('profiles')+'</b><p>'+T('process')+esc(d.names.process)+'<br>'+T('printer')+esc(d.names.machine)+'<br>'+T('filaments')+(d.names.filaments||[]).map((name,i)=>'<br>&nbsp;&nbsp;'+(i+1)+'. '+esc(name)).join('')+'</p></section>';
const important=x=>x&&['warn','err'].includes(x.level);const parameters=(d.parameters||[]).filter(important),options=(d.options||[]).filter(important),cross=(d.cross_checks||[]).filter(important),alerts=d.gcode_alerts||[];
const filamentRows=(d.filament_parameters||[]).filter(important);const total=parameters.length+options.length+cross.length+alerts.length+filamentRows.length;
if(!total){html+='<section class="ok"><b>'+T('empty')+'</b><p class="muted">'+T('empty_note')+'</p></section>';}
// Affichage vertical des consignes par filament dans la cellule température.
function valueCell(p){
 const value=String(p.value??'');
 if(p.name==='Température buse' && /Filament\s+\d+\s*\(/i.test(value)){
   const parts=value.split(/\s*[·•]\s*(?=Filament\s+\d+\s*\()/i);
   if(parts.length>1)return parts.map(part=>'<div class="filament-temp">'+esc(part.trim())+'</div>').join('');
 }
 return esc(paResultText(value));
}
function table(title,rows,heads,render){if(!rows.length)return;html+='<section><b>'+title+'</b><table><tr>'+heads.map(h=>'<th>'+h+'</th>').join('')+'</tr>';for(const p of rows)html+=render(p);html+='</table></section>';}
table(T('parameters'),parameters,[T('parameter'),T('value'),T('state'),T('advice')],p=>'<tr><td>'+esc(paText(p.name))+'</td><td>'+valueCell(p)+'</td><td class="'+esc(p.level)+'">'+esc(paText(p.status))+'</td><td>'+adviceCell(p)+'</td></tr>');
table(T('filament_advice'),filamentRows,[T('parameter'),T('value'),T('state'),T('advice')],p=>'<tr><td>'+esc(paText(p.name))+'</td><td>'+esc(paResultText(p.value))+'</td><td class="'+esc(p.level)+'">'+esc(paText(p.status))+'</td><td>'+adviceCell(p)+'</td></tr>');
table(T('options'),options,[T('option'),T('state'),T('evaluation'),T('advice')],p=>'<tr><td>'+esc(paText(p.name))+'</td><td>'+esc(paResultText(p.value))+'</td><td class="'+esc(p.level)+'">'+esc(paText(p.status))+'</td><td>'+adviceCell(p)+'</td></tr>');
table(T('cross'),cross,[T('theme'),T('diagnostic'),T('advice')],p=>'<tr><td>'+esc(paText(p.name))+'</td><td class="'+esc(p.level)+'">'+esc(paText(p.status))+'</td><td>'+adviceCell(p)+'</td></tr>');
table(T('gcode'),alerts,[T('section'),T('problem'),T('advice')],a=>'<tr><td>'+esc(paResultText(a.section))+'</td><td class="'+(a.level==='err'?'err':'warn')+'">'+esc(paResultText(a.problem))+'</td><td>'+esc(paResultText(a.advice))+'</td></tr>');
root.innerHTML=html;});
// Relecture des profils à chaque retour dans l'onglet PrinterAssist.
// Certains conteneurs OrcaSlicer gardent la page chargée en arrière-plan.
let lastRefresh=0;
function refreshOnReturn(){
  const now=Date.now();
  if(now-lastRefresh<600)return;
  lastRefresh=now;
  analyse();
}
window.addEventListener('load',()=>{orca.postMessage({type:'get_language'});setTimeout(refreshOnReturn,300);});
window.addEventListener('focus',refreshOnReturn);
window.addEventListener('pageshow',e=>{if(e.persisted)refreshOnReturn();});
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refreshOnReturn();});
</script></body></html>'''

# Keys correspond to the active flattened OrcaSlicer configuration.
FIELDS = [
 ('Hauteur de couche',('layer_height',),'mm'),
 ('Nombre de parois',('wall_loops','perimeters'),''),
 ('Densité de remplissage',('sparse_infill_density','fill_density'),'%'),
 ('Motif de remplissage',('sparse_infill_pattern','fill_pattern'),''),
 ('Vitesse paroi externe',('outer_wall_speed','external_perimeter_speed'),'mm/s'),
 ('Vitesse paroi interne',('inner_wall_speed','perimeter_speed'),'mm/s'),
 ('Vitesse remplissage',('sparse_infill_speed','infill_speed'),'mm/s'),
 ('Vitesse remplissage plein',('internal_solid_infill_speed','solid_infill_speed'),'mm/s'),
 ('Vitesse surface supérieure',('top_surface_speed','top_solid_infill_speed'),'mm/s'),
 ('Vitesse première couche',('initial_layer_speed','first_layer_speed'),'mm/s'),
 ('Vitesse déplacement',('travel_speed',),'mm/s'),
 ('Accélération impression',('default_acceleration','printing_acceleration'),'mm/s²'),
 ('Accélération paroi externe',('outer_wall_acceleration','external_perimeter_acceleration'),'mm/s²'),
 ('Accélération déplacement',('travel_acceleration',),'mm/s²'),
 ('Diamètre de buse',('nozzle_diameter',),'mm'),
 ('Température buse',('nozzle_temperature','temperature'),'°C'),
 ('Température plateau',('hot_plate_temp','bed_temperature'),'°C'),
 ('Débit volumétrique filament',('filament_max_volumetric_speed',),'mm³/s'),
 ('Ratio de débit',('filament_flow_ratio',),''),
 ('Couches supérieures',('top_shell_layers','top_solid_layers'),''),
 ('Couches inférieures',('bottom_shell_layers','bottom_solid_layers'),''),
 ('Ventilation maximale',('fan_max_speed','overhang_fan_speed'),'%'),
]

def numeric(value):
    if isinstance(value,(list,tuple)):
        value = value[0] if value else None
    if isinstance(value,(int,float)) and not isinstance(value,bool):
        return float(value) if math.isfinite(value) else None
    if isinstance(value,str):
        import re
        m=re.search(r'[-+]?\d+(?:[.,]\d+)?',value)
        if m:
            try:return float(m.group().replace(',','.'))
            except ValueError:pass
    return None

# Traduction d'affichage uniquement : les valeurs internes OrcaSlicer restent intactes.
DISPLAY_TRANSLATIONS = {
    'grid': 'Grille', 'gyroid': 'Gyroïde', 'rectilinear': 'Rectiligne',
    'aligned rectilinear': 'Rectiligne aligné', 'line': 'Lignes', 'lines': 'Lignes',
    'cubic': 'Cubique', 'adaptive cubic': 'Cubique adaptatif',
    'adaptivecubic': 'Cubique adaptatif', 'support cubic': 'Cubique de soutien',
    'honeycomb': 'Nid d’abeilles', '3d honeycomb': 'Nid d’abeilles 3D',
    'triangles': 'Triangles', 'tri-hexagon': 'Tri-hexagonal',
    'concentric': 'Concentrique', 'archimedean chords': 'Cordes d’Archimède',
    'octagram spiral': 'Spirale octagramme', 'hilbert curve': 'Courbe de Hilbert',
    'lightning': 'Éclair', 'cross hatch': 'Hachures croisées',
    'crosshatch': 'Hachures croisées', 'zig zag': 'Zigzag', 'zigzag': 'Zigzag',
    'monotonic': 'Monotone', 'monotonic line': 'Lignes monotones',
    'no ironing': 'Aucun lissage', 'none': 'Aucun',
    'top': 'Surfaces supérieures', 'topmost': 'Surfaces supérieures les plus hautes',
    'all solid': 'Toutes les surfaces pleines',
    'all top surfaces': 'Toutes les surfaces supérieures',
    'all solid surfaces': 'Toutes les surfaces pleines',
    'inner wall/outer wall': 'Interne → externe',
    'outer wall/inner wall': 'Externe → interne',
    'inner/outer': 'Interne → externe', 'outer/inner': 'Externe → interne',
    'inner wall/outer wall/inner wall': 'Interne → externe → interne',
    'inner/outer/inner': 'Interne → externe → interne',
    'enabled': 'Activé', 'disabled': 'Désactivé',
}

def translate_display(value, key=None):
    """Traduit les énumérations connues sans toucher aux données analysées."""
    if isinstance(value, (list, tuple)):
        return ', '.join(translate_display(v, key) for v in value)
    if value is None:
        return 'Non disponible'
    if not isinstance(value, str):
        return str(value)
    normalized = ' '.join(value.strip().lower().replace('_', ' ').replace('-', ' ').split())
    if key in ('filament_type', 'filament_vendor'):
        return value  # Identifiants de matériaux et marques : ne pas modifier.
    return DISPLAY_TRANSLATIONS.get(normalized, value)

def show(value,unit):
    if value is None:return 'Non disponible'
    if isinstance(value,(list,tuple)):
        value=', '.join(map(str,value))
    return str(value)+((' '+unit) if unit else '')

def parse_bool(value):
    """Convertit les booléens du profil sans confondre une valeur inconnue avec False."""
    if isinstance(value, (list, tuple)):
        if not value: return None
        if len(value) > 1:
            states = [parse_bool(x) for x in value]
            return states[0] if all(x == states[0] for x in states) else None
        return parse_bool(value[0])
    if isinstance(value, bool): return value
    if isinstance(value, (int, float)) and value in (0, 1): return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ('true','1','yes','on','oui'): return True
        if v in ('false','0','no','off','non'): return False
    return None

# Lecture typée des options : ne jamais assimiler une valeur absente à « désactivée ».
# Les clés correspondent à plusieurs générations de profils OrcaSlicer / Slic3r.
def first_value(config, *aliases):
    for key in aliases:
        if key in config and config[key] is not None:
            return key, config[key]
    return None, None

def first_item(value):
    if isinstance(value, (tuple, list)):
        return value[0] if value else None
    return value

def ironing_enabled(value):
    """Interprète le type de lissage OrcaSlicer sans faux positif sur 'no ironing'."""
    value=first_item(value)
    if value is None:return None
    boolean=parse_bool(value)
    if boolean is not None:return boolean
    if isinstance(value,str):
        v=' '.join(value.strip().lower().replace('_',' ').replace('-',' ').split())
        if v in ('no ironing','no ironing enabled','none','disabled','disable','off','no','0','false','aucun','désactivé','desactive'):
            return False
        if v in ('top','topmost','all','all solid','all top surfaces','all solid surfaces','ironing','on','enabled','yes','1','true'):
            return True
    return None

def option_row(name, value, comment='', key=None, missing=False):
    if missing:
        return dict(name=name, key=key or '', value='Non disponible', status='Non vérifiable',
                    level='muted', comment='Clé absente de la configuration active.')
    return dict(name=name, key=key or '', value=value, status='À vérifier selon la pièce' if comment else 'Information',
                level='warn' if comment else 'ok', comment=comment)

def boolean_option(config, name, keys, goal, tips=None):
    key, raw=first_value(config,*keys)
    if key is None:return option_row(name,'',missing=True)
    value=parse_bool(raw)
    if value is None:
        return option_row(name, f'Valeur à interpréter : {str(raw)[:80]}',
                          f'Clé source : {key}. Cette valeur ne correspond pas à un booléen reconnu.')
    comment=(tips or {}).get((goal,value),'')
    return option_row(name,'Activée' if value else 'Désactivée',comment,key)

def analyze_options(config, goal='balanced'):
    results=[]
    results.append(boolean_option(config,'Éviter de traverser les parois',
        ('reduce_crossing_wall','avoid_crossing_perimeters'),goal,
        {('quality',False):'En cas de traces de déplacement, envisager cette option puis comparer les trajets dans l’aperçu.'}))
    results.append(boolean_option(config,'Détection des parois fines',
        ('detect_thin_wall','thin_walls'),goal,
        {('quality',False):'Si des détails fins manquent dans l’aperçu, essayer cette option ; son intérêt dépend du générateur de parois.'}))

    # Z-hop : hauteur numérique en mm, pas une case à cocher. Certains profils
    # distinguent aussi le type de levage et sa condition d’activation.
    key,raw=first_value(config,'z_hop','retract_lift','z_hop_height')
    if key is None:
        results.append(option_row('Levage Z pendant la rétraction','',missing=True))
    else:
        h=numeric(first_item(raw))
        if h is None:
            results.append(option_row('Levage Z pendant la rétraction',f'Valeur à interpréter : {str(raw)[:80]}',
                                      f'Hauteur non numérique (clé : {key}).'))
        elif h < 0:
            results.append(option_row('Levage Z pendant la rétraction',f'{h:g} mm',
                                      'Hauteur négative inhabituelle : vérifier le profil.'))
        else:
            note=''
            if h>0 and goal=='speed':note='Le levage peut augmenter le temps de déplacement ; à conserver s’il évite les collisions.'
            results.append(option_row('Levage Z pendant la rétraction',
                f'Hauteur configurée : {h:g} mm'+(' (nulle)' if h==0 else ''),note))

    key,raw=first_value(config,'ironing_type','ironing')
    if key is None:results.append(option_row('Lissage des surfaces','',missing=True))
    else:
        enabled=ironing_enabled(raw)
        state=('Activé' if enabled is True else 'Désactivé' if enabled is False else 'Valeur non reconnue')
        if key=='ironing_type':state+=f' (mode : {translate_display(first_item(raw), key)})'
        tip=('Le lissage augmente le temps d’impression : vérifier son utilité sur la pièce.' if enabled is True and goal=='speed' else
             'Pour une surface supérieure plane et visible, le lissage peut être testé.' if enabled is False and goal=='quality' else '')
        results.append(option_row('Lissage des surfaces',state,tip,key))

    results.append(boolean_option(config,'Supports activés',
        ('enable_support','support_material'),goal,
        {('balanced',True):'Vérifier dans l’aperçu que les supports sont nécessaires.',
         ('quality',True):'Vérifier les surfaces de contact des supports dans l’aperçu.',
         ('balanced',False):'En présence de surplombs non imprimables, examiner les supports ou l’orientation.',
         ('quality',False):'Si des surplombs ne sont pas imprimables, examiner les supports ou l’orientation.'}))

    # Refroidissement : fan_always_on décrit le ventilateur permanent, PAS
    # l’existence du refroidissement. Lire plutôt les consignes min/max.
    key,raw=first_value(config,'fan_max_speed','max_fan_speed','fan_min_speed','min_fan_speed')
    if key is not None:
        maxkey,maxraw=first_value(config,'fan_max_speed','max_fan_speed')
        minkey,minraw=first_value(config,'fan_min_speed','min_fan_speed')
        vmax=numeric(first_item(maxraw)) if maxkey else None
        vmin=numeric(first_item(minraw)) if minkey else None
        parts=[]
        if vmin is not None:parts.append(f'min {vmin:g} %')
        if vmax is not None:parts.append(f'max {vmax:g} %')
        state='Consignes : '+', '.join(parts) if parts else f'Valeur : {raw}'
        tip=''
        if vmax is not None and (vmax<0 or vmax>100):tip='Consigne hors de la plage 0–100 % : vérifier le profil.'
        elif vmax is not None and vmin is not None and vmin>vmax:tip='La consigne minimale dépasse la maximale : vérifier le profil.'
        results.append(option_row('Ventilateur de refroidissement',state,tip))
    else:
        key,raw=first_value(config,'fan_always_on','cooling')
        if key is None:results.append(option_row('Ventilateur de refroidissement','',missing=True))
        else:
            v=parse_bool(raw)
            label=('Ventilation permanente : '+('oui' if v else 'non')) if v is not None and key=='fan_always_on' else f'Option {key} : {raw}'
            results.append(option_row('Ventilateur de refroidissement',label,
                'Cette option ne suffit pas à déterminer les vitesses réelles du ventilateur.'))

    # La rétraction peut être définie par sa longueur, par le firmware ou par
    # des options auxiliaires. retract_when_changing_layer n’active PAS la rétraction.
    key,raw=first_value(config,'retraction_length','retract_length','filament_retraction_length')
    fwkey,fwraw=first_value(config,'use_firmware_retraction')
    fw=parse_bool(fwraw) if fwkey else None
    if key is not None:
        distance=numeric(first_item(raw))
        if distance is None:results.append(option_row('Rétraction',f'Valeur : {raw}',
                                                    'Longueur de rétraction non numérique.'))
        else:
            state=f'Longueur configurée : {distance:g} mm'
            if fw is True:state+=' ; rétraction firmware activée'
            elif fw is False:state+=' ; rétraction firmware désactivée'
            results.append(option_row('Rétraction',state))
    elif fwkey is not None:
        results.append(option_row('Rétraction',
            'Rétraction firmware '+('activée' if fw else 'désactivée') if fw is not None else f'Option firmware : {fwraw}',
            'La longueur de rétraction n’est pas exposée : impossible de conclure sur la rétraction effective.'))
    else:results.append(option_row('Rétraction','',missing=True))

    # Ordre des parois : l’enum wall_sequence est plus précis qu’un booléen.
    key,raw=first_value(config,'wall_sequence','external_perimeters_first','outer_wall_first')
    if key is None:results.append(option_row('Ordre d’impression des parois','',missing=True))
    elif key=='wall_sequence':
        v=str(first_item(raw)).strip()
        known={'inner wall/outer wall':'Interne → externe',
               'outer wall/inner wall':'Externe → interne',
               'inner/outer':'Interne → externe','outer/inner':'Externe → interne',
               'inner wall/outer wall/inner wall':'Interne → externe → interne',
               'inner/outer/inner':'Interne → externe → interne'}
        state=known.get(v.lower(),f'Ordre configuré : {translate_display(v, key)}')
        results.append(option_row('Ordre d’impression des parois',state))
    else:
        enabled=parse_bool(raw)
        state=('Paroi externe en premier' if enabled else 'Paroi interne en premier') if enabled is not None else f'Valeur : {raw}'
        results.append(option_row('Ordre d’impression des parois',state))
    # Conseils contextuels sur les options : éviter d'assimiler « désactivé » à un défaut.
    # Les règles sans information de géométrie sont explicitement conditionnelles.
    contextual = {
        'Éviter de traverser les parois': {
            ('quality',False): 'Si des marques de déplacement apparaissent, essayer d’activer cette option ; vérifier l’aperçu des trajectoires.',
            ('speed',True): 'Cette option peut rallonger les déplacements : comparer les temps estimés avant de la désactiver.'},
        'Détection des parois fines': {
            ('quality',False): 'Si des détails fins disparaissent dans l’aperçu, tester cette option et comparer les trajectoires.',
            ('speed',True): 'Vérifier que cette option est nécessaire pour la géométrie ; elle peut générer de petits mouvements.'},
        'Supports activés': {
            ('speed',True): 'Contrôler les surplombs dans l’aperçu : supprimer uniquement les supports inutiles.',
            ('balanced',True): 'Si les supports consomment beaucoup de filament, vérifier les surplombs et comparer une autre orientation ; ne retirer que les supports inutiles.',
            ('strength',False): 'Pour des surplombs importants, vérifier l’aperçu et l’orientation avant de conclure que les supports sont inutiles.'},
    }
    for row in results:
        rules=contextual.get(row['name'],{})
        if row['value']=='Activée': active=True
        elif row['value']=='Désactivée': active=False
        else:continue
        tip=rules.get((goal,active))
        if tip and not row['comment']:
            row.update(comment=tip,status='Optimisation conditionnelle',level='warn')
    option_keys = {
        'Éviter de traverser les parois': ('reduce_crossing_wall','avoid_crossing_perimeters'),
        'Détection des parois fines': ('detect_thin_wall','thin_walls'),
        'Levage Z pendant la rétraction': ('z_hop','retract_lift','z_hop_height'),
        'Lissage des surfaces': ('ironing_type','ironing'),
        'Supports activés': ('enable_support','support_material'),
        'Ventilateur de refroidissement': ('fan_max_speed','max_fan_speed','fan_min_speed','min_fan_speed','fan_always_on','cooling'),
        'Rétraction': ('retraction_length','retract_length','filament_retraction_length','use_firmware_retraction'),
        'Ordre d’impression des parois': ('wall_sequence','external_perimeters_first','outer_wall_first'),
    }
    for row in results:
        row['key'] = next((k for k in option_keys.get(row['name'], ()) if k in config), '')
    return results

# Plages de vigilance purement indicatives pour filaments standards, non
# spécifiques à la Kobra 3 et jamais considérées comme des limites fabricant.
# Les versions haute vitesse / débit élevé exigent une calibration dédiée.
FLOW_ADVISORY = {
    # (bas, haut, libellé) : repères de départ indicatifs, non certifiés.
    'PLA': (10.0, 18.0, 'PLA standard'),
    'PETG': (8.0, 15.0, 'PETG standard'),
    'ABS': (10.0, 20.0, 'ABS standard'),
    'ASA': (10.0, 18.0, 'ASA standard'),
    'TPU': (3.0, 8.0, 'TPU souple'),
}

def material_name(config, filament_names=()):
    raw = config.get('filament_type')
    if isinstance(raw, (list, tuple)):
        raw = raw[0] if raw else None
    if raw is not None and str(raw).strip():
        return str(raw).strip()
    # Le nom du preset n'est pas une preuve suffisante du type de matière.
    return None

def volumetric_advice(flow, material, filament_names=()):
    if flow is None or flow <= 0:
        return ('À vérifier', 'warn', 'Débit volumétrique non positif ou non exploitable : vérifier le profil filament.') if flow is not None else ('Non vérifiable','muted','')
    if not material:
        return ('Information','ok','Type de matière non renseigné : aucun débit conseillé fiable sans identification du filament.')
    upper = str(material).strip().upper()
    if 'TPU' in upper or 'TPE' in upper: group='TPU'
    elif 'PETG' in upper: group='PETG'
    elif 'ASA' in upper: group='ASA'
    elif 'ABS' in upper: group='ABS'
    elif 'PLA' in upper: group='PLA'
    else: group=None
    if group is None:
        return ('Information','ok',f'Pas de plage indicative disponible pour {material} : consulter la fiche fabricant et calibrer le débit maximal.')
    low, high, standard = FLOW_ADVISORY[group]
    names = ' '.join(str(x) for x in filament_names).lower()
    highspeed = any(term in (upper+' '+names).lower() for term in ('high speed','high-speed','high flow','high-flow','hyper','rapid','hs-'))
    if highspeed:
        if flow > high:
            return ('À confirmer','warn',f'Débit configuré : {flow:g} mm³/s. Le repère pour {standard} est {low:g}–{high:g} mm³/s, mais ce filament semble haute vitesse : ne pas lui appliquer ce plafond standard. Débit conseillé : celui mesuré par calibration sur cette imprimante, à la température utilisée, ou la valeur documentée par le fabricant.')
        if flow < low:
            return ('Optimisation possible','warn',
                    f'Débit configuré : {flow:g} mm³/s, inférieur même au repère standard de {low:g}–{high:g} mm³/s pour {standard}. '
                    'Ce filament semble haute vitesse : sa plage réelle doit être confirmée par le fabricant ou par calibration. '
                    'Un débit aussi bas peut ralentir l’impression, sans être dangereux.')
        return ('Conforme','ok','')
    if flow < low:
        return ('Optimisation possible','warn',
                f'Débit configuré : {flow:g} mm³/s, inférieur au repère indicatif de {low:g}–{high:g} mm³/s pour {standard}. '
                f'Cela ne présente pas de risque de sous-extrusion en soi, mais peut ralentir fortement l’impression. '
                f'Si la qualité est bonne, essayer progressivement {low:g} mm³/s, puis calibrer le débit maximal pour ce filament, '
                f'cette température et cette tête d’impression. Ne pas augmenter sans vérification.')
    if flow > high:
        return ('Calibration conseillée','warn',f'Débit configuré : {flow:g} mm³/s. Pour {standard}, plage de départ conseillée : {low:g}–{high:g} mm³/s (repère indicatif, non constructeur). Essayer au plus {high:g} mm³/s en attendant une calibration du débit maximal, puis retenir la valeur mesurée pour ce filament, cette température et cette tête d’impression.')
    return ('Conforme','ok','')

# Repères de diagnostic seulement : le ratio de débit correct doit être calibré.
# Les filaments chargés, expansifs ou spéciaux peuvent nécessiter d'autres valeurs.
def flow_ratio_advice(ratio, material):
    if ratio is None:
        return ('Non vérifiable', 'muted', '')
    if ratio <= 0:
        return ('Anomalie', 'err', 'Ratio de débit nul ou négatif : vérifier le profil filament.')
    if ratio < 0.85 or ratio > 1.15:
        return ('Calibration prioritaire', 'warn',
                f'Ratio configuré : {ratio:g}. Valeur très éloignée de 1,00 ; risque de sous-extrusion ou de surextrusion. '
                'Vérifier les unités et réaliser une calibration du ratio de débit dans OrcaSlicer avant de modifier le profil.')
    if ratio < 0.95:
        return ('À vérifier', 'warn',
                f'Ratio configuré : {ratio:g}, inférieur au repère indicatif 0,95–1,05. '
                'Cela peut être normal après calibration. Si aucune calibration n’a été faite, '
                'tester le ratio de débit avec le filament et la température actifs ; ne pas augmenter automatiquement.')
    if ratio > 1.05:
        return ('À vérifier', 'warn',
                f'Ratio configuré : {ratio:g}, supérieur au repère indicatif 0,95–1,05. '
                'Cela peut être normal après calibration. Si aucune calibration n’a été faite, '
                'vérifier le ratio de débit pour éviter une éventuelle surextrusion ; ne pas diminuer automatiquement.')
    return ('Conforme', 'ok', '')

def analyze_config(config, goal="balanced", filament_names=()):
    """Conseils non intrusifs fondés sur la configuration active résolue."""
    rows=[]
    if goal not in ('balanced','quality','strength','speed'):
        goal='balanced'
    def number(*keys):
        for key in keys:
            if key in config:
                n=numeric(config[key])
                if n is not None:return n
        return None
    nozzle=number('nozzle_diameter')
    layer=number('layer_height')
    flow_limit=number('filament_max_volumetric_speed')
    material=material_name(config, filament_names)
    infill=number('sparse_infill_density','fill_density')
    walls=number('wall_loops','perimeters')
    # Largeurs de ligne propres à chaque famille de mouvements. Les valeurs 0
    # signifient souvent « automatique » : ne pas les traiter comme 0 mm.
    widths={
        'Vitesse paroi externe':('outer_wall_line_width','external_perimeter_extrusion_width'),
        'Vitesse paroi interne':('inner_wall_line_width','perimeter_extrusion_width'),
        'Vitesse remplissage':('sparse_infill_line_width','infill_extrusion_width'),
        'Vitesse remplissage plein':('internal_solid_infill_line_width','solid_infill_extrusion_width'),
        'Vitesse surface supérieure':('top_surface_line_width','top_infill_extrusion_width'),
        'Vitesse première couche':('initial_layer_line_width','first_layer_extrusion_width'),
    }
    def width_for(label):
        # Une largeur explicitement définie peut être en mm ou en % du diamètre.
        for key in (*widths[label],'line_width','extrusion_width'):
            if key not in config:continue
            raw=config[key]
            if isinstance(raw,(list,tuple)):raw=raw[0] if raw else None
            w=numeric(raw)
            if w is None or w<=0:continue
            if isinstance(raw,str) and '%' in raw:
                return (nozzle*w/100,'profil') if nozzle and nozzle>0 else (None,None)
            return w,'profil'
        # Pour les profils à largeur automatique, la valeur exacte calculée par
        # OrcaSlicer n'est pas forcément exposée par l'API.
        return None,None
    for label,aliases,unit in FIELDS:
        key=next((k for k in aliases if k in config and config[k] is not None),None)
        val=config.get(key) if key else None
        n=numeric(val)
        status,level,comment='Conforme','ok',''
        if key is None:
            status,level='Non disponible','muted'
        elif label=='Densité de remplissage' and n is not None:
            if n<0 or n>100:
                status,level,comment='Anomalie','err','La densité de remplissage doit être comprise entre 0 et 100 %. Vérifier le profil.'
            elif n>60 and goal not in ('strength','speed'):
                status,level,comment='Conseil','warn','Remplissage très élevé : vérifier si la pièce exige cette densité. Des parois supplémentaires sont souvent plus efficaces pour certaines sollicitations.'
            elif n>35 and goal=='balanced':
                status,level,comment='Optimisation','warn','Remplissage élevé : essayer 15 à 25 % si la géométrie et la résistance le permettent ; comparer également la consommation de matière.'
            elif n<10 and goal=='strength':
                status,level,comment='Conseil','warn','Remplissage faible pour un objectif de solidité : vérifier les charges, l’orientation et les parois avant d’augmenter la densité.'
        elif label=='Nombre de parois' and n is not None:
            if n<1:
                status,level,comment='À examiner','warn','Aucune paroi : vérifier que le modèle et le mode d’impression le permettent.'
            elif n==1 and goal!='speed':
                status,level,comment='Conseil','warn','Une seule paroi peut être fragile : envisager 2 à 3 parois selon la pièce.'
            elif n<=2 and goal=='strength':
                status,level,comment='Conseil','warn','Pour une pièce sollicitée, envisager 3 à 4 parois ; deux parois ne sont pas une erreur en soi.'
            elif n==2 and infill is not None and infill>=35 and goal in ('balanced',):
                status,level,comment='Optimisation','warn','Remplissage élevé avec deux parois : envisager une paroi supplémentaire et moins de remplissage, après essai.'
        elif label=='Hauteur de couche' and n is not None and nozzle:
            if goal=='quality' and n>nozzle*0.5 and n<=nozzle*0.8:
                low=nozzle*0.3
                high=nozzle*0.4
                compromise=nozzle*0.5
                status,level,comment='Optimisation','warn',f'Pour privilégier la finition, essayer une hauteur de couche de {low:.2f} à {high:.2f} mm avec une buse de {nozzle:g} mm ; {compromise:.2f} mm est un compromis qualité/temps. La hauteur actuelle de {n:g} mm privilégie davantage la rapidité. Ces valeurs sont indicatives.'
            elif n>nozzle*0.8:
                status,level,comment='À examiner','warn',(f'Hauteur élevée pour une buse de {nozzle:g} mm : en mode Qualité, essayer {nozzle*0.3:.2f} à {nozzle*0.4:.2f} mm.' if goal=='quality' else 'Hauteur supérieure à 80 % du diamètre de buse : réduire la hauteur (règle indicative).')
            elif n<nozzle*0.2 and goal=='speed':
                status,level,comment='Conseil','warn','Hauteur très faible pour cette buse : impression potentiellement longue sans gain visible sur toutes les pièces.'
        elif label=='Motif de remplissage' and isinstance(val,str) and val.lower() in ('grid','grille'):
            if goal=='speed':
                status,level,comment='Conseil','warn','La grille peut accumuler du plastique aux croisements. Pour gagner du temps, comparer avec un remplissage rectiligne dans l’aperçu et le temps estimé.'
            elif goal=='strength':
                status,level,comment='Conseil','warn','Pour une pièce mécanique, comparer grille, cubique et gyroïde selon la direction des efforts ; l’orientation et les parois restent déterminantes.'
            elif goal=='quality':
                status,level,comment='Conseil','warn','Les croisements de la grille peuvent créer des surépaisseurs et des contacts avec la buse. Tester le rectiligne ou le gyroïde si ce défaut apparaît.'
            else:
                status,level,comment='Conseil','warn','La grille croise les lignes sur une même couche. Le rectiligne limite les croisements ; le gyroïde convient à de nombreuses géométries.'
        elif label=='Débit volumétrique filament':
            status,level,comment=volumetric_advice(n,material,filament_names)
        elif label=='Couches supérieures' and n is not None and layer and layer>0:
            thickness=n*layer
            if n<2 and infill is not None and infill>0:
                status,level,comment='Conseil','warn','Très peu de couches supérieures : risque de fermeture incomplète au-dessus du remplissage.'
            elif thickness<0.6 and goal in ('balanced','quality','strength') and infill is not None and infill>0:
                status,level,comment='Optimisation','warn',f'Épaisseur supérieure ≈ {thickness:.2f} mm. Envisager environ 0,6 à 1 mm selon matériau, portée et finition.'
        elif label=='Couches inférieures' and n is not None and n<2 and goal in ('balanced','strength'):
            status,level,comment='Conseil','warn','Très peu de couches inférieures : vérifier la tenue du fond de la pièce.'
        elif label=='Vitesse première couche' and n is not None and n>80 and goal in ('quality','balanced'):
            status,level,comment='Conseil','warn','Première couche rapide : en cas de défaut d’adhérence, tester une vitesse inférieure. Ce seuil est indicatif, pas constructeur.'
        elif label=='Accélération impression' and n is not None:
            machine_acc=number('machine_max_acceleration_extruding','machine_max_acceleration_x')
            if machine_acc and n>machine_acc:
                status,level,comment='À examiner','warn',f'Accélération demandée supérieure à la limite déclarée dans le profil machine ({machine_acc:g} mm/s²). Vérifier le firmware et le profil.'
        elif label=='Ventilation maximale' and n is not None and (n<0 or n>100):
            status,level,comment='Anomalie','err','Ventilation hors plage 0–100 % : vérifier la valeur et son unité.'
        elif label=='Ratio de débit':
            status,level,comment=flow_ratio_advice(n,material)
        elif label=='Température buse' and n is not None:
            max_temp=number('nozzle_max_temperature','machine_max_nozzle_temperature')
            if max_temp and n>max_temp:
                status,level,comment='Anomalie','err',f'Température supérieure à la limite machine déclarée ({max_temp:g} °C).'
        # Les conseils restent volontairement vides quand aucune incohérence vérifiable n'est détectée.
        display=show(translate_display(val, key) if isinstance(val, (str,list,tuple)) else val,unit)
        if unit=='%' and display.endswith('% %'):display=display[:-2].rstrip()
        rows.append({'name':label,'key':key or '', 'value':display,'status':status,'level':level,'comment':comment})
    rows.append({'name':'Matière du filament', 'key':'filament_type', 'value':material or 'Non renseignée',
                 'status':'Information' if material else 'Non vérifiable',
                 'level':'ok' if material else 'muted', 'comment':''})
    return rows

def analyze_cross_checks(config, goal='balanced', filament_names=()):
    """V32.4 : vérifications croisées contextuelles sans supposer la géométrie."""
    out=[]
    def num(*keys):
        _, raw=first_value(config,*keys)
        return numeric(raw)
    def val(*keys):
        _, raw=first_value(config,*keys)
        return first_item(raw)
    def flag(*keys):
        return parse_bool(val(*keys))
    def add(name, comment, status='À vérifier', level='warn'):
        key_map = {
            'Compromis hauteur / finition':'layer_height',
            'Temps et hauteur de couche':'layer_height',
            'Temps et remplissage':'sparse_infill_density',
            'Motif et temps':'sparse_infill_pattern',
            'Parois et temps':'outer_wall_speed',
            'Remplissage et temps':'sparse_infill_speed',
            'Temps et épaisseur supérieure':'top_shell_layers',
            'Hauteur de couche et débit':'layer_height',
            'Cohésion des couches':'layer_height',
            'Compromis parois / remplissage':'wall_loops',
            'Résistance et matière':'wall_loops',
            'Épaisseur du fond':'bottom_shell_layers',
            'Accélération des contours':'outer_wall_acceleration',
            'Qualité des dessus':'top_shell_layers',
            'Fines couches et dessus':'top_surface_speed',
            'Dessus et faible remplissage':'top_shell_layers',
            'Finition des parois':'outer_wall_speed',
            'Surface supérieure':'top_surface_speed',
            'Adhérence première couche':'initial_layer_speed',
            'Fermeture des surfaces':'top_shell_layers',
            'Supports et rapidité':'enable_support',
            'Lissage et temps':'ironing_type',
            'Refroidissement':'fan_min_speed',
            'Refroidissement et matière':'fan_min_speed',
            'Rétraction':'retraction_length',
        }
        candidate = key_map.get(name, '')
        alternatives = {
            'outer_wall_speed':('external_perimeter_speed',),
            'top_surface_speed':('top_solid_infill_speed',),
            'initial_layer_speed':('first_layer_speed',),
            'top_shell_layers':('top_solid_layers',),
            'bottom_shell_layers':('bottom_solid_layers',),
            'sparse_infill_density':('fill_density',),
            'sparse_infill_pattern':('fill_pattern',),
            'sparse_infill_speed':('infill_speed',),
            'wall_loops':('perimeters',),
            'outer_wall_acceleration':('external_perimeter_acceleration',),
            'enable_support':('support_material',),
            'ironing_type':('ironing',),
            'fan_min_speed':('min_fan_speed',),
            'retraction_length':('retract_length','filament_retraction_length'),
        }
        key = next((k for k in (candidate, *alternatives.get(candidate, ())) if k in config), candidate)
        display_value = translate_display(first_item(config.get(key))) if key and key in config else ''
        out.append(dict(name=name, key=key, value=display_value, comment=comment, status=status, level=level))
    layer=num('layer_height'); nozzle=num('nozzle_diameter')
    outer=num('outer_wall_speed','external_perimeter_speed')
    top=num('top_surface_speed','top_solid_infill_speed')
    inner=num('inner_wall_speed','perimeter_speed')
    first=num('initial_layer_speed','first_layer_speed')
    material=material_name(config,filament_names)
    if goal=='quality' and outer is not None and inner is not None and outer>inner:
        add('Finition des parois',f'Paroi externe ({outer:g} mm/s) plus rapide que la paroi interne ({inner:g} mm/s). Conseil : ralentissez légèrement la paroi externe pour améliorer l’aspect, puis comparez sur une pièce test.')
    if goal=='quality' and top is not None and outer is not None and top>outer*1.5:
        add('Surface supérieure',f'Surface supérieure à {top:g} mm/s contre {outer:g} mm/s pour la paroi externe : le dessus peut présenter davantage de marques. Conseil : essayez de réduire la vitesse du dessus et comparez le résultat.')
    if first is not None and outer is not None and first>outer and goal in ('quality','balanced'):
        add('Adhérence première couche',f'Première couche à {first:g} mm/s, plus rapide que la paroi externe ({outer:g} mm/s). une première couche trop rapide peut moins bien adhérer. Conseil : ralentissez-la si vous constatez un décollement.')
    tops=num('top_shell_layers','top_solid_layers'); infill=num('sparse_infill_density','fill_density')
    if goal in ('quality','balanced','strength') and tops is not None and layer and infill is not None and infill>0 and tops*layer<0.6:
        add('Fermeture des surfaces',f'Épaisseur de dessus ≈ {tops*layer:.2f} mm sur remplissage {infill:g} %. le dessus risque de laisser voir le remplissage. Conseil : ajoutez des couches supérieures si des trous ou des marques apparaissent.')
    # Ne pas prétendre voir les surplombs du modèle depuis le profil seul.
    support=flag('enable_support','support_material')
    if support is True and goal=='speed':
        add('Supports et rapidité','Les supports peuvent rallonger l’impression. Conseil : vérifiez dans l’aperçu s’ils sont nécessaires ou si une autre orientation permet de les réduire.')
    if support is False and goal=='quality':
        # Pas d'alerte sans géométrie ; absence de supports n'est pas un défaut.
        pass
    ironing=val('ironing_type','ironing')
    if ironing is not None and goal=='speed':
        enabled=ironing_enabled(ironing)
        if enabled is True:add('Lissage et temps','Le lissage peut augmenter le temps d’impression. Conseil : comparez la durée avec et sans lissage et désactivez-le si la finition du dessus est inutile.')
    # Le fan_min/max ne permet pas de conclure seul au refroidissement effectif.
    fan_min=num('fan_min_speed','min_fan_speed');fan_max=num('fan_max_speed','max_fan_speed')
    if fan_min is not None and fan_max is not None and fan_min>fan_max:
        add('Refroidissement',f'Consigne minimale ({fan_min:g} %) supérieure à la maximale ({fan_max:g} %) : contrôler le profil filament.','Incohérence','err')
    if goal in ('quality','strength','balanced') and material in ('ABS','ASA') and fan_min is not None and fan_min>=80:
        add('Refroidissement et matière',f'Ventilation minimale de {fan_min:g} % avec {material} : vérifier la compatibilité avec le filament et le risque de déformation. Les ventilateurs de ponts peuvent avoir d’autres consignes.')
    # Rétraction : conseil seulement en présence de valeurs clairement suspectes.
    retract=num('retraction_length','retract_length','filament_retraction_length')
    if retract is not None and retract<0:
        add('Rétraction','La rétraction ne peut pas avoir une longueur négative. Conseil : corrigez ce réglage dans le profil.','Incohérence','err')
    if goal in ('quality','balanced') and retract is not None and retract>8:
        add('Rétraction',f'Rétraction de {retract:g} mm : valeur élevée pour de nombreuses configurations ; vérifier le type d’extrudeur et les tests de rétraction, sans appliquer une valeur universelle.')
    # Conseils ciblés par objectif, déclenchés uniquement avec des valeurs exploitables.
    # Les seuils sont des repères de discussion, jamais des limites universelles.
    walls=num('wall_loops','perimeters')
    bottom=num('bottom_shell_layers','bottom_solid_layers')
    pattern=str(val('sparse_infill_pattern','fill_pattern') or '').strip().lower()
    speed_infill=num('sparse_infill_speed','infill_speed')
    acceleration_outer=num('outer_wall_acceleration','external_perimeter_acceleration')
    acceleration_print=num('default_acceleration','printing_acceleration')
    if goal=='balanced':
        if walls is not None and infill is not None and walls<=2 and infill>=30:
            add('Compromis parois / remplissage',f'{walls:g} parois et {infill:g} % de remplissage : selon les efforts, essayer une paroi supplémentaire et un remplissage plus modéré, puis comparer temps et résistance.')
        if layer and nozzle and layer>nozzle*0.65 and layer<=nozzle*0.8:
            add('Compromis hauteur / finition',f'Hauteur de {layer:g} mm avec buse de {nozzle:g} mm : pour un aspect plus fin, comparer avec environ {nozzle*0.5:.2f} mm, sans obligation de modifier le profil.')
    elif goal=='quality':
        if outer and top and top>outer*1.2 and top<=outer*1.5:
            add('Finition des surfaces',f'Surface supérieure à {top:g} mm/s et paroi externe à {outer:g} mm/s : si des marques apparaissent sur le dessus, tester une vitesse supérieure plus proche de celle des parois.')
        if acceleration_outer and acceleration_print and acceleration_outer>=acceleration_print and acceleration_print>0:
            add('Accélération des contours',f'Accélération externe {acceleration_outer:g} mm/s² égale ou supérieure à celle d’impression ({acceleration_print:g} mm/s²) : si des vibrations marquent les contours, essayer une accélération externe plus basse après calibration.')
        if infill is not None and infill<10 and tops is not None and tops<=3 and layer:
            add('Qualité des dessus',f'{infill:g} % de remplissage et {tops:g} couches supérieures : vérifier dans l’aperçu la portée des pontages sous les surfaces visibles ; renforcer le dessus si des creux apparaissent.')
    elif goal=='strength':
        if walls is not None and walls<3:
            # Déjà conseillé par le tableau Paramètres : ne pas dupliquer.
            pass
        if infill is not None and infill>=45 and walls is not None and walls<=3:
            add('Résistance et matière',f'{infill:g} % de remplissage avec {walls:g} parois : envisager davantage de parois plutôt qu’un remplissage encore plus dense, puis tester la pièce dans son sens de sollicitation.')
        if layer and nozzle and layer>nozzle*0.75 and layer<=nozzle*0.8:
            add('Cohésion des couches',f'Hauteur de {layer:g} mm proche de la limite indicative de la buse ({nozzle:g} mm). Pour une pièce sollicitée, comparer une couche plus modérée et vérifier la température et l’adhésion inter-couches.')
        if bottom is not None and layer and bottom*layer<0.6 and bottom>=2:
            add('Épaisseur du fond',f'Fond ≈ {bottom*layer:.2f} mm : si la pièce doit supporter des efforts ou des fixations, envisager davantage de couches inférieures selon la géométrie.')
    elif goal=='speed':
        if layer and nozzle and 0<layer<nozzle*0.4:
            add('Temps et hauteur de couche',f'Hauteur de {layer:g} mm pour une buse de {nozzle:g} mm : une hauteur proche de {nozzle*0.5:.2f} mm peut réduire le nombre de couches, si la finition et les détails le permettent.')
        if infill is not None and infill>25 and infill<=60:
            add('Temps et remplissage',f'Le remplissage est à {infill:g} %. Pour une pièce décorative, essayez 15 à 20 % et comparez le temps estimé. Vérifiez que les couches du dessus restent bien soutenues.')
        if pattern in ('gyroid','honeycomb','3d honeycomb') and infill is not None and infill>0:
            add('Motif et temps',f'Motif {translate_display(pattern)} : le rectiligne peut être plus rapide sur certaines pièces. Comparer le temps estimé et conserver le motif actuel si ses propriétés mécaniques sont nécessaires.')
        if outer and inner and outer<inner*0.45:
            add('Parois et temps',f'Paroi externe à {outer:g} mm/s contre {inner:g} mm/s en interne : si l’aspect est secondaire, comparer une vitesse externe un peu plus élevée, dans les limites validées de la machine et du filament.')
        if speed_infill and outer and speed_infill<outer*0.7:
            add('Remplissage et temps',f'Remplissage à {speed_infill:g} mm/s contre {outer:g} mm/s pour les contours : si le profil est calibré, comparer un remplissage plus rapide sans dépasser les limites de débit ni dégrader l’adhérence.')
    # V32.4 : relations multi-paramètres. Ce sont des hypothèses à vérifier,
    # jamais une prédiction de la qualité d'une géométrie inconnue.
    line_width=num('line_width','extrusion_width')
    if line_width is None or line_width<=0:
        # La largeur automatique est résolue par le slicer ; ne pas l'inventer.
        line_width=None
    if line_width and nozzle and line_width>nozzle*2:
        add('Largeur et diamètre de buse',
            f'Largeur de ligne {line_width:g} mm pour une buse de {nozzle:g} mm : vérifier la largeur choisie et la compatibilité avec le profil.',
            'Incohérence possible','warn')
    first_layer=num('initial_layer_print_height','first_layer_height')
    if first_layer and nozzle and first_layer>nozzle*0.8:
        add('Première couche et buse',
            f'Première couche de {first_layer:g} mm avec une buse de {nozzle:g} mm : '
            'hauteur supérieure au repère indicatif de 80 % du diamètre. Vérifier l’adhérence et la calibration.')
    if tops is not None and layer and infill is not None and infill>0 and tops*layer>=0.6 and infill<8 and goal=='quality':
        add('Dessus et faible remplissage',
            f'Le dessus mesure environ {tops*layer:.2f} mm, mais le remplissage est de {infill:g} %. '
            'Une grande portée entre lignes de remplissage peut marquer le dessus : vérifier les pontages dans l’aperçu.')
    if goal=='strength' and walls is not None and infill is not None and walls>=4 and infill>=60:
        add('Matière et solidité',
            f'{walls:g} parois et {infill:g} % de remplissage : forte consommation potentielle. '
            'La résistance dépend aussi de l’orientation, de l’adhésion des couches et du sens de charge ; '
            'tester une éprouvette avant d’augmenter davantage la matière.')
    if goal=='speed' and tops is not None and layer and tops*layer>1.6 and infill is not None and infill>0:
        add('Temps et épaisseur supérieure',
            'Un dessus très épais peut allonger l’impression. Conseil : si cette surface n’a pas besoin d’être résistante, testez moins de couches supérieures en vérifiant qu’aucun trou n’apparaît.')
    if goal=='quality' and layer and nozzle and outer and top and layer<=nozzle*0.45 and top>outer*1.6:
        add('Fines couches et dessus',
            f'Couches fines ({layer:g} mm) mais surface supérieure à {top:g} mm/s '
            f'contre {outer:g} mm/s pour la paroi externe : la finition du dessus peut limiter le gain de qualité. '
            'Comparer une vitesse supérieure plus modérée sur une pièce test.')
    if False:  # Retiré : conseil trop vague sur le débit, sans réglage directement utile.
        # Ne pas prétendre qu'une grande hauteur accélère systématiquement :
        # elle augmente le débit demandé à vitesse identique.
        add('Hauteur de couche et débit',
            'Des couches plus épaisses ne rendent pas toujours l’impression plus rapide : le filament peut atteindre sa limite de débit. Conseil : comparez le temps estimé et la vue « débit volumétrique » dans l’aperçu.')
    if not out:
        out.append(dict(name='Contrôles croisés',status='Aucun signal détecté',level='ok',comment='Aucune incohérence démontrable avec les paramètres croisés disponibles. Cela ne valide pas la géométrie ni la calibration du filament.'))
    return out

# Analyse prudente du G-code personnalisé : aucune alerte pour les séquences
# dont la validité dépend du firmware ou des macros du slicer.
GCODE_SECTIONS = {
    'Démarrage': ('machine_start_gcode','start_gcode'),
    'Fin': ('machine_end_gcode','end_gcode'),
    'Changement de filament': ('machine_filament_change_gcode','change_filament_gcode'),
    'Démarrage filament': ('filament_start_gcode',),
    'Fin filament': ('filament_end_gcode',),
}

def _script_text(raw):
    """Normalize string/list/wrapper/JSON-encoded script values without executing them."""
    import json
    if raw is None:
        return ''
    if isinstance(raw, bytes):
        return _script_text(raw.decode('utf-8', errors='replace'))
    if isinstance(raw, (list, tuple)):
        return '\n'.join(_script_text(item) for item in raw)
    if isinstance(raw, dict):
        for key in ('value', 'gcode', 'script', 'text'):
            if key in raw:
                return _script_text(raw[key])
        return str(raw)
    if not isinstance(raw, str):
        for attr in ('value', 'get_value'):
            value = getattr(raw, attr, None)
            if value is not None:
                try:
                    return _script_text(value() if callable(value) else value)
                except Exception:
                    pass
        return str(raw)
    text = raw.strip()
    # JSON arrays, JSON strings and some serialized profile values.
    if text.startswith(('[', '"', '{')):
        try:
            decoded = json.loads(text)
            if decoded != text:
                return _script_text(decoded)
        except (ValueError, TypeError, RecursionError):
            pass
    # Some API wrappers expose literal backslash-n rather than newlines.
    if '\n' not in text and (r'\n' in text or r'\r' in text):
        text = text.replace(r'\r\n', '\n').replace(r'\n', '\n').replace(r'\r', '\n')
    return text


def analyze_gcode(config):
    """Audit statique conservateur des scripts personnalisés, sans exécution.

    Ne prétend pas interpréter les macros propriétaires ni le G-code généré
    après découpage. Les limites machine ne sont utilisées que si explicites.
    """
    import re
    alerts, diagnostics = [], []
    def add(section, line, problem, advice, level='err'):
        alerts.append(dict(section=section, problem=f'Ligne {line} : {problem}',
                           advice=advice, level=level))
    def number(text, letter):
        m = re.search(r'(?<![A-Za-z_])'+letter+r'\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+))(?![\w.])', text, re.I)
        return float(m.group(1)) if m else None
    # Seules les limites de dimensions explicitement disponibles sont fiables.
    def limit(*keys):
        for k in keys:
            if k in config:
                v=numeric(first_item(config[k]))
                if v is not None and v>0:return v
        return None
    x_max=limit('printable_width','bed_size_x')
    y_max=limit('printable_depth','bed_size_y')
    for section, aliases in GCODE_SECTIONS.items():
        found=[(k,_script_text(config[k])) for k in aliases if k in config]
        key, raw=next(((k,v) for k,v in found if v.strip()),(None,''))
        if key is None:continue
        lines=raw.splitlines()
        diagnostics.append(dict(section=section,key=key,lines=len(lines)))
        xyz_absolute=True
        e_absolute=None
        homed=False
        hotend_waited=False
        for lineno,line in enumerate(lines,1):
            code=line.split(';',1)[0].strip()
            if not code or code.startswith(('#','(')):continue
            # Le code peut contenir des placeholders et des blocs conditionnels
            # OrcaSlicer. Ne pas interpréter leur syntaxe comme du G-code brut.
            if code.startswith(('{','[','}')):continue
            m=re.match(r'^([GMT]\d+(?:\.\d+)?)\b',code,re.I)
            if not m:continue
            cmd=m.group(1).upper()
            tail=code[m.end():]
            # Paramètres numériques manifestement incorrects, sans confondre
            # les placeholders du slicer avec des nombres.
            for bad in re.finditer(r'(?<![A-Za-z_])([XYZEFSPR])\s*([+-]?(?:\d+\.\d*\.|\.\.|\d+\.\d+\.))(?=\s|$)',tail,re.I):
                add(section,lineno,f'paramètre {bad.group(1).upper()} mal formé dans {cmd}.',
                    'Corriger la valeur numérique.', 'err')
            if cmd in ('M104','M109','M140','M190'):
                for letter in ('S','R'):
                    temp=number(tail,letter)
                    if temp is not None and temp<0:
                        add(section,lineno,f'{cmd} demande {temp:g} °C (température négative).',
                            'Supprimer ou corriger cette consigne avant toute impression.')
                    # Seuils conservateurs de sécurité, pas limites firmware.
                    if temp is not None and temp>(500 if cmd in ('M104','M109') else 200):
                        add(section,lineno,f'{cmd} demande {temp:g} °C, valeur exceptionnellement élevée.',
                            'Contrôler la consigne et les limites réelles de la machine avant impression.')
                if cmd=='M109' and any(number(tail,k) is not None for k in ('S','R')):
                    hotend_waited=True
            if cmd=='G28':homed=True
            if cmd=='G90':xyz_absolute=True
            if cmd=='G91':xyz_absolute=False
            if cmd=='M82':e_absolute=True
            if cmd=='M83':e_absolute=False
            if cmd in ('G0','G1'):
                feed=number(tail,'F')
                if feed is not None and feed<=0:
                    add(section,lineno,f'{cmd} contient une avance F={feed:g} non positive.',
                        'Utiliser une avance strictement positive en mm/min.')
                # Pas de contrôle de bornes sur G91 ou avant G28 : position inconnue.
                if xyz_absolute and homed:
                    for axis,maximum in (('X',x_max),('Y',y_max)):
                        pos=number(tail,axis)
                        if maximum is not None and pos is not None and (pos < -1 or pos > maximum+1):
                            add(section,lineno,f'coordonnée {axis}={pos:g} hors plage indicative 0–{maximum:g} mm.',
                                'Vérifier les dimensions et les décalages du plateau ; la zone utile peut être décentrée.', 'warn')
                extrusion=number(tail,'E')
                if extrusion is not None and extrusion>100 and e_absolute is False:
                    add(section,lineno,f'extrusion relative E={extrusion:g} mm inhabituellement élevée.',
                        'Vérifier la quantité extrudée et le mode M83 ; certains scripts de purge sont spécifiques.', 'warn')
                if extrusion is not None and extrusion>0 and not hotend_waited and section=='Démarrage':
                    # M109 peut être exécuté par le firmware ou dans une macro ;
                    # une alerte informative est préférable à un diagnostic erroné.
                    add(section,lineno,'extrusion avant attente de chauffe M109 visible dans ce script.',
                        'Vérifier si la chauffe est assurée par le firmware ou une macro ; sinon attendre la température.', 'warn')
                    hotend_waited=True # éviter les répétitions
            if cmd=='M106':
                fan=number(tail,'S')
                if fan is not None and not (0<=fan<=255):
                    add(section,lineno,f'M106 S{fan:g} hors plage habituelle 0–255.',
                        'Contrôler la commande de ventilation et le firmware.', 'warn')
            if cmd in ('M204','M205'):
                for letter in ('P','T','R','X','Y','Z','E','S'):
                    v=number(tail,letter)
                    if v is not None and v<0:
                        add(section,lineno,f'{cmd} {letter}{v:g} contient une valeur négative.',
                            'Vérifier la signification du paramètre pour le firmware utilisé.', 'warn')
    return alerts, diagnostics

# Les réglages de filament peuvent être des tableaux (un élément par bobine).
# Ne pas traiter uniquement le premier filament lors d'une impression multicolore.
FILAMENT_SETTING_KEYS = {
    'filament_type', 'filament_vendor', 'filament_max_volumetric_speed',
    'filament_flow_ratio', 'nozzle_temperature', 'nozzle_temperature_initial_layer',
    'temperature', 'fan_max_speed', 'fan_min_speed', 'overhang_fan_speed',
    'hot_plate_temp', 'bed_temperature', 'filament_retraction_length',
}
FILAMENT_ROW_KEYS = FILAMENT_SETTING_KEYS - {'filament_vendor', 'nozzle_temperature_initial_layer', 'fan_min_speed', 'filament_retraction_length'}

def per_filament_config(config, index, count):
    selected = dict(config)
    for key in FILAMENT_SETTING_KEYS:
        value = config.get(key)
        if isinstance(value, (list, tuple)) and len(value) == count:
            selected[key] = value[index]
    return selected

@orca.plugin
class PrinterAssist(orca.base):
    def register_capabilities(self):
        orca.register_capability(PrinterAssistPage)

class PrinterAssistPage(orca.pages.PagesPluginCapabilityBase):
    def get_name(self):return 'PrinterAssist'
    def get_ui(self):return HTML
    def get_icon(self):
        # Le gestionnaire d'extensions peut demander un chemin de fichier local.
        # L'icône doit être installée à côté du script Python.
        return icon_path()

    def on_message(self,data):
        if not isinstance(data,dict) or data.get('type') not in ('analyze_active','ready','get_language'):return
        if data.get('type') == 'get_language':
            self.post_message({'type':'pa_language','language':_orca_language()})
            return
        try:
            goal=data.get('goal','balanced')
            bundle=orca.host.preset_bundle()
            keys=bundle.full_config_keys()
            config={}
            for key in keys:
                try:config[key]=bundle.full_config_value(key)
                except Exception:pass
            def preset_name(p):
                if p is None:return 'Indisponible'
                name=getattr(p,'name',None)
                if callable(name):name=name()
                return str(name) if name else 'Profil actif'
            process=preset_name(bundle.current_process_preset())
            machine=preset_name(bundle.current_printer_preset())
            filaments=[str(x) for x in bundle.current_filament_preset_names()]
            gcode_alerts, _gcode_debug = analyze_gcode(config)
            filament_rows=[]
            if len(filaments)>1:
                for index, filament_name in enumerate(filaments):
                    selected=per_filament_config(config,index,len(filaments))
                    for row in analyze_config(selected,goal,[filament_name]):
                        if row.get('key') in FILAMENT_ROW_KEYS and row.get('level') in ('warn','err'):
                            row=dict(row)
                            row['name']=f"Filament {index+1} ({filament_name}) — {row['name']}"
                            filament_rows.append(row)
            process_rows=analyze_config(config, goal, filaments)
            if len(filaments)>1:
                process_rows=[r for r in process_rows if r.get('key') not in FILAMENT_ROW_KEYS]
            self.post_message({'type':'analysis_result','success':True,'count':len(config),
                'names':{'process':process,'machine':machine,'filaments':filaments},
                'parameters':process_rows,
                'filament_parameters':filament_rows,
                'options':analyze_options(config, goal),
                'cross_checks':analyze_cross_checks(config, goal, filaments),
                'gcode_alerts':gcode_alerts,
                'note':''
                })
        except Exception as exc:
            self.post_message({'type':'analysis_result','success':False,'error':str(exc)})
