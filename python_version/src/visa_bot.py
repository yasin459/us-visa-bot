#!/usr/bin/env python3

import os
import time
import logging
from datetime import datetime
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class VisaBot:
    def __init__(self):
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.schedule_id = os.getenv('SCHEDULE_ID')
        self.facility_id = os.getenv('FACILITY_ID')
        self.locale = os.getenv('LOCALE', 'pt-BR')
        self.refresh_delay = int(os.getenv('REFRESH_DELAY', '3'))
        self.base_uri = f'https://ais.usvisa-info.com/{self.locale}/niv'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

    def login(self) -> None:
        """Login to the visa appointment system."""
        logger.info("Logging in")
        
        # Get initial cookies and CSRF token
        response = self.session.get(f'{self.base_uri}/users/sign_in')
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
        
        # Perform login
        login_data = {
            'utf8': '✓',
            'user[email]': self.email,
            'user[password]': self.password,
            'policy_confirmed': '1',
            'commit': 'Acessar',
            'authenticity_token': csrf_token
        }
        
        self.session.post(
            f'{self.base_uri}/users/sign_in',
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        )

    def check_available_date(self) -> Optional[str]:
        """Check for available appointment dates."""
        url = f'{self.base_uri}/schedule/{self.schedule_id}/appointment/days/{self.facility_id}.json'
        params = {'appointments[expedite]': 'false'}
        
        response = self.session.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            raise Exception(data['error'])
            
        return data[0]['date'] if data else None

    def check_available_time(self, date: str) -> Optional[str]:
        """Check for available appointment times on a specific date."""
        url = f'{self.base_uri}/schedule/{self.schedule_id}/appointment/times/{self.facility_id}.json'
        params = {
            'date': date,
            'appointments[expedite]': 'false'
        }
        
        response = self.session.get(url, params=params)
        data = response.json()
        
        if 'error' in data:
            raise Exception(data['error'])
            
        return (data.get('business_times', [None])[0] or 
                data.get('available_times', [None])[0])

    def book_appointment(self, date: str, time: str) -> None:
        """Book an appointment for the specified date and time."""
        url = f'{self.base_uri}/schedule/{self.schedule_id}/appointment'
        
        # Get fresh CSRF token
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']
        
        booking_data = {
            'utf8': '✓',
            'authenticity_token': csrf_token,
            'confirmed_limit_message': '1',
            'use_consulate_appointment_capacity': 'true',
            'appointments[consulate_appointment][facility_id]': self.facility_id,
            'appointments[consulate_appointment][date]': date,
            'appointments[consulate_appointment][time]': time,
            'appointments[asc_appointment][facility_id]': '',
            'appointments[asc_appointment][date]': '',
            'appointments[asc_appointment][time]': ''
        }
        
        self.session.post(
            url,
            data=booking_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )

    def run(self, current_booked_date: str) -> None:
        """Main loop to check and book appointments."""
        if not current_booked_date:
            logger.error(f"Invalid current booked date: {current_booked_date}")
            return

        logger.info(f"Initializing with current date {current_booked_date}")
        
        try:
            self.login()
            
            while True:
                date = self.check_available_date()
                
                if not date:
                    logger.info("No dates available")
                elif date > current_booked_date:
                    logger.info(f"Nearest date is further than already booked ({current_booked_date} vs {date})")
                else:
                    current_booked_date = date
                    time = self.check_available_time(date)
                    
                    if time:
                        self.book_appointment(date, time)
                        logger.info(f"Booked time at {date} {time}")
                
                time.sleep(self.refresh_delay)
                
        except Exception as e:
            logger.error(f"Error occurred: {str(e)}")
            logger.info("Trying again")
            self.run(current_booked_date)

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python visa_bot.py <current_booked_date>")
        sys.exit(1)
        
    current_booked_date = sys.argv[1]
    bot = VisaBot()
    bot.run(current_booked_date)

if __name__ == '__main__':
    main() 