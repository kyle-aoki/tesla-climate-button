sudo cp tesla-climate-button.service /etc/systemd/system/tesla-climate-button.service
sudo systemctl enable tesla-climate-button.service
sudo systemctl start tesla-climate-button.service
sudo systemctl status tesla-climate-button.service

# sudo systemctl stop tesla-climate-button.service
# sudo journalctl -u tesla-climate-button.service --no-pager
