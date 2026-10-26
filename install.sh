#!/bin/bash
# ==========================================
#   Netra Recon Installation Script
# ==========================================

set -e
APP_NAME="netra-recon"
INSTALL_DIR="/opt/$APP_NAME"
BIN_PATH="/usr/local/bin/$APP_NAME"
UNINSTALLER="$INSTALL_DIR/uninstall.sh"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_REQ="$SCRIPT_DIR/requirements.txt"

# Colors
RED="\e[31m"; GREEN="\e[32m"; YELLOW="\e[33m"; BLUE="\e[34m"; RESET="\e[0m"

echo ""
echo -e "${BLUE}==========================================${RESET}"
echo -e "${BLUE}        NETRA RECON GLOBAL INSTALLER TOOL        ${RESET}"
echo -e "${BLUE}==========================================${RESET}"
echo ""

# --- Step 1: Privilege check ---
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[❌] Please run this installer as root (sudo ./install.sh)${RESET}"
    exit 1
fi

# --- Step 2: Requirements check ---
command -v python3 >/dev/null 2>&1 || { echo -e "${RED}[ERROR] Python3 not found.${RESET}"; exit 1; }
python3 -m venv --help >/dev/null 2>&1 || {
    echo -e "${RED}[ERROR] Python venv support is missing. Install python3-venv (or python3-full).${RESET}"
    exit 1
}

echo -e "${GREEN}[✔] Python environment verified.${RESET}"

# --- Step 3: Remove old installation ---
echo -e "${YELLOW}[INFO] Cleaning previous installations...${RESET}"
rm -rf "$INSTALL_DIR" "$BIN_PATH"

# --- Step 4: Copy Netra Recon to /opt ---
echo -e "${BLUE}[INFO] Copying Netra Recon source to $INSTALL_DIR...${RESET}"
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/netra_recon" "$INSTALL_DIR/"
cp "$LOCAL_REQ" "$INSTALL_DIR/requirements.txt"
cp "$SCRIPT_DIR/pyproject.toml" "$SCRIPT_DIR/README.md" "$INSTALL_DIR/"

# --- Step 5: Install dependencies in an isolated environment ---
echo -e "${BLUE}[INFO] Creating isolated Python environment...${RESET}"
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/python" -m pip install --upgrade pip
"$INSTALL_DIR/venv/bin/python" -m pip install -r "$INSTALL_DIR/requirements.txt"
chmod -R 755 "$INSTALL_DIR"

# --- Step 6: Create global launcher ---
echo -e "${BLUE}[INFO] Creating global launcher in /usr/local/bin...${RESET}"
cat <<EOF > "$BIN_PATH"
#!/bin/bash
if [ "\$1" == "uninstall" ]; then
    sudo bash $UNINSTALLER
else
    exec /opt/netra-recon/venv/bin/python -m netra_recon "\$@"
fi
EOF
chmod +x "$BIN_PATH"

# --- Step 7: Create uninstaller ---
echo -e "${BLUE}[INFO] Creating uninstaller script...${RESET}"
cat <<'UNINSTALL' > "$UNINSTALLER"
#!/bin/bash
# ==========================================
#   Netra Recon Uninstallation Script (Auto)
# ==========================================
APP_NAME="netra-recon"
INSTALL_DIR="/opt/$APP_NAME"
BIN_PATH="/usr/local/bin/$APP_NAME"
RED="\e[31m"; GREEN="\e[32m"; YELLOW="\e[33m"; BLUE="\e[34m"; RESET="\e[0m"

echo ""
echo -e "${BLUE}==========================================${RESET}"
echo -e "${BLUE}          NETRA RECON UNINSTALLER TOOL          ${RESET}"
echo -e "${BLUE}==========================================${RESET}"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}[❌] Please run as root (sudo netra-recon uninstall)${RESET}"
    exit 1
fi

echo -e "${YELLOW}This will permanently remove Netra Recon.${RESET}"
read -p "Type 'yes' to confirm: " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${YELLOW}[INFO] Uninstallation cancelled.${RESET}"
    exit 0
fi

rm -rf "$INSTALL_DIR" "$BIN_PATH"
echo -e "${GREEN}[✔] Netra Recon successfully removed.${RESET}"
echo ""
UNINSTALL

chmod +x "$UNINSTALLER"

# --- Step 8: Verification ---
echo -e "${BLUE}[INFO] Verifying installation...${RESET}"
"$INSTALL_DIR/venv/bin/python" -c "import netra_recon" >/dev/null && \
echo -e "${GREEN}[✔] Verification successful.${RESET}" || \
{ echo -e "${RED}[❌] Verification failed.${RESET}"; exit 1; }

# --- Step 9: Final summary ---
echo ""
echo -e "${BLUE}==========================================${RESET}"
echo -e "${GREEN}✅ NETRA RECON INSTALLED SUCCESSFULLY (GLOBAL)${RESET}"
echo -e "${BLUE}==========================================${RESET}"
echo ""
echo -e "📦 Location:      $INSTALL_DIR"
echo -e "⚙️  Executable:    $BIN_PATH"
echo -e "📜 Requirements:  Installed from $(basename "$LOCAL_REQ")"
echo -e "🧹 Uninstall via: ${YELLOW}netra-recon uninstall${RESET}"
echo ""
echo -e "🚀 Launch Netra Recon globally using: ${YELLOW}netra-recon${RESET}"
echo ""
echo -e "${BLUE}==========================================${RESET}"
echo ""
