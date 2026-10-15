"""
Chat con el Agente Recomendador de Instrumentos Musicales
TFG — Noelia FC
"""
import time
import uuid
import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.rule import Rule

BASE_URL = "http://127.0.0.1:2024"
AGENT    = "assistant"

# Usuario fijo para las pruebas (el que tiene 2 reviews: Korg + LED)
USER_ID  = "AGCI7FAH4GL5FI65HYLKWTMFZ2CQ"

console = Console()


def chat():
    sesion = f"chat_{uuid.uuid4().hex[:8]}"

    console.print(Rule("[bold]Agente Recomendador Musical[/bold]"))
    console.print(f"[dim]Usuario: {USER_ID}[/dim]")
    console.print(f"[dim]Sesión:  {sesion}[/dim]")
    console.print("[dim]'salir' para salir · 'nueva' para nueva conversación[/dim]\n")

    es_primer_mensaje = True

    while True:
        try:
            texto = console.input("[bold cyan]Tú ›[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not texto:
            continue
        if texto.lower() in ("salir", "exit"):
            break
        if texto.lower() == "nueva":
            console.print()
            chat()
            return

        # En el primer mensaje identificamos al usuario de forma transparente
        if es_primer_mensaje:
            prompt_completo = f"Soy el usuario {USER_ID}. {texto}"
            es_primer_mensaje = False
        else:
            prompt_completo = texto

        _enviar(prompt_completo, sesion)


    console.print("\n[dim]Hasta luego.[/dim]\n")


def _enviar(prompt: str, sesion: str):
    url = f"{BASE_URL}/agents/{AGENT}/{sesion}"
    try:
        t0 = time.time()
        r  = requests.post(url, json={"prompt": prompt}, timeout=120)
        dt = round(time.time() - t0, 1)

        if r.status_code == 200:
            texto = r.json().get("text", "")
            console.print(f"\n[bold green]Agente[/bold green] [dim]({dt}s)[/dim]")
            console.print(Markdown(texto))
            console.print()
        elif r.status_code == 429:
            console.print("[yellow]⚠ Cuota de API agotada. Espera un momento.[/yellow]\n")
        else:
            try:
                err = r.json().get("error", {}).get("details", r.text)
            except Exception:
                err = r.text
            console.print(f"[red]Error {r.status_code}:[/red] {err}\n")

    except requests.exceptions.ConnectionError:
        console.print("[red]✗ Sin conexión. ¿Está corriendo 'pyflue dev'?[/red]\n")
    except requests.exceptions.Timeout:
        console.print("[yellow]⚠ Tiempo de espera agotado.[/yellow]\n")


if __name__ == "__main__":
    chat()