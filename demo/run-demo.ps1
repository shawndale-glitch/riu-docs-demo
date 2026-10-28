<#
.SYNOPSIS
  One-button, self-running demo of the RIU docs-as-code POC (English or Spanish).

.DESCRIPTION
  Runs in seven acts, narrating each one in the console, then opens the built site in
  Chrome (or Firefox) on a self-running guided tour. Nothing in the repository is changed:
  every "what if" scenario works on copies in .demo-tmp\, which is deleted at the end.

    Act 0  Preflight          Python, virtual environment, dependencies
    Act 1  The repository     what lives where
    Act 2  Same checks as CI  sensitive data, terms, Markdown lint, API sync, self-test
    Act 3  Guardrail, live    a file with a (fake) DNI, IBAN and company e-mail is blocked
    Act 4  FigJam intake      unchanged board / reworded board / broken board
    Act 5  Conformance        an app bound to a renamed API operation fails, then passes
    Act 6  Build              mkdocs build --strict
    Act 7  Guided tour        serve the site and open the tour in the browser

  -Lang switches the console narration AND the browser tour captions. Output printed by
  the Python tools themselves (intake and conformance reports) stays in English.

.PARAMETER Pace
  Multiplies every pause. 1 = normal, 1.5 = slower, 0.5 = rehearsal speed.
.PARAMETER Interactive
  Wait for Enter between acts instead of pausing on a timer.
.PARAMETER Lang
  en (default) or es. RUN-DEMO-ES.cmd passes -Lang es.
.PARAMETER NoBrowser
  Build and serve, but don't open a browser.
.PARAMETER TourOnly
  Skip acts 1-5: just prepare, build, serve and open the guided tour (OPEN-TOUR.cmd).
.PARAMETER Port
  Port for the local site. Default 8000; the next free port is used if it's busy.

.EXAMPLE
  demo\RUN-DEMO.cmd          (double-click: English)
  demo\RUN-DEMO-ES.cmd       (double-click: Spanish)
  powershell -ExecutionPolicy Bypass -File demo\run-demo.ps1 -Lang es -Pace 1.3
#>
param(
  [double]$Pace = 1.0,
  [switch]$Interactive,
  [ValidateSet("en", "es")][string]$Lang = "en",
  [switch]$NoBrowser,
  [int]$Port = 8000,
  [switch]$TourOnly
)

# Saved as UTF-8 WITH a byte-order mark: Windows PowerShell 5.1 needs the BOM to read the
# Spanish accents correctly. Keep the BOM if you edit this file.

$ErrorActionPreference = "Continue"
$Repo = Split-Path -Parent $PSScriptRoot
Set-Location $Repo

# The tooling prints Unicode (check marks, arrows). Without this, Python on a Spanish
# Windows console (cp1252) crashes with UnicodeEncodeError in the middle of the demo.
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$Tmp = Join-Path $Repo ".demo-tmp"
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
$script:Server = $null

# Pick the English or Spanish text. Every line the audience reads goes through T.
function T([string]$En, [string]$Es) { if ($Lang -eq "es") { return $Es } return $En }

$Host.UI.RawUI.WindowTitle = (T "RIU Genesis Documentation - docs-as-code POC demo" "RIU Genesis Documentation - demo de la POC docs-as-code")

# ---------------------------------------------------------------------------------------
# Presentation helpers
# ---------------------------------------------------------------------------------------
function Wait-Beat([double]$Seconds) {
  if ($Interactive) { return }
  Start-Sleep -Milliseconds ([int]($Seconds * $Pace * 1000))
}

function Next-Act {
  if ($Interactive) {
    Write-Host ""
    Write-Host (T "  [Enter] to continue" "  [Intro] para continuar") -ForegroundColor DarkGray -NoNewline
    [void](Read-Host)
  } else { Wait-Beat 2.5 }
}

function Say([string]$Text, [string]$Color = "Gray") {
  # Typewriter effect: reads as if someone is talking, and gives the audience time to follow.
  $delay = [int](14 * $Pace)
  Write-Host "  " -NoNewline
  foreach ($ch in $Text.ToCharArray()) {
    Write-Host $ch -NoNewline -ForegroundColor $Color
    if ($delay -gt 0) { Start-Sleep -Milliseconds $delay }
  }
  Write-Host ""
}

