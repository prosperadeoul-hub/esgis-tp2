import json
import boto3
import os
from botocore.exceptions import ClientError
from datetime import datetime

# 1. RÉCUPÉRATION DYNAMIQUE (Variable d'env envoyée par ton template)
# On ne met plus 's3-trigger-db' en dur pour éviter toute confusion
TABLE_NAME = os.environ.get('DYNAMODB_TABLE')
REGION_NAME = os.environ.get('AWS_REGION_NAME', 'eu-west-3')

# Initialisation du client DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=REGION_NAME)
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    print(f"Utilisation de la table : {TABLE_NAME}")
    
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']
        
        # 2. FILTRE EXTENSION (N'ajouter que des images)
        extensions_valides = ('.jpg', '.jpeg', '.png')
        if not file_key.lower().endswith(extensions_valides):
            print(f"Fichier rejeté (Format non image) : {file_key}")
            continue

        try:
            # 3. FILTRE DOUBLONS (Sur TA table kadeoul-...)
            response = table.get_item(Key={'id': file_key})
            
            if 'Item' in response:
                print(f"Doublon détecté : '{file_key}' est déjà présent dans {TABLE_NAME}.")
            else:
                # Si le nom du fichier n'existe pas, on l'ajoute
                print(f"Nouveau fichier détecté. Ajout de '{file_key}'...")
                table.put_item(
                    Item={
                        'id': file_key,
                        'bucket': bucket_name,
                        'added_at': datetime.now().isoformat(),
                        'owner': 'kadeoul'
                    }
                )
                print(f"Succès : '{file_key}' inséré dans {TABLE_NAME}.")

        except ClientError as e:
            print(f"Erreur DynamoDB : {e.response['Error']['Message']}")
            
    return {
        'statusCode': 200,
        'body': json.dumps('Traitement terminé')
    }