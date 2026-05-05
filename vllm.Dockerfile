FROM rocm/pytorch:rocm7.2.2_ubuntu24.04_py3.12_pytorch_release_2.8.0
ENV ROCM_PATH=/opt/rocm
ENV LD_LIBRARY_PATH=$ROCM_PATH/lib:$LD_LIBRARY_PATH
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y git python3-pip && rm -rf /var/lib/apt/lists/*

# Install the ROCm-specific vLLM wheel
RUN pip install --no-cache-dir https://github.com/vllm-project/vllm/releases/download/v0.7.2/vllm-0.7.2+rocm62-cp312-cp312-linux_x86_64.whl

EXPOSE 8000
WORKDIR /app
ENTRYPOINT ["python3", "-m", "vllm.entrypoints.openai.api_server"]
