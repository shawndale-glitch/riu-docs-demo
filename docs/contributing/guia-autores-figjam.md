# Guía para autores: diagramas de proceso en FigJam

Esta guía es para quien dibuja un proceso en FigJam (expertos de negocio, consultores, analistas). Explica cómo construir el diagrama para que la **validación automática** lo acepte a la primera, y qué pasa después.

Las reglas exactas están en [`governance/workflow-rules.yaml`](https://github.com/shawndale-glitch/riu-docs-demo/blob/main/governance/workflow-rules.yaml). Cada regla tiene un código (R1…R9, W1…W8). Si la validación rechaza tu diagrama, el aviso cita ese código; búscalo en la tabla de esta página.

## Antes de empezar

1. **Parte de la plantilla en español**, *Borrador Design Kit Esp*. Incluye las reglas, la leyenda y un ejemplo completo que pasa la validación sin avisos. Pide el enlace al responsable de documentación.
2. **Usa solo los componentes de la biblioteca** *Process Design Standards/Components* (publicada en la organización RIUSA de Figma). Ábrela desde el panel de recursos de FigJam. No dibujes formas sueltas de FigJam.
3. **Un proceso = una sección de FigJam.** El nombre de la sección empieza por el ID del proceso, por ejemplo `FO-001 Solicitud de check-in anticipado`.

## La cabecera

Cada sección tiene **un único** bloque de cabecera. Rellena todos los campos; si un campo conserva el texto por defecto de la biblioteca, el diagrama se rechaza (R9).

| Campo | Qué poner | Ejemplo | Regla |
|---|---|---|---|
| ID del proceso | Prefijo del área + número. Subproceso: añade `.n` | `FO-001`, `RP-12.1` | R1 |
| Nombre del proceso | Nombre corto, en forma de acción | Solicitud de check-in anticipado | — |
| Responsable | Persona que responde del contenido | Nombre y apellido | — |
| Versión | `v` + tres números | `v1.0.0` | R7 |
| Estado | Borrador, En revisión, Aprobado u Obsoleto | Borrador | R7 |
| Última actualización | Fecha en formato AAAA-MM-DD | 2026-10-15 | R7 |
| Actual / futuro | Actual (as-is) o Futuro (to-be) | Futuro (to-be) | R7 |

Los prefijos de área válidos están en [`governance/areas.yaml`](https://github.com/shawndale-glitch/riu-docs-demo/blob/main/governance/areas.yaml). Si tu área no aparece, pide que se añada antes de empezar.

**La versión de la cabecera es una comprobación, no la que manda.** El sistema calcula la versión comparando con la anterior. Si tu número es menor, el informe muestra los dos valores y te pide que actualices la cabecera.

## Cómo construir el diagrama

### Errores: bloquean siempre

| Código | Regla | Cómo evitarlo |
|---|---|---|
| R1 | Una sola cabecera; ID con formato válido y prefijo conocido | No copies una cabecera de otro proceso dentro de la misma sección |
| R2 | Todas las formas son componentes publicados de la biblioteca, y cada paso tiene texto | Nada de rectángulos, notas o marcos de FigJam; no uses los conectores retirados de la biblioteca |
| R3 | Cada conector une dos elementos de la biblioteca; los enlaces a sistemas, documentos, almacenes de datos o anotaciones son discontinuos o punteados | Usa los conectores nativos de FigJam y engánchalos a las formas, no al aire |
| R4 | Una decisión (XOR) tiene al menos dos salidas, cada una con una condición distinta | Etiqueta cada flecha de salida: «Sí» / «No», o la condición concreta |
| R5 | Un único inicio; todo paso se alcanza desde él; sin callejones sin salida; los eventos de fin no tienen salidas | Recorre el diagrama con el dedo desde el inicio hasta cada fin |
| R6 | Los carriles son componentes *Swimlane* con un rol, y el centro de cada paso cae dentro de un solo carril | No dejes pasos a caballo entre dos carriles |
| R7 | Fecha, estado, actual/futuro y versión con los valores permitidos | Ver la tabla de la cabecera |
| R8 | Ningún marcador de «paso eliminado» en un diagrama que va a revisión o aprobación | Borra los pasos eliminados antes de pasar a En revisión |
| R9 | Ningún texto por defecto de la biblioteca en etiquetas, roles o cabecera | Busca «Verbo + objeto», «¿Pregunta?», «Rol o nombre»… y sustitúyelos |

### Avisos: se toleran en Borrador, bloquean En revisión y Aprobado

| Código | Regla | Cómo evitarlo |
|---|---|---|
| W1 | Las tareas son verbo + objeto, de al menos dos palabras | «Validar disponibilidad», no «Validación» |
| W2 | Los carriles no se solapan; al menos 20 px entre carriles | Activa el ajuste a la cuadrícula |
| W3 | No hay texto suelto en la sección | Si importa, conviértelo en una anotación y únela a un paso |
| W4 | Las notas adhesivas se exportan como notas y se revisan antes de aprobar | Resuelve o elimina las notas antes de pasar a Aprobado |
| W5 | Cada sistema, documento, almacén de datos y anotación está unido a un paso | Un conector punteado desde el paso que lo usa |
| W6 | Puntos de dolor solo en diagramas actuales; marcadores de paso cambiado o eliminado solo en futuros | Revisa el campo Actual / futuro |
| W7 | Una decisión es una pregunta de sí o no que termina en «?» | «¿Hay habitación disponible?» |
| W8 | Como máximo 15 actividades y subprocesos por diagrama | Agrupa el resto en un subproceso con su propia sección |

### Lo que revisan las personas, no la validación

- El flujo se lee de izquierda a derecha y el camino feliz es una línea recta.
- Los mapas mentales son solo para talleres. Antes de revisión, conviértelos en una tabla de reglas (Condición · Aprobador · Excepción por · ID del proceso).

## Enviar el diagrama

1. En FigJam, haz clic derecho en la sección → **Copiar enlace**.
2. Envía el enlace al responsable de documentación, o lanza tú mismo el flujo **Workflow intake** en la pestaña *Actions* del repositorio si tienes acceso.
3. La validación tarda unos minutos. Hay dos resultados posibles:

| Resultado | Qué recibes | Qué haces |
|---|---|---|
| **Aceptado** | Una *pull request* con la página del proceso generada y la versión calculada | Revisa que la página dice lo que querías decir y apruébala |
| **Rechazado** | Una incidencia con una línea por problema y un enlace directo a cada elemento del tablero | Corrige el tablero en FigJam y vuelve a enviar el mismo enlace |

Nada inválido llega a la documentación publicada: mientras corriges, sigue publicada la última versión válida. Si un diagrama sigue rechazado después de 3 intentos o 10 días, se escala al equipo de documentación para ayudarte.

**La validación solo corrige lo mecánico** (espacios, formato de fecha). Todo lo que cambia el significado vuelve a ti, porque nadie más sabe qué querías decir con una salida sin etiqueta o una flecha suelta.

## Estados y aprobación

| Estado en la cabecera | Significa | Avisos (W) |
|---|---|---|
| Borrador | En construcción; versiones `0.x` | Permitidos |
| En revisión | Listo para que lo revise un experto | Bloquean |
| Aprobado | Validado; se publica como versión liberada para los equipos de desarrollo | Bloquean |
| Obsoleto | Sustituido por otro proceso o versión | — |

Solo una versión **Aprobada** y sin avisos se libera a los equipos que construyen las aplicaciones. Quien aprueba la *pull request* no puede ser quien la creó.

## Lista de comprobación antes de pasar a En revisión

- [ ] Una sola cabecera, sin textos por defecto, con fecha AAAA-MM-DD.
- [ ] Todas las formas vienen de la biblioteca; ninguna forma suelta de FigJam.
- [ ] Cada decisión es una pregunta con «?» y todas sus salidas tienen etiqueta.
- [ ] Hay un inicio, todos los caminos terminan, y cada paso está dentro de un carril.
- [ ] Sistemas, documentos y anotaciones unidos a su paso con línea punteada.
- [ ] Sin notas adhesivas ni texto suelto pendientes.
- [ ] 15 actividades o menos; el resto, en subprocesos.
