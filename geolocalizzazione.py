
import socket
import locale
locale.getlocale()
## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
ip_address = socket.gethostbyname(hostname)
## printing the hostname and ip_address
#print(f"Hostname: {hostname}")
#print(f"IP Address: {ip_address}")
import geoip2.database

def get_user_info(ip_address):
    """
    Retrieves user information (flag, country, language, and IP) using a local geolocalization library.

    Args:
        ip_address (str): The user's IP address.

    Returns:
        dict: A dictionary containing the user's information.
        
        Keys:
            flag (str): URL of the country's flag.
            country (str): Name of the country.
            language (str): Language spoken in the country.
            ip_address (str): The user's IP address.
    """

    try:
        # Load the GeoLite2 City database
        reader = geoip2.database.Reader('GeoLite2-City.mmdb')

        # Retrieve city information based on IP address
        response = reader.city(ip_address)

        # Extract country information
        country_code = response.country.iso_code
        country_name = response.country.name
        language = response.country.languages[0].name

        # Check if it's a local IP address
        if ip_address.startswith('127.'):
            country_code = 'IT'
            country_name = 'Italy'
            language = 'Italian'# Check if it's a local IP address
        if ip_address.startswith('192.'):
            country_code = 'IT'
            country_name = 'Italy'
            language = 'Italian'

        # Get country flag URL
        flag_url = f"https://flagcdn.com/{country_code.lower()}.svg"

        # Return user information
        return {
            'country_flag': flag_url,
            'country_name': country_name,
            'country_code': country_code,
            'language': language,
            'ip_address': ip_address
        }

    except Exception as e:
        #print(f"Error retrieving user info: {e}")
        #print ("Getting default values Lang: IT")
        return {
            'flag': "No Image Avaliable",
            'country_name': "Italy",
            'country_code': "IT",
            'language': "Italian",
            'ip_address': ip_address
        }
    
user_info=get_user_info(ip_address)
#print (user_info['country'])