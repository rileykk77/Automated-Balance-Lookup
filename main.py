import paramiko
import os
import posixpath
import stat
import json
import lmdb
from openpyxl import Workbook

def sftp_recursive_download(sftp, remote_path, local_path):
    os.makedirs(local_path, exist_ok=True)
    for entry in sftp.listdir_attr(remote_path):
        remote_entry_path = posixpath.join(remote_path, entry.filename)
        local_entry_path = os.path.join(local_path, entry.filename)
        if stat.S_ISDIR(entry.st_mode):
            sftp_recursive_download(sftp, remote_entry_path, local_entry_path)
        else:
            print(f"Downloading {remote_entry_path} to {local_entry_path}")
            sftp.get(remote_entry_path, local_entry_path)

def download_lmdb(remote_host, port, username, private_key_path, remote_lmdb_path, local_lmdb_path, key_passphrase=None):
    # Load private key
    private_key = paramiko.Ed25519Key.from_private_key_file(private_key_path, key_passphrase)
    
    # Establish the transport connection over SSH using private key for authentication
    transport = paramiko.Transport((remote_host, port))
    transport.connect(username=username, pkey=private_key)
    
    # Open SFTP client
    sftp = paramiko.SFTPClient.from_transport(transport)
    
    # Recursively download the LMDB directory
    sftp_recursive_download(sftp, remote_lmdb_path, local_lmdb_path)
    
    sftp.close()
    transport.close()

# Function to process LMDB data
def process_lmdb_data(db_path, output_file, max_entries=10):
    """
    Reads key-value pairs from an LMDB database, processes them, 
    and saves the first `max_entries` pairs to a JSON file.

    Args:
        db_path (str): Path to the LMDB database directory.
        output_file (str): Path to the output JSON file.
        max_entries (int): Maximum number of entries to save.
    """
    with lmdb.open(db_path, readonly=True) as env:
        with env.begin() as txn:
            cursor = txn.cursor()
            result = {}
            count = 0
            
            for key, value in cursor:
                # Convert the key to a readable hexadecimal string
                hex_key = key.hex()
                
                # Try decoding the value to a JSON object
                try:
                    readable_value = value.decode('utf-8')
                    try:
                        # Parse the JSON if the decoded value is JSON-formatted
                        readable_value = json.loads(readable_value)
                    except json.JSONDecodeError:
                        pass  # Keep it as a decoded string if not JSON
                except UnicodeDecodeError:
                    # Fallback to hexadecimal representation if decoding fails
                    readable_value = value.hex()
                
                # Store the processed key-value pair
                result[hex_key] = readable_value
                count += 1
                
                # if count >= max_entries:
                #     break
    # print(count)

    with open(output_file, 'w') as json_file:
        json.dump(result, json_file, indent=4)

def get_balance_of_every_address(jsonfile, outputJson):
    new_json = {}
    total_coins = 0
    with open(jsonfile, 'r') as file:
        data = json.load(file)

    for key, value in data.items():
        address = value["address"]
        amount = value["amount"]
        
        if address not in new_json:
            new_json[address] = {
                "total_amount": 0,
                "entries": {}
            }
        
        new_json[address]["total_amount"] += amount
        total_coins += amount
        
        new_json[address]["entries"][key] = {
            "txOutId": value["txOutId"],
            "txOutIndex": value["txOutIndex"],
            "amount": value["amount"],
            "address": value["address"]
        }

    print(len(new_json))
    # print(new_json["02da1328fdcd8a3c0a2eb6216bc970ac27980583d48d44f04a8541300241a25b93"])
    print(total_coins)

    with open(outputJson, 'w') as file:
        json.dump(new_json, file, indent=4)

    print("New JSON structure created successfully!")


def get_balance_of_every_address_excel(jsonfile, output_xlsx):
    new_dict = {}
    total_coins = 0
    
    # Read your original JSON data
    with open(jsonfile, 'r') as file:
        data = json.load(file)
    
    # Process the data and sum up amounts by address
    for key, value in data.items():
        address = value["address"]
        amount = value["amount"]
        
        if address not in new_dict:
            new_dict[address] = 0
        
        new_dict[address] += amount
        total_coins += amount
    
    print(f"Unique addresses: {len(new_dict)}")
    print(f"Total coins: {total_coins}")

    # Create a new workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active
    ws.title = "Balances"

    # Write the header row
    ws.append(["Address", "Balance"])
    sorted_data = sorted(new_dict.items(), key=lambda x: x[1], reverse=True)

    # Write each address and its total balance to the sheet
    for address, balance in sorted_data:
        ws.append([address, balance])
    
    # Save the workbook to the specified output file
    wb.save(output_xlsx)
    print("Excel file created successfully!")


if __name__ == "__main__":
    remote_host = '188.166.1.234'
    port = 22
    username = 'root'
    private_key_path = os.path.expanduser("~/.ssh/id_ed25519")
    remote_lmdb_path = '/home/dragon/node/utxo'
    local_lmdb_path = '/Users/riley_work/Documents/codes/Automated-Balance-Lookup/data/utxo'
    
    # If your private key has a passphrase, set it here; otherwise, leave as None
    key_passphrase = None  
    
    download_lmdb(remote_host, port, username, private_key_path, remote_lmdb_path, local_lmdb_path, key_passphrase)

    # read lmdb
    # Path to your LMDB data file
    db_path = './data/utxo'

    # File to store the JSON output
    output_file = 'utxo_lmdb_entries.json'
    process_lmdb_data(db_path, output_file)

    # balance_sheet = 'balances.json'
    # get_balance_of_every_address(output_file, balance_sheet)

    get_balance_of_every_address_excel(output_file,'sorted_balance.xlsx')


