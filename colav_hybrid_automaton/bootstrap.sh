# Install nvm if you don't have it
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc

# Install and use Node 20
nvm install 20
nvm use 20
nvm alias default 20

# Now install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

pip install -r ./requirements.txt

# 3 Clone colav-interfaces repository
cd ~/ros2_ws/src && git clone 

# build colav-interfaces, then build colav-interfaces colav-hybrid-automaton-interfaces and colav-hybrid-automaton

