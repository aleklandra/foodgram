import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from recipes.models import Ingredient

from foodgram import settings

DATA_DICT = {
    'ingredients.csv': Ingredient,
}


class Command(BaseCommand):
    help = 'Insert csv into data model'

    def handle(self, *args, **options):
        dir = Path(f'{settings.BASE_DIR}/data')

        for file in DATA_DICT:
            with open(Path(dir, file), 'r', encoding="utf8") as f:
                dict_file = csv.DictReader(f)
                foodgram_data = [DATA_DICT[file](**row) for row in dict_file]
                DATA_DICT[file].objects.all().delete()
                DATA_DICT[file].objects.bulk_create(foodgram_data)
