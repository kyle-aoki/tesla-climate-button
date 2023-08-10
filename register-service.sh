sudo cp tesla-ac-button.service /etc/systemd/system/tesla-ac-button.service
sudo systemctl enable tesla-ac-button.service
sudo systemctl start tesla-ac-button.service
sudo systemctl status tesla-ac-button.service

# sudo systemctl stop tesla-ac-button.service
# sudo journalctl -u tesla-ac-button.service --no-pager
