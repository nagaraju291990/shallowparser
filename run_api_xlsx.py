import pandas as pd
import requests
import sys
import json
# Load the Excel file
file_path = sys.argv[1]  # Update this with your actual file path
lang = sys.argv[2]  # Language code, e.g., 'hin' for Hindi
df = pd.read_excel(file_path, engine='openpyxl')

# Optional: Rename columns if needed
# df.columns = ['Index', 'Sentence_ID', 'Text']

# Create a dictionary to store API responses
results = {}

# Function to call your API
def call_api(text):
	url = "https://ssmt.iiit.ac.in/shallow_parser_for_mt"  # Replace with your API endpoint
	payload = {"text": text, 'language': lang, 'mode': 'list' }  # Adjust payload as per your API requirements
	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json'
	}
	r = requests.post(url, headers=headers, json=payload)
	output = json.loads(r.text)
	return output

output = []

# Iterate over the rows and call the API
for idx, row in df.iterrows():
	sentence_id = row['Sentence_id']
	text = row['Malayalam']
	try:
		response = call_api(text)
	except:
		reponse = {"error": "API call failed for sentence ID {}".format(sentence_id)}
	results = {"sentence_id": sentence_id, "result": response, 'text': text}
	output.append(results)
# Print or process the results
print(output)
