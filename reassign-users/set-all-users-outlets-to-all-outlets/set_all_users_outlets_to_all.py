# This script will set all users to have access to all outlets in Lightspeed Retail.
# Do not edit this file, instead, run the script with the following command:
# python3 set_all_users_outlets_to_all.py -t API_TOKEN -d DOMAIN_PREFIX -p CURRENT_USER_PASSWORD

import requests
import argparse

class Client:
  def __init__(self, token, domain_prefix, current_user_password):
    self.token = token
    self.current_user_password = current_user_password
    self.base_url = f"https://{domain_prefix}.retail.lightspeed.app"
    self.headers = {
      "Content-Type": "application/json",
      "authorization": f"Bearer {self.token}",
      "Origin": self.base_url
    }

    self.params = {
      "page_size": 10000,  # just being lazy and don't want to figure out pagination
      "deleted": "false"
    }

  def parse_response(self, response):
    if response.status_code == 200:
      json_response = response.json()
      return json_response
    else:
      return {
        "error": response.status_code,
        "message": response.text
      }

  def get_all_user_ids(self):
    url = f"{self.base_url}/api/2.0/users"
    response = requests.get(url, headers=self.headers, params=self.params)
    data = self.parse_response(response)
    if "error" in data:
      raise Exception("Request to get users failed")
    
    ids = [entry['id'] for entry in data['data']]
    return ids
  
  def set_all_users_to_all_outlets(self):
    count = 0
    user_ids = self.get_all_user_ids()
    for user_id in user_ids:
      response = self.set_user_to_all_outlets(user_id)
      if "error" in response:
        print(f"Failed to update user {user_id}, request failed with message {response['message']}")
        continue
      count += 1
    print("All done! Updated %s users" % count)


  def set_user_to_all_outlets(self, user_id):
    graphql_endpoint = f"{self.base_url}/api/graphql"
    # GraphQL mutation
    mutation_query = """
    mutation {
      editUser(request: {
        id: "%s",
        currentUserPassword: "%s",
        outletIds: []
      }) {
        user {
          id
          username
        }
        validations {
          outletInvalid
        }
      }
    }
    """ % (user_id, self.current_user_password)
    
    payload = {
        "query": mutation_query
    }

    response = requests.post(graphql_endpoint, json=payload, headers=self.headers)
    return self.parse_response(response)

def main():
  parser = argparse.ArgumentParser(description='Set all users to all outlets')
  parser.add_argument('-t', type=str, help='Lightspeed API token')
  parser.add_argument('-d', type=str, help='Lightspeed domain prefix')
  parser.add_argument('-p', type=str, help='Current user password')
  args = parser.parse_args()

  token = args.t
  domain_prefix = args.d
  current_user_password = args.p

  client = Client(token, domain_prefix, current_user_password)
  client.set_all_users_to_all_outlets()

if __name__ == "__main__":
  main()
