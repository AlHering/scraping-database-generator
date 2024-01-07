#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

printf "\n%s\n" "${delimiter}"
printf "Creating virtualenv environment"
printf "\n%s\n" "${delimiter}"
python3.10 -m "$VENV_DIR" venv_cpu
source "${VENV_DIR}/bin/activate"

if [[ "$CUDA_SUPPORT" = "true" ]]
then
    REQUIREMENTS="${SCRIPT_DIR}/requirements_pip_gpu.txt"
else
    REQUIREMENTS="${SCRIPT_DIR}/requirements_cpu.txt"
fi
fi
printf "\n%s\n" "${delimiter}"
printf "Installing pip requirements"
printf "\n%s\n" "${delimiter}"
python -m pip install --no-cache-dir -r "${REQUIREMENTS}"

printf "\n%s\n" "${delimiter}"
printf "Finished installation"
printf "\n%s\n" "${delimiter}"

exit 0
