import base58
import json

# Remplacez ceci par votre clé privée en base58
base58_private_key = '4dLa3N6gsf1V8zPFdxB3yEx7iNkFszQczWbx4J7QqQbmJ5g7nmBAzrPqBhEr7EKsKssmd1py9qAbLqiWAMgYEMig'

# Décoder la clé privée en bytes
private_key_bytes = base58.b58decode(base58_private_key)

# Vérifier la longueur de la clé privée
if len(private_key_bytes) != 64:
    raise ValueError("La clé privée doit comporter 64 octets.")

# Convertir les bytes en une liste d'entiers
private_key_list = list(private_key_bytes)

# Enregistrer la liste dans un fichier JSON
with open('phantom_keypair.json', 'w') as f:
    json.dump(private_key_list, f)

print("Le fichier 'phantom_keypair.json' a été créé avec succès.")
