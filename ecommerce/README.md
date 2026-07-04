Installing WeasyPrint (and system dependencies)

This project uses WeasyPrint to generate PDF invoices. WeasyPrint requires system libraries (Cairo, Pango, GDK-PixBuf) in addition to the Python package. Below are concise, tested steps for Windows (MSYS2 recommended) and Fedora Linux.

Important: On Windows, using WSL (Ubuntu) or a Linux container is often simpler than installing native build deps. If possible, prefer WSL or Docker for production PDF generation.

Windows (MSYS2):

1. Install MSYS2 from https://www.msys2.org/ and follow the installer instructions.
2. Open the MSYS2 MinGW 64-bit shell and update packages:

pacman -Syu
# If prompted, close and re-open the MinGW64 shell, then run:
pacman -Su

3. Install the required libraries (run in the MSYS2 MinGW64 shell):

pacman -S --noconfirm mingw-w64-x86_64-cairo mingw-w64-x86_64-pango mingw-w64-x86_64-gdk-pixbuf mingw-w64-x86_64-libffi mingw-w64-x86_64-libpng mingw-w64-x86_64-libjpeg-turbo

4. Add the MSYS2 mingw64/bin directory to your Windows PATH (or run Python/pip from the MSYS2 shell).

5. Install the Python package in your virtualenv:

python -m pip install --upgrade pip
pip install weasyprint
# Optional fallback
pip install xhtml2pdf

Alternative (Windows / WSL):

If you use WSL (recommended), follow the Linux instructions in a WSL shell.

Fedora Linux:

Install system dependencies and then install the Python package:

sudo dnf install -y cairo pango gdk-pixbuf2 libffi libjpeg-turbo-devel libpng-devel
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install weasyprint
# Optional fallback
pip install xhtml2pdf

Verify installation:

python -c "import weasyprint; print('weasyprint', weasyprint.__version__)"

If the import succeeds and prints a version, WeasyPrint is ready.

If you want, I can also add a short CI step (GitHub Actions) to install the system deps inside a container for automated testing. Would you like that?
