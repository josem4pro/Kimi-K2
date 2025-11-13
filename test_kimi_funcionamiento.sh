#!/bin/bash
# Script de prueba para verificar el funcionamiento de kimi y sus alias

echo '═══════════════════════════════════════════════'
echo 'PRUEBA DE KIMI K2 THINKING EN LENOVO'
echo '═══════════════════════════════════════════════'
echo ''

echo '1. Verificando instalación del script...'
if [ -x ~/.local/bin/kimi ]; then
    echo '   ✓ Script kimi instalado y ejecutable'
else
    echo '   ✗ Script kimi NO encontrado'
    exit 1
fi

echo ''
echo '2. Verificando dependencias Python...'
~/Kimi-K2/venv/bin/python3 -c 'import dotenv, openai' 2>/dev/null
if [ $? -eq 0 ]; then
    echo '   ✓ Dependencias Python OK (dotenv, openai)'
else
    echo '   ✗ Faltan dependencias Python'
    exit 1
fi

echo ''
echo '3. Verificando archivo .env...'
if [ -f ~/.env ] && grep -q CHUTES_API_KEY ~/.env; then
    echo '   ✓ Archivo .env con CHUTES_API_KEY configurado'
else
    echo '   ✗ Falta .env o CHUTES_API_KEY'
    exit 1
fi

echo ''
echo '4. Verificando alias en .bash_aliases...'
if grep -q 'kimih' ~/.bash_aliases && grep -q 'kimis' ~/.bash_aliases; then
    echo '   ✓ Alias kimih y kimis configurados'
else
    echo '   ✗ Faltan alias en .bash_aliases'
    exit 1
fi

echo ''
echo '5. Prueba funcional del script (help)...'
~/.local/bin/kimi --help > /tmp/kimi_help_test.txt 2>&1
if [ $? -eq 0 ]; then
    echo '   ✓ Script kimi responde correctamente'
else
    echo '   ✗ Error al ejecutar kimi'
    exit 1
fi

echo ''
echo '═══════════════════════════════════════════════'
echo '✓✓✓ TODAS LAS PRUEBAS PASARON ✓✓✓'
echo '═══════════════════════════════════════════════'
echo ''
echo 'Uso en sesión interactiva:'
echo '  kimi          - Modo interactivo'
echo '  kimis "..."   - Simple mode (rápido)'
echo '  kimih "..."   - Heavy mode (8 trayectorias)'
echo ''
