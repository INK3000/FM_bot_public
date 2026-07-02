import asyncio

import betterlogging as logging
import gspread
import pandas as pd
from algoliasearch.search.client import SearchClient

from .app.cls_permume import Perfume
from .app.settings import settings

logging.basic_colorized_config(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_worksheet():
    logger.info("Connecting to Google Sheets")
    sa = gspread.service_account()
    logger.info("Opening FM Parfumes worksheet")
    sh = sa.open_by_key(settings.google_sheet_id)
    logger.info("Getting all records from All worksheet")
    wks = sh.get_worksheet_by_id(settings.google_wks_id)
    return wks


def get_all_parfumes(wks: gspread.worksheet.Worksheet):
    all_records = wks.get_all_records()
    logger.warning(all_records[0])
    all_parfumes = [Perfume.from_dict(record) for record in all_records]
    return all_parfumes


async def add_to_algolia(client, data):
    # index = client.init_index(settings.algolia_index_name)

    logger.info("Starting saving all parfumes to Algolia... \n")
    records = []
    for idx, perfume in enumerate(data, start=1):
        logger.info(f'Saving "{perfume.name}" to Algolia ({idx}/{len(data)})')
        record = {
            "objectID": perfume.number,
            "name": perfume.name,
            "brand": perfume.brand,
            "description_ru": perfume.description_ru,
            "description_lt": perfume.description_lt,
            "description_en": perfume.description_en,
            "url_ru": perfume.url_ru,
            "url_lt": perfume.url_lt,
            "url_en": perfume.url_en,
            "image_id": perfume.image_id
        }
        records.append(record)
    await client.save_objects(
        index_name=settings.algolia_index_name,
        objects=records,
    )
    # index.save_objects(records).wait()
    logger.info("Finished saving all parfumes to Algolia")


def search_algolia(client, query):
    index = client.init_index(settings.algolia_index_name)
    return index.search(query)


def get_df_parfumes(wks):
    df = pd.DataFrame.from_records(wks.get_all_records())
    df.set_index("Number", inplace=True)
    return df


async def main():
    wks = get_worksheet()
    all_parfumes = get_all_parfumes(wks)

    async with SearchClient(settings.algolia_app_id, settings.algolia_backend_api_key) as client:
        await add_to_algolia(client, all_parfumes)

    # Search for duplicates
    # df = get_df_parfumes(wks)
    # ic(df[['Name', 'Brand']][df.duplicated(keep=False, subset=['Description'])])



if __name__ == "__main__":
    asyncio.run(main())
