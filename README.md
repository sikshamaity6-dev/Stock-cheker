# Shein Wishlist Checker Bot

## Overview
The Shein Wishlist Checker Bot is a tool designed to help users monitor their Shein wishlists. It alerts users when items from their wishlist go on sale or become available.

## Features
- **Real-time Monitoring**: Keeps track of wishlist items.
- **Price Alerts**: Notifies when there are changes in prices.
- **Availability Notifications**: Alerts when out-of-stock items come back in stock.

## Prerequisites
- Python 3.6 or higher
- Basic knowledge of how to use command-line interfaces

## Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/sikshamaity6-dev/Stock-cheker.git
   cd Stock-cheker
   ```
2. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
- Create a configuration file named `config.json` in the root directory with the following structure:
   ```json
   {
     "wishlist_items": [
       "item_url_1",
       "item_url_2"
     ],
     "notification_settings": {
       "email": true,
       "sms": false
     }
   }
   ```

## Usage
1. **Run the bot**:
   ```bash
   python shein_wishlist_checker.py
   ```
2. **Check your notifications**: Set up your preferred notification method as specified in the configuration file.

## Contribution
Feel free to submit pull requests for any new features or bug fixes.

## License
This project is licensed under the MIT License.

## Acknowledgments
- Thanks to all contributors and the open-source community.