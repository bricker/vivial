FROM node:18

# lang platform dependency installation/build deps
RUN apt update && \
    apt install -y curl git gcc make python3 python3-pip libssl-dev libbz2-dev liblzma-dev

# Install Python
RUN curl https://pyenv.run | bash && \
    export PATH="$HOME/.pyenv/bin:$PATH" && \
    pyenv install 3.11.2 && \
    alias python=python3
