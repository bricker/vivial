FROM node:20

# lang platform dependency installation/build deps
RUN apt update && \
    apt install -y curl git gcc make python3 python3-pip libssl-dev libbz2-dev liblzma-dev

# install pyenv


# Install Python
# Increase the chances that the build will have all dependencies.
# https://github.com/pyenv/pyenv/wiki/Common-build-problems
#    apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
#        libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
#        xz-utils tk-dev libffi-dev liblzma-dev python-openssl git && \
RUN curl https://pyenv.run | bash && \
    export PATH="$HOME/.pyenv/bin:$PATH" && \
    pyenv install 3.11.2

# install nvm
# RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash && \
#     source ~/.bashrc && \
#     nvm install 20

# install postgres? (change docker img name)
#RUN apt install postgres
