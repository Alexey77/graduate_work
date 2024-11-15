from datetime import datetime

import mwparserfromhell
from pydantic import BaseModel


class WikiPage(BaseModel):
    page_id: int
    title: str
    wikitext: str
    text: str | None = None
    url: str
    source: str
    lang: str
    revision_id: int
    created_at: datetime
    updated_at: datetime
    time_request: datetime

    def model_post_init(self, __context):
        if self.text is None and self.wikitext:
            wikicode = mwparserfromhell.parse(self.wikitext)
            self.text = wikicode.strip_code()

