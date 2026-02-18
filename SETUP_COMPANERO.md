# Guía rápida para instalar (Windows)

Esta guía es para un compañero que **no tiene nada instalado**.

## 1) Instalar Python 3.11

Opción recomendada con `winget`:

```powershell
winget install -e --id Python.Python.3.11
```

Luego verifica:

```powershell
py -0p
```

Debe aparecer `3.11` en la lista.

## 2) Descargar el proyecto

- Clona el repositorio o descarga el ZIP y descomprímelo.
- Abre una terminal en la carpeta `Compiladores-Skuld-`.

## 3) Configurar entorno del proyecto (recomendado)

Ejecuta el script de setup una sola vez:

```powershell
.\setup_env.ps1
```

Esto crea `.venv311` con **Python 3.11** e instala dependencias.

## 4) Ejecutar el IDE

```powershell
.\run_ide.ps1
```

## 5) Alternativa manual (si no quieres scripts)

```powershell
py -3.11 -m venv .venv311
.venv311\Scripts\activate
```

## 6) Instalar dependencias (modo manual)

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 7) Ejecutar el IDE (modo manual)

```powershell
python -m ide.main
```

## Atajos útiles dentro del IDE

- `Ctrl+F`: buscar texto en el editor activo.
- `Ctrl+S`: guardar archivo actual.
- `Ctrl+G`: guardar como.
- `Ctrl+1`: alternar (abrir/cerrar) panel Analizadores.
- `Ctrl+2`: alternar (abrir/cerrar) panel Terminal.
- `Ctrl+3`: alternar (abrir/cerrar) Árbol de archivos.

## Paneles laterales e inferiores

- En los paneles de **Analizadores** y **Terminal** hay:
	- botón `_` para minimizar.
	- botón `✕` para cerrar temporalmente.
- Si los cierras, vuelve a abrirlos con `Ctrl+1`, `Ctrl+2` o `Ctrl+3`.

## 6) (Opcional) Generar ejecutable .exe

```powershell
python build_exe.py
```

## Solución rápida a errores comunes

- **`No module named ide`**: usar `python -m ide.main`.
- **Error instalando PyQt5 en 3.12+**: usar **Python 3.11**.
