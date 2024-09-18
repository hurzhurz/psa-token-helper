#!/bin/bash
Xvfb $DISPLAY -screen 0 1024x768x8 -nolisten tcp 2>/dev/null >/dev/null &
QTWEBENGINE_DISABLE_SANDBOX=1 python3 psa-token-helper-auto.py $@ 2>/dev/null
