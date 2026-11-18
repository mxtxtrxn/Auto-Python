# Auto-Python

Aplicacion de escritorio para la impresion de etiquetas en una linea de
produccion. La interfaz esta hecha con Tkinter, los catalogos se guardan en
MySQL o MariaDB y las etiquetas se generan en PDF con `blabel`.

## Funcionalidad

- Catalogos de clientes, modelos y numeros de parte.
- Escaneo de codigos de barras para identificar el numero de parte.
- Conteo de piezas y cierre automatico de producciones.
- Impresion de etiquetas a partir de plantillas HTML y hojas de estilo CSS.
- Ventana de administracion protegida con usuario y contrasena.

## Estructura

```text
Auto-Python/
  src/labelprint/
    __main__.py            punto de entrada
    app.py                 ventana principal y flujo de produccion
    config.py              lectura de configuracion
    database.py            conexion a MySQL y llamadas a procedimientos
    repositories/          acceso a datos por catalogo
    ui/                    ventanas de administracion
  templates/               plantillas HTML para las etiquetas
  styles/                  hojas de estilo de las etiquetas
  sql/schema.sql           esquema y datos de ejemplo
  docs/INSTALL.md          guia de instalacion
  tests/                   pruebas
```

## Requisitos

- Python 3.9 o superior.
- MySQL 8 o MariaDB 10.5.
- `mysql-connector-python` y `blabel`.
- Para la linea de produccion: `RPi.GPIO` y `pycups` en Raspberry Pi.

## Puesta en marcha

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp config.example.ini config.ini
```

Edita `config.ini` con los datos de tu servidor e importa el esquema:

```bash
mysql -u root -p < sql/schema.sql
```

Despues inicia la aplicacion desde la raiz del repositorio:

```bash
PYTHONPATH=src python3 -m labelprint
```

En Windows el entorno se activa con `.venv\Scripts\Activate.ps1` y el comando
es `$env:PYTHONPATH="src"; python -m labelprint`.

## Configuracion

La conexion se toma de `config.ini`. Las variables de entorno tienen prioridad:

| Variable | Valor por defecto |
| --- | --- |
| `LABELPRINT_DB_HOST` | `localhost` |
| `LABELPRINT_DB_DATABASE` | `db_labelprint` |
| `LABELPRINT_DB_USER` | `labelprint` |
| `LABELPRINT_DB_PASSWORD` | vacio |

No guardes `config.ini` en el repositorio. Ya esta incluido en `.gitignore`.

## Datos de ejemplo

El esquema crea el cliente `Cliente Demo`, el modelo `Modelo Base` y el numero
de parte `PN-1001`. Todos los datos son ficticios. La cuenta de administracion
de ejemplo es `supervisor` con la contrasena `demo1234`; cambiala antes de usar
la aplicacion en un entorno real.

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest
```

## Notas

- Las rutas de plantillas y estilos se guardan en la base de datos y son
  relativas a la raiz del repositorio.
- En equipos sin `RPi.GPIO`, `pycups` o `blabel` la ventana principal abre en
  modo limitado y muestra el aviso correspondiente.
