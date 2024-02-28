# Dokumentation des Projekts

![Beispielergebniss](data/poem_2024-02-08-21-01-46.png)

Dieses Projekt besteht aus mehreren Teilen:
- der Poetry-Client Poetry-DB, der von der PoetryDB-API gedichte abruft. (poetry_client.api.PoetryDB)
- der Image-Generator, der aus dem Gedicht ein Bild generiert. (ptoimg.pti.ImageGenerator)

Aus dem Projektverzeichnis kann das Programm mit folgendem Befehl gestartet werden:
``` bash
poetry run python -m src/wppproject
```

## Poetry-API

``` python
    @typechecked
    def get_poems_by_author(self, author: str) -> dict:
        """Get poems by a specific author."""
        return self._get(f"author/{author}")
```

Über den ***Decorator*** `typechecked` aus dem Paket `typeguard` werden die Parameter und Rückgabewerte mittels der ***Type Hints*** an die API überprüft. So ist sichergestellt, dass keine falschen Werte übergeben werden und die API auch die erwarteten Werte zurückgibt.

Wenn ein Fehler bei dem Request auftaucht, wird ein Wertefehler erhoben. Dieser muss dann in der aufrufenden Funktion behandelt werden: 
``` python
    try:
        poem = pdb.get_random_poems(1, min_lines=2, max_lines=20)
        print(poem)
    except Exception as e:
        print(e)
        print("Failed to get a poem.")
        exit(1)
```
Hier wird auf das ***Try-Except***-Konstrukt gesetzt, da zu erwarten ist, dass es hier normalerweise nicht zum Fehlerfall kommt, es also nur selten zu dem zeitaufwendigen Fall der Exception kommt.

Durch einen selbst geschriebenen ***Decorator*** wird die Laufzeit der Funktion `get_random_poems` gemessen und ausgegeben. Das ist sinvoll, um einen Eindruck von der Laufzeit der API zu bekommen. 

``` python
    def timer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"Time taken: {round(end - start, 2)}s for {func.__name__}.")
            return result
        return wrapper
```

Aus der ***Config***-Datei wird die URL für die API geladen. Sollte diese nicht vorhanden sein, wird auf den Standardwert zurückgegriffen. So kann, sollte der Server der API umziehen, die URL in der Config-Datei angepasst werden, ohne dass der Code geändert werden muss.
    
    
## Image Generator

Aus dem Gedicht soll ein Bild generiert werden. Dabei kommt OpenAI zum Einsatz. Sollte kein API-Key vorhanden sein, wird ein zufälliges der bereits erzeugten Bilder wieder verwendent. In der Config-Datei kann OpenAI deaktiviert werden und der Bildstyle angeasst werden. Da die API von OpenAI nicht kostenlos ist, wird vor jeder Anfrage geprüft, ob die Anfrage durchgeführt werden soll. Der Bildstyle wird durch DALL-E interpretiert, weshalb ein beliebiger Text eingegeben werden kann. 

Über die API wird im Onlinemodus auch Audio generiert und wiedergegeben. 

## PyTests 

In vier ***PyTests*** wird die Funktionalität der API getestet. Dabei kommen ***Asserts*** zum Einsatz. An sonstigen Stellen im Code werden keine Asserts verwendet, da diese nicht in der Produktionsumgebung laufen sollten. Sie dienen onehin nur zur Fehlerfindung und -behebung. So sind sie für die Tests gut geeignet. Die Tests prüfen die Methoden `get_poems_by_author`, `get_poems_by_title`, `get_random_poems` und `get_poem_lines_by_title` auf ihre Funktionalität.
