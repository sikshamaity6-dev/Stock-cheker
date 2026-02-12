# Shein Wishlist Checker Bot

## Overview
The Shein Wishlist Checker Bot is an application that allows users to monitor their Shein wishlist and receive notifications about price changes and item availability. This bot is built using Python and utilizes the Shein API to automate the process of checking the wishlist.

## Setup Instructions

### Prerequisites
Before you begin, ensure you have the following software installed:
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps
1. **Clone the repository**
   ```bash
   git clone https://github.com/sikshamaity6-dev/Stock-cheker.git
   cd Stock-cheker
   ```

2. **Install dependencies**
   Use pip to install the required packages. It's recommended to create a virtual environment first:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use 'venv\Scripts\activate'
   pip install -r requirements.txt
   ```

3. **Set up environment variables**  
   Create a `.env` file in the root of the project and add the following variables:
   ```
   SHEIN_EMAIL=your_email@example.com
   SHEIN_PASSWORD=your_password
   ```
   Replace `your_email@example.com` and `your_password` with your Shein account credentials.

4. **Run the Bot**
   To start the bot, run:
   ```bash
   python main.py
   ```

5. **Check Your Wishlist**  
   The bot will automatically check your wishlist at specified intervals and alert you of any changes.

## Usage Instructions
- Ensure that the bot is running to receive notifications.
- You can customize the check interval in the `config.py` file.
- For troubleshooting, check the logs in the `logs/` directory.

## Contribution
Contributions are welcome! Please open an issue or submit a pull request with your suggestions and improvements.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.