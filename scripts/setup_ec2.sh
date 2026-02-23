#!/bin/bash

echo "=== VMS - Setup Servidor EC2 ==="
echo ""

# Atualizar sistema
echo "1. Atualizando sistema..."
sudo apt-get update
sudo apt-get upgrade -y

# Instalar Docker
echo "2. Instalando Docker..."
sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu

# Instalar ferramentas
echo "3. Instalando ferramentas..."
sudo apt-get install -y git curl jq make htop

# Configurar firewall
echo "4. Configurando firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8554/tcp
sudo ufw --force enable

# Criar diretórios
echo "5. Criando estrutura de diretórios..."
mkdir -p /home/ubuntu/backups
mkdir -p /home/ubuntu/logs
mkdir -p /home/ubuntu/actions-runner

# Configurar swap (recomendado para instâncias menores)
echo "6. Configurando swap..."
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Configurar limites do sistema
echo "7. Configurando limites do sistema..."
cat << EOF | sudo tee -a /etc/security/limits.conf
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
EOF

# Otimizações de rede
echo "8. Otimizando rede..."
cat << EOF | sudo tee -a /etc/sysctl.conf
net.core.somaxconn = 1024
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.ip_local_port_range = 10000 65535
EOF
sudo sysctl -p

# Configurar log rotation
echo "9. Configurando log rotation..."
cat << EOF | sudo tee /etc/logrotate.d/vms
/home/ubuntu/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
EOF

# Configurar cron para backups
echo "10. Configurando backup automático..."
(crontab -l 2>/dev/null; echo "0 2 * * * /home/ubuntu/VMS/scripts/backup_db.sh >> /home/ubuntu/logs/backup.log 2>&1") | crontab -

echo ""
echo "=== Setup concluído! ==="
echo ""
echo "Próximos passos:"
echo "1. Relogar para aplicar grupo docker: exit e ssh novamente"
echo "2. Clonar repositório: git clone https://github.com/SEU_USUARIO/VMS.git"
echo "3. Configurar .env: cd VMS && cp .env.example .env && nano .env"
echo "4. Iniciar serviços: docker-compose up -d"
echo "5. Configurar GitHub Actions Runner (ver documentação)"
echo ""
