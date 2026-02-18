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

## 3) Crear y activar entorno virtual

```powershell
py -3.11 -m venv venv
venv\Scripts\activate
```

## 4) Instalar dependencias

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Ejecutar el IDE

```powershell
python -m ide.main
```

## 6) (Opcional) Generar ejecutable .exe

```powershell
python build_exe.py
```

## Solución rápida a errores comunes

- **`No module named ide`**: usar `python -m ide.main`.
- **Error instalando PyQt5 en 3.12+**: usar **Python 3.11**.
