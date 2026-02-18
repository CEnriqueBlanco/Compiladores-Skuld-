# Reading Steiner IDE (Skuld)

Primera entrega: interfaz visual (mockup) del IDE para el lenguaje **Skuld** con tema **Lab Member 004**.

## Requisitos

- Python 3.10+ (recomendado)
- Windows

## Instalación

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar el IDE

```powershell
python ide\main.py
```

## Generar ejecutable (.exe)

```powershell
pip install pyinstaller
python build_exe.py
```

El ejecutable se genera en `dist\ReadingSteiner.exe`.

## Alcance de esta entrega

- Ventana principal y paneles completos
- Editor con numeración de líneas
- Explorador de archivos (estructura estática)
- Consola con pestañas y mensajes de ejemplo
- Splash screen con branding
- Tema visual aplicado

## Estructura

```
ide/
  main.py
  main_window.py
  code_editor.py
  file_explorer.py
  console_panel.py
  splash_screen.py
  theme/
    steins_gate_theme.py
examples/
  hello_world.stn
resources/
  icons/
```