function Act([string]$Number, [string]$Title, [string]$Why) {
  $word = T "ACT" "ACTO"
  Write-Host ""
  Write-Host ("  " + ("=" * 86)) -ForegroundColor DarkCyan
  Write-Host ("  $word $Number  |  $Title") -ForegroundColor Cyan
  Write-Host ("  " + ("=" * 86)) -ForegroundColor DarkCyan
  if ($Why) { Say $Why "White" }
  Write-Host ""
  Wait-Beat 1.5
}

function Show-Command([string]$Text) {
  Write-Host ("  > " + $Text) -ForegroundColor Yellow
  Wait-Beat 0.8
}

function Ok([string]$Text)   { Write-Host ("  " + (T "[PASS] " "[OK] ") + $Text) -ForegroundColor Green }
function Bad([string]$Text)  { Write-Host ("  " + (T "[STOP] " "[BLOQUEADO] ") + $Text) -ForegroundColor Red }
function Note([string]$Text) { Write-Host ("  (i) " + $Text) -ForegroundColor DarkGray }

# Run a Python tool, print its output indented, return its exit code.
# Material for MkDocs prints a boxed notice about MkDocs 2.0; it's filtered out of the demo.
function Invoke-Tool([string[]]$ToolArgs, [switch]$Quiet, [int]$MaxLines = 60) {
  $out = & $Py @ToolArgs 2>&1 | ForEach-Object { "$_" }
  $code = $LASTEXITCODE
  if (-not $Quiet) {
    $lines = $out | Where-Object {
      $_ -notmatch ("^\s*(\\u2502|" + [char]0x2502 + ")") -and $_ -notmatch 'RemoteException' -and $_.Trim() -ne ""
    }
    $lines | Select-Object -First $MaxLines | ForEach-Object {
      $color = "Gray"
      if ($_ -match '^#') { $color = "White" }
      if ($_ -match ([string][char]0x274C + "|rejected|FAIL|ERROR")) { $color = "Red" }
      if ($_ -match ([string][char]0x2705 + "|accepted|^PASS|: pass|up to date|0 finding|0 error")) { $color = "Green" }
      if ($_ -match ([string][char]0x26A0 + "|warning")) { $color = "Yellow" }
      Write-Host ("      " + $_) -ForegroundColor $color
    }
  }
  return $code
}

function Cleanup {
  # The venv's python.exe is a launcher that starts a child python.exe, so stop the whole
  # process tree; stopping only the launcher leaves the web server running on the port.
  if ($script:Server) {
    & taskkill.exe /PID $script:Server.Id /T /F 2>&1 | Out-Null
  }
  if (Test-Path $Tmp) { Remove-Item $Tmp -Recurse -Force -ErrorAction SilentlyContinue }
}

function Find-Browser {
  # Chrome first, then Firefox. Microsoft Edge is deliberately never used, so the demo
  # never falls back to the Windows default browser either.
  $candidates = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles\Mozilla Firefox\firefox.exe",
    "${env:ProgramFiles(x86)}\Mozilla Firefox\firefox.exe"
  )
  foreach ($c in $candidates) { if ($c -and (Test-Path $c)) { return $c } }
  return $null
}

function Test-PortFree([int]$P) {
  $l = $null
  try {
    $l = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $P)
    $l.Start(); return $true
  } catch { return $false } finally { if ($l) { $l.Stop() } }
}

