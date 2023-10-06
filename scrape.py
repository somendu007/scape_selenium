import time
import uuid
from selenium import webdriver
import psycopg2


driver_path = '/Users/somendupatel/Downloads/chrome-mac-arm64'
driver = webdriver.Chrome(executable_path=driver_path)

# LinkedIn account URL to scrape
account_url = 'https://www.linkedin.com/company/chelsea-football-club/'

# PostgreSQL database connection parameters
db_params = {
    'database': 'your_database_name',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'your_database_host',
    'port': 'your_database_port',
}

def scrape_linkedin_account_info():
    driver.get(account_url)
    time.sleep(5)  # Add a delay to allow page to load

    # Extract account information
    account_name = driver.find_element_by_xpath('//h1[@class="org-top-card-summary__title t-24 t-black truncate"]/span').text
    followers = int(driver.find_element_by_xpath('//a[@data-control-name="org_profile_about_link_followers"]/span').text.replace(',', ''))
    profile_image_url = driver.find_element_by_xpath('//div[@class="org-top-card-primary-content__logo rounded-1"]/img').get_attribute('src')
    bio = driver.find_element_by_xpath('//p[@class="break-words"]').text

    # Generate a unique UUID for the account_id
    account_id = uuid.uuid4()

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Check if the account already exists in the database
    cursor.execute("SELECT COUNT(*) FROM social_account_info WHERE account_url = %s", (account_url,))
    existing_record_count = cursor.fetchone()[0]

    if existing_record_count > 0:
        # Update the existing record
        cursor.execute("UPDATE social_account_info SET name = %s, followers = %s, profile_image_url = %s, bio = %s, updated_date_utc = current_timestamp WHERE account_url = %s", (account_name, followers, profile_image_url, bio, account_url))
    else:
        # Insert a new record
        cursor.execute("INSERT INTO social_account_info (account_id, platform, account, account_url, name, followers, profile_image_url, bio) VALUES (%s, 'linkedin', %s, %s, %s, %s, %s, %s)", (account_id, account_url, account_name, account_url, followers, profile_image_url, bio))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    scrape_linkedin_account_info()
    driver.quit()
