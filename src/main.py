import json
import boto3
import os
from botocore.exceptions import ClientError
from datetime import datetime

# 1. Utilisation des variables d'environnement passées par le template
TABLE_NAME = os.environ.get('DYNAMODB_TABLE', 's3-trigger-db')
REGION_NAME = os.environ.get('AWS_REGION_NAME', 'eu-west-3')

# Initialisation du client DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=REGION_NAME)
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    print("Event reçu: ", json.dumps(event))
    
    for record in event['Records']:
        # Récupération des infos S3
        bucket_name = record['s3']['bucket']['name']
        file_key = record['s3']['object']['key']
        
        print(f"Analyse du fichier : {file_key}")

        try:
            #on vérifie si le fichier existe déjà dans la BD
            response = table.get_item(Key={'id': file_key})
            
            if 'Item' in response:
                print(f"Action annulée : Le fichier '{file_key}' existe déjà dans la table {TABLE_NAME}.")
            else:
                # Si le fichier n'existe pas, on l'ajoute
                print(f"Le fichier '{file_key}' est nouveau. Insertion en cours...")
                table.put_item(
                    Item={
                        'id': file_key,
                        'bucket': bucket_name,
                        'added_at': datetime.now().isoformat(),
                        'status': 'PROCESSED'
                    }
                )
                print(f"Succès : '{file_key}' ajouté à DynamoDB.")

        except ClientError as e:
            print(f"Erreur lors de l'accès à DynamoDB : {e.response['Error']['Message']}")
            return {
                'statusCode': 500,
                'body': json.dumps("Erreur lors du traitement")
            }
    
    return {
        'statusCode': 200,
        'body': json.dumps('Traitement terminé avec succès !')
    }