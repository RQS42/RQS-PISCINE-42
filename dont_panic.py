# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    dont_panic.py                                      :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: RQS_42 <RQS_42@student.42.fr>            +#+  +:+       +#+           #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2026/08/19 00:28:54 by RQS_42           #+#    #+#               #
#    Updated: 2026/08/19 00:28:54 by RQS_42          ###   ########.fr         #
#                                                                              #
# **************************************************************************** #

#!/usr/bin/env python3
"""
🏊 42 Piscine Exam Simulator - Universal Launcher
Unified cross-platform simulator for macOS, Linux, and Windows.
Supports encrypted exercise pools, structured exam archives,
and full progression statistics.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from deep_thought_core.improbability_drive import ExamEngine


def main():
    try:
        engine = ExamEngine(BASE_DIR)
        engine.start_shell()
    except KeyboardInterrupt:
        print("\nExiting examshell. Good luck with your Piscine!")
        sys.exit(0)


if __name__ == "__main__":
    main()
