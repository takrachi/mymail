#!/usr/bin/env python2.7
import imaplib, email, getpass
from email.header import decode_header
from itertools import cycle
from Crypto.Cipher import AES

# Constantes
FILE_ACC = 'account.enc'
IV = '\x00' * 16
IMAPS = {'outlook.com' : 'imap-mail.outlook.com', 'gmail.com' : 'imap.gmail.com', 'hotmail.com' : 'imap-mail.outlook.com', 'ens.etsmtl.ca' : 'imaps.etsmtl.ca'}

# Classe qui analyse le fichier des comptes chiffre
class Accounts:
    def __init__(self):
        self.key = getpass.getpass('Enter your key : ')
        self.accounts = self.getAccounts()

    def pkcs7_unpad(self, plaintext):
        return plaintext[:len(plaintext)-ord(plaintext[-1:])]

    def getAccounts(self):
        return [i.split(',') for i in self.pkcs7_unpad(AES.new(self.key, AES.MODE_CBC, IV).decrypt(open(FILE_ACC, 'r').read())).split('\n')]

    def list(self):
        for i in self.accounts:
            print "[*] %s" % i[0]

# Classe pour couleurs sur terminal
class colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BGPURPLE = '\033[0;37;45m'

# Fonction qui va chercher les courriels et affiche ceux qui sont non-lu
def getemail(acc):
    print colors.BOLD + "\n==> %s" % acc[0] + colors.ENDC

    # Connection au serveur
    mail = imaplib.IMAP4_SSL(IMAPS[acc[0].split("@")[1]])
    mail.login(acc[0], acc[1])
    mail.select("inbox") 
    
    # Selectionner les courriels marque comme non-lu
    typ, data = mail.uid('search', None, '(UNSEEN)')
    
    # Courriel non-lu trouves
    if data[0] != '':
        print colors.GREEN + " ++ New mails" + colors.ENDC
        uids = data[0].split()
        typ, messages = mail.uid('fetch', ','.join(uids[-5:]), '(BODY.PEEK[HEADER])')
        
        # Parcourt les nouveau courriels
        for _, message in messages[::2]:
            msg_d = decode_header(email.message_from_string(message).get('from'))
            try:
                msg_d = msg_d[0][0].decode(str(msg_d[0][1]))
            except LookupError:
                msg_d = msg_d[0][0].decode('iso-8859-1')

            # Affiche information du courriel
            msg_d = msg_d.split('<')
            print colors.YELLOW + " [From] " + colors.ENDC + "%s" % msg_d[0].replace("\"","").replace('\n','')

    # Aucun nouveau couriel
    else : print colors.RED + " -- No mails" + colors.ENDC

    # Fin
    mail.close()
    mail.logout()

if __name__ == '__main__':
    acc = Accounts()
    [getemail(i) for i in acc.accounts]
