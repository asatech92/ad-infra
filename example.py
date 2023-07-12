import requests

def vulnerable_function():
    # Insecure request
    response = requests.get('https://insecure-site.com')
    return response.text

def main():
    data = vulnerable_function()
    print(data)

if __name__ == '__main__':
    main()
