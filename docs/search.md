# Search Indexer

The `search` module reads perfume records from Google Sheets and saves them to an Algolia index used by the Telegram bot.

## Structure

```text
search/
├── __main__.py
├── requirements.txt
└── app/
    ├── __init__.py
    ├── cls_permume.py
    └── settings.py
```

Note: the filename is currently `cls_permume.py`.

## Configuration

File: `search/app/settings.py`

| Variable | Description |
|---|---|
| `ALGOLIA_APP_ID` | Algolia application ID. |
| `ALGOLIA_BACKEND_API_KEY` | Algolia API key used to save objects. |
| `ALGOLIA_INDEX_NAME` | Target Algolia index. |
| `GOOGLE_SPREADSHEET_ID` | Google spreadsheet ID. |
| `GOOGLE_WORKSHEET_ID` | Numeric worksheet ID. |

`env.seal()` is used, so unexpected environment variables may fail settings loading for this module.

## Perfume Data Class

File: `search/app/cls_permume.py`

```python
@dataclass
class Perfume:
    number: int
    brand: str
    name: str
    description_ru: str
    description_en: str
    description_lt: str
    image_url: str
    image_id: str
    url_ru: str
    url_en: str
    url_lt: str
```

The class provides:

- `as_list()`
- `as_dict()`
- `from_dict()`

Google Sheets record keys must match these dataclass field names.

## Main Flow

File: `search/__main__.py`

```python
async def main():
    wks = get_worksheet()
    all_parfumes = get_all_parfumes(wks)

    async with SearchClient(
        settings.algolia_app_id,
        settings.algolia_backend_api_key,
    ) as client:
        await add_to_algolia(client, all_parfumes)
```

Steps:

1. Connect to Google Sheets with `gspread.service_account()`.
2. Open the spreadsheet by `GOOGLE_SPREADSHEET_ID`.
3. Open the worksheet by `GOOGLE_WORKSHEET_ID`.
4. Convert all records to `Perfume` objects.
5. Save the records to Algolia with `SearchClient.save_objects()`.

## Algolia Records

`add_to_algolia()` currently writes these fields:

```python
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
    "image_id": perfume.image_id,
}
```

`image_url` is present in the local data class but is not currently saved to Algolia.

Example object:

```json
{
  "objectID": 557,
  "name": "Essence",
  "brand": "Narciso Rodriguez",
  "description_ru": "Essence Narciso Rodriguez ...",
  "description_en": "Essence by Narciso Rodriguez ...",
  "description_lt": "Essence Narciso Rodriguez ...",
  "url_ru": "https://example.com/perfume/557",
  "url_en": "https://example.com/perfume/557",
  "url_lt": "https://example.com/perfume/557",
  "image_id": "AgACAg..."
}
```

## Usage

Run indexing:

```bash
python -m search
```

The script logs the first spreadsheet record at warning level and logs each perfume as it is added to the batch.

## Helper Functions

| Function | Description |
|---|---|
| `get_worksheet()` | Opens the configured Google worksheet. |
| `get_all_parfumes()` | Converts worksheet records to `Perfume` objects. |
| `add_to_algolia()` | Saves all records to the configured Algolia index. |
| `search_algolia()` | Legacy helper for synchronous index search style. |
| `get_df_parfumes()` | Builds a pandas DataFrame indexed by the `Number` column. |

## Dependencies

Module requirements are listed in `search/requirements.txt`. The root `pyproject.toml` also includes search-related packages.
