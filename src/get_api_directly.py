import requests

def call_api(api_url, api_key=None):
    try:
        headers = {"Authorization: ApiKey {api_key}"} if api_key else {}

        response = requests.get(api_url, api_key)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Print or process the API response
            print("API Response:")
            print(response.json())
        else:
            # Print the error message if the request was not successful
            print(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"An error occurred: {e}")


# Example usage:
api_url = 'https://search.dip.bundestag.de/api/v1/plenarprotokoll/18001'
api_key = 'rgsaY4U.oZRQKUHdJhF9qguHMkwCGIoLaqEcaHjYLF'

#response = call_api(api_url, api_key=api_key)
response = requests.get('https://search.dip.bundestag.de/api/v1/plenarprotokoll?f.id=908&f.id=0&format=json&apikey=rgsaY4U.oZRQKUHdJhF9qguHMkwCGIoLaqEcaHjYLF')
print(response)
