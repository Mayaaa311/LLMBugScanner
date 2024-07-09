#!/bin/bash

# Function to download llama2 model
download_llama2() {
    echo "Downloading llama-2-7b.Q5_K_M.gguf model..."
    mkdir -p models
    cd models
    huggingface-cli download TheBloke/Llama-2-7B-GGUF llama-2-7b.Q5_K_M.gguf --local-dir . --local-dir-use-symlinks False
    cd ..
    echo "llama-2-7b.Q5_K_M.gguf model downloaded successfully!"
}

# Function to download llama3 model
download_llama3() {
    echo "Downloading llama3 model..."
    curl -fsSL https://ollama.com/install.sh | sh
    ollama pull llama3
    echo "llama3 model downloaded successfully!"
}

# Function to download codellama model
download_codellama() {
    echo "Downloading codellama model..."
    curl -fsSL https://ollama.com/install.sh | sh
    ollama pull codellama
    echo "codellama model downloaded successfully!"
}

# Function to download all models
download_all() {
    download_llama2
    download_llama3
    download_codellama
}

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --model)
            MODEL="$2"
            shift
            ;;
        *)
            echo "Unknown parameter passed: $1"
            exit 1
            ;;
    esac
    shift
done

# Execute the appropriate function based on the model specified
case $MODEL in
    llama2)
        download_llama2
        ;;
    llama3)
        download_llama3
        ;;
    codellama)
        download_codellama
        ;;
    *)
        echo "No model or invalid model specified. Downloading all models..."
        download_all
        ;;
esac
