# Guia de instalacion

Esta guia describe una instalacion tipica en Linux o Raspberry Pi. En Windows
la aplicacion funciona igual salvo el control de hardware y la impresora.

## 1. Dependencias del sistema

```bash
sudo apt-get update
sudo apt-get install mariadb-server python3-venv
```

Opcional para la impresora y el escaner en Raspberry Pi:

```bash
sudo apt-get install cups python3-cups bluetooth bluez
```

## 2. Entorno de Python

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Base de datos

Crea la base y carga el esquema:

```bash
sudo mysql < sql/schema.sql
```

Despues crea un usuario con permisos sobre `db_labelprint` y anota sus datos:

```sql
CREATE USER 'labelprint'@'localhost' IDENTIFIED BY 'tu-clave';
GRANT ALL PRIVILEGES ON db_labelprint.* TO 'labelprint'@'localhost';
FLUSH PRIVILEGES;
```

## 4. Configuracion

```bash
cp config.example.ini config.ini
```

Edita `config.ini` o define las variables de entorno:

```bash
export LABELPRINT_DB_USER=labelprint
export LABELPRINT_DB_PASSWORD=tu-clave
```

## 5. Ejecucion

```bash
PYTHONPATH=src python3 -m labelprint
```

Tambien puedes usar `./run.sh` desde la raiz del repositorio.

## 6. Etiquetas

Las plantillas HTML viven en `templates/` y las hojas de estilo en `styles/`.
La ruta de ambas se guarda en la tabla `catModelos`. Usa rutas relativas a la
raiz del repositorio para que funcionen en cualquier equipo.

## Problemas frecuentes

- `RPi.GPIO no esta disponible`: la aplicacion se abrio fuera de una Raspberry
  Pi. La ventana funciona, pero el conteo por sensor queda deshabilitado.
- `La impresion no esta disponible`: falta `pycups` o `blabel`.
- `No hay registros`: revisa la conexion y que el esquema se haya cargado.
