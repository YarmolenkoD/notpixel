import webbrowser
import os
import json
from bot.config import settings

from bot.utils import logger

async def generate_template_html_page(templates: dict):
    html_content = '''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Templates List</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; }
            .template { display: inline-block; margin: 20px; width: 128px; height: 128px; }
            .image-container { display: flex; width: 128px; height: 128px; justify-content: center; align-items: center; }
            img { width: auto; height: auto; border-radius: 8px; object-fit: contain; }
            .templateId { font-weight: bold; }
            .subscribers { color: gray; }
        </style>
    </head>
    <body>
        <h1>Notpixel Templates List</h1>
        <div id="templates">
    '''

    # Generate HTML for each template
    for template in templates:
        html_content += f'''
            <div class="template">
                <div class="image-container">
                    <img src="{template["url"]}" alt="Template {template["templateId"]}">
                </div>
                <p class="templateId">ID: {template["templateId"]}</p>
                <p class="subscribers">Subscribers: {template["subscribers"]}</p>
            </div>
        '''

    # Close HTML tags
    html_content += '''
        </div>
    </body>
    </html>
    '''

    if settings.OPEN_TEMPLATES_LIST_IN_BROWSER:
        with open("templates.html", "w") as file:
            file.write(html_content)
            logger.success(f"Templates page successfully generated to templates.html file")

    with open("templates.json", "w") as file:
        file.write(json.dumps(templates, indent=4))
        logger.success(f"Templates successfully saved to templates.json file")

    if settings.OPEN_TEMPLATES_LIST_IN_BROWSER:
        try:
            file_path = os.path.abspath("templates.html")
            webbrowser.open(f"file://{file_path}")
        except Exception as error:
            logger.warning(f"Can't open templates list page in browser, but you can find templates ids in templates.json file.")