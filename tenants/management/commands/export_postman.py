import os
import json
import subprocess
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Exports OpenAPI schema and converts it to a refined Postman collection.'

    def handle(self, *args, **options):
        schema_file = 'schema.yml'
        collection_file = 'sovereign_postman_collection.json'
        
        self.stdout.write(self.style.SUCCESS('Generating OpenAPI Schema...'))
        subprocess.run(['python3', 'manage.py', 'spectacular', '--file', schema_file], check=True)
        
        self.stdout.write(self.style.SUCCESS(f'Converting {schema_file} to Postman Collection...'))
        subprocess.run(['npx', '-y', 'openapi-to-postmanv2', '-s', schema_file, '-o', collection_file], check=True)
        
        self.stdout.write(self.style.SUCCESS('Refining Postman Collection with Tenant Variables...'))
        self.refine_collection(collection_file)
        
        if os.path.exists(schema_file):
            os.remove(schema_file)
            
        self.stdout.write(self.style.SUCCESS(f'Successfully delivered {collection_file} 🥂🚀🏛️'))

    def refine_collection(self, file_path):
        with open(file_path, 'r') as f:
            collection = json.load(f)

        variables = collection.get('variable', [])
        
        # Add tenant_slug if missing
        if not any(v['key'] == 'tenant_slug' for v in variables):
            variables.append({
                "key": "tenant_slug",
                "value": "acme",
                "type": "string"
            })

        # Update baseUrl
        for var in variables:
            if var['key'] == 'baseUrl':
                var['value'] = 'http://{{tenant_slug}}.localhost:8000'

        collection['variable'] = variables

        with open(file_path, 'w') as f:
            json.dump(collection, f, indent=2)
