import requests

url = "http://reserve.rit.edu"  # Replace with your target URL

# Send GET request and allow it to follow redirects
response = requests.get(url, allow_redirects=True)

# Print the final URL after all redirects
print("Final URL:", response.url)

# Print the HTML content of the landing page
print(response.text)