# ---------------------------------------------------------------------------------------
try {
  Clear-Host
  Write-Host ""
  Write-Host "   RIU Genesis Documentation" -ForegroundColor Cyan
  Write-Host (T "   Docs-as-code proof of concept  |  self-running demo" "   Prueba de concepto docs-as-code  |  demo automática") -ForegroundColor DarkCyan
  Write-Host ""
  Say (T "All content in this repository is fictional sample content. No RIU company data." `
         "Todo el contenido de este repositorio es ficticio, de ejemplo. No contiene datos de RIU.")
  Say (T "Nothing in the repository is changed by this demo: what-if scenarios run on copies." `
         "La demo no modifica nada del repositorio: los escenarios hipotéticos se ejecutan sobre copias.")
  Wait-Beat 2

  # -------------------------------------------------------------------------------------
  Act "0" (T "Preflight" "Comprobaciones previas") `
      (T "Same environment CI uses: Python, a virtual environment, pinned dependencies." `
         "El mismo entorno que usa la integración continua (CI): Python, un entorno virtual y dependencias con versión fijada.")
  if (-not (Test-Path $Py)) {
    Show-Command "python -m venv .venv"
    & python -m venv .venv
  }
  Show-Command "pip install -r requirements.txt"
  & $Py -m pip install --quiet --disable-pip-version-check -r requirements.txt 2>&1 | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Bad (T "Dependency install failed. Check the network, then re-run." "Falló la instalación de dependencias. Revisa la red y vuelve a ejecutar.")
    exit 1
  }
  $ver = (& $Py --version 2>&1) -join ""
  Ok ($ver + (T ", MkDocs and Material for MkDocs ready" ", MkDocs y Material for MkDocs listos"))
  if (Test-Path $Tmp) { Remove-Item $Tmp -Recurse -Force }
  New-Item -ItemType Directory -Path $Tmp | Out-Null
  Next-Act

  if (-not $TourOnly) {  # acts 1-5 are skipped with -TourOnly
  # -------------------------------------------------------------------------------------
  Act "1" (T "The repository is the single source" "El repositorio es la única fuente") `
      (T "Everything the site shows, and every rule that protects it, is a text file under version control." `
         "Todo lo que muestra el sitio, y cada regla que lo protege, es un fichero de texto bajo control de versiones.")
  $tree = @(
    @("docs/",              (T "the pages: Markdown, one file per topic" "las páginas: Markdown, un fichero por tema")),
    @("mkdocs.yml",         (T "site settings and the menu (nav); a page not in nav fails the build" "configuración del sitio y el menú (nav); una página fuera del menú rompe el build")),
    @("governance/",        (T "the rules as data: sensitive data, terms, process lint, reviewers" "las reglas como datos: datos sensibles, terminología, validación de procesos, revisores")),
    @("tooling/",           (T "converters and checks: FigJam, Excel, API specs, conformance" "conversores y comprobaciones: FigJam, Excel, especificaciones de API, conformidad")),
    @("workflows/",         (T "process models generated from FigJam (workflow.yaml)" "modelos de proceso generados desde FigJam (workflow.yaml)")),
    @("conformance/",       (T "generated test scenarios developers run against their apps" "escenarios de prueba generados que desarrollo ejecuta contra sus aplicaciones")),
    @(".github/workflows/", (T "CI: the same checks on every pull request, then build and publish" "CI: las mismas comprobaciones en cada pull request; después, build y publicación")),
    @(".github/CODEOWNERS", (T "who must approve changes, folder by folder" "quién debe aprobar los cambios, carpeta por carpeta"))
  )
  foreach ($row in $tree) {
    Write-Host ("    {0,-22}" -f $row[0]) -ForegroundColor Yellow -NoNewline
    Write-Host $row[1] -ForegroundColor Gray
    Wait-Beat 0.35
  }
  Write-Host ""
  Show-Command "git log --oneline -3"
  git log --oneline -3 2>$null | ForEach-Object { Write-Host ("      " + $_) -ForegroundColor Gray }
  Say (T "Every change has an author, a date, a reason and a reviewer. That's the audit trail." `
         "Cada cambio tiene autor, fecha, motivo y revisor. Esa es la pista de auditoría.")
  Next-Act

  # -------------------------------------------------------------------------------------
  Act "2" (T "The same checks CI runs on every pull request" "Las mismas comprobaciones que CI ejecuta en cada pull request") `
      (T "If any of these fail, the pull request can't be merged. Authors can run them locally first." `
         "Si alguna falla, la pull request no se puede integrar. Los autores pueden ejecutarlas antes en su equipo.")
  $checks = @(
    @((T "Sensitive data (DNI, NIE, IBAN, cards, phones)" "Datos sensibles (DNI, NIE, IBAN, tarjetas, teléfonos)"), @("tooling/sensitive_scan.py")),
    @((T "Product names and house terms" "Nombres de producto y terminología de la casa"), @("tooling/terms_check.py")),
    @((T "Markdown lint" "Formato Markdown (lint)"), @("-m", "pymarkdown", "--config", ".pymarkdown.json", "scan", "-r", "docs", "README.md", "CONTRIBUTING.md", "governance")),
    @((T "API reference matches its spec" "La referencia de API coincide con su especificación"), @("tooling/api_render.py", "docs/api/specs/front-desk.openapi.yaml", "--asyncapi", "docs/api/specs/front-desk.asyncapi.yaml", "--check")),
    @((T "Pipeline self-test (rules fire on broken boards)" "Autoprueba del flujo (las reglas saltan con tableros rotos)"), @("tooling/selftest.py"))
  )
  $failed = 0
  foreach ($c in $checks) {
    Show-Command ("python " + ($c[1] -join " "))
    $code = Invoke-Tool $c[1] -MaxLines 14
    if ($code -eq 0) { Ok $c[0] } else { Bad $c[0]; $failed++ }
    Write-Host ""
    Wait-Beat 0.8
  }
  if ($failed -eq 0) {
    Say (T "All green. This is the state a reviewer sees before approving." `
           "Todo en verde. Esto es lo que ve un revisor antes de aprobar.") "Green"
  }
  Next-Act

  # -------------------------------------------------------------------------------------
  Act "3" (T "Guardrail, live: personal data never gets in" "Control en directo: los datos personales no entran") `
      (T "Simulate an author pasting a payroll example into a page. Fake values, real check." `
         "Simulamos que un autor pega un ejemplo de nómina en una página. Valores falsos, comprobación real.")
  $leak = Join-Path $Tmp "ejemplo-nomina.md"
  # The fake values are assembled at run time. Written out literally, they would make this
  # script fail the repository's own sensitive-data check once it's committed.
  $fakeDni  = "1234" + "5678" + "Z"
  $fakeIban = "ES91" + " 2100 0418" + " 4502 0005 1332"
  $fakeMail = "nominas" + "@" + "riu" + ".com"
  @(
    "# Ejemplo de nomina (fake data for the demo)",
    "",
    "Empleado con DNI $fakeDni, cuenta $fakeIban.",
    "Dudas: $fakeMail"
  ) | Set-Content -Path $leak -Encoding UTF8
  Note (T "Wrote .demo-tmp\ejemplo-nomina.md with a fake DNI, a test IBAN and a company e-mail address." `
          "Creado .demo-tmp\ejemplo-nomina.md con un DNI falso, un IBAN de prueba y un correo corporativo.")
  Show-Command "python tooling/sensitive_scan.py .demo-tmp/ejemplo-nomina.md"
  $code = Invoke-Tool @("tooling/sensitive_scan.py", $leak)
  if ($code -ne 0) {
    Bad (T "Blocked. In CI this pull request can't be merged; with pre-commit it can't even be committed." `
           "En CI esta pull request no se puede integrar; con pre-commit ni siquiera se puede hacer el commit.")
    Say (T "Note the values are masked: the report never repeats the data it found." `
           "Los valores aparecen enmascarados: el informe nunca repite los datos que encuentra.")
  } else { Note (T "Unexpected: the scan passed." "Inesperado: la comprobación ha pasado.") }
  Say (T "The patterns live in governance/sensitive-data.yaml. Changing them is itself a reviewed change." `
         "Los patrones están en governance/sensitive-data.yaml. Cambiarlos también requiere revisión.")
  Next-Act

  # -------------------------------------------------------------------------------------
  Act "4" (T "FigJam to repository: intake decides, not a person's memory" "De FigJam al repositorio: decide el intake, no la memoria de nadie") `
      (T "A process author draws in FigJam. Intake lints the drawing, computes the version, and writes the page and the developer model." `
         "Un autor dibuja el proceso en FigJam. El intake valida el diagrama, calcula la versión y genera la página y el modelo para desarrollo.")
  Say (T "4a. The board as it is today: nothing changed since the last export." `
         "4a. El tablero tal como está hoy: nada ha cambiado desde la última exportación.") "White"
  Show-Command "python tooling/workflow_intake.py workflows/front-office/FO-001/board.json --dry-run"
  [void](Invoke-Tool @("tooling/workflow_intake.py", "workflows/front-office/FO-001/board.json", "--dry-run") -MaxLines 30)
  Wait-Beat 3
  Write-Host ""
  Say (T "4b. The author rewords one step and bumps the header to v0.1.1." `
         "4b. El autor reformula un paso y sube la cabecera a v0.1.1.") "White"
  $board = (& $Py demo/board_scenarios.py wording 2>&1 | Select-Object -Last 1)
  Show-Command "python tooling/workflow_intake.py $board --dry-run"
  [void](Invoke-Tool @("tooling/workflow_intake.py", $board, "--dry-run") -MaxLines 30)
  Say (T "Wording only, so a PATCH: 0.1.0 -> 0.1.1. The version is computed, and a person confirms the meaning." `
         "Solo cambia la redacción, así que es un PATCH: 0.1.0 -> 0.1.1. La versión se calcula y una persona confirma el significado.")
  Wait-Beat 3
  Write-Host ""
  Say (T "4c. Now a careless edit: a library placeholder left in a label, and a decision that isn't a question." `
         "4c. Ahora un descuido: un texto de ejemplo de la librería sin cambiar y una decisión que no es una pregunta.") "White"
  $board = (& $Py demo/board_scenarios.py broken 2>&1 | Select-Object -Last 1)
  Show-Command "python tooling/workflow_intake.py $board --dry-run"
  $code = Invoke-Tool @("tooling/workflow_intake.py", $board, "--dry-run") -MaxLines 30
  if ($code -ne 0) {
    Bad (T "Rejected. Nothing written; the last good version stays published." `
           "Rechazado. No se escribe nada; sigue publicada la última versión válida.")
  }
  Say (T "Each finding links to the exact shape on the FigJam board, so the author knows what to fix." `
         "Cada hallazgo enlaza con la forma exacta del tablero FigJam, para que el autor sepa qué corregir.")
  Next-Act

  # -------------------------------------------------------------------------------------
  Act "5" (T "Conformance: the docs check the application" "Conformidad: la documentación comprueba la aplicación") `
      (T "A fictional front-desk app declares which API operation implements each FO-001 step." `
         "Una aplicación ficticia de recepción declara qué operación de la API implementa cada paso de FO-001.")
  # The check only accepts validated releases. FO-001 is still a draft, so the demo uses a
  # copy marked as the 1.0.0 release; the committed model is not touched.
  $model = Join-Path $Tmp "FO-001.workflow.yaml"
  (Get-Content workflows/front-office/FO-001/workflow.yaml -Encoding UTF8) `
    -replace '^  version: 0\.1\.0$', '  version: 1.0.0' `
    -replace '^  status: draft$', '  status: validated' | Set-Content $model -Encoding UTF8
  Note (T "Using a copy of FO-001 marked as release 1.0.0 (the real one is still a draft)." `
          "Usamos una copia de FO-001 marcada como versión 1.0.0 (la real sigue en borrador).")
  $specs = @("--openapi", "docs/api/specs/front-desk.openapi.yaml", "--asyncapi", "docs/api/specs/front-desk.asyncapi.yaml")
  Say (T "5a. The app's bindings as committed." "5a. Los bindings de la aplicación tal como están.") "White"
  Show-Command "python tooling/workflow_conformance.py check --bindings examples/consumer-demo/bindings.yaml ..."
  $code = Invoke-Tool (@("tooling/workflow_conformance.py", "check", "--model", $model, "--bindings", "examples/consumer-demo/bindings.yaml", "--range", "^1.0.0") + $specs)
  if ($code -ne 0) {
    Bad (T "The API renamed checkInGuest to checkInReservation; the app still binds the old name." `
           "La API renombró checkInGuest a checkInReservation; la aplicación sigue usando el nombre antiguo.")
  }
  Wait-Beat 3
  Write-Host ""
  Say (T "5b. The developer updates one line in bindings.yaml." "5b. El desarrollador cambia una línea en bindings.yaml.") "White"
  $fixed = Join-Path $Tmp "bindings.yaml"
  (Get-Content examples/consumer-demo/bindings.yaml -Encoding UTF8) `
    -replace 'operation_id: checkInGuest', 'operation_id: checkInReservation' | Set-Content $fixed -Encoding UTF8
  Show-Command ("python tooling/workflow_conformance.py check --bindings " + (T "(fixed bindings)" "(bindings corregidos)") + " ...")
  $code = Invoke-Tool (@("tooling/workflow_conformance.py", "check", "--model", $model, "--bindings", $fixed, "--range", "^1.0.0") + $specs)
  if ($code -eq 0) {
    Ok (T "Every step on the happy path is bound to a real operation or event." `
          "Cada paso del camino principal está ligado a una operación o evento real.")
  }
  Say (T "The documentation found a broken integration before anyone opened a test environment." `
         "La documentación detectó una integración rota antes de abrir siquiera un entorno de pruebas.")
  Next-Act

  }  # end of acts 1-5 (skipped with -TourOnly)
  # -------------------------------------------------------------------------------------
  Act "6" (T "Build the site, strictly" "Generar el sitio en modo estricto") `
      (T "Strict mode turns every warning into an error: a broken link or a page missing from the menu stops the build." `
         "El modo estricto convierte cada aviso en error: un enlace roto o una página fuera del menú detienen el build.")
  Show-Command "mkdocs build --strict"
  $code = Invoke-Tool @("-m", "mkdocs", "build", "--strict") -MaxLines 12
  if ($code -ne 0) {
    Bad (T "Build failed. The site was not refreshed." "El build ha fallado. El sitio no se ha actualizado.")
    exit 1
  }
  $pages = (Get-ChildItem site -Recurse -Filter index.html | Measure-Object).Count
  Ok (T "Site built: $pages pages in site\" "Sitio generado: $pages páginas en site\")
  Next-Act

  # -------------------------------------------------------------------------------------
  Act "7" (T "The result: a guided tour of the site" "El resultado: una visita guiada al sitio") `
      (T "The browser now runs a self-paced tour. Space pauses it, the arrow keys move between stops, Esc ends it." `
         "El navegador inicia ahora una visita automática. Espacio la pausa, las flechas cambian de parada y Esc la termina.")
  while (-not (Test-PortFree $Port)) { $Port++ }
  $script:Server = Start-Process -FilePath $Py -ArgumentList @("-m", "http.server", "$Port", "--bind", "127.0.0.1", "--directory", (Join-Path $Repo "site")) `
    -WorkingDirectory $Repo -WindowStyle Hidden -PassThru
  Start-Sleep -Seconds 2
  $url = "http://127.0.0.1:$Port/?tour=1&lang=$Lang"
  Ok ((T "Serving the built site at " "Sitio publicado en local en ") + "http://127.0.0.1:$Port/")
  $browser = Find-Browser
  if ($NoBrowser) {
    Note ((T "Open this address yourself: " "Abre esta dirección: ") + $url)
  } elseif ($browser) {
    Start-Process -FilePath $browser -ArgumentList @("--new-window", $url)
    Ok ((T "Tour opened in " "Visita abierta en ") + [System.IO.Path]::GetFileNameWithoutExtension($browser))
  } else {
    Note ((T "Chrome or Firefox not found. Open this address in either: " "No se encuentra Chrome ni Firefox. Abre esta dirección en uno de ellos: ") + $url)
  }
  Write-Host ""
  Write-Host (T "  The tour runs on its own (about 8 minutes). Leave this window open." `
                "  La visita avanza sola (unos 8 minutos). Deja esta ventana abierta.") -ForegroundColor White
  Write-Host (T "  Press Enter here when you're done to stop the site and clean up." `
                "  Pulsa Intro aquí al terminar para detener el sitio y limpiar.") -ForegroundColor DarkGray
  [void](Read-Host)
}
finally {
  Cleanup
  Write-Host (T "  Demo finished. Site stopped, scratch files removed. The repository is unchanged." `
                "  Demo terminada. Sitio detenido y ficheros temporales eliminados. El repositorio no ha cambiado.") -ForegroundColor DarkCyan
}
