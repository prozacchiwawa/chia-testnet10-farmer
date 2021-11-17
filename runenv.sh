#!/bin/bash

CERTSFILE="/tmp/chia.${PPID}"
if curl -o ${CERTSFILE} http://localhost:9987/config.tgz ; then
    CHIA_ROOT_DIR="/tmp/chia.${PPID}.root"
    mkdir -p "${CHIA_ROOT_DIR}"
    (cd "${CHIA_ROOT_DIR}" && tar xf "${CERTSFILE}")
    export CHIA_ROOT="${CHIA_ROOT_DIR}/mainnet"
    echo "using CHIA_ROOT=${CHIA_ROOT}" >&2
    exec /bin/bash
else
    echo "Failed to download ssl chia root data.  Docker image might not be running" >&2
    exit 1
fi
