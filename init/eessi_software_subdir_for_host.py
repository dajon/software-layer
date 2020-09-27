#!/usr/bin/env python3
#
# Determine EESSI software subdirectory to use for current build host, using archspec
#
import glob
import os
import sys
import archspec.cpu

VENDOR_MAP = {
    'GenuineIntel': 'intel',
    'AuthenticAMD': 'amd',
}

GENERIC = 'generic'
X86_64 = 'x86_64'

KNOWN_CPU_UARCHS = archspec.cpu.TARGETS


def error(msg):
    sys.stderr.write('ERROR: ' + msg + '\n')
    sys.exit(1)


def warning(msg):
    sys.stderr.write('WARNING: ' + msg + '\n')


if len(sys.argv) == 2:
    eessi_prefix = sys.argv[1]
else:
    error("Usage: %s <prefix path>" % sys.argv[0])

eessi_software_layer_path = os.path.join(eessi_prefix, 'software')
if not os.path.exists(eessi_software_layer_path):
    error("Specified prefix '%s' does not exist!" % eessi_software_layer_path)

# determine host CPU vendor/family/name
host_cpu = archspec.cpu.host()
host_vendor = VENDOR_MAP.get(host_cpu.vendor)
host_cpu_family = host_cpu.family.name
host_cpu_name = host_cpu.name

# determine available targets in 'software' subdirectory of specified prefix (only for host CPU family/vendor)
if host_cpu_family == X86_64:
    paths = glob.glob(os.path.join(eessi_software_layer_path, host_cpu_family, host_vendor, '*'))
    # also consider x86_64/generic
    generic_path = os.path.join(eessi_software_layer_path, host_cpu_family, GENERIC)
    if os.path.exists(generic_path):
        paths.append(generic_path)
else:
    paths = glob.glob(os.path.join(eessi_software_layer_path, host_cpu_family, '*'))

if not paths:
    error("No targets found for " + host_cpu_family)

targets = [os.path.basename(p) for p in paths]

# retain only targets compatible with host, and sort them
target_uarchs = []
for uarch in targets:
    if uarch == GENERIC:
        continue
    if uarch in KNOWN_CPU_UARCHS:
        target_uarchs.append(KNOWN_CPU_UARCHS[uarch])
    else:
        warning("Ignoring unknown target '%s'" % uarch)

host_uarch = KNOWN_CPU_UARCHS[host_cpu_name]
compat_target_uarchs = sorted([x for x in target_uarchs if x <= host_uarch])

if compat_target_uarchs:
    compat_target_names = [x.name for x in compat_target_uarchs]
    cnt = len(compat_target_uarchs)
elif GENERIC in targets:
    compat_target_uarchs = [GENERIC]
else:
    error("No targets compatible with %s found!" % host_uarch)

# last target is best pick for current host
selected_uarch = str(compat_target_uarchs[-1])

if selected_uarch and selected_uarch != GENERIC:
    parts = (host_cpu_family, host_vendor, selected_uarch)
else:
    parts = (host_cpu_family, selected_uarch)

print(os.path.join(*parts))
