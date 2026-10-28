/*
 * Self-running guided tour of the docs-as-code POC.
 *
 * How it works
 *   - Loaded on every page (mkdocs.yml -> extra_javascript), but does nothing unless the
 *     URL carries ?tour=<stop number>. Normal readers never see it.
 *   - Each stop is a page plus a caption (English and Spanish). The panel counts down,
 *     scrolls the page gently, then moves to the next stop by changing the URL.
 *   - Space = pause/resume, Right/Left = next/previous, Esc = exit. ES/EN switches language.
 *   - Optional ?lang=es and ?speed=1.5 (slower) or ?speed=0.7 (faster).
 *
 * Paths are relative to the site root, which is worked out from this script's own URL,
 * so the tour works under `mkdocs serve`, a static server, or GitHub Pages sub-paths.
 */
(function () {
  "use strict";

  var SCRIPT_URL = (document.currentScript && document.currentScript.src) || "";
  var ROOT = SCRIPT_URL ? new URL("../", SCRIPT_URL).href : "/";

  var STOPS = [
    {
      path: "", secs: 35,
      title: { en: "The site readers see", es: "El sitio que ven los lectores" },
      say: {
        en: "This is the published site. Everything here is built automatically from Markdown files in a Git repository. Nobody edits the website itself: you change the source, it gets reviewed, and the site is rebuilt.",
        es: "Este es el sitio publicado. Todo se genera automáticamente a partir de ficheros Markdown en un repositorio Git. Nadie edita la web directamente: se cambia la fuente, se revisa y el sitio se vuelve a generar."
      }
    },
    {
      path: "demo/poc-walkthrough/", secs: 45, focus: "The big picture",
      title: { en: "One door in", es: "Una sola puerta de entrada" },
      say: {
        en: "Every source has one route in: FigJam, Excel, API specs, Word, or a direct edit. Every route ends in the same pull request, with the same automated checks and a human approval. One door, one set of rules.",
        es: "Cada fuente tiene una única vía de entrada: FigJam, Excel, especificaciones de API, Word o una edición directa. Todas terminan en la misma pull request, con las mismas comprobaciones automáticas y la aprobación de una persona."
      }
    },
    {
      path: "demo/poc-walkthrough/", secs: 45, focus: "3. Automated guardrails",
      title: { en: "Guardrails as data", es: "Controles definidos como datos" },
      say: {
        en: "The same checks run on the author's machine, in CI on every pull request, and on demand: strict build, sensitive data (DNI, NIE, IBAN, cards, phones), product terms, Markdown lint, API sync and a pipeline self-test. The rules are YAML files, so changing a rule is itself a reviewed change.",
        es: "Las mismas comprobaciones se ejecutan en el equipo del autor, en CI en cada pull request y bajo demanda: build estricto, datos sensibles (DNI, NIE, IBAN, tarjetas, teléfonos), terminología, formato Markdown, sincronía con la API y autoprueba. Las reglas son ficheros YAML: cambiar una regla también se revisa."
      }
    },
    {
      path: "processes/front-office/FO-001/", secs: 50,
      title: { en: "From a FigJam board to a process page", es: "De un tablero FigJam a una página de proceso" },
      say: {
        en: "FO-001 was drawn in FigJam by a process author. The intake script read the board, checked it against the design rules, computed the version, and generated this page: diagram, steps table, business rules. Every step links back to the exact shape on the board.",
        es: "FO-001 se dibujó en FigJam. El script de intake leyó el tablero, lo validó contra las reglas de diseño, calculó la versión y generó esta página: diagrama, tabla de pasos y reglas de negocio. Cada paso enlaza con la forma exacta del tablero."
      }
    },
    {
      path: "processes/front-office/FO-001/", secs: 35, focus: "Conformance",
      title: { en: "Docs that developers can test against", es: "Documentación contra la que se puede probar" },
      say: {
        en: "The same model is released to developers as workflow.yaml plus generated Gherkin scenarios. Applications declare which version they implement, and a conformance check proves every step is bound to a real API operation or event.",
        es: "El mismo modelo se entrega a desarrollo como workflow.yaml y escenarios Gherkin generados. Cada aplicación declara qué versión implementa y una comprobación de conformidad verifica que cada paso está ligado a una operación o evento real de la API."
      }
    },
    {
      path: "guides/handle-late-check-out-request/", secs: 45,
      title: { en: "AI drafts, people decide", es: "La IA redacta, las personas deciden" },
      say: {
        en: "This page came from a fictional Word handbook through the import agent. Note what it did not do: it did not guess. It marked the page DRAFT, flagged the source as over 12 months old, marked unknowns TBC, and listed a contradiction for an owner to resolve.",
        es: "Esta página viene de un manual Word ficticio a través del agente de importación. Fíjate en lo que no hizo: no inventó. Marcó la página como DRAFT, avisó de que la fuente tiene más de 12 meses, marcó lo desconocido como TBC y listó una contradicción para que la resuelva su responsable."
      }
    },
    {
      path: "reference/identifier-glossary/", secs: 35,
      title: { en: "Precision that prevents integration bugs", es: "Precisión que evita errores de integración" },
      say: {
        en: "Integration problems often start with 'the ID'. The glossary fixes four terms: internal ID, external reference, locator, correlation ID. The style guide requires them, and the terms check flags vague wording.",
        es: "Muchos problemas de integración empiezan por 'el ID'. El glosario fija cuatro términos: ID interno, referencia externa, localizador e ID de correlación. La guía de estilo los exige y la comprobación de terminología avisa del lenguaje ambiguo."
      }
    },
    {
      path: "mapping/perfil-de-huesped/", secs: 50,
      title: { en: "Excel stays the source; the page is generated", es: "Excel sigue siendo la fuente; la página se genera" },
      say: {
        en: "Mapping teams keep working in their Excel shell workbook. A script validates it and regenerates these tables, recording the file, sheet, version and SHA-256 hash. Hand-written explanation outside the generated blocks is kept. The workbook itself never enters the repository.",
        es: "El equipo de mapeo sigue trabajando en su libro Excel. Un script lo valida y regenera estas tablas, registrando fichero, hoja, versión y hash SHA-256. El texto escrito a mano fuera de los bloques generados se conserva. El Excel nunca entra en el repositorio."
      }
    },
    {
      path: "mapping/decision-log/", secs: 30,
      title: { en: "Decisions written once, linked everywhere", es: "Cada decisión se escribe una vez y se enlaza" },
      say: {
        en: "Every mapping decision and gap gets a permanent number. Pages link to D-001 or G-001 instead of repeating the reasoning, so the 'why' is always one click away and never drifts.",
        es: "Cada decisión y cada carencia del mapeo recibe un número permanente. Las páginas enlazan a D-001 o G-001 en lugar de repetir el razonamiento, así el 'porqué' siempre está a un clic y no se desactualiza."
      }
    },
    {
      path: "api/front-desk/", secs: 35,
      title: { en: "API reference generated from the spec", es: "Referencia de API generada desde la especificación" },
      say: {
        en: "This page is rendered from the OpenAPI and AsyncAPI files. CI fails if the page and the spec drift apart. The same spec is what process bindings are checked against.",
        es: "Esta página se genera desde los ficheros OpenAPI y AsyncAPI. CI falla si la página y la especificación dejan de coincidir. Es la misma especificación contra la que se comprueban los procesos."
      }
    },
    {
      path: "contributing/guia-autores-figjam/", secs: 30,
      title: { en: "Business authors never touch Git", es: "Los autores de negocio no tocan Git" },
      say: {
        en: "Process authors get a Spanish guide for drawing in FigJam with the standard component library. They work in their tool; the pipeline does the rest.",
        es: "Los autores de procesos tienen una guía en español para dibujar en FigJam con la librería de componentes estándar. Trabajan en su herramienta; el flujo automatizado hace el resto."
      }
    },
    {
      path: "contributing/style-guide/", secs: 25,
      title: { en: "Short, enforceable rules", es: "Reglas breves y verificables" },
      say: {
        en: "Four topic types, one template each, and rules that the checks can enforce. Consistency comes from templates and automation, not from memory.",
        es: "Cuatro tipos de tema, una plantilla para cada uno y reglas que las comprobaciones pueden verificar. La coherencia viene de las plantillas y la automatización, no de la memoria."
      }
    },
    {
      path: "demo/poc-walkthrough/", secs: 0, focus: "What's real and what's sample",
      title: { en: "What's real, and what's next", es: "Qué es real y qué viene después" },
      say: {
        en: "The tooling is working today on sample content. Next steps: move the repository to RIU's GitHub Enterprise Server, create the reviewer teams, decide how the site is hosted, and onboard the first real area. End of tour.",
        es: "Las herramientas ya funcionan hoy con contenido de ejemplo. Próximos pasos: mover el repositorio al GitHub Enterprise Server de RIU, crear los equipos revisores, decidir dónde se publica el sitio e incorporar la primera área real. Fin del recorrido."
      }
    }
  ];

  // ---- state -------------------------------------------------------------------------
  function store(key, val) {
    try { if (val === undefined) return window.sessionStorage.getItem(key); window.sessionStorage.setItem(key, val); }
    catch (e) { return null; }
    return null;
  }

  var params = new URLSearchParams(window.location.search);

  function startTour(evt) {
    if (evt) evt.preventDefault();
    window.location.href = urlFor(0);
  }

  // The "Start the tour" button on the walkthrough page.
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest("a.tour-start");
    if (a) startTour(e);
  });

  // Small "Tour" button in the corner of every page, shown whenever the tour isn't running.
  function addLauncher() {
    if (document.querySelector(".tour-launch")) return;
    var launch = document.createElement("button");
    launch.type = "button";
    launch.className = "tour-launch";
    launch.title = "Start the guided tour / Iniciar la visita guiada";
    launch.setAttribute("aria-label", launch.title);
    launch.innerHTML = "&#9654; Tour";
    launch.addEventListener("click", startTour);
    document.body.appendChild(launch);
  }

  if (!params.has("tour")) {
    addLauncher();
    // The POC walkthrough page walks through by itself: after a short countdown the tour
    // starts. Esc (or the "stay" link) cancels it for the rest of this browser tab.
    if (/\/demo\/poc-walkthrough\/(index\.html)?$/.test(window.location.pathname) &&
        store("tour-autostart") !== "off") {
      autoStart(8);
    }
    return;
  }

  function autoStart(seconds) {
    var btn = document.querySelector(".tour-launch");
    var es = (store("tour-lang") || "en") === "es";
    var left = seconds;
    var stay = document.createElement("a");
    stay.href = "#";
    stay.className = "tour-stay";
    stay.textContent = es ? "Quedarme aquí" : "Stay on this page";
    btn.insertAdjacentElement("beforebegin", stay);
    function label() {
      btn.innerHTML = "&#9654; " + (es ? "La visita empieza en " : "Tour starts in ") + left + "s";
    }
    function cancel(e) {
      if (e) e.preventDefault();
      clearInterval(t);
      store("tour-autostart", "off");
      btn.innerHTML = "&#9654; Tour";
      stay.remove();
      document.removeEventListener("keydown", onKey);
    }
    function onKey(e) { if (e.key === "Escape") cancel(e); }
    stay.addEventListener("click", cancel);
    document.addEventListener("keydown", onKey);
    label();
    var t = setInterval(function () {
      left -= 1;
      if (left <= 0) { clearInterval(t); startTour(); } else { label(); }
    }, 1000);
  }

  var index = Math.max(0, Math.min(STOPS.length - 1, (parseInt(params.get("tour"), 10) || 1) - 1));
  var lang = params.get("lang") || store("tour-lang") || "en";
  var speed = parseFloat(params.get("speed") || store("tour-speed") || "1") || 1;
  store("tour-lang", lang);
  store("tour-speed", String(speed));

  function urlFor(i) {
    // Outside the tour `lang` isn't set yet: reuse the language last chosen in this tab.
    var l = (typeof lang === "string" && lang) || store("tour-lang") || "en";
    var q = "?tour=" + (i + 1) + "&lang=" + l;
    return ROOT + STOPS[i].path + q;
  }

  var stop = STOPS[index];
  var total = Math.round(stop.secs * speed);
  var remaining = total;
  var paused = false;
  var userScrolled = false;
  var timer = null;

  // ---- panel -------------------------------------------------------------------------
  var panel = document.createElement("aside");
  panel.className = "tour-panel";
  panel.setAttribute("role", "status");
  panel.setAttribute("aria-live", "polite");
  panel.innerHTML =
    '<div class="tour-head">' +
    '  <span class="tour-count"></span>' +
    '  <button type="button" class="tour-lang" title="Language / Idioma"></button>' +
    '</div>' +
    '<h2 class="tour-title"></h2>' +
    '<p class="tour-say"></p>' +
    '<div class="tour-bar"><span></span></div>' +
    '<div class="tour-buttons">' +
    '  <button type="button" data-act="prev" title="Previous (Left arrow)">&#9664;</button>' +
    '  <button type="button" data-act="pause" title="Pause (Space)"></button>' +
    '  <button type="button" data-act="next" title="Next (Right arrow)">&#9654;</button>' +
    '  <button type="button" data-act="exit" title="Exit (Esc)">&#10005;</button>' +
    '</div>';
  document.body.appendChild(panel);
  document.documentElement.classList.add("tour-on");

  function render() {
    panel.querySelector(".tour-count").textContent =
      (lang === "es" ? "Parada " : "Stop ") + (index + 1) + " / " + STOPS.length;
    panel.querySelector(".tour-lang").textContent = lang === "es" ? "EN" : "ES";
    panel.querySelector(".tour-title").textContent = stop.title[lang] || stop.title.en;
    panel.querySelector(".tour-say").textContent = stop.say[lang] || stop.say.en;
    panel.querySelector('[data-act="pause"]').innerHTML = paused ? "&#9654;&#xFE0E; " + (lang === "es" ? "Seguir" : "Resume") : "&#10073;&#10073; " + (lang === "es" ? "Pausa" : "Pause");
    var pct = total > 0 ? 100 * (total - remaining) / total : 100;
    panel.querySelector(".tour-bar span").style.width = pct + "%";
    panel.classList.toggle("tour-paused", paused);
    panel.classList.toggle("tour-last", index === STOPS.length - 1);
  }

  function go(i) {
    if (i < 0 || i >= STOPS.length) return;
    window.location.href = urlFor(i);
  }

  function exitTour() {
    clearInterval(timer);
    panel.remove();
    document.documentElement.classList.remove("tour-on");
    var clean = window.location.pathname + window.location.hash;
    window.history.replaceState(null, "", clean);
    addLauncher();
  }

  panel.addEventListener("click", function (e) {
    var btn = e.target.closest("button");
    if (!btn) return;
    if (btn.classList.contains("tour-lang")) {
      lang = lang === "es" ? "en" : "es";
      store("tour-lang", lang);
      render();
      return;
    }
    var act = btn.getAttribute("data-act");
    if (act === "prev") go(index - 1);
    if (act === "next") go(index + 1);
    if (act === "pause") { paused = !paused; render(); }
    if (act === "exit") exitTour();
  });

  document.addEventListener("keydown", function (e) {
    if (e.target && /input|textarea/i.test(e.target.tagName)) return;
    if (e.key === " ") { e.preventDefault(); paused = !paused; render(); }
    else if (e.key === "ArrowRight") go(index + 1);
    else if (e.key === "ArrowLeft") go(index - 1);
    else if (e.key === "Escape") exitTour();
  });

  ["wheel", "touchmove"].forEach(function (ev) {
    window.addEventListener(ev, function () { userScrolled = true; }, { passive: true });
  });

  // ---- scrolling -----------------------------------------------------------------------
  function findHeading(text) {
    var hs = document.querySelectorAll(".md-content h1, .md-content h2, .md-content h3");
    for (var i = 0; i < hs.length; i++) {
      if (hs[i].textContent.replace(/¶/g, "").trim().indexOf(text) === 0) return hs[i];
    }
    return null;
  }

  var startY = 0;
  function setStart() {
    var h = stop.focus ? findHeading(stop.focus) : null;
    if (h) {
      h.classList.add("tour-focus");
      startY = h.getBoundingClientRect().top + window.scrollY - 90;
      window.scrollTo({ top: startY, behavior: "smooth" });
    }
  }

  // Scroll slowly from the start position toward the end of the page (or 1.5 screens),
  // finishing at 85% of the stop's time so the reader sees the content without rushing.
  function autoScroll() {
    if (paused || userScrolled || total <= 0) return;
    var elapsed = total - remaining;
    var lead = Math.min(6, total * 0.2);
    if (elapsed < lead) return;
    var maxY = document.documentElement.scrollHeight - window.innerHeight;
    var target = stop.focus ? Math.min(maxY, startY + window.innerHeight * 1.5) : maxY;
    var span = Math.max(1, total * 0.85 - lead);
    var t = Math.min(1, (elapsed - lead) / span);
    window.scrollTo({ top: startY + (target - startY) * t, behavior: "auto" });
  }

  // ---- clock -----------------------------------------------------------------------------
  render();
  window.setTimeout(setStart, 600);
  if (total > 0) {
    timer = window.setInterval(function () {
      if (paused) return;
      remaining = Math.max(0, remaining - 0.25);
      autoScroll();
      render();
      if (remaining <= 0) { clearInterval(timer); go(index + 1); }
    }, 250);
  }
})();
