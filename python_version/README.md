# US Visa Appointment Bot (Python Version)

This is a Python version of the US Visa Appointment Bot that helps automate the process of checking and booking visa appointments.

## Features

- Automated login to the US Visa appointment system
- Continuous checking for available appointment dates
- Automatic booking of earlier appointments when available
- Configurable refresh delay
- Error handling and automatic retry
- Detailed logging

## Requirements

- Python 3.7 or higher
- Required Python packages (listed in `requirements.txt`):
  - requests
  - beautifulsoup4
  - python-dotenv

## Installation

1. Clone the repository
2. Navigate to the `python_version` directory
3. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the `python_version` directory with the following variables:

```env
EMAIL=your_email@example.com
PASSWORD=your_password
SCHEDULE_ID=your_schedule_id
FACILITY_ID=your_facility_id
LOCALE=pt-BR  # or your preferred locale
REFRESH_DELAY=3  # delay in seconds between checks
```

## Usage

Run the bot with your current booked date as an argument:

```bash
python src/visa_bot.py YYYY-MM-DD
```

For example:
```bash
python src/visa_bot.py 2024-12-31
```

The bot will continuously check for earlier appointments and automatically book them when found.

## Logging

The bot logs all activities to the console with timestamps. You can monitor the bot's activity through these logs.

## Error Handling

The bot includes error handling and will automatically retry operations if they fail. If an error occurs, it will log the error and attempt to restart the process.

## Security Note

Keep your `.env` file secure and never commit it to version control. The file is already included in `.gitignore` by default.

## License

This project is licensed under the same terms as the original JavaScript version. 