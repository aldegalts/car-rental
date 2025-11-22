from fastapi.templating import Jinja2Templates
import os

# Определяем путь к папке с шаблонами
templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
templates = Jinja2Templates(directory=templates_dir)

